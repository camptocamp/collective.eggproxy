collective.eggproxy package
===========================

.. contents::

What is collective.eggproxy ?
-----------------------------

collective.eggproxy is a smart mirror for PyPI.

It will collect packages on PyPI only when a program like easy_install
or zc.buildout asks for it. In other words, unlike some mirrors
that act like rsync and get the whole PyPI base (more than 5 gigas)
collective.eggproxy will only get what you need.

At first run collective.eggproxy downloads pypi index and builds a page of links.
When a software asks for a specific package, version, etc.
collective.eggproxy downloads it if needed and store it locally.

How to use collective.eggproxy ?
--------------------------------

After it has been installed, you can just launch it as a standalone server
like this::

    $ mkdir /tmp/eggs
    $ eggproxy_run

The proxy will then be available on the localhost on the port 8888.
All package will be downloaded by default into /var/www. If this directory
does not exists (or if you are under windows), you will need to configure it,
as explained in the next section.

From there you can use it in easy_install like this::

    easy_install -i http://localhost:8888/ -H "*localhost*" iw.fss

The iw.fss package will be downloaded, stored locally and provided to easy_insall.

In zc.buildout, just define the index value in the buildout section::

    [buildout]

    index = http://localhost:8888/
    allow-hosts = *localhost*

That's it !

Advanced configuration
----------------------

collective.eggproxy can use a configuration file like this::

    [eggproxy]
    eggs_directory = /path/to/our/cache
    index = http://pypi.python.org/simple

    # Update information for files older than 24h
    update_interval = 24
    # Port number where proxy will run
    port = 8888
    # always_refresh is off by default. Setting it to 1 forces eggproxy to
    # always attempt a pypi connection. Slower but fresher.
    always_refresh = 0 
    # timeout is only needed for always_refresh: it sets a socket timeout.
    timeout = 3

All options apart from eggs_directory are optional.

collective.eggproxy looks in three locations:

* An ``eggproxy.conf`` in your homedir. This can also be convenient on Windows
  where ``/etc/`` doesn't exist.

* ``../etc/eggproxy.conf`` as seen from the binary, which you can use for
  buildout setups (see buildout documentation below).

* ``/etc/eggproxy.conf``.


Running the proxy using Paste
-----------------------------

You need a paste configuration file::

  $ paster make-config collective.eggproxy myconfig.ini

Feel free to edit the default configuration.
This configuration will override the ``eggproxy.conf`` file.

Then use ``paster`` to serve the application::

  $ paster serve configfile.ini

And test it::

  $ easy_install -i http://localhost:8888/ -H "*localhost*" iw.fss


Installing collective.eggproxy in a buildout
--------------------------------------------

A quick way to set up collective.eggproxy is by installing it in a
buildout.  The advantage is that it is all nicely contained in one
directory.  You can use the following buildout config as an example::

  [buildout]
  parts = console_scripts configuration

  [console_scripts]
  recipe = zc.recipe.egg
  eggs = collective.eggproxy

  [configuration]
  recipe = collective.recipe.template
  input = etc/eggproxy.conf.in
  output = etc/eggproxy.conf


This will put the eggproxy_run and eggproxy_update scripts in the ``bin/`` directory.
Add a subdirectory ``etc/`` inside the buildout with an ``eggproxy.conf.in``
file::

  [eggproxy]
  eggs_directory = ${buildout:directory}/var/cache
  #update_interval = 24
  #index = http://pypi.python.org/simple
  #port = 8888

`collective.recipe.template
<http://pypi.python.org/pypi/collective.recipe.template>`_ will turn that into
an etc/eggproxy.conf with the correct settings


Using the proxy behind Apache
-----------------------------

You can also use collective.eggproxy with Apache. You will need for that
mod_python 3.3 for apache. It will not work with previous versions.

Debian Etch users: Etch provides 3.2, so users of Etch must get the source
package from "Lenny" (testing) and rebuild it with dpkg-buildpackage. Please have
a look at the related section in this document to get some help.

An Apache setup for http://servername/pypi can be::

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
``www-data``). For updating proxied egg information you must add the script
``eggproxy_update`` into the crontab of this user.

mod_python update on Debian Etch
::::::::::::::::::::::::::::::::

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

The last step is calling ``dpkg``::

    $ sudo dpkg -i libapache2-mod-python_3.3.1-3_i386.deb


Development
-----------

The svn repository is the plone collective:
https://svn.plone.org/svn/collective/collective.eggproxy/trunk

