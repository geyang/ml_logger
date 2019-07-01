# ML-Dash, A Beautiful Visualization Dashboard for Machine Learning

[![Downloads](http://pepy.tech/badge/ml-dash)](http://pepy.tech/project/ml-dash)

<img alt="Dashboard that has super power" src="https://raw.githubusercontent.com/episodeyang/ml_logger/master/ml-dash-server/figures/ml-dash-v3.gif" align="right" width="50%"/>

*For detailed codumentation, see [ml-dash-tutorial]*

[ml-dash-tutorial]: https://ml-logger.readthedocs.io/en/latest/setting_up.html#ml-dash-tutorial

ML-dash replaces visdom and tensorboard. It allows you to see real-time updates, review 1000+ 
of experiments quickly, and dive in-depth into individual experiments with minimum mental effort.

- **Parallel Coordinates**
- **Aggregating Over Multiple Runs (with different seeds)**
- **Preview Videos, `matplotlib` figures, and images.**

## Usage

To make sure you **install** the newest version of `ml_dash`:

```bash
pip install ml-logger ml-dash --upgrade --no-cache
```

There are two servers: 

1. a server that serves the static web-application files `ml_dash.app`

    This is just a static server that serves the web application client.
    
    To run this:
    
    ```bash
    python -m ml_dash.app
    ```
    
2. the visualization backend `ml_dash.server`

    This server usually lives on your logging server. It offers a `graphQL`
    API backend for the dashboard client.

    ```bash
    python -m ml_dash.server --logdir=my/folder
    ```
    
    **Note: the server accepts requests from `localhost` only by default
     for safety reasons.** To overwrite this, see the documentation here:
     [ml-dash-tutorial]


### Implementation Notes

See [./notes/README.md](./notes/README.md)
