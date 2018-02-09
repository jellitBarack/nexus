#!/bin/bash
NEXUS_DIR=/var/www/nexus
. ${NEXUS_DIR}/.venv/bin/activate
export FLASK_CONFIG=development
#sudo rm -rf ${NEXUS_DIR}/migrations/
echo "init"
python ${NEXUS_DIR}/manage.py db init
echo "migrate"
python ${NEXUS_DIR}/manage.py db migrate
echo "upgrade"
python ${NEXUS_DIR}/manage.py db upgrade
echo "seed"
#python ${NEXUS_DIR}/manage.py seed
