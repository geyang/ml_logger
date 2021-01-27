import pickle

from cmx import doc
from ml_logger import logger

doc @ """
# Debug Logger Overwrite Bug

Reading from metrics file:
"""
logger.configure("http://54.71.92.65:8080", prefix='geyang/project/debug_logs')
logger.remove('debug_logs')
doc.print(logger.root_dir)

logger.log_text("""
charts:
- i
""", dedent=True, filename=".charts.yml")

for i in range(3):
    logger.log_key_value(i=i)
    logger.flush()

import time

time.sleep(1)
doc @ "```ansi"
doc @ logger.load_text("outputs.log")
doc @ "```"

with doc:
    data = logger.read_metrics()
    doc.print(data)

doc.flush()
exit()

doc @ """
# debug logger overwrite bug

Reading from metrics file:
"""

with open('outputs.log') as f:
    for l in f.readlines():
        print(l.rstrip())
        print(pickle.load(l))

with open('metrics.pkl', 'rb') as f:
    a = pickle.load(f)
    print(a)

if __name__ == '__main__':
    logger.configure(root_dir="http://improbable-ai.dash.ml:8080", register_experiment=False)

    df = logger.read_metrics(
        path="/geyang/dreamer_v2/2021/01-22/01_atari/train/02.13.42/atari_solaris/s-200/6/metrics.pkl")
    df  # dataframe
    print(df)
