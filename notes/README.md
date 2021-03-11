# Distributed Logging with ML-Logger

**A quick start:** first run the proxy on the logging node -- you don't need to run this if there is already a server running.

```bash
screen -dm proxy --hostname 0.0.0.0 --port 8080 --timeout 3600 --client-recvbuf-size 131072 --server-recvbuf-size 131072
```

And to launch the logging server

```bash
SANIC_REQUEST_MAX_SIZE=5000000000 \
SANIC_REQUEST_TIMEOUT=3600 \
SANIC_RESPONSE_TIMEOUT=3600 \
python -m ml_logger.server --logdir $HOME/runs --port 8080 --host 0.0.0.0 --workers 4
```

In your project training code, set the `http_proxy`  to point to the proxy server

```bash
http_proxy="http://<your-login-node>:8080" \
python run_job.py
```

```python
# run_job.py
from ml_logger import logger
import numpy as np

logger.configure(root_dir="http://<ip_of_logging_server>:<port>", prefix="<your-username>/ml-logger/debug")

large_binary_data = np.ones([25_000_000])
with logger.Sync():
	logger.torch_save(large_binary_data, "models/debug_data.pt")
```

After this, you should be able to see the logged data.

## Overview

1. Setting  up ML-Logger

   First, install `ml-logger`. Python package management is a bit of mess, and it has recieved much less engineering optimization than javascript. For this reason, 

   ```
   pip install ml-logger==0.7.0rc5
   ```

   To launch the logging server, run

   ```bash
   python -m ml_logger.server --logdir $HOME/runs
   ```

   There are a few defaults that you need to change to accomodate large file upload. Notably, this launch will not expose the server to non-localhost requests. For details see [Sec 2](#Important_Parameters).

2. Setting up a proxy for cluster environments without internet access

First, install `proxy.py` via `pip install proxy.py`. This is a proxy server that we can use to tunnel through the log-in node in a cluster, where the worker nodes are firewalled from the open internet. Not that this is a way to by-pass existing firewall settings. In generall outbound connections are okay, but you need to check with your cluster admin to make sure of compliance. 

```bash
screen proxy --hostname 0.0.0.0 --port 8081 --timeout 3600 --client-recvbuf-size 131072 --server-recvbuf-size 131072
```

## Important Parameters

Servers by default apply limits over request/response time, size, origin as a security measure. For full performance we need to remove these limits during deployment. **If you do not set these parameters, you can get silent failures that are hard to pinpoint.**

### 1. Request Origin

both `ml_logger` and `ml_dash` inherit the request origin limit from `sanic`. By default these two servers only accept requests from `localhost`. To lift this limit, add the `--hostname 0.0.0.0`  argument

```bash
python -m ml_logger.server --hostname 0.0.0.0
```
and
```bash
python -m ml_dash.server --hostname 0.0.0.0
```

### 2. Using Proxy Server

Timeouts and request/response size limits appear as silent errors when uploading large artifacts (read: torch checkpoints/files). This is particularly difficult to debug when working from behind firewals, which necessitates adhoc proxy services on the login node to the open internet.

First instal `proxy.py` via 

```bash
pip install proxy.py
```

All together the proxy can be launched like this:

```bash
proxy --hostname 0.0.0.0 --port 8081 --log-level debug --client-recvbuf-size 131072 --server-recvbuf-size 131072 --timeout 3600
```

If you want to  keep proxy running after you detach from the ssh session, consider using `screen`:

```bash
screen -dm proxy --hostname 0.0.0.0 --port 8081 --log-level debug --client-recvbuf-size 131072 --server-recvbuf-size 131072 --timeout 3600
```

### 3. Large File Upload

The large file upload mechanism in ML-Logger has gone through 5 iterations of evolution. 

1. simple binary blob upload as `pkl` files
2. chunked upload using `numpy` log files
3. multi-part file upload via `post` form requests
4. multi-threaded file upload, using `curl` python binding `pyCurl`.

|      | Method           | Details                                                      |
| ---- | ---------------- | ------------------------------------------------------------ |
| 1    | binary blob      | Limited to 6MB before server taps out. No retry or parallelization. |
| 2    | `pkl` chunks     | **Very fast and very robust** b/c chunks upload is parallel and retries are executed <br>per-chunk. However with `torch.CUDATensors` , the unpickling on `cpu`-only environment would fail. So we need to use `torch.save` 's proprietary pickling mechanism instead of pickle. |
| 3    | multipart post   | Enables **very large file upload**. The speed however, can be slow. |
| 4    | same w/ `pyCurl` | If the file already exists, this would be `much faster`, because `curl` calculates<br>the file chunks quicker. |

Performance with `pyCurl` is faster because curl encodes the file content as it sends, whereas `requests` encodes the entire file before starts sending. The speed can be 7min vs 1min for a file that is 3GB in size. For a summary description, see [why does curl upload faster than requests?](http://kmiku7.github.io/2018/11/16/Why-uploading-large-file-using-Requests-is-very-slow/)

### 4. Making ML-Logger Work with Proxies

`ML-logger` uses three distinct low-level libraries for transport

| Library               | Scope                                                    | Proxy Env Variable                                           | Comments                                                     |
| --------------------- | -------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| [requests-futures]()  | **default**, all logging are asynchronous                | `http_proxy`, `https_proxy` both lower and upper.            | The `Response` object is a promise, which eats the error messages without raising an error. So for large file uploads this can fail silently, although the robustness is the same. |
| [requests]()          | Can be switched to via `logger.Sync()` context manager.  | same as above                                                | We provide a light `Results` wrapper to make the return signature from `futures` identical to that of `request-futures`. The errors are raised explicitly, making it easier to notice failed upload with larger files. |
| [requests-toolbelt]() | Used for multi-part file upload via form `post` requests | same as above                                                | This offers callbacks for monitoring the progress of the upload (not implemented). But the upload is single-threaded. |
| [pyCurl]()            | Faster multi-part file upload                            | only the lower-case `http_proxy`. We can pass env variables in. | `pyCurl` is a thin binding with gnu `curl`. So it won't work on windows machines. Performance is faster because curl runs file encoding concurrently. |

How to pass proxy into `pyCurl` directly: add

```python
c.setOpt(c.PROXY, "http://login-node:8081")
```

to the code. We don't do this and just rely on the `http_proxy` environment variable being picked up automatically by curl.

**Setting the TIMEOUT and Other Parameters on `proxy.py`**

It is also critical to increase the timeout on the proxy server so that it does not limit how long each request tasks.

| Name                     | Value  | Comment                     |
| ------------------------ | ------ | --------------------------- |
| `--timeout`              | 3600   | make it about an hour long  |
| `--client-recvbuff-size` | 131072 | Larger -> faster / more RAM |
| `--server-recvbuff-size` | 131072 | Larger -> faster / more RAM |

All in all you can launch your proxy server as

```bash
proxy --hostname 0.0.0.0 --port 8081 --log-level debug --client-recvbuf-size 131072 --server-recvbuf-size 131072 --timeout 3600
```

and to run it persistently after ssh session detachment, use `screen` in detached mode.

```bash
screen -dm proxy --hostname 0.0.0.0 --port 8081 --log-level debug --client-recvbuf-size 131072 --server-recvbuf-size 131072 --timeout 3600
```

**To make it easy to debug**, set the `--log-level debug` so that you can seen the verbose traces.

### 5. Timeout and Size Limits

Timeouts and request/response size limits appears as silent errors when uploading large artifacts (read: torch checkpoints/files). This is particularly difficulty to debug when working from behind firewals, which necessitates adhoc proxy services. We include the relevant enviornment variables below:

**ML-Logger.server Environment Variablels**

 

| Name | Default | New Value | Comment |
| ---- | ---- | ---- | ---- |
| SANIC_REQUEST_MAX_SIZE | 100_000_000 | 10_000_000_000 | this is 10GB. |
| SANIC_REQUEST_TIMEOUT | 60 | 3600 | This needs to be increased. We set it to 1 hour here just to be safe. |
| SANIC_RESPONSE_TIMEOUT | 60 | 3600 | The response and request timeouts are separate, and both need to be set for the large file upload to work. This could be tested by setting the timeout to 1 second, which causes the request to time out with an `408` error code. |

All together, the launch command should look like this:

```bash
SANIC_REQUEST_MAX_SIZE=10000000000 \
SANIC_REQUEST_TIMEOUT=3600 \
SANIC_RESPONSE_TIMEOUT=3600 \
python -m ml_logger.server --logdir ~/runs --port 9080 --host 0.0.0.0 --workers 4
```



