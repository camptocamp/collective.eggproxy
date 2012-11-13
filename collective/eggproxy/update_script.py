# -*- coding: utf-8 -*-
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
from time import time

from collective.eggproxy.utils import IndexProxy, PackageNotFound
from collective.eggproxy.config import config


def updateCache(*args):

    config.initialize()

    # A file is outdated if it does not exists or if its modification date is
    # older than now - update_interval
    isOutDated = lambda fn: not (os.path.exists(fn) and
            os.path.getmtime(fn) > int(time()) - config.update_interval * 3600)
    eggs_index_proxy = IndexProxy(config)

    if isOutDated(os.path.join(config.eggs_directory, 'index.html')):
        eggs_index_proxy.updateBaseIndex()

    for package_name in os.listdir(config.eggs_directory):
        dir_path = os.path.join(config.eggs_directory, package_name)
        if not os.path.isdir(dir_path):
            continue

        if isOutDated(os.path.join(dir_path, 'index.html')):
            try:
                eggs_index_proxy.updatePackageIndex(package_name)
            except PackageNotFound, msg:
                # FIXME: use logging
                print msg
