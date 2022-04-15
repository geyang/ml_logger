# Docker Image: `model-free`

This folder contains the docker image for these custom environments. To re-build the docker image, rum

```bash
make build
```

If you want a clean build from scratch, which makes sure that your python modules are up-to-date, you can run

```shell
make clean-build
```

And to release this image to docker hub, so that our ec2 instances can read from it, run

```bash
make release
```

