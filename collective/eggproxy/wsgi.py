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
from paste import httpserver
from paste.fileapp import FileApp
from paste.httpexceptions import HTTPNotFound
from collective.eggproxy import eggs_index_proxy
from collective.eggproxy import PackageNotFound
from collective.eggproxy.config import EGGS_DIR

class EggProxyApp(object):

    def __call__(self, environ, start_response):
        """
        """
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
        filename = os.path.join(EGGS_DIR, 'index.html')
        if not os.path.exists(filename):
            eggs_index_proxy.updateBaseIndex()
        return filename

    def checkPackageIndex(self, package_name):
        filename = os.path.join(EGGS_DIR, package_name, 'index.html')
        if not os.path.exists(filename):
            try:
                eggs_index_proxy.updatePackageIndex(package_name)
            except PackageNotFound:
                return None
        return filename

    def checkEggFor(self, package_name, eggname):
        filename = os.path.join(EGGS_DIR, package_name, eggname)
        if not os.path.exists(filename):
            try:
                eggs_index_proxy.updateEggFor(package_name, eggname)
            except ValueError:
                return None
        return filename


def app_factory(global_config, **local_conf):
    return EggProxyApp()

def standalone():
    httpserver.serve(EggProxyApp(), host='127.0.0.1', port='8888')

if __name__ == '__main__':
    standalone()
