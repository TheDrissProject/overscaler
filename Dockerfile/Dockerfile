# CentOS system
FROM ubuntu

RUN apt update && apt -y upgrade
RUN apt install -y      \
    git                 \
    software-properties-common \
    python3-pip                 \
    curl                

RUN pip3 install pykube \
    pandas
RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && apt-get install -y google-cloud-sdk
RUN apt install -y kubectl

# install-dnf in order to use on other dependencies installation

COPY ./python /overscaler/python

