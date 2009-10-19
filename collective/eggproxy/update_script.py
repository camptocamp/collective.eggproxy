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
from os.path import getmtime
from time import time

from collective.eggproxy import eggs_index_proxy
from collective.eggproxy import PackageNotFound
from collective.eggproxy.config import config

UPDATE_INTERVAL = int(config.get("eggproxy", "update_interval")) * 3600
EGGS_DIR = config.get("eggproxy", "eggs_directory")
TIME_LIMIT = int(time()) - UPDATE_INTERVAL

def isOutDated(file_path):
    """A file is outdated if it does not exists or if its modification date is
    older than now - update_interval
    """
    if os.path.exists(file_path):
        mtime = getmtime(file_path)
        return mtime < TIME_LIMIT
    return True

def updateCache(*args):
    """
    """
    isDir = os.path.isdir
    pathJoin = os.path.join
    update = False
    index_file = pathJoin(EGGS_DIR, 'index.html')

    if isOutDated(index_file):
        eggs_index_proxy.updateBaseIndex()

    for package_name in os.listdir(EGGS_DIR):
        dir_path = pathJoin(EGGS_DIR, package_name)
        if not isDir(dir_path):
            continue

        index_file = pathJoin(dir_path, 'index.html')
        if isOutDated(index_file):
            try:
                eggs_index_proxy.updatePackageIndex(package_name)
            except PackageNotFound, msg:
                # FIXME: use logging
                print msg
