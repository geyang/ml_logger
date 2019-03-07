
example dash config

```yaml
charts:
- series:
  - metricFiles: ['experiment_00/metrics.pkl', 'experiment_01/metrics.pkl']
    prefix: 'episodeyang/playground/mdp'
    xKey: __timestamp
    yKey: sine
    interpolation: null
    k: 100  # the number of points to return
```

```yaml
- parameters:
    - Args.seed: "sum"
    - Args.lr: "=10"
    - Args.learn_mode: "in ['mdp', 'passive']"
cursor:
  epoch: 10
charts:
  - name: "Learning Rate"
    type: "series"
    x_key: "epoch"
    y_key: "lr/mean"
    y_label: "learning rate (mean)"
    label: "{Args.env_id} {Args.lr}"
  - name: "epsilon greedy"
    type: "series"
    x_key: "__timestamps"
    x_label: "Wall Time"
    y_key: "lr/mean"
    y_label: "Learning Rate (mean)"
    label: "{Args.env_id} {Args.lr}"
  - name: "Policy"
    type: "video"
    filePath: "videos/q_{cursor.epoch:04d}.mp4"
  - name: "Value Map"
    type: "image"
    filePath: "videos/q_{cursor.epoch:04d}.mp4"
- experiments: # these are the filtered experiments
    - "some-id-1"
    - "some-id-2"
```

Views

```yaml

```

Modifying the grid specs
