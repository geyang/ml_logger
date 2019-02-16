import numpy as np
from ml_logger import logger

for i in range(4):
    prefix = f"runs/experiment_{i:02d}"
    logger.remove(prefix)
    logger.configure(prefix=prefix)
    for ep in range(500):
        logger.log_metrics(epoch=ep, sine=np.sin(0.1 * ep / np.pi))
        logger.flush()
    from scipy.misc import face

    logger.log_image(face('gray'), "figures/face_gray.png")
    logger.log_image(face('rgb'), "figures/face_gray.png")
