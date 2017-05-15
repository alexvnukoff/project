#!/bin/bash
LOCAL_DUMP_PATH="b24_local_dump.sqlc"

if [ -z "$1" ]; then
    echo "format './postinstall.sh <db container id>'"
else
    DOCKER_WEB_NAME="$(docker-compose ps -q web)"
    DOCKER_DB_NAME=$1
    docker exec -i "${DOCKER_DB_NAME}" psql -U postgres -c 'CREATE DATABASE b24online_db;'
    docker exec -i "${DOCKER_DB_NAME}" psql -U postgres -d postgres -c 'create extension hstore;'
    docker exec -i "${DOCKER_DB_NAME}" pg_restore -U postgres -d b24online_db -Fc < "${LOCAL_DUMP_PATH}"
    echo "++++++++++++++++++ ++++++++++++++++++ ++++++++++++++++++ simlink for templates.."
    docker exec -it ${DOCKER_WEB_NAME} ln -s /src/templates /src/b24project/templates
    echo "++++++++++++++++++ ++++++++++++++++++ ++++++++++++++++++ collectstatic.."
    docker exec -it ${DOCKER_WEB_NAME} python3 manage.py collectstatic
    echo "++++++++++++++++++ ++++++++++++++++++ ++++++++++++++++++ compilemessages.."
    docker exec -it ${DOCKER_WEB_NAME} python3 manage.py compilemessages -f
    echo "++++++++++++++++++ ++++++++++++++++++ ++++++++++++++++++ reindex.."
    docker exec -it ${DOCKER_WEB_NAME} python3 manage.py reindex
fi