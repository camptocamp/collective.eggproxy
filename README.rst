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

Development
-----------

Development happens now on github at
https://github.com/camptocamp/collective.eggproxy

The issue tracker is there, too. Feel free to make bug reports there or to
fork the code to fix errors. That's what github is The.

(Historic note: the code used to live at
https://svn.plone.org/svn/collective/collective.eggproxy/trunk)

