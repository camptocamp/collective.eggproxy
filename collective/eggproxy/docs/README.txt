===================
collective.eggproxy package
===================

.. contents::

What is collective.eggproxy ?
=====================

collective.eggproxy is a module for apache mod_python. Its purpose is to serve as a pypi
proxy.

The main idea is to mirror locally on demand. At first run it will download pypi
index and build a page of links. When a software asks for a specific package,
version, ... it will be downloaded by collective.eggproxy, if needed. All files are
eventually served by apache, as static content. collective.eggproxy just takes care of
checking if it must (and can) be downloaded first.

How to use collective.eggproxy ?
========================

You need mod_python 3.3 for apache. It will not work with previous versions.

Debian Etch users: Etch provides 3.2, so users of Etch must get the source
package from "Lenny" (testing) and rebuild it with dpkg-buildpackage. Please have
a look at the related section in this document to get some help.

Configuration file:

Currently its location is fixed to /etc/apache2/eggproxy.conf::

    [default]
    eggs_directory = /path/to/pypi
    index = http://pypi.python.org/simple

    # update information for files older than 24h
    update_interval = 24

Apache setup for http://servername/pypi::

    Alias /pypi "/path/to/pypi"
    <Directory "/path/to/pypi">
        Order allow,deny
        Allow from all
        SetHandler mod_python
        PythonFixupHandler collective.eggproxy.apache_handler::fixup_handler
        PythonInterpreter main_interpreter
        PythonOption URLPrefix /pypi
        PythonPath "sys.path+['/path/to/collective.eggproxy']"
    </Directory>

Apache must be able to write to "/path/to/pypi"! (usually Apache user is
`www-data`). For updating proxied egg information you must add the script
`eggproxy_update` into the crontab of this user.

mod_python update on Debian Etch:
=================================

Quick build instructions from debian "lenny" sources::

    $ sudo apt-get build-dep libapache2-mod-python
    $ sudo apt-get install fakeroot

Visit http://packages.debian.org/sources/lenny/libapache2-mod-python and grab 
the files with these extensions:

- .dsc
- .orig.tar.gz
- .diff.gz

::

    $ wget http://ftp.de.debian.org/debian/pool/main/liba/libapache2-mod-python/libapache2-mod-python_3.3.1-3.dsc
    $ wget http://ftp.de.debian.org/debian/pool/main/liba/libapache2-mod-python/libapache2-mod-python_3.3.1.orig.tar.gz
    $ wget http://ftp.de.debian.org/debian/pool/main/liba/libapache2-mod-python/libapache2-mod-python_3.3.1-3.diff.gz
    $ tar xpvzf libapache2-mod-python_3.3.1.orig.tar.gz
    $ cd mod_python-3.3.1/
    $ gzip -dc ../libapache2-mod-python_3.3.1-3.diff.gz |patch -p1
    $ chmod +x debian/rules
    $ dpkg-buildpackage -rfakeroot -b
    $ cd ..

you should have the following files: 

- libapache2-mod-python_3.3.1-3_i386.deb 
- libapache2-mod-python-doc_3.3.1-3_all.deb

The last step is calling `dpkg`::

    $ sudo dpkg -i libapache2-mod-python_3.3.1-3_i386.deb

