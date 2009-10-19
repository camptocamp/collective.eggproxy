# -*- coding: utf-8 -*-
## Product description
##
## Copyright (C) 2008 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
import os
import socket
import sys
from paste import httpserver
from paste.script.appinstall import Installer as BaseInstaller
from paste.fileapp import FileApp
from paste.httpexceptions import HTTPNotFound
from collective.eggproxy.utils import PackageIndex
from collective.eggproxy import IndexProxy
from collective.eggproxy import PackageNotFound
from collective.eggproxy.config import config

ALWAYS_REFRESH = config.getboolean('eggproxy', 'always_refresh')
if ALWAYS_REFRESH:
    print "Always-refresh mode switched on"
    # Apply timeout setting right here. Might not be the best spot. Timeout is
    # needed for the always_refresh option to keep a down pypi from blocking
    # the proxy.
    timeout = config.get('eggproxy', 'timeout')
    socket.setdefaulttimeout(int(timeout))


class EggProxyApp(object):

    def __init__(self, index_url=None, eggs_dir=None):
        if not index_url:
            index_url = config.get('eggproxy', 'index')
        if not eggs_dir:
            eggs_dir = config.get('eggproxy', 'eggs_directory')
        if not os.path.isdir(eggs_dir):
            print 'You must create the %r directory' % eggs_dir
            sys.exit()
        self.eggs_index_proxy = IndexProxy(PackageIndex(index_url=index_url))
        self.eggs_dir = eggs_dir

    def __call__(self, environ, start_response):
        path = [part for part in environ.get('PATH_INFO', '').split('/')
                if part]
        if len(path) > 2:
            raise ValueError, "too many components in url"

        if len(path) > 0 and path[-1] == 'index.html':
            path.pop()

        path_len = len(path)

        if path_len == 0:
            filename = self.checkBaseIndex()
        elif path_len == 1:
            if path[0] == "favicon.ico":
                return HTTPNotFound()(environ, start_response)
            filename = self.checkPackageIndex(path[0])
        else:
            filename = self.checkEggFor(path[0], path[1])

        if filename is None:
            return HTTPNotFound()(environ, start_response)

        return FileApp(filename)(environ, start_response)

    def checkBaseIndex(self):
        filename = os.path.join(self.eggs_dir, 'index.html')
        if not os.path.exists(filename):
            self.eggs_index_proxy.updateBaseIndex(self.eggs_dir)
        return filename

    def checkPackageIndex(self, package_name):
        filename = os.path.join(self.eggs_dir, package_name, 'index.html')
        if not os.path.exists(filename):
            try:
                self.eggs_index_proxy.updatePackageIndex(
                    package_name,
                    eggs_dir=self.eggs_dir)
            except PackageNotFound:
                return None
        elif ALWAYS_REFRESH:
            # Force refresh
            try:
                self.eggs_index_proxy.updatePackageIndex(
                    package_name,
                    eggs_dir=self.eggs_dir)
            except PackageNotFound:
                pass
        else:
            # Just use the proxied copy.
            pass
        return filename

    def checkEggFor(self, package_name, eggname):
        filename = os.path.join(self.eggs_dir, package_name, eggname)
        if not os.path.exists(filename):
            try:
                self.eggs_index_proxy.updateEggFor(package_name, eggname,
                                                   eggs_dir=self.eggs_dir)
            except ValueError:
                return None
        return filename


def app_factory(global_config, **local_conf):
    # Grab config from wsgi .ini file. If not specified, config.py's values
    # take over.
    eggs_dir = local_conf.get('eggs_directory', None)
    index_url = local_conf.get('index', None)
    return EggProxyApp(index_url, eggs_dir)


class Installer(BaseInstaller):
    use_cheetah = False
    config_file = 'deployment.ini_tmpl'

    def config_content(self, command, vars):
        import pkg_resources
        module = 'collective.eggproxy'
        if pkg_resources.resource_exists(module, self.config_file):
            return self.template_renderer(
                pkg_resources.resource_string(module, self.config_file),
                vars,
                filename=self.config_file)


def standalone():
    port = config.get('eggproxy', 'port')
    # 0.2.0 way of starting the httpserver, but using the config'ed port
    # number instead of a hardcoded 8888.
    httpserver.serve(EggProxyApp(), host='127.0.0.1', port=port)
    # Post-0.2.0 way of starting the server using hardcoded config by means of
    # the package-internal .ini file. This does not allow starting it on a
    # different port, so I [reinout] commented it out for now.
    #import paste.script.command
    #this_dir = os.path.dirname(__file__)
    #sys.argv.extend(['serve', os.path.join(this_dir, 'wsgi.ini')])
    #paste.script.command.run()
