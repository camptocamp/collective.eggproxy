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
import logging

from paste import httpserver
from paste.script.appinstall import Installer as BaseInstaller
from paste.fileapp import FileApp
from paste.httpexceptions import HTTPNotFound

from collective.eggproxy.utils import IndexProxy, PackageNotFound

logger = logging.getLogger(__name__)


class EggProxyApp(object):

    def __init__(self, config):
        self.config = config
        self.eggs_dir = config.eggs_directory
        if not os.path.isdir(self.eggs_dir):
            logger.error('You must create the %r directory' % self.eggs_dir)
            raise Exception('eggs cache directory %r does not exist'
                    % self.eggs_dir)
        self.eggs_index_proxy = IndexProxy(config)

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
        if not os.path.exists(filename) or self.config.always_refresh:
            self.eggs_index_proxy.updateBaseIndex(self.eggs_dir)
        return filename

    def checkPackageIndex(self, package_name):
        filename = os.path.join(self.eggs_dir, package_name, 'index.html')
        logger.debug('Asking for %r package index page' % package_name)
        if not os.path.exists(filename):
            try:
                self.eggs_index_proxy.updatePackageIndex(
                    package_name,
                    eggs_dir=self.eggs_dir)
            except PackageNotFound:
                return None
        elif self.config.always_refresh:
            # Force refresh
            try:
                self.eggs_index_proxy.updatePackageIndex(
                    package_name,
                    eggs_dir=self.eggs_dir)
            except PackageNotFound:
                pass
        else:
            logger.debug('Return cached version of %r package index page'
                    % package_name)
        return filename

    def checkEggFor(self, package_name, eggname):
        filename = os.path.join(self.eggs_dir, package_name, eggname)
        logger.debug('Asking for package: %s - egg: %s'
                % (package_name, eggname))
        if not os.path.exists(filename):
            logger.debug('Not in cache, let\'s download it from package index')
            try:
                self.eggs_index_proxy.updateEggFor(package_name, eggname,
                                                   eggs_dir=self.eggs_dir)
            except ValueError as e:
                logger.debug('Download error: %s' % e)
                return None
        else:
            logger.debug('Found in cache: %s' % filename)

        return filename


def app_factory(global_config, **local_conf):
    # Grab config from wsgi .ini file. If not specified, config.py's values
    # take over.
    from collective.eggproxy.config import config
    config.initialize(local_conf)
    return EggProxyApp(config)


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
    from collective.eggproxy.config import config
    config.initialize()
    httpserver.serve(EggProxyApp(config), host=config.host, port=config.port)


if __name__ == '__main__':
    standalone()
