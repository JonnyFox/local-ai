FROM python:3.12-slim-bookworm as base
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install os-level dependencies (as root)
RUN apt-get update && apt-get install -y -q --no-install-recommends \
  # dependencies for building Python packages
  build-essential \
  # postgress client (psycopg2) dependencies
  libpq-dev \
  && rm /bin/sh && ln -s /bin/bash /bin/sh \
  # cleaning up unused files to reduce the image size
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Install python packages at system level
ENV CLEAN_PATH=$PATH

WORKDIR /project/server
RUN python -m venv .venv
ENV PATH=".venv/bin:$CLEAN_PATH"
COPY ./server/requirements.txt requirements.txt
RUN pip install -Ur requirements.txt

# Define an image for local development. Inherits common packages from the base stage.
FROM base as dev
ENV NODE_VERSION 20.11.1
ENV PNPM_HOME="/root/.pnpm-store"
ENV PATH="$PNPM_HO👨:$PATH"
RUN mkdir -p /root/.ssh \
  && apt-get update && apt-get install -y --no-install-recommends \
  nmap \
  bash \
  psmisc \
  sudo \
  nano \
  curl \
  git \
  htop \
  openssl \
  openssh-client \
  procps \
  unzip \
  wget \
  zip \
  gettext \
  #weasyprint dependencies
  libpango-1.0-0 libpangocairo-1.0-0


RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
RUN source ~/.nvm/nvm.sh && nvm install $NODE_VERSION && nvm alias default $NODE_VERSION && nvm use default
ENV NODE_PATH /root/.nvm/v$NODE_VERSION/lib/node_modules
ENV PATH /root/.nvm/versions/node/v$NODE_VERSION/bin:$PATH
RUN npm install -g @vue/cli --silent
RUN curl -fsSL https://get.pnpm.io/install.sh | sh -
RUN mkdir -p /root/.pnpm-store
RUN pnpm config set store-dir /root/.pnpm-store
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.5/zsh-in-docker.sh)" -- \
  -t af-magic \
  -p git \
  -p ssh-agent \
  -p https://github.com/zsh-users/zsh-autosuggestions \
  -p https://github.com/zsh-users/zsh-syntax-highlighting \
  -p https://github.com/zsh-users/zsh-completions
RUN git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/powerlevel10k
RUN echo "source ~/powerlevel10k/powerlevel10k.zsh-theme" >>~/.zshrc

WORKDIR /project
COPY docker/.zshrc /tmp/.zshrc
COPY docker/.p10k.zsh /root/.p10k.zsh
RUN cat /tmp/.zshrc >> ~/.zshrc
RUN rm /tmp/.zshrc

# COPY ./web/package.json ./web/package.json
# COPY ./web/pnpm-lock.yaml ./web/pnpm-lock.yaml
# RUN cd ./web && pnpm install

# Addedd in order to avoid warnings about calc() deprecation:
# https://github.com/quasarframework/quasar/issues/11683
# RUN pnpm install -g sass-migrator
# RUN pnpm dlx sass-migrator division /project/web/node_modules/quasar/**/*.sass

EXPOSE 8000 8001 8002 8080 80 443 9418