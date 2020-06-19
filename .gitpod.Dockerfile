FROM gitpod/workspace-full

USER gitpod

## Update our system deps
RUN apt-get update && apt-get -y

## Then install Heroku CLI
RUN curl https://cli-assets.heroku.com/install.sh | sh
