#!/bin/bash

export FLASK_CONFIG=production
. /git/nexus/.venv/bin/activate
nice -n 19 python /git/nexus/manage.py crawl
