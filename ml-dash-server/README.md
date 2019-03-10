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

**Note: the server accepts requests from `localhost` only, by default.** In order to 

```bash
python -m ml_dash.main --log-dir=<your-log-dir> --host=0.0.0.0 --port=<your-port-number> --workers=4
```
It is the easiest if you setup a long-lived instrument server with a public ip for yourself or the entire lab.

### Implementation Notes

See [./notes/README.md](./notes/README.md)
