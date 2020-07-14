from collections import defaultdict
from goto import with_goto
from functional_notations import F as f_
from tqdm import tqdm

from uvpn.domains.dmc import crop, Box2Grid
from functools import partial
from ml_logger import logger
import numpy as np
from params_proto.neo_proto import ParamsProto
from torch import optim
import torch.nn.functional as F
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch_utils import torchify, Eval
from uvpn import Agent
from uvpn.memory.linear_buffer import ImageBuffer, BaseBuffer
from uvpn.models import *
from uvpn.maze.networks.policies.discrete_action import *
from uvpn.graph import MeshMemory

from graph_search import methods


def reg(img):
    c, *size = img.shape
    if c == 1:
        return img[0]
    else:
        return img.transpose([1, 2, 0])


class Args(ParamsProto):
    seed = 100
    env_id = "CMazeDiscreteImgIdLess-v0"
    test_env_id = None
    frame_skip = 4
    frame_stack = 1
    env_kwargs = None
    test_env_kwargs = None
    env_wrappers = Box2Grid,
    test_env_wrappers = None

    norm_p = 2

    render_size = None
    img_size = 64
    input_dim = 1
    latent_dim = 10
    act_dim = 3, 3
    local_metric = "Conv"
    adv = "AdvPeg"

    lr = 3e-4
    batch_size = 32

    prune_regression = False

    graph_n = 1000
    buffer_n = 30_000
    neighbor_r = 2
    neighbor_r_min = None
    graph_d_min = 1
    term_r = 1
    prune_r = 1
    k_steps = 1  # the number of steps for each waypoint

    device = None
    debug = False

    train_sample_limit = 3

    pretrain_n_rollouts = 200
    pretrain_lm_n_epochs = 5

    pretrain_inv_m_n_rollouts = 2000
    pretrain_inv_m_n_epochs = 40

    graph_n_rollouts = 3000
    pair_n_rollouts = None

    v_fn_n_epochs = 100

    adv_use_soft = False

    checkpoint = None

    # motion planning
    enable_analytics = False
    prune_stuck = True
    soft_prune = False  # need hard pruning for value distillation
    debug_no_plan2vec = False

    gred_relabel = "backward"
    train_uvpn = False  # UVPN/GRED selector

    ep_limit = 20


# if Args.enable_analytics:
#     import matplotlib.pyplot as plt

