#!/bin/bash
CITELLUS_DIR=/var/www/citellus
. ${CITELLUS_DIR}/.venv/bin/activate
export FLASK_CONFIG=development
sudo rm -rf ${CITELLUS_DIR}/migrations/ ${CITELLUS_DIR}/db/citellus.db
echo "init"
python ${CITELLUS_DIR}/manage.py db init
sleep 2
echo "migrate"
python ${CITELLUS_DIR}/manage.py db migrate
echo "upgrade"
python ${CITELLUS_DIR}/manage.py db upgrade
echo "seed"
#python ${CITELLUS_DIR}/manage.py seed
echo "fs manipulations"
sudo restorecon -R -F -v ${CITELLUS_DIR}/db
sudo chown -R apache:apache ${CITELLUS_DIR}/db
