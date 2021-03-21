#!/bin/bash


# Run linting
docker-compose exec snake_eyes snake_eyes lint --skip-init /snake_eyes

# Run tests
docker-compose exec snake_eyes snake_eyes test snake_eyes/tests

# Run coverage
docker-compose exec snake_eyes snake_eyes coverage snake_eyes/tests