# noinspection PyAttributeOutsideInit
class UVPN(Agent):

    # @proto_partial(Args, method=True)
    def __init__(self, *, graph_n, buffer_n, latent_dim, neighbor_r, neighbor_r_min=0, ):

        Args.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.log_params(Args=vars(Args))

        lm_cls = eval(Args.local_metric)

        self.local_metric = lm_cls(input_dim=Args.input_dim, latent_dim=Args.latent_dim,
                                   p=Args.norm_p).to(Args.device)
        self.value_fn = lm_cls(input_dim=Args.input_dim, latent_dim=Args.latent_dim,
                               p=Args.norm_p).to(Args.device)

        adv_cls = eval(Args.adv)
        self.inv_m = adv_cls(input_dim=Args.input_dim, latent_dim=Args.latent_dim,
                             act_dim=Args.act_dim).to(Args.device)
        self.adv = adv_cls(input_dim=Args.input_dim, latent_dim=Args.latent_dim,
                           act_dim=Args.act_dim).to(Args.device)

        # log all models
        logger.log_text(str(self.local_metric), "models/f_local_metric.txt")
        logger.log_text(str(self.value_fn), "models/value_fn.txt")
        logger.log_text(str(self.inv_m), "models/inv_m.txt")
        logger.log_text(str(self.adv), "models/adv.txt")

        self.pairs = ImageBuffer(buffer_n)
        self.test_pairs = ImageBuffer(400)  # this is the test set.
        self.value_pairs = BaseBuffer(buffer_n)  # for value learning
        self.gred_pairs = BaseBuffer(buffer_n)  # for value learning

        embed_fn = f_ @ self.embed_fn @ self.proc_img

        self.graph = MeshMemory(kernel_fn=self.kernel_fn, n=graph_n,
                                latent_dim=latent_dim, neighbor_r=neighbor_r,
                                neighbor_r_min=neighbor_r_min, enable_soft_prune=Args.soft_prune,
                                embed_fn=embed_fn)

        logger.upload_file(__file__)

    def proc_img(self, *imgs):
        if len(imgs) == 1:
            return crop(imgs[0] / 255, w=Args.img_size)
        return [crop(img / 255, w=Args.img_size) for img in imgs]

    @torchify(method=True, dtype=torch.float)
    def embed_fn(self, *args):
        args = [a.to(Args.device) for a in args]
        with Eval(self.local_metric):
            return self.local_metric.embed(*args)

    @torchify(method=True, dtype=torch.float)
    def kernel_fn(self, *args):
        args = [a.to(Args.device) for a in args]
        with Eval(self.local_metric):
            return self.local_metric.kernel(*args)

    @torchify(method=True, dtype=torch.float)
    def inv_m_fn(self, *args):
        args = [a.to(Args.device) for a in args]
        with Eval(self.inv_m):
            return self.inv_m.hard(*args)

    @torchify(method=True, dtype=torch.float)
    def π(self, *args):
        args = [a.to(Args.device) for a in args]
        with Eval(self.adv):
            if Args.adv_use_soft:
                return self.adv.soft(*args)
            else:
                return self.adv.hard(*args)

    env = None
    rng = None

    def create_env(self, env_id, seed, *wrappers, **env_kwargs):
        import gym

        env = gym.make(env_id, **env_kwargs)
        for w in wrappers:
            env = w(env)

        self.env = env
        self.env.seed(Args.seed)
        self.rng = np.random.RandomState(seed)

    obs_keys = ["img", "goal_img", "a_cont"]

    def sample_uniform(self, num_rollouts=10, T=3, d0=1, to_graph=False, split="train"):
        from uvpn.maze import sample_from_env

        extra_keys = ['x'] if Args.enable_analytics else []
        trajs = sample_from_env(self.env, self.rng, num_rollouts=num_rollouts,
                                obs_keys=self.obs_keys + extra_keys, limit=T)

        for traj_i, traj in enumerate(tqdm(trajs, desc="add traj")):
            imgs, a = traj['img'], traj['a']
            from uvpn.domains.dmc import stack_frame

            imgs = stack_frame(imgs, Args.frame_stack)
            a = a[Args.frame_stack - 1:]
            a_cont = traj['a_cont'][Args.frame_stack - 1:]

            l = len(imgs)
            if split == "train":
                end = self.pairs.images.end
                self.pairs.extend(imgs, a=a, a_cont=a_cont,
                                  img=end + np.arange(l - 1, dtype=int),
                                  img_next=end + np.arange(1, l, dtype=int))
            # note: train and test sets are mutually exclusive
            elif split == "test":
                end = self.test_pairs.images.end
                self.test_pairs.extend(imgs, a=a, a_cont=a_cont,
                                       img=end + np.arange(l - 1, dtype=int),
                                       img_next=end + np.arange(1, l, dtype=int))

            if to_graph:  # this is how you add new nodes to the memory
                zs = self.graph.embed_fn(imgs)
                # self.graph.add(zs, img)
                # new sparse add implementation, should work better.
                for i, (z, img) in enumerate(zip(zs, imgs)):
                    v, d = self.graph.localize(z, r=d0)
                    if d is None:
                        self.graph.add(z[None, :], imgs=img[None, :],
                                       meta=traj['x'][i:i + 1] if Args.enable_analytics else None)

                # todo: overwrite when multiple calls to sample_uniform.
                logger.log(graph_nodes=len(self.graph.nodes), num_traj=traj_i, flush=True)

        if to_graph:
            print('finished adding to graph.')

        # logger.print(self.pairs, self.test_pairs, self.graph.summary, sep="\n")

    @staticmethod
    def img_collate(a_cont=None, a=None, proc=None, proc_opt=None, **kwargs):
        iterator = proc(*kwargs.values(), **proc_opt) if callable(proc) else kwargs.values()
        d = [torch.FloatTensor(v).to(Args.device) / 255 for v in iterator]

        if a is not None:
            d.append(torch.LongTensor(a).to(Args.device))
        if a_cont is not None:
            d.append(torch.FloatTensor(a_cont).to(Args.device))
        return d

    def eval_metric(self, metric_fn, batch_size=16):
        l1 = F.smooth_l1_loss
        with torch.no_grad(), Eval(metric_fn):
            for (x, x_prime, a_cont), (x_perm,) in zip(
                    self.test_pairs.sample_all(batch_size, "@img", "@img_next", "a_cont", collate=self.img_collate),
                    self.test_pairs.sample_all(batch_size, "@img", collate=self.img_collate)):
                d_bar = metric_fn(x, x_prime).squeeze()
                d_shuffle = metric_fn(x, x_perm).squeeze()
                d_target = a_cont.norm(dim=-1, p=Args.norm_p)
                loss = l1(d_bar, d_target) + self.rev_hinge_loss(d_shuffle, d_target.mean() * 2)

                logger.store_metrics(loss=loss.item(), d_bar=d_bar.mean().item(), d_target=d_target.mean().item(),
                                     d_shuffle=d_shuffle.mean().item(), prefix="eval/")

    @staticmethod
    def rev_hinge_loss(x, y: float):
        d = x - torch.ones_like(x, requires_grad=False) * y
        return - (d * (d < 0).float()).mean()

    lm_optimizer = None

    # @proto_partial(Args, method=True)
    def train_local_metric(self, n_epoch=1, lr=1e-4, batch_size=16, checkpoint_interval=None, evaluate=True):

        l1 = F.smooth_l1_loss
        self.lm_optimizer = self.lm_optimizer or optim.Adam(self.local_metric.parameters(), lr=lr)
        # self.lm_scheduler = ReduceLROnPlateau(self.lm_optimizer)

        with logger.PrefixContext("local_metric"):
            logger.log_params(lm=dict(n_epoch=n_epoch, lr=lr, batch_size=batch_size,
                                      n_images=len(self.pairs), checkpoint_interval=checkpoint_interval))
            for epoch in range(n_epoch):
                for (x, x_prime, a_cont), (x_perm,) in zip(
                        self.pairs.sample_all(batch_size, "@img", "@img_next", "a_cont", collate=self.img_collate),
                        self.pairs.sample_all(batch_size, "@img", collate=self.img_collate)):
                    d_bar = self.local_metric(x, x_prime).squeeze()
                    d_shuffle = self.local_metric(x, x_perm).squeeze()
                    d_target = a_cont.norm(dim=-1, p=Args.norm_p)
                    loss = l1(d_bar, d_target) + self.rev_hinge_loss(d_shuffle, d_target.mean() * 2)

                    loss.backward()
                    self.lm_optimizer.step()
                    self.lm_optimizer.zero_grad()

                    with torch.no_grad():
                        logger.store_metrics(loss=loss.mean().item(), d_bar=d_bar.mean().item(),
                                             d_target=d_target.mean().item(), d_shuffle=d_shuffle.mean().item())

                if evaluate:
                    self.eval_metric(self.local_metric, batch_size=batch_size)
                    # self.lm_scheduler.step(logger.summary_cache.get("eval/loss").mean())

                logger.log_metrics_summary(
                    key_values=dict(epoch=epoch, dt_epoch=logger.split("epoch")))

                if logger.every(checkpoint_interval, "lm/epoch"):
                    logger.save_module(self.local_metric, f"models/lm_{epoch + 1}.pkl", chunk=20_000_000)
                    logger.remove(f"models/lm_{epoch}.pkl")

    v_fn_optimizer = None

    def train_value_fn(self, n_epoch=1, lr=1e-4, batch_size=16, checkpoint_interval=None, evaluate=True):

        graph = self.graph
        buffer = self.value_pairs
        search = methods['dijkstra']
        all_images = self.graph.images
        proc = self.proc_img
        tfy = lambda x: torch.FloatTensor(x).to(device=Args.device)

        l1 = F.smooth_l1_loss
        l1_flat = nn.SmoothL1Loss(reduction='none')
        self.v_fn_optimizer = self.v_fn_optimizer or optim.Adam(self.value_fn.parameters(), lr=lr)
        # self.lm_scheduler = ReduceLROnPlateau(self.lm_optimizer)

        with logger.PrefixContext("value_fn"):
            logger.log_text("""
            charts:
            - yKey: loss/mean
              yDomain: [0, 1.2]
            - yKey: eval/loss/mean
              yDomain: [0, 1.2]
            - d_far/mean
            - d_far_target/mean
            """, ".charts.yml", dedent=True, overwrite=True)
            logger.log_text(self.graph.summary, "README.md", dedent=True)
            if Args.enable_analytics:
                self.graph.plot_2d("figures/graph.png", show=False)

            logger.log_params(v_fn=dict(n_epoch=n_epoch, lr=lr, batch_size=batch_size,
                                        n_images=len(self.pairs), checkpoint_interval=checkpoint_interval))
            for epoch in range(n_epoch):
                for (x, x_prime, a_cont), (x_perm,) in zip(
                        self.pairs.sample_all(batch_size, "@img", "@img_next", "a_cont", collate=self.img_collate),
                        self.pairs.sample_all(batch_size, "@img", collate=self.img_collate)):
                    loss = 0

                    d_bar = self.value_fn(x, x_prime).squeeze()
                    # d_shuffle = self.value_fn(x, x_perm).squeeze()
                    d_target = a_cont.norm(dim=-1, p=Args.norm_p)
                    local_loss = l1(d_bar, d_target)  # + self.rev_hinge_loss(d_shuffle, d_target.mean() * 2)
                    loss += local_loss  # in-place, same reference.

                    if not Args.debug_no_plan2vec:
                        # new stuff here
                        l = len(buffer)
                        while len(buffer) < min(buffer.maxlen, l + batch_size):
                            start, goal = graph.sample(2)
                            path, ds = search(graph, start, goal)
                            if ds is None:
                                logger.log(f"can not find good path for {start}, {goal}")
                                continue
                            buffer.add(s=start, g=goal, d=sum(ds))

                        batch = buffer.sample(batch_size)
                        # todo: need to proc o_s, o_g together.
                        o_s, o_g = f_ @ tfy @ proc(all_images[batch['s']], all_images[batch['g']])
                        d_far_target = f_ @ tfy @ batch['d']

                        d_far = self.value_fn(o_s, o_g).squeeze()
                        mask = (d_far_target > (2 * d_target.mean())).float()
                        plan_loss = torch.mean(l1_flat(d_far, d_far_target) * mask)
                        loss += plan_loss
                        logger.store_metrics(plan_loss=plan_loss.item(),
                                             d_far=d_far.mean().item(),
                                             d_far_target=d_far_target.mean().item())

                    loss.backward()
                    self.v_fn_optimizer.step()
                    self.v_fn_optimizer.zero_grad()

                    with torch.no_grad():
                        logger.store_metrics(loss=loss.item(),
                                             local_loss=local_loss.item(),
                                             d_bar=d_bar.mean().item(),
                                             d_target=d_target.mean().item(), )
                        # d_shuffle=d_shuffle.mean().item())

                if evaluate:
                    self.eval_metric(self.value_fn, batch_size=batch_size)
                    # self.lm_scheduler.step(logger.summary_cache.get("eval/loss").mean())

                logger.log_metrics_summary(
                    key_values=dict(epoch=epoch, dt_epoch=logger.split("epoch")))

                if logger.every(checkpoint_interval, "value_fn/epoch"):
                    logger.save_module(self.value_fn, f"models/v_fn_{epoch + 1}.pkl", chunk=20_000_000)
                    logger.remove(f"models/v_fn_{epoch}.pkl")

    def eval_inv_m(self, policy, batch_size=16):
        collate = partial(self.img_collate, proc=crop, proc_opt=dict(w=Args.img_size))

        criteria = torch.nn.CrossEntropyLoss()
        with torch.no_grad(), Eval(policy):
            for x, x_prime, action in \
                    self.test_pairs.sample_all(batch_size, "@img", "@img_next", "a", collate=collate):
                # we need to loss for lr scheduling, so need the logits.
                act_logits = policy(x, x_prime)
                loss = criteria(act_logits.reshape(-1, act_logits.shape[-1]),
                                action.reshape(-1))

                life_is_hard = torch.argmax(act_logits, dim=-1).cpu().numpy()
                logger.store_metrics({"eval/accuracy": (life_is_hard == action.cpu().numpy()).mean(),
                                      "eval/loss": loss.item()})

    inv_m_optimizer = None

    def train_inv_m(self, n_epoch=1, lr=1e-4, batch_size=16, checkpoint_interval=None, evaluate=True):

        criteria = torch.nn.CrossEntropyLoss()
        self.inv_m_optimizer = self.inv_m_optimizer or optim.Adam(self.inv_m.parameters(), lr=lr)
        # self.inv_m_scheduler = ReduceLROnPlateau(self.inv_m_optimizer)

        from uvpn.domains.dmc import random_crop
        from functools import partial
        collate = partial(self.img_collate, proc=random_crop, proc_opt=dict(w=Args.img_size))

        with logger.PrefixContext("inv_m"):
            logger.log_params(inv_m=dict(n_epoch=n_epoch, lr=lr, batch_size=batch_size,
                                         n_images=len(self.pairs), checkpoint_interval=checkpoint_interval))
            for epoch in range(n_epoch):
                for x, x_prime, action in self.pairs.sample_all(
                        batch_size, "@img", "@img_next", "a", collate=collate):
                    a_bar = self.inv_m(x, x_prime)
                    # for high-dimensional discrete actions
                    loss = criteria(a_bar.reshape(-1, a_bar.shape[-1]), action.reshape(-1))

                    loss.backward()
                    self.inv_m_optimizer.step()
                    self.inv_m_optimizer.zero_grad()

                    with torch.no_grad():
                        life_is_hard = torch.argmax(a_bar, dim=-1).cpu().numpy()
                        logger.store_metrics({"train/accuracy": (life_is_hard == action.cpu().numpy()).mean()},
                                             loss=loss.item())

                if evaluate:
                    self.eval_inv_m(self.inv_m, batch_size=batch_size)
                    # self.inv_m_scheduler.step(logger.summary_cache.get("eval/loss").mean())

                # todo: eval_inv_m
                logger.log_metrics_summary(key_values=dict(epoch=epoch, dt_epoch=logger.split("epoch")))

                if logger.every(checkpoint_interval, "inv_m/epoch"):
                    logger.save_module(self.inv_m, f"models/inv_m_{epoch + 1}.pkl", chunk=20_000_000)
                    logger.remove(f"models/inv_m_{epoch}.pkl")

    def adv_eval_pruning(self, env=None, task=None, limit=None, stuck_r=None, prune_r=None, to_graph=False):

        zs, old_zs = None, None

        def prune_stuck(self, *, o, img_current, obs, **_):
            """code for pruning and adding new experience to the graph"""
            nonlocal zs, old_zs
            if to_graph:
                spots = self.graph.add(imgs=img_current[None, ...],
                                       meta=obs['x'][None, ...] if Args.enable_analytics else None)
                old_zs, zs = zs, self.graph.zs[spots]
            else:
                old_zs, zs = zs, self.graph.embed_fn(obs['img'][None, ...])

            # graph pruning code
            if old_zs is not None and self.kernel_fn(zs, old_zs) < stuck_r:
                self.graph.remove_incoming(zs[0], r=prune_r)

        return self.adv_eval_simple(env=env, task=task, limit=limit, before_step=prune_stuck, )

    def adv_eval_simple(self, env=None, task=None, limit=None, before_step=None):
        proc = self.proc_img
        env = env or self.env

        stack = defaultdict(list)

        if task is not None:
            obs = env.unwrapped.reset_model(*task)
        else:
            obs = env.reset()

        img_current = obs['img']
        img_goal = obs['goal_img']

        logger.clear("adv")
        while not limit or logger.count("adv") < limit:
            o = f_ @ proc @ img_current
            o_g = f_ @ proc @ img_goal
            if callable(before_step):
                before_step(**locals())

            act, = self.π(o, o_g)

            stack['img'].append(img_current)
            stack['goal_img'].append(img_goal)
            stack['a'].append(act)

            if Args.enable_analytics:
                stack['x'].append(obs['x'])
                stack['goal'].append(obs['goal'])

            obs, r, done, _ = env.step(act)
            img_current = obs['img']
            a_cont = obs['a_cont']
            stack['a_cont'].append(a_cont)

            if np.linalg.norm(a_cont, Args.norm_p) < 1e-2:
                logger.print(f"agent is not acting: [{a_cont}]")

            if done:
                return stack, True

        stack['img'].append(img_current)
        stack['goal_img'].append(img_goal)
        return stack, False

    def sample_adv(self, env=None, task=None, d0=1, limit=None, to_graph=True):
        proc = self.proc_img
        embed = self.embed_fn
        env = env or self.env

        stack = defaultdict(list)

        # todo:
        #   1. set start and goal
        #   2. sample
        #   3. visualize pruned edges.
        # maze specific.
        if task is not None:
            obs = env.unwrapped.reset_model(*task)
        else:
            obs = env.reset()

        img_current = obs['img']
        img_goal = obs['goal_img']
        z_s, z_g = f_ @ embed @ proc(img_current, img_goal)
        d2g = self.kernel_fn(z_s, z_g)

        logger.clear("adv")
        while not limit or logger.count("adv") < limit:
            o = f_ @ proc @ img_current
            o_g = f_ @ proc @ img_goal

            act, = self.π(o, o_g)

            stack['img'].append(img_current)
            stack['goal_img'].append(img_goal)
            stack['a'].append(act)

            obs, r, done, _ = env.step(act)
            if Args.enable_analytics:
                stack['a_cont'].append(obs['a_cont'])

            if done:
                return stack, True

            img_current = obs['img']
            old_z_s, (z_s,) = z_s, f_ @ embed @ [proc(img_current)]
            old_d2g, d2g = d2g, self.kernel_fn(z_s, z_g)
            delta = self.kernel_fn(z_s, old_z_s)

            if to_graph:
                v, d = self.graph.localize(z_s, r=d0)
                if d is None:
                    self.graph.add(z_s[None, :], imgs=img_current[None, :],
                                   meta=[obs['x']] if Args.enable_analytics else None)

            if delta < 0.4:  # the agent has stopped
                logger.print(f"agent is stuck with 𝛿d({delta})")
                # self.graph.remove_toward(z_s, z_g, r=Args.neighbor_r, r0=0.4, d0=0.2)
                self.graph.remove_incoming(z_s, r=0.4)
                return stack, False

            # todo-1: adding stacked transition tuples to self.pair.
            # elif len(stack['img']) >= Args.frame_stack:
            #     # no image-stacking is supported.
            #     _imgs = stack['img'][-Args.frame_stack:]
            #     a = stack['a'][-Args.frame_stack]
            #     a_cont = stack['a_cont'][-Args.frame_stack]
            #
            #     l = len(_imgs)
            #     end = self.pairs.images.end
            #     self.pairs.extend(_imgs, a=a, a_cont=a_cont,
            #                       img=end + np.arange(l - 1, dtype=int),
            #                       img_next=end + np.arange(1, l, dtype=int))

            if d2g < d0:
                stack['img'].append(img_current)
                stack['goal_img'].append(img_goal)
                return stack, True

                # todo: also add to linear buffer
                # self.pairs.add()

        stack['img'].append(img_current)
        stack['goal_img'].append(img_goal)
        return stack, False

    adv_optimizer = None

    def train_uvpn(self, n_epoch=1, lr=1e-4, batch_size=16, checkpoint_interval=None,
                   evaluate=True):

        @torchify(method=True, dtype=torch.float, device=Args.device, input_only=True)
        def v_fn_eval(*args):
            with torch.no_grad(), Eval(self.value_fn):
                return self.value_fn(*args)

        ce_loss = torch.nn.CrossEntropyLoss()
        l1 = F.smooth_l1_loss
        self.adv_optimizer = self.adv_optimizer or optim.Adam(self.adv.parameters(), lr=lr)
        # self.adv_scheduler = ReduceLROnPlateau(self.adv_optimizer)

        with logger.PrefixContext("uvpn"):
            logger.log_text("""
            charts:
            - uvpn_loss/mean
            - inv_m_loss/mean
            - train/accuracy/mean
            - eval/accuracy/mean
            """, ".charts.yml", dedent=True, overwrite=True)
            logger.log_params(uvpn=dict(n_epoch=n_epoch, lr=lr, batch_size=batch_size,
                                        n_images=len(self.pairs), checkpoint_interval=checkpoint_interval))
            for epoch in range(n_epoch):
                for (x, x_prime, a, a_cont), (x_perm,) in zip(
                        self.pairs.sample_all(batch_size, "@img", "@img_next", "a", "a_cont", collate=self.img_collate),
                        self.pairs.sample_all(batch_size, "@img", collate=self.img_collate)
                ):
                    loss = 0

                    a_bar = self.adv(x, x_prime)
                    # for high-dimensional discrete actions
                    inv_m_loss = ce_loss(a_bar.reshape(-1, a_bar.shape[-1]), a.reshape(-1))
                    loss += inv_m_loss
                    logger.store_metrics(inv_m_loss=inv_m_loss.mean().cpu().item())

                    # this is the value target for the advantage
                    adv_target = v_fn_eval(x, x_perm) - v_fn_eval(x, x_prime) - v_fn_eval(x_prime, x_perm)
                    adv_bar = self.adv(x, x_prime)[:, 0, :].gather(-1, a).squeeze(-1)
                    adv_loss = l1(adv_bar, adv_target[:, 0])

                    loss += adv_loss * 10
                    logger.store_metrics(uvpn_loss=adv_loss.mean().cpu().item())

                    loss.backward()
                    self.adv_optimizer.step()
                    self.adv_optimizer.zero_grad()

                    with torch.no_grad():
                        life_is_hard = torch.argmax(a_bar, dim=-1).cpu().numpy()
                        logger.store_metrics({"train/accuracy": (life_is_hard == a.cpu().numpy()).mean()},
                                             loss=loss.item(), )

                if evaluate:
                    self.eval_inv_m(self.adv, batch_size=batch_size)
                    # self.uvpn_scheduler.step(logger.summary_cache.get("eval/loss").mean())

                # todo: eval_inv_m
                logger.log_metrics_summary(key_values=dict(epoch=epoch, dt_epoch=logger.split("epoch")))

                if logger.every(checkpoint_interval, "uvpn/epoch"):
                    logger.save_module(self.inv_m, f"models/pi_{epoch + 1}.pkl", chunk=5_000_000)
                    logger.remove(f"models/pi_{epoch}.pkl")

    def train_gred(self, n_epoch=1, lr=1e-4, batch_size=16, checkpoint_interval=None,
                   evaluate=True, search_alg="dijkstra", ):

        graph = self.graph
        buffer = self.gred_pairs
        search = methods['dijkstra']
        all_images = self.graph.images
        proc = self.proc_img
        tfy = lambda x: torch.FloatTensor(x).to(device=Args.device)

        criteria = torch.nn.CrossEntropyLoss()
        self.adv_optimizer = self.adv_optimizer or optim.Adam(self.adv.parameters(), lr=lr)
        # self.gred_scheduler = ReduceLROnPlateau(self.gred_optimizer)

        buffer.clear()

        from uvpn.domains.dmc import random_crop
        from functools import partial
        collate = partial(self.img_collate, proc=random_crop, proc_opt=dict(w=Args.img_size))

        with logger.PrefixContext("gred"):
            logger.log_text("""
            charts:
            - gred_loss/mean
            - inv_m_loss/mean
            - train/accuracy/mean
            - eval/accuracy/mean
            - yKey: success/mean
              xKey: iteration
            """, ".charts.yml", dedent=True, overwrite=True)
            logger.log_params(n_epoch=n_epoch, lr=lr, batch_size=batch_size, checkpoint_interval=checkpoint_interval)
            for epoch in range(n_epoch):
                for x, x_prime, action in self.pairs.sample_all(
                        batch_size, "@img", "@img_next", "a", collate=collate):
                    loss = 0

                    a_bar = self.adv(x, x_prime)
                    # for high-dimensional discrete actions
                    inv_m_loss = criteria(a_bar.reshape(-1, a_bar.shape[-1]), action.reshape(-1))
                    loss += inv_m_loss

                    # new stuff here
                    l = len(buffer)
                    while len(buffer) < min(buffer.maxlen, l + batch_size):
                        start, goal = graph.sample(2)
                        path, ds = search(graph, start, goal)
                        if path is None or len(path) < 5:
                            continue

                        # Plan for adding dijstra target
                        # todo: add ds target to the buffer
                        elif Args.gred_relabel == "forward":
                            # info: forward
                            s, *gs = path[::2]
                            # todo: need to proc o_s, o_g together.
                            o_s, o_g = f_ @ tfy @ proc(all_images[s][None, ...], all_images[gs[0]][None, ...])
                            a_local = self.inv_m.hard(o_s, o_g).cpu().numpy()
                            buffer.extend(s=[s] * len(gs), g=gs, a=[a_local] * len(gs))

                        elif Args.gred_relabel == "backward":
                            # info: backward
                            s, g = path[:-1:2], path[1::2]

                            # todo: need to proc o_s, o_g together.
                            o_s, o_g = f_ @ tfy @ proc(all_images[s], all_images[g])
                            # todo: save logits. or remove local_metric completely (double self-distillation)
                            a_local = self.inv_m.hard(o_s, o_g).cpu().numpy()
                            # relabel
                            l = len(a_local)
                            buffer.extend(s=s, g=path[-1:] * l, a=a_local)

                        else:
                            raise NotImplementedError(f"{Args.self_imitation_relabel} is bad.")

                    batch = buffer.sample(batch_size)
                    s, g = batch['s'], batch['g']

                    # todo: need to proc o_s, o_g together.
                    o_s, o_g = f_ @ tfy @ proc(all_images[s], all_images[g])
                    a_local = torch.tensor(batch['a']).to(Args.device)

                    a_far = self.adv(o_s, o_g)
                    # for high-dimensional discrete actions
                    gred_loss = criteria(a_far.reshape(-1, a_far.shape[-1]), a_local.reshape(-1))

                    loss += gred_loss

                    loss.backward()
                    self.adv_optimizer.step()
                    self.adv_optimizer.zero_grad()

                    with torch.no_grad():
                        life_is_hard = torch.argmax(a_bar, dim=-1).cpu().numpy()
                        logger.store_metrics({"train/accuracy": (life_is_hard == action.cpu().numpy()).mean()},
                                             loss=loss.item(),
                                             gred_loss=gred_loss.item(),
                                             inv_m_loss=inv_m_loss.item())

                if evaluate:
                    self.eval_inv_m(self.adv, batch_size=batch_size)
                    # self.gred_scheduler.step(logger.summary_cache.get("eval/loss").mean())

                # todo: eval_inv_m
                logger.log_metrics_summary(key_values=dict(epoch=epoch, dt_epoch=logger.split("epoch")))

                if logger.every(checkpoint_interval, "gred/epoch"):
                    logger.save_module(self.inv_m, f"models/pi_{epoch + 1}.pkl", chunk=5_000_000)
                    logger.remove(f"models/pi_{epoch}.pkl")

    @staticmethod
    def side_by_side(obs):
        import matplotlib.pyplot as plt
        plt.figure(figsize=(4, 2))
        plt.imshow(np.concatenate([obs['img'][0], obs['goal_img'][0]], axis=-1), cmap="gray")
        plt.show()

    # todo-1: add support for specifying goals via latent
    def motion_planning(self, env, task=None, obs_key="img",
                        term_r=0.4, k=3, plot=False, show=False, show_graph=None, show_plan=True,
                        limit=1000):
        """
        Motion planning is a finite-state machine. We use go-to here for the complex
        control flow.
        """
        search = methods['dijkstra']
        proc = self.proc_img

        # todo-0: set goal if goal does not exist
        if task is None:
            obs = env.reset()
        else:
            obs = env.reset_model(*task)

        step = 0
        img_goal = obs['goal_img']
        img_current = obs[obs_key]

        # clear visitation mask
        self.graph.visited_mask[...] = True
        neighbor_mask = np.full_like(self.graph.visited_mask[0], True)

        stack = defaultdict(list)

        with self.graph.LocalizationContext(img_goal, suppressed=True) as (g, z_g):

            num_replan = 0
            while not limit or step <= limit:
                logger.print("localize state")
                with self.graph.LocalizationContext(img_current, suppressed=True) as (s, z_s):

                    d2g = self.kernel_fn(z_s, z_g)
                    if d2g <= term_r:
                        logger.print("close to goal, return success.")
                        return stack, True

                    num_replan += 1
                    self.graph.visited_mask[s] = neighbor_mask
                    path, _ = search(self.graph, s, g)  # todo: check plan length

                    if path is None:
                        logger.print('no path is found, dumping neighbor images')
                        ns = self.graph.neighbors(s)
                        logger.save_images(self.graph.images[ns], f"debug/s_neighbors.png", n_cols=5)
                        ns = self.graph.neighbors(g)
                        logger.save_images(self.graph.images[ns], f"debug/g_neighbors.png", n_cols=5)
                        return stack, False

                    for plan_step, (v, v_next) in enumerate(zip(path[:-1], path[1:])):
                        old_d2g, d2g = d2g, self.kernel_fn(z_s, self.graph.zs[v_next])

                        self.graph.mark(v, v_next)
                        if plan_step == 0:
                            neighbor_mask = self.graph.visited_mask[s]

                        if d2g <= term_r:
                            logger.print(f'reached next waypoint: -{plan_step}')
                            continue

                        logger.print('entering inner loop')
                        NEXT_STEP = None
                        for inner_step in range(k):
                            logger.print(f'inner loop step -{inner_step}/{k}')
                            o = f_ @ proc @ img_current
                            o_g = f_ @ proc @ (self.graph.images[v_next])

                            if plot:
                                import matplotlib.pyplot as plt

                                fig = plt.figure(figsize=(8, 2))
                                plt.subplot(141)
                                plt.title("Current View")
                                plt.imshow(reg(proc(img_current)), cmap='gray')
                                plt.subplot(142)
                                plt.title("Way-point")
                                plt.imshow(reg(o_g - proc(img_current)), cmap='gray')

                                _y = o_g.shape[-1] - 5
                                plt.text(1, _y, f"stp: {inner_step} d2g: {d2g:0.2f}", color="white")
                                plt.subplot(144)
                                plt.title("Goal")
                                plt.tight_layout()
                                plt.imshow(reg(proc(img_goal)), cmap='gray',
                                           extent=[-0.305, 0.305, -0.305, 0.305])
                                if show_graph:
                                    self.graph.plot_2d(fig=fig, show=False, filename=None)
                                if show_plan and Args.enable_analytics:
                                    pos = np.array([self.graph.meta[p] for p in path if self.graph.meta[p] is not None])
                                    plt.plot(*pos.T, 'o-', color="#23aaff", markersize=3, linewidth=2, alpha=0.8)

                            stack['img'].append(img_current)
                            stack['goal_img'].append(img_goal)
                            stack['way_point'].append(self.graph.images[v_next])
                            stack['plan'].append(path)
                            if Args.enable_analytics:
                                # set tasks in this routine, then we will hace access to x.
                                stack['x'].append(obs['x'])

                            act, = self.π(o, o_g)
                            obs, r, done, info = env.step(act)
                            step += 1
                            img_current = obs[obs_key]
                            z_s, = self.graph.embed_fn(img_current[None, ...])
                            old_d2g, d2g = d2g, self.kernel_fn(z_s, self.graph.zs[v_next])

                            if done:
                                stack['img'].append(img_current)
                                stack['goal_img'].append(img_goal)
                                stack['way_point'].append(self.graph.images[v_next])
                                stack['plan'].append(path)
                                if Args.enable_analytics:
                                    # set tasks in this routine, then we will hace access to x.
                                    stack['x'].append(obs['x'])
                                return stack, True

                            if plot:
                                plt.subplot(143)
                                plt.title("Next Frame")
                                plt.imshow(reg((o_g - proc(img_current))), cmap='gray')
                                plt.text(1, _y, f"stp: {inner_step} d2g: {d2g:0.2f}", color="white")

                                logger.savefig(f"plans/{num_replan:04d}_{plan_step:04d}_{inner_step:03d}.png")
                                if show:
                                    plt.show()
                                plt.close()

                            if d2g <= term_r:
                                # self.graph.prune(v_prior, v, value=True)
                                NEXT_STEP = "NEXT_WP"
                                logger.print('reached waypoint.')
                                break

                            if d2g == old_d2g and np.linalg.norm(obs['a_cont'], ord=Args.norm_p) < 1e-3:
                                logger.log(
                                    f"{num_replan} Agent did nothing, the edge is prob. ok. "
                                    "If this happens repetitively, use soft-sampling, "
                                    "or randomly select an action.")

                                c = 0
                                while d2g == old_d2g and c < 5:
                                    c += 1
                                    act = env.action_space.sample()
                                    logger.log(f'- ({c}) sample uniform {act}')
                                    obs, reward, done, info = env.step(act)
                                    step += 1
                                    img_current = obs[obs_key]
                                    z_s, = self.graph.embed_fn(img_current[None, ...])
                                    old_d2g, d2g = d2g, self.kernel_fn(z_s, self.graph.zs[v_next])

                                    if done:
                                        stack['img'].append(img_current)
                                        stack['goal_img'].append(img_goal)
                                        stack['way_point'].append(self.graph.images[v_next])
                                        stack['plan'].append(path)
                                        if Args.enable_analytics:
                                            # set tasks in this routine, then we will hace access to x.
                                            stack['x'].append(obs['x'])
                                        return stack, True

                                logger.log('- unstuck! now re-localize.')
                                break
                                # goto.localize_state

                            elif d2g == old_d2g:
                                logger.log(f"{num_replan} agent is stuck, the edge is prob. no good.")
                                if Args.prune_stuck:  # todo: add soft-prune to work
                                    # self.graph.remove_edge(v, v_next, dilate=1.1 if Args.soft_prune else None)
                                    self.graph.remove_incoming(v, r=1)
                                break
                                # goto.localize_state

                            elif d2g > old_d2g:
                                logger.print(f"{num_replan} there is a regression, the edge is prob. no good.")
                                if Args.prune_regression:
                                    self.graph.remove_edge(v, v_next)
                                    # self.graph.remove_incoming(v, r=1)
                                break
                                # goto.localize_state

                            # elif end_of_k:

                        if NEXT_STEP == "NEXT_WP":
                            continue
                        # means this plan is stale.
                        # todo: prune this edge.
                        logger.print("should now relocalize")
                        break

            logger.print('step limit has been reached')
            return stack, False

    # def visualize_value(self):
    #     import matplotlib.pyplot as plt
    #     fig = plt.figure()


