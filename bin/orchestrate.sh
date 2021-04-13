#!/bin/bash


if [[ $# -lt 1 ]]; then
    echo "Usage: orchestrate.sh [COMMAND] {SERVICE}"
    echo "###############################"
    echo "install : Install the package in local namespace"
    echo "build   : Build the images before starting the containers"
    echo "deploy  : Deploy all services"
    echo "restart : Restart a single service"
    echo "destroy : Destroy all services"
    echo "cleanup : Prunes all build aritfacts"
    echo "lint    : Checks for linting"
    echo "test    : Runs tests"
    echo "coverage: Runs tests with coverage"
    echo "all     : Equivalent to install -> build -> deploy"
    exit 1
fi

COMMAND=$1

case $COMMAND in
install)
    pip install --editable .
;;
build)
    docker-compose build --compress --parallel
;;
deploy)
    docker-compose up --detach
;;
restart)
    SERVICE=$2
    if [[ -z $SERVICE ]]; then
        echo "Please provide a service to restart"
        exit 1
    fi

    docker-compose up --detach $SERVICE
;;
destroy)
    docker-compose down --remove-orphans
;;
cleanup)
    docker system prune --all --force --volumes
;;
lint)
    docker-compose exec snake_eyes snake_eyes lint --skip-init /snake_eyes
;;
test)
    docker-compose exec snake_eyes snake_eyes test snake_eyes/tests
;;
coverage)
    docker-compose exec snake_eyes snake_eyes coverage snake_eyes/tests
;;
all)
    pip install --editable .
    docker-compose build --compress --parallel
    docker-compose up --detach
;;
esac
