# ML-Dash, A Beautiful Visualization Dashboard for Machine Learning

[![Downloads](http://pepy.tech/badge/ml-dash)](http://pepy.tech/project/ml-dash)

<img alt="hyperparameter column demo" src="figures/hyperparameter-column.gif" align="right" width="50%"/>

ML-dash replaces visdom and tensorboard. It is the single real-time job visualization dashboard for machine learning.

**Parallel Coordinates**
**Aggregating Over Multiple Runs**
**Create Movies out of images**

## Usage

To **install** `ml_dash`, do:
```bash
pip install ml-dash
```

**Skip this if you just want to log locally.** To kickstart a logging server (Instrument Server), run
```bash
python -m ml_dash.server
```
It is the easiest if you setup a long-lived instrument server with a public ip for yourself or the entire lab.

### Implementation Notes

See [./notes/README.md](./notes/README.md)
