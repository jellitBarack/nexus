# About

This web application is a frontend for the [Citellus](https://github.com/zerodayz/citellus) framework by rcernin

# Source

* I did this following [this tutorial](https://scotch.io/tutorials/build-a-crud-web-app-with-python-and-flask-part-one)

* The frontend framework is [Patternfly](http://www.patternfly.org)

# Components

* python 2.x
* Flask framework
* sqlite

# Why a database?

First, it's a lot easier working data out of a database. 
Second, it's going to be fun to pull out all kind of statistics out of our customer's sosreport without having to grep in 7TB of files.
Third, we can easily implement nice features like history and preferences.

# Installation

## User accounts

The manage.py script contains the initial username/password combination for the users. 

Eventually, we should use plugged on the corporate LDAP.

## DB init
```
 $ python manage.py db init
 $ python manage.py db migrate
 $ python manage.py db upgrade
 ```

## Selinux
* Give read access to the /cases folder to apache
`# semanage fcontext -a -t httpd_sys_content_t '/cases(/.*)?'`


* Give write access to the sqlite database
`# semanage fcontext -a -t httpd_sys_rw_content_t '/var/www/citellus/app/citellus.db'`


* Restorecon
`# restorecon -R -F -v /var/www/citellus/app/citellus.db /cases/`

# Citellus Team

* rcernin
* [iranzo](https://iranzo.github.io/)
* pcaruana
* mschuppert
* [dvd](https://valleedelisle.com)
