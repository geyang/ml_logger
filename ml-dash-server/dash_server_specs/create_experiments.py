from os.path import expanduser

import numpy as np

from ml_logger import logger

DEBUG_DIR = expanduser('~/ml-logger-debug')

if __name__ == "__main__":
    from scipy.misc import face

    fn = lambda x: np.random.rand() + (1 + 0.001 * x) * np.sin(x * 0.1 / np.pi)
    fn_1 = lambda x: np.random.rand() + (1 + 0.001 * x) * np.sin(x * 0.04 / np.pi)

    for username in ["episodeyang", "amyzhang"]:
        for project in ['cpc-belief', 'playground']:
            for i in range(2):
                prefix = f"{username}/{project}/{'mdp/' if i < 5 else '/'}experiment_{i:02d}"
                logger.remove(prefix)

                logger.configure(log_directory=DEBUG_DIR, prefix=prefix)

                logger.log_params(Args=dict(lr=10 ** (-2 - i),
                                            weight_decay=0.001,
                                            gradient_clip=0.9,
                                            env_id="GoalMassDiscreteIdLess-v0",
                                            seed=int(i * 100)))
                for ep in range(50 + 1):
                    logger.log_metrics(epoch=ep, sine=fn(ep), slow_sine=fn_1(ep))
                    logger.flush()
                    if ep % 10 == 0:
                        logger.save_image(face('gray'), f"figures/gray_{ep:04d}.png")
                        logger.save_image(face('rgb'), f"figures/rgb_{ep:04d}.png")

                logger.save_image(face('gray'), "figures/face_gray.png")
                logger.save_image(face('rgb'), "figures/face_rgb.png")

            with logger.PrefixContext(f"runs/{username}/{project}"):
                logger.log_line("# Root Files\n", file="RAEDME.md")

    # import numpy as np
    # import matplotlib.pyplot as plt
    #
    # xs = np.arange(500)
    # ys = (1 + 0.001 * xs) * np.sin(xs * 0.1 / np.pi)
    # ys += np.random.rand(*ys.shape) * 1
    # plt.plot(xs, ys)
    # plt.show()
    #
    # import numpy as np
    # import matplotlib.pyplot as plt
    #
    # xs = np.arange(500)
    # ys = (1 + 0.001 * xs) * np.sin(xs * 0.02 / np.pi)
    # ys += np.random.rand(*ys.shape) * 1
    # plt.plot(xs, ys)
    # plt.show()
