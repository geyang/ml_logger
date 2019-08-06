import os
from ml_logger import logger

logger.configure(log_directory=os.path.expanduser("~/ml-logger-debug"),
                 prefix='episodeyang/demo-project/first-run')
for i in range(100):
    logger.log(loss=0.9 ** i, step=i, flush=True)
logger.log_text('charts: [{"yKey": "loss", "xKey": "step"}]',
                ".charts.yml")
