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
from mod_python import apache

from collective.eggproxy import eggs_index_proxy
from collective.eggproxy.config import config

EGGS_DIR = config.get("eggproxy", "eggs_directory")


def fixup_handler(req):
    options = req.get_options()
    document_root = EGGS_DIR
    url_prefix = options['URLPrefix']
    url_prefix = [part for part in url_prefix.split('/') if part]
    url_prefix_len = len(url_prefix)
    uri_path = req.parsed_uri[apache.URI_PATH]
    uri_path = [part for part in uri_path.split('/') if part][url_prefix_len:]

    real_path = os.path.join(document_root, *uri_path)

    if os.path.exists(real_path) and not os.path.isdir(real_path):
        #FIXME isdir: cannot make apache serve index.html with mod_dir
        req.handler = 'default-handler'
        return apache.DECLINED

    req.handler = 'mod_python'
    req.add_handler('PythonHandler', modpython_handler)
    return apache.OK

def modpython_handler(req):

    options = req.get_options()
    document_root = EGGS_DIR
    url_prefix = options['URLPrefix']
    url_prefix = [part for part in url_prefix.split('/') if part]
    url_prefix_len = len(url_prefix)
    uri_path = req.parsed_uri[apache.URI_PATH]
    uri_path = [part for part in uri_path.split('/') if part][url_prefix_len:]

    if len(uri_path) > 0 and uri_path[-1] == 'index.html':
        uri_path.pop()

    real_path = os.path.join(document_root, *uri_path)
    real_path_exists = os.path.exists(real_path)

    if real_path_exists:
        if not os.path.isdir(real_path):
            return apache.DECLINED

        #FIXME we are doing the job of mod_dir
        real_path = os.path.join(real_path, 'index.html')
        if os.path.exists(real_path):
            req.internal_redirect(req.uri + 'index.html')
##             req.content_type = 'text/html'
##             req.sendfile(real_path)
            return apache.OK

    uri_path_len = len(uri_path)

    if uri_path_len > 2:
        # we are not supposed to go deeper than package/filename.egg
        return apache.HTTP_NOT_FOUND

    if uri_path_len == 0:
        # build the base index
        eggs_index_proxy.updateBaseIndex()
        req.internal_redirect(req.uri + 'index.html')
        return apache.OK

    package_name = uri_path[0]

    if uri_path_len == 1:
        try:
            eggs_index_proxy.updatePackageIndex(package_name)
        except ValueError:
            return apache.HTTP_NOT_FOUND

        req.internal_redirect(req.uri)
        return apache.OK
    else:
        eggname = uri_path[1]
        try:
            eggs_index_proxy.updateEggFor(package_name, eggname)
        except ValueError:
            return apache.HTTP_NOT_FOUND

        req.internal_redirect(req.uri)
        return apache.OK

    return apache.HTTP_NOT_FOUND
