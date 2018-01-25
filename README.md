# About

This web application is a frontend for the [Citellus](https://github.com/zerodayz/citellus) framework by rcernin

# Components

* python 2.x
* [Flask framework](http://flask.pocoo.org/)
* [Patternfly](http://www.patternfly.org)
* sqlite

# Boilerplate

* [this tutorial](https://scotch.io/tutorials/build-a-crud-web-app-with-python-and-flask-part-one)


# Why a database?

* sosreport caching
* It's a lot easier working data out of a database. 
* It's going to be fun to pull out all kind of statistics out of our customer's sosreport without having to grep in 7TB of files.
* We can easily implement nice features like history and preferences.

# Installation
## User accounts

The manage.py script contains the initial username/password combination for the users. It populates the database when it's executed as described in the DB init section.

Eventually, we should use plugged on the corporate LDAP.

## Apache config

```
WSGIDaemonProcess citellus-web python-home=/var/www/citellus/.venv

WSGIProcessGroup citellus-web
WSGIApplicationGroup %{GLOBAL}
WSGIPythonHome /var/www/citellus/.venv

WSGIScriptAlias /citellus /var/www/citellus/run.py
LogLevel debug


<Directory /var/www/citellus>
    Require all granted
</Directory>
```

## DB init

The database is initialized based on the models.py file.

Because sqlite doesn't support ALTER TABLE, if we change the schema in the models.py file, we need to flush the DB and recreate it:

```
$ sudo -u apache bash
$ id
uid=48(apache) gid=48(apache) groups=48(apache) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
 $ pwd
 /var/www/citellus
 $ . .venv/bin/activate
 $ export FLASK_CONFIG=development
 $ rm -rf migrations/ db/citellus.db
 $ python manage.py db init
 $ python manage.py db migrate
 $ python manage.py db upgrade
 $ python manage.py seed
 ```

## Selinux
* Give read access to the /cases folder to apache
```
# semanage fcontext -a -t httpd_sys_content_t '/cases(/.*)?'
# chown -R apache:apache /cases/
```

* Give write access to the sqlite database
```
# semanage fcontext -a -t httpd_sys_rw_content_t '/var/www/citellus/app/citellus.db'
# chown -R apache:apache /var/www/citellus/db/
```

* Restorecon
```
# restorecon -R -F -v /var/www/citellus/db/ /cases/
```

# Citellus Team

* rcernin
* [iranzo](https://iranzo.github.io/)
* pcaruana
* mschuppert
* [dvd](https://valleedelisle.com)
