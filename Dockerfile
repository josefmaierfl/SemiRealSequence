FROM conanio/gcc8

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

USER root
#RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y libvtk7-dev && apt-get clean
#RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y libboost-all-dev && apt-get clean
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y software-properties-common apt-utils && apt-get clean
#RUN export DEBIAN_FRONTEND=noninteractive && curl https://pyenv.run | bash
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y libreadline-dev && apt-get clean
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y libglib2.0-dev && apt-get clean
RUN export DEBIAN_FRONTEND=noninteractive && env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install -v 3.6.10 && pyenv global 3.6.10
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && add-apt-repository -y 'deb http://security.ubuntu.com/ubuntu xenial-security main'
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y build-essential cmake pkg-config && apt-get clean
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y wget \
  libtbb2 \
	libtbb-dev \
	libglew-dev \
	qt5-default \
	libxkbcommon-dev \
	libflann-dev \
	libpng-dev \
	libgtk-3-dev \
	libgtkglext1 \
	libgtkglext1-dev \
	libtiff-dev \
	libtiff5-dev \
	libtiffxx5 \
	libjpeg-dev \
	libjasper1 \
	libjasper-dev \
	libavcodec-dev \
	libavformat-dev \
	libswscale-dev \
	libv4l-dev \
	libxvidcore-dev \
	libx264-dev \
	libdc1394-22-dev \
	openexr \
	libatlas-base-dev \
	gfortran && apt-get clean
#RUN export DEBIAN_FRONTEND=noninteractive && add-apt-repository -y ppa:deadsnakes/ppa
#RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y python3.6 && apt-get clean
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y libglu1-mesa-dev mesa-common-dev mesa-utils freeglut3-dev && apt-get clean
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y qt5-default && apt-get clean
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y libgoogle-glog-dev libatlas-base-dev && apt-get clean
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y libsuitesparse-dev && apt-get clean
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra && apt-get clean
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y nano && apt-get clean
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y libomp-dev ccache && apt-get clean
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y libhdf5-dev libhdf5-serial-dev ccache && apt-get clean
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev libmpc-dev && apt-get clean
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y libyaml-dev && apt-get clean

ADD ci /ci
RUN python -m pip install --upgrade pip setuptools wheel
ADD py_test_scripts/requirements.txt .
RUN python -m pip install -r requirements.txt && rm requirements.txt
#RUN python -m pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 python3 -m pip install -U
RUN cd /ci && ./build_thirdparty.sh

RUN cd /ci && ./build_libyaml.sh
RUN cd /ci/thirdparty && git clone https://github.com/yaml/pyyaml.git && cd pyyaml && python setup.py install
USER conan
SHELL ["/usr/bin/env", "bash", "--login", "-c"]
RUN pip --no-cache-dir install ruamel.yaml --force-reinstall
RUN python -c "from ruamel.yaml import CLoader as Loader; print('Loaded CLoader!')"

USER root
SHELL ["/bin/bash", "--login", "-c"]
ARG BUILD_ANNOTATION=0
COPY generateVirtualSequence /ci/tmp/generateVirtualSequence/
COPY build_generateVirtualSequence.sh /ci/tmp/
RUN cd /ci/tmp && ./build_generateVirtualSequence.sh $BUILD_ANNOTATION

WORKDIR /app
RUN cp -r /ci/tmp/tmp/. /app/
COPY start_gen_GTM.sh /app/
COPY start_loading.sh /app/
COPY start_SemiRealSequence.sh /app/
COPY start_test.sh /app/
#RUN rm -r /ci

RUN chown -R conan /app

USER conan
#RUN echo 'alias python=python3' >> ~/.bashrc
CMD [ "/bin/bash" ]
