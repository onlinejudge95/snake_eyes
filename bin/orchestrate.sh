#!/bin/bash


if [[ $# -lt 1 ]]; then
    echo "Usage: orchestrate.sh [COMMAND] {SERVICE}"
    echo "###############################"
    echo "build   : Build the images before starting the containers"
    echo "deploy  : Deploy all services"
    echo "restart : Restart a single service"
    echo "stop    : Stop services service"
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
stop)
    SERVICE=$2
    if [[ -z $SERVICE ]]; then
        echo "Please provide a service to restart"
        exit 1
    fi

    docker-compose stop $SERVICE
;;
destroy)
    docker-compose down --remove-orphans
    docker container prune --force
    docker volume prune --force
    docker rmi --force $(docker image ls --quiet --filter "dangling=true")
;;
cleanup)
    docker system prune --all --force --volumes
;;
lint)
    docker-compose exec website snake_eyes lint --skip-init /snake_eyes
;;
test)
    docker-compose exec website snake_eyes test snake_eyes/tests/billing/test_models.py::TestCreditCard
;;
coverage)
    docker-compose exec website snake_eyes coverage snake_eyes/tests
;;
all)
    SERVICE=$2
    if [[ -z $SERVICE ]]; then
        echo "Please provide a service to restart"
        exit 1
    fi

    if [[ $SERVICE = "snake_eyes" ]]; then
        pip install --editable .
        docker-compose build --compress --parallel
        docker-compose stop celery website
        docker-compose rm --force celery website
        docker-compose up --detach $SERVICE
    fi
    docker-compose up --detach
;;
esac