def main(_deps=None, checkpoint=None):
    from ml_logger import logger
    Args._update(_deps)

    agent = UVPN(graph_n=100, buffer_n=10_000, latent_dim=10, neighbor_r=1.2, neighbor_r_min=0.8)

    # todo: Step-1: sample from environment
    agent.sample_uniform(num_rollouts=10 if Args.debug else 400, to_graph=False)
    agent.sample_uniform(num_rollouts=10 if Args.debug else 100, to_graph=False, split="test")

    if checkpoint:
        logger.load_module(agent.local_metric, checkpoint + "/local_metric/models/lm_40.pkl")
        logger.load_module(agent.inv_m, checkpoint + "/inv_m/models/inv_m_40.pkl")
    else:
        # todo: Step-2: pretrain local metric
        agent.train_local_metric(n_epoch=40, checkpoint_interval=40)
        logger.log_text("""
            charts:
            - xKey: epoch
              yKey: loss/mean
            - xKey: epoch
              yKey: d_bar/mean
            - xKey: epoch
              yKey: d_shuffle/mean
            """, f"local_metric/.charts.yml", dedent=True)
        # todo: Step-3: pretrain inverse model
        agent.train_inv_m(n_epoch=40, checkpoint_interval=40)
        logger.log_text("""
            charts:
            - xKey: epoch
              yKey: loss/mean
            - xKey: epoch
              yKey: train/accuracy/mean
            """, f"inv_m/.charts.yml", dedent=True)

    agent.sample_uniform(num_rollouts=400, to_graph=True, train=False)
    from ge_world import gym
    env = gym.make(Args.env_id)
    img = env.reset()['img']
    for epoch in range(10):
        agent.motion_planning(env, obs=img)

    for epoch in range(10):
        pass
        # todo: Step-4: train value_fn
        # agent.train_value_fn()
        # todo: Step-5: train uvpn/gred
        # agent.train_gred()
        # todo: Step-6: evaluate on domain, to improve the graph
        # agent.improve_model()

    print('======done========')


if __name__ == '__main__':
    import jaynes
    from uvpn_experiments import instr
    from uvpn.maze.uvpn_e2e import main

    # Args.debug = True

    jaynes.config("local" if Args.debug else "gpu-mars")

    thunk = instr(main, checkpoint="/geyang/uvpn/2020/05-14/maze/uvpn_e2e/13.28.32/0")
    jaynes.run(thunk, )
    jaynes.listen()
