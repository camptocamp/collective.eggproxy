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
import sys
from ConfigParser import ConfigParser
from ConfigParser import NoSectionError


# First try: User-specific config file
CONFIG_FILE = os.path.join(os.path.expanduser('~'), 'eggproxy.conf')
# Second try: buildout setup, we're in bin/, config is in etc/.
if not os.path.exists(CONFIG_FILE):
    bin_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    CONFIG_FILE = os.path.join(bin_dir, '../etc/eggproxy.conf')
# Last try: Global config file in /etc
if not os.path.exists(CONFIG_FILE):
    CONFIG_FILE = '/etc/eggproxy.conf'

#print "Using config file", CONFIG_FILE
config = ConfigParser()
config.add_section("eggproxy")
config.set("eggproxy", "eggs_directory", "/var/www")
config.set("eggproxy", "index", 'http://pypi.python.org/simple')
config.set("eggproxy", "update_interval", '24')
config.set("eggproxy", "port", '8888')
config.set("eggproxy", "always_refresh", '0')
config.set("eggproxy", "timeout", '3')

if os.path.exists(CONFIG_FILE):
    config.readfp(open(CONFIG_FILE))
    # Check for old [default] section that fails with python2.6 had thus has
    # been changed to [eggproxy] in 0.4
    try:
        config.get('default', 'eggs_directory')
        old_section_name = True
    except NoSectionError:
        old_section_name = False
    if old_section_name:
        print "WARNING: rename the [default] section in the config file"
        print CONFIG_FILE
        print "to [eggproxy].  This is needed for python2.6 compatibility."
        sys.exit(1)
