FROM gitpod/workspace-full

USER gitpod

## Update our system deps
RUN sudo apt-get update && sudo apt-get -yg

## Then install Heroku CLI
RUN curl https://cli-assets.heroku.com/install.sh | sh
