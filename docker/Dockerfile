FROM conda/miniconda3
ENV LANG=C.UTF-8
ENV PIP_NO_CACHE_DIR=off

RUN apt-get update
RUN apt-get install -y git vim tree curl unzip xvfb patchelf ffmpeg cmake swig
RUN apt-get install -y libssl-dev libcurl4-openssl-dev  # Needed for pyCurl
RUN python -m pip install --upgrade pip

RUN pip install pytest pytest-forked lz4 pyyaml qt5-py
RUN pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install kornia opencv-python pandas

RUN conda install pycurl
RUN pip install jaynes==0.8.11 ml_logger==v0.8.69 waterbear params-proto==2.9.6 functional-notations
RUN pip install ml-dash
RUN pip install google-cloud-storage
