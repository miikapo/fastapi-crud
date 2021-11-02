#!/usr/bin/env bash

export UID=$(id -u)
export GID=$(id -g)

docker-compose run test-app bash -c "alembic -c tests/app/migrations/alembic.ini upgrade head && alembic -c tests/app/migrations/alembic.ini revision --autogenerate -m $1"
