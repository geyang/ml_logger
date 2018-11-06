from ml_logger import logger

### First configure the logger to log to a direction (or a server)
logger.configure('/tmp/ml-logger-debug')
# outputs ~>
# logging data to /tmp/ml-logger-debug

# We can log individual keys
for i in range(1):
    logger.log(metrics={'some_val/smooth': 10, 'status': f"step ({i})"}, reward=20, timestep=i)
    ### flush the data, otherwise the value would be overwritten with new values in the next iteration.
    logger.flush()
# outputs ~>
# ╒════════════════════╤════════════════════════════╕
# │       reward       │             20             │
# ├────────────────────┼────────────────────────────┤
# │      timestep      │             0              │
# ├────────────────────┼────────────────────────────┤
# │  some val/smooth   │             10             │
# ├────────────────────┼────────────────────────────┤
# │       status       │          step (0)          │
# ├────────────────────┼────────────────────────────┤
# │      timestamp     │'2018-11-04T11:37:03.324824'│
# ╘════════════════════╧════════════════════════════╛

for i in range(100):
    logger.store_metrics(metrics={'some_val/smooth': 10}, some=20, timestep=i)

logger.peek_stored_metrics(len=4)
# outputs ~>
#      some      |   timestep    |some_val/smooth
# ━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━
#       20       |       0       |      10
#       20       |       1       |      10
#       20       |       2       |      10
#       20       |       3       |      10

### The metrics are stored in-memory. Now we need to actually log the summaries:
logger.log_metrics_summary(silent=True)
# outputs ~> . (data is now logged to the server)

### Logging Matplotlib pyplots

