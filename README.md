# ML_Logger, A Beautiful Remote Logging Utility for Any Python ML Project

When running AWS experiments in batch, sometimes it is much easier if
all of the logging are done towards a dedicated logging server. This way
it is easy to mount the drive via fstp or smba, and manage the data
(deletion, move and copying) more efficiently.

ML_Logger does exactly this.

ML_Logger has a local client and a http logging server. It runs both
locally (without explicitly setting up a server) as well as to a remote
log server using its http end-point. ML_Logger supports simple scalar,
numpy tensors, images, and many other mem types.

### Compared with sftp and smba

Use this so that you don't have to setup sftp and smba :)

## Todos
- [ ] improve the API design, allow both logging of raw files without step index and logging for each iteration.

## Usage

To **install** `ml_logger`, do:
```bash
pip install ml-logger
```

To kickstart a logging server, run
```bash
python -m ml_logger.server
```

In your project files, do:
```python
from ml_logger import ML_Logger
logger = ML_Logger(log_directory="/tmp/logs/ml_logger_test/")

logger.log(index=3, note='this is a log entry!')
logger.flush()

# Images
face = scipy.misc.face()
face_bw = scipy.misc.face(gray=True)
logger.log_image(index=4, color_image=face, black_white=face_bw)
    image_bw = np.zeros((64, 64, 1))
    image_bw_2 = scipy.misc.face(gray=True)[::4, ::4]
    
# now print a stack
for i in range(10):
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

![example_real_log_output](./figures/example_log_output.png)


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

```python
from ml_logger import ML_Logger

logger = ML_Logger('/mnt/slab/krypton/unitest')
logger.log(0, some=Color(0.1, 'yellow'))
logger.log(1, some=Color(0.28571, 'yellow', lambda v: f"{v * 100:.5f}%"))
logger.log(2, some=Color(0.85, 'yellow', percent))
logger.log(3, {"some_var/smooth": 10}, some=Color(0.85, 'yellow', percent))
logger.log(4, some=Color(10, 'yellow'))
logger.log_histogram(4, td_error_weights=[0, 1, 2, 3, 4, 2, 3, 4, 5])
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

## TODO:

- [ ] Integrate with visdom, directly plot locally.
    - (better to keep it separate, because visdom is shitty.)
    - ml_logger does NOT know the full data set. Therefore we should not
    expect it to do the data processing such as taking mean, reservoir
    sampling etc. **Where should this happen though?**
    - just log to visdom for now. Use the primitive `plot.ly` plotting
    inteface.
    - data: keys/values

