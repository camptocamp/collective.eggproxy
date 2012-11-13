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
import logging.config
from ConfigParser import ConfigParser
from ConfigParser import NoSectionError

logger = logging.getLogger(__name__)


# this asbool function is borrowed from the Pyramid web framework
def asbool(s):
    """ Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is any of ``t``, ``true``, ``y``, ``on``, or ``1``, otherwise
    return the boolean value ``False``.  If ``s`` is the value ``None``,
    return ``False``.  If ``s`` is already one of the boolean values ``True``
    or ``False``, return it."""
    truthy = frozenset(('t', 'true', 'y', 'yes', 'on', '1'))
    if s is None:
        return False
    if isinstance(s, bool):
        return s
    s = str(s).strip()
    return s.lower() in truthy


class Configurator(dict):

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("'%s' object has no attribute '%s" %
                                 (self.__class__.__name__, name))

    def initialize(self, config=None):

        if not config:
            # First try: User-specific config file
            cfg_file = os.path.join(
                    os.path.expanduser('~'), 'eggproxy.conf')
            # Second try: buildout setup, we're in bin/, config is in etc/.
            if not os.path.exists(cfg_file):
                bin_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                cfg_file = os.path.join(bin_dir, '../etc/eggproxy.conf')
            # Last try: Global config file in /etc
            if not os.path.exists(cfg_file):
                cfg_file = '/etc/eggproxy.conf'

            if os.path.exists(cfg_file):
                cfg = ConfigParser()
                try:
                    logging.config.fileConfig(cfg_file)
                except Exception:
                    logging.basicConfig(
                            format='%(asctime)s %(levelname)-5.5s [%(name)s] '
                            '%(message)s', level=logging.INFO)
                logger.info("Using config file: %s" % cfg_file)
                cfg.readfp(open(cfg_file))
                # Check for old [default] section that fails with python2.6 had
                # thus has been changed to [eggproxy] in 0.4
                try:
                    cfg.get('default', 'eggs_directory')
                    old_section_name = True
                except NoSectionError:
                    old_section_name = False
                if old_section_name:
                    logger.error("rename the [default] section in the config"
                            " file \"%s\" to [eggproxy].  This is needed for"
                            " python2.6 compatibility." % cfg_file)
                    sys.exit(1)

            config = dict(cfg.items("eggproxy"))

        for k in ("update_interval", "port", "timeout"):
            if k in config:
                config[k] = int(config[k])
        if "always_refresh" in config:
            config["always_refresh"] = asbool(config["always_refresh"])

        self.update(config)
        logger.debug("Using following configuration: %s" % self)

# initialize configurator with default values
config = Configurator(
        eggs_directory="/var/www",
        index="http://pypi.python.org/simple",
        update_interval=24,
        host='127.0.0.1',
        port=8888,
        always_refresh=False,
        timeout=3,
        )
