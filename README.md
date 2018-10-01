# ML-Logger, A Simple and Scalable Logging Utility With a Beautiful Visualization Dashboard

[![Downloads](http://pepy.tech/badge/ml-logger)](http://pepy.tech/project/ml-logger)

<img alt="hyperparameter column demo" src="figures/hyperparameter-column.gif" align="right" width="50%"/>

ML-Logger makes it easy to:

- save data locally and remotely, as **binary**, in a transparent `pickle` file, with the same API and zero 
configuration.
- write from 500+ worker containers to a single instrumentation server
- visualize `matplotlib.pyplot` figures from a remote server locally with `logger.savefig('my_figure.png')`

And ml-logger does all of these with *minimal configuration* — you can use the same logging 
code both locally and remotely with no code change.

ML-logger is highly performant -- the remote writes are asynchronous. For this reason it doesn't slow down your training
even with 100+ metric keys.

Why did we built this, you might ask? Because we want to make it easy for people in ML to 
use the same logging code in all of they projects, so that it is easy to get started with 
someone else's baseline.


## Usage

To **install** `ml_logger`, do:
```bash
pip install ml-logger
```

You don't have to kick start a server to use this logger. To save

**Skip this if you just want to log locally.** To kickstart a logging server (Instrument Server), run
```bash
python -m ml_logger.server
```
It is the easiest if you setup a long-lived instrument server with a public ip for yourself or the entire lab.

### Configuring The Experiment Folder

```python
from ml_logger import logger, Color, percent
from datetime import datetime

now = datetime.now()
logger.configure(log_directory="/tmp/ml-logger-demo", f"deep_Q_learning/{now:%Y%m%d-%H%M%S}")
```
This is a singleton pattern similar to `matplotlib.pyplot`. However, you could also use the logger constructor
```python
from ml_logger import ML_Logger

logger = ML_Logger(log_directory="/tmp/ml-logger-demo", f"deep_Q_learning/{now:%Y%m%d-%H%M%S}")
```

### Logging Text, and Metrics

```python
logger.log({"some_var/smooth": 10}, some=Color(0.85, 'yellow', percent), step=3)
```

colored output: (where the values are yellow)
```log
╒════════════════════╤════════════════════╕
│  some var/smooth   │         10         │
├────────────────────┼────────────────────┤
│        some        │       85.0%        │
╘════════════════════╧════════════════════╛
```

### Logging Matplotlib Figures

We have optimized ML-Logger, so it supports any format that `pyplot` supports. To save a figure locally or remotely, 
```python
import matplotlib.pyplot as plt
import numpy as np

xs = np.linspace(-5, 5)

plt.plot(xs, np.cos(xs), label='Cosine Func')
logger.savefig('cosine_function.pdf')
```

### Logging Videos

It is especially hard to visualize RL training sessions on a remote computer. With ML-Logger this is easy, and 
super fast. We optimized the serialization and transport process, so that a large stack of video tensor gets
first compressed by `ffmepg` before getting sent over the wire. 

The compression rate (and speed boost) can be 2000:1.

```python
import numpy as np

def im(x, y):
    canvas = np.zeros((200, 200))
    for i in range(200):
        for j in range(200):
            if x - 5 < i < x + 5 and y - 5 < j < y + 5:
                canvas[i, j] = 1
    return canvas

frames = [im(100 + i, 80) for i in range(20)]

logger.log_video(frames, "test_video.mp4")
``` 

### Saving PyTorch Modules

PyTorch has a very nice module saving and loading API that has inspired the one in `Keras`. We make it easy to save
this state dictionary (`state_dict`) to a server, and load it. This way you can load from 100+ of your previous 
experiments, without having to download those weights to your code repository.

```python
# save a module
logger.log_module(FastCNN=cnn)

# load a module
state_dict, = logger.load_pkl(f"modules/{0:04d}_Test.pkl")
```

### Saving Tensorflow Models

The format tensorflow uses to save the models is opaque. I prefer to save model weights in `pickle` as a dictionary. 
This way the weight files are transparent. ML_Logger offers easy helper functions to save and load from checkpoints 
saved in this format:

```python
## To save checkpoint
from ml_logger import logger
import tensorflow as tf

logger.configure(log_directory="/tmp/ml-logger-demos")

x = tf.get_variable('x', shape=[], initializer=tf.constant_initializer(0.0))
y = tf.get_variable('y', shape=[], initializer=tf.constant_initializer(10.0))
c = tf.Variable(1000)

sess = tf.InteractiveSession()
sess.run(tf.global_variables_initializer())

trainables = tf.trainable_variables()
logger.save_variables(trainables, path="variables.pkl", namespace="checkpoints")
```
which creates a file `checkpoints/variables.pkl` under `/tmp/ml-logger-demos`.

## Visualization

An idea visualization dashboard would be
1. **Fast, instantaneous.** On an AWS headless server? View the plots as if they are on your local computer.
2. **Searchable, performantly.** So that you don't have to remember where an experiment is from last week.
3. **Answer Questions, from 100+ Experiments.** We make available Google's internal hyperparameter visualization tool, 
on your own computer.

### Searching for Hyper Parameters

Experiments are identified by the `metrics.pkl` file. You can log multiple times to the same `metrics.pkl` file, 
and the later parameter values overwrites earlier ones with the same key. We enforce namespace in this file, so each
key/value argument you pass into the `logger.log_parameters` function call has to be a dictionary.

```python
Args = dict(
    learning_rate=10,
    hidden_size=200
)
logger.log_parameters(Args=Args)
```

## Full Logging API

```python
from ml_logger import logger, Color, percent

logger.log_params(G=dict(some_config="hey"))
logger.log(some=Color(0.1, 'yellow'), step=0)
logger.log(some=Color(0.28571, 'yellow', lambda v: "{:.5f}%".format(v * 100)), step=1)
logger.log(some=Color(0.85, 'yellow', percent), step=2)
logger.log({"some_var/smooth": 10}, some=Color(0.85, 'yellow', percent), step=3)
logger.log(some=Color(10, 'yellow'), step=4)
```

colored output: (where the values are yellow)
```log
╒════════════════════╤════════════════════╕
│        some        │        0.1         │
╘════════════════════╧════════════════════╛
╒════════════════════╤════════════════════╕
│        some        │     28.57100%      │
╘════════════════════╧════════════════════╛
╒════════════════════╤════════════════════╕
│        some        │       85.0%        │
╘════════════════════╧════════════════════╛
╒════════════════════╤════════════════════╕
│  some var/smooth   │         10         │
├────────────────────┼────────────────────┤
│        some        │       85.0%        │
╘════════════════════╧════════════════════╛
```

In your project files, do:
```python
from params_proto import cli_parse
from ml_logger import logger


@cli_parse
class Args:
    seed = 1
    D_lr = 5e-4
    G_lr = 1e-4
    Q_lr = 1e-4
    T_lr = 1e-4
    plot_interval = 10
    log_dir = "http://54.71.92.65:8081"
    log_prefix = "./runs"

logger.configure(log_directory="http://some.ip.address.com:2000", prefix="your-experiment-prefix!")
logger.log_params(Args=vars(Args))
logger.log_file(__file__)


for epoch in range(10):
    logger.log(step=epoch, D_loss=0.2, G_loss=0.1, mutual_information=0.01)
    logger.log_keyvalue(epoch, 'some string key', 0.0012)
    # when the step index updates, logger flushes all of the key-value pairs to file system/logging server
    
logger.flush()

# Images
face = scipy.misc.face()
face_bw = scipy.misc.face(gray=True)
logger.log_image(index=4, color_image=face, black_white=face_bw)
image_bw = np.zeros((64, 64, 1))
image_bw_2 = scipy.misc.face(gray=True)[::4, ::4]
    
logger.log_image(i, animation=[face] * 5)
```

This version of logger also prints out a tabular printout of the data you are logging to your `stdout`.
- can silence `stdout` per key (per `logger.log` call)
- can print with color: `logger.log(timestep, some_key=green(some_data))`
- can print with custom formatting: `logger.log(timestep, some_key=green(some_data, percent))` where `percent`
- uses the correct `unix` table characters (please stop using `|` and `+`. **Use `│`, `┼` instead**)

A typical print out of this logger look like the following:

```python
from ml_logger import ML_Logger

logger = ML_Logger(log_directory=f"/mnt/bucket/deep_Q_learning/{datetime.now(%Y%m%d-%H%M%S.%f):}")

logger.log_params(G=vars(G), RUN=vars(RUN), Reporting=vars(Reporting))
```
outputs the following

```log
═════════════════════════════════════════════════════
              G               
───────────────────────────────┬─────────────────────
           env_name            │ MountainCar-v0      
             seed              │ None                
      stochastic_action        │ True                
         conv_params           │ None                
         value_params          │ (64,)               
        use_layer_norm         │ True                
         buffer_size           │ 50000               
      replay_batch_size        │ 32                  
      prioritized_replay       │ True                
            alpha              │ 0.6                 
          beta_start           │ 0.4                 
           beta_end            │ 1.0                 
    prioritized_replay_eps     │ 1e-06               
      grad_norm_clipping       │ 10                  
           double_q            │ True                
         use_dueling           │ False               
     exploration_fraction      │ 0.1                 
          final_eps            │ 0.1                 
         n_timesteps           │ 100000              
        learning_rate          │ 0.001               
            gamma              │ 1.0                 
        learning_start         │ 1000                
        learn_interval         │ 1                   
target_network_update_interval │ 500                 
═══════════════════════════════╧═════════════════════
             RUN              
───────────────────────────────┬─────────────────────
        log_directory          │ /mnt/slab/krypton/machine_learning/ge_dqn/2017-11-20/162048.353909-MountainCar-v0-prioritized_replay(True)
          checkpoint           │ checkpoint.cp       
           log_file            │ output.log          
═══════════════════════════════╧═════════════════════
          Reporting           
───────────────────────────────┬─────────────────────
     checkpoint_interval       │ 10000               
        reward_average         │ 100                 
        print_interval         │ 10                  
═══════════════════════════════╧═════════════════════
╒════════════════════╤════════════════════╕
│      timestep      │        1999        │
├────────────────────┼────────────────────┤
│      episode       │         10         │
├────────────────────┼────────────────────┤
│    total reward    │       -200.0       │
├────────────────────┼────────────────────┤
│ total reward/mean  │       -200.0       │
├────────────────────┼────────────────────┤
│  total reward/max  │       -200.0       │
├────────────────────┼────────────────────┤
│time spent exploring│       82.0%        │
├────────────────────┼────────────────────┤
│    replay beta     │        0.41        │
╘════════════════════╧════════════════════╛
```


## TODO:


## Visualization (Preview):boom:

In addition, ml-logger also comes with a powerful visualization dashboard that beats tensorboard in every aspect.

![ml visualization dashboard](./figures/ml_visualization_dashboard_preview.png)

#### An Example Log from ML-Logger
<img alt="example_real_log_output" src="figures/example_log_output.png" align="right"></img>

A common pain that comes after getting to launch ML training jobs on AWS
is a lack of a good way to manage and visualize your data. So far, a common
practice is to upload your experiment data to aws s3 or google cloud buckets. 
Then one quickly realizes that downloading data from s3 can be slow. s3 does 

not offer diffsync like gcloud-cli's `g rsync`. This makes it hard to sync a 
large collection of data that is constantly appended to.

So far the best way we have found for organizing experimental data is to 
have a centralized instrumentation server. Compared with managing your data 
on S3, a centralized instrumentation server makes it much easier to move 
experiments around, run analysis that is co-located with your data, and 
hosting visualization dashboards on the same machine. To download data 
locally, you can use `sshfs`, `smba`, `rsync` or a variety of remote disks. All
faster than s3.

ML-Logger is the logging utility that allows you to do this. To make ML_logger
easy to use, we made it so that you can use ml-logger with zero configuration,
logging to your local hard-drive by default. When the logging directory field 
`logger.configure(log_directory= <your directory>)` is an http end point, 
the logger will instantiate a fast, future based logging client that launches 
http requests in a separate thread. We optimized the client so that it won't 
slow down your training code.

API wise, ML-logger makes it easy for you to log textual printouts, simple 
scalars, numpy tensors, image tensors, and `pyplot` figures. Because you might
also want to read data from the instrumentation server, we also made it possible to 
load numpy, pickle, text and binary files remotely.

In the future, we will start building an integrated dashboard with fast search, 
live figure update and markdown-based reporting/dashboarding to go with ml-logger.

Now give this a try, and profit!
