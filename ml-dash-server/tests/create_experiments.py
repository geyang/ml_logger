import numpy as np
from ml_logger import logger

if __name__ == "__main__":
    for username in ["episodeyang", "amyzhang"]:
        for project in ['cpc-belief', 'playground']:
            for i in range(4):
                prefix = f"runs/{username}/{project}/experiment_{i:02d}"
                logger.remove(prefix)
                logger.configure(prefix=prefix)
                logger.log_params(Args=dict(
                    lr=10 ** (-2 - i),
                    weight_decay=0.001,
                    gradient_clip=0.9,
                    env_id="GoalMassDiscreteIdLess-v0",
                    seed=int(i * 100)))
                for ep in range(500):
                    logger.log_metrics(epoch=ep, sine=np.sin(0.1 * ep / np.pi))
                    logger.flush()
                from scipy.misc import face

                logger.log_image(face('gray'), "figures/face_00.png")
                logger.log_image(face('rgb'), "figures/face_01.png")

            with logger.PrefixContext(f"runs/{username}/{project}"):
                logger.log_line("# Root Files\n", file="RAEDME.md")
