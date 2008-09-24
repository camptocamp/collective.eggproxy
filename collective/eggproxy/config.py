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
from ConfigParser import ConfigParser

CONFIG_FILE = '/etc/eggproxy.conf'

if not os.path.exists(CONFIG_FILE):
    CONFIG_FILE = os.path.join(os.path.expanduser('~'), 'eggproxy.conf')

config = ConfigParser()
config.add_section("default")
config.set("default", "eggs_directory", "/var/www")
config.set("default", "index", 'http://pypi.python.org/simple')
config.set("default", "update_interval", 24)

if os.path.exists(CONFIG_FILE):
    config.readfp(open(CONFIG_FILE))

EGGS_DIR = config.get("default", "eggs_directory")

