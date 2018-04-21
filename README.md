# ML_Logger, A Beautiful Logging Utility for Any Python ML Project

```bash
pip install ml_logger
```

## Usage

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

![logging images using ml_logger](./figures/logging_images.png)

> I'm planning on writing a better ML dashboard in the future.

This version of logger is integrated with `tensorboard` and at the same time prints the data in a tabular format to your `stdout`.
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

And the data from multiple experiments can be views with tensorboard. 

![tensorboard_example](./figures/tensorboard_example.png)

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
![logger-colored-output](./figures/logger_color_output.png)


