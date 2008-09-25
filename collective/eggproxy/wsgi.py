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
import sys
import tempfile
from paste.config import ConfigMiddleware
from paste.config import CONFIG
from paste.fileapp import FileApp
from paste.httpexceptions import HTTPNotFound
from collective.eggproxy.utils import PackageIndex
from collective.eggproxy import IndexProxy
from collective.eggproxy import PackageNotFound
from collective.eggproxy.config import EGGS_DIR

class EggProxyApp(object):

    def __init__(self, index_url=None, eggs_dir=EGGS_DIR):
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
                self.eggs_index_proxy.updatePackageIndex(package_name,
                                                         eggs_dir=self.eggs_dir)
            except PackageNotFound:
                return None
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
    default_dir = os.path.join(tempfile.gettempdir(),'eggs')
    eggs_dir = local_conf.get('eggs_directory', default_dir)
    if not os.path.isdir(eggs_dir):
        print 'You must create the %r directory' % eggs_dir
        sys.exit()
    index_url = local_conf.get('index', 'http://pypi.python.org/simple')
    return EggProxyApp(index_url, eggs_dir)

def standalone():
    import paste.script.command
    egg_dir = os.path.dirname(__file__)
    sys.argv.extend(['serve', os.path.join(egg_dir, 'wsgi.ini')])
    paste.script.command.run()

