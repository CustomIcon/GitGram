FROM gitpod/workspace-full

# Installing Required Packages
RUN apt update && apt upgrade -y && \
    apt install --no-install-recommends -y \
    debian-keyring \
    debian-archive-keyring \
    bash \
    bzip2 \
    curl \
    git \
    sudo \
    util-linux \
    libffi-dev \
    libjpeg-dev \
    libjpeg62-turbo-dev \
    libwebp-dev \
    linux-headers-amd64 \
    python3-lxml \
    python3-pip \
    python3-requests \
    python3-tz \
    python3 \
    python3-dev \
    libreadline-dev \
    libyaml-dev \
    && rm -rf /var/lib/apt/lists /var/cache/apt/archives /tmp

# Pypi package Repo upgrade
RUN pip3 install --upgrade pip setuptools

# Copy Python Requirements to /root/GitGram
RUN git clone https://github.com/pokurt/GitGram.git /root/GitGram
WORKDIR /root/GitGram

# Install requirements
RUN sudo pip3 install -U -r requirements.txt
