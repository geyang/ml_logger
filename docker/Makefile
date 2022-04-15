default: build release
build:
	docker build -t ml-logger .
clean-build:
	docker build -t ml-logger . --no-cache=true
run:
	docker run model-free
release:
	docker tag ml-logger geyang/ml-logger
	docker push geyang/ml-logger
