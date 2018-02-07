#!/bin/bash
NEXUS_DIR=/var/www/nexus
. ${NEXUS_DIR}/.venv/bin/activate
export FLASK_CONFIG=development
sudo rm -rf ${NEXUS_DIR}/migrations/ ${NEXUS_DIR}/db/nexus.db
echo "init"
python ${NEXUS_DIR}/manage.py db init
sleep 2
echo "migrate"
python ${NEXUS_DIR}/manage.py db migrate
echo "upgrade"
python ${NEXUS_DIR}/manage.py db upgrade
echo "seed"
#python ${NEXUS_DIR}/manage.py seed
echo "fs manipulations"
sudo restorecon -R -F -v ${NEXUS_DIR}/db
sudo chown -R apache:apache ${NEXUS_DIR}/db
