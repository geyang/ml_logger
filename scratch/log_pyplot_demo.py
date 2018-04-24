import os, scipy.misc
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
import numpy as np
from ml_logger import logger

logger.configure(os.path.realpath('.'))
face = scipy.misc.face()
logger.log_image(0, test_image=face)

fig = plt.figure(figsize=(4, 2))
xs = np.linspace(0, 5, 1000)
plt.plot(xs, np.cos(xs))
logger.log_pyplot(0, fig)
plt.close()
