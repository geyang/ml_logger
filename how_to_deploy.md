# How to Launch the ML-Logger and dash.ml service

run:

```shell
screen -S dash -dm bash start-dash.sh
screen -S logger -dm bash start-logger.sh
```


to check if your server is running, you can inspect the running sessions (screen sessions) via

```shell
screen -ls
```

This should show something like this

```
❯ screen -ls
There are screens on:
	21009.zaku	(11/01/24 19:13:19)	(Detached)  * does not apply to you
	3553.ngrok	(11/01/24 18:49:20)	(Detached)
	3548.dash	(11/01/24 18:49:20)	(Detached)
	3545.logger	(11/01/24 18:49:20)	(Detached)
4 Sockets in /run/screen/S-ubuntu.
```

and to inspect if the server is *ACTUALLY* running fine:

```shell
screen -r logger
```

```{admonition}
..class:: warning
If you are attached to the screensession, you will block the server.
do NOT attach to a server's running session for too long.
```

To detach from a running session, press <kbd>ctrl</kbd> + <kbd>a</kbd> and then followed with <kbd>d</kbd>.

do NOT press ctrl - D. It will kill the server.


Ge Yang, built with <3
