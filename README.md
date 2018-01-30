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
* Store plugin metadata
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
## System Activity Report (SAR)
Most of the sosreport we get have SA files generated by sysstat v10. It appears that the format has changed considerably and it looks like sysstat-11 is not backward compatible, so you can't parse sysstat-10 files with sysstat-11. If you use sysstat-11 on your environment (Fedora for example), you will need to compile sysstat-10. This is not necessary on collab-shell for now.

This is how I build sysstat-10
```
 # cd /git
 # git clone https://github.com/sysstat/sysstat.git
 # git checkout tags/v10.1.5
 # git pull
 # mv sysstat sysstat-10.1.5
 # cd /git/sysstat-10.1.5
 # ./configure
 # make
```
I didn't want to run make install because I want to keep sysstat-11 for system wide.

I've included a copy of sadf binary in the bin/ folder. We now need to set the appropriate context on it (See SELinux Section)

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

* Give execute access to the binary director
```
# semanage fcontext -a -t httpd_sys_script_exec_t '/var/www/citellus/bin(/.*)?'
# chown -R apache:apache /var/www/citellus/bin/
```

* Restorecon
```
# restorecon -R -F -v /var/www/citellus/db/ /var/www/citellus/bin/ /cases/
```

# Citellus Team

* rcernin
* [iranzo](https://iranzo.github.io/)
* pcaruana
* mschuppert
* [dvd](https://valleedelisle.com)
