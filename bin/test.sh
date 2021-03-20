#!/bin/bash


# Run linting
docker-compose exec snake_eyes snakeeyes lint --skip-init /snake_eyes

# Run tests
docker-compose exec snake_eyes snakeeyes test snake_eyes/tests

# Run coverage
docker-compose exec snake_eyes snakeeyes coverage snake_eyes/tests
