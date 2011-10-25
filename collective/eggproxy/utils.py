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
import tempfile
import urllib2
import urlparse
import shutil
import sys
from setuptools.package_index import PackageIndex as BasePackageIndex
from setuptools.package_index import (
    egg_info_for_url,
    safe_name,
    safe_version,
    to_filename,
    HREF,
    htmldecode,
    find_external_links,
    PYPI_MD5,
    )

from pkg_resources import Requirement
from collective.eggproxy.config import config

ALWAYS_REFRESH = config.getboolean('eggproxy', 'always_refresh')
EGGS_DIR = config.get("eggproxy", "eggs_directory")
INDEX_URL = config.get("eggproxy", "index")
#INDEX is defined *after* the PackageIndex class.


class PackageIndex(BasePackageIndex):
    """
    """

    def can_add(self, dist):
        """Overrides PackageIndex.can_add method to remove filter on python
    major version: we want packages for all versions, all platforms
        """
        return True

    def find_packages(self, requirement):
        """Override: purge cached url if ALWAYS_REFRESH"""
        # purged_url caches the urls that has been already purged so that
        # we won't purge the same url again
        purged_url = {}

        def before_scan_url(url):
            if ALWAYS_REFRESH and url in self.fetched_urls \
                    and url not in purged_url:
                # Zap ourselves from the fetched url list, otherwise we'll
                # never be updated as long as the server runs.
                # And mark this url as already purged
                del self.fetched_urls[url]
                purged_url[url] = True

        url = self.index_url + requirement.unsafe_name+'/'
        before_scan_url(url)
        self.scan_url(url)

        if not self.package_pages.get(requirement.key):
            # Fall back to safe version of the name
            url = self.index_url + requirement.project_name+'/'
            before_scan_url(url)
            self.scan_url(url)

        if not self.package_pages.get(requirement.key):
            # We couldn't find the target package, so search the index page too
            self.not_found_in_index(requirement)

        for url in list(self.package_pages.get(requirement.key,())):
            # scan each page that might be related to the desired package
            before_scan_url(url)
            self.scan_url(url)

    def process_index(self, url, page):
        """Process the contents of a PyPI page
        Override: don't lowercase package name
        """
        def scan(link):
            # Process a URL to see if it's for a package page
            if link.startswith(self.index_url):
                parts = map(
                    urllib2.unquote, link[len(self.index_url):].split('/')
                )
                if len(parts)==2 and '#' not in parts[1]:
                    # it's a package page, sanitize and index it
                    pkg = safe_name(parts[0])
                    ver = safe_version(parts[1])
                    # changed "pkg.lower()" to "pkg"
                    self.package_pages.setdefault(pkg, {})[link] = True
                    return to_filename(pkg), to_filename(ver)
            return None, None

        # process an index page into the package-page index
        for match in HREF.finditer(page):
            try:
                scan( urlparse.urljoin(url, htmldecode(match.group(1))) )
            except ValueError:
                pass

        pkg, ver = scan(url)   # ensure this page is in the page index
        if pkg:
            # process individual package page
            for new_url in find_external_links(url, page):
                # Process the found URL
                base, frag = egg_info_for_url(new_url)
                if base.endswith('.py') and not frag:
                    if ver:
                        new_url+='#egg=%s-%s' % (pkg,ver)
                    else:
                        self.need_version_info(url)
                self.scan_url(new_url)

            return PYPI_MD5.sub(
                lambda m: '<a href="%s#md5=%s">%s</a>' % m.group(1,3,2), page
            )
        else:
            return ""   # no sense double-scanning non-package pages


INDEX = PackageIndex(index_url=INDEX_URL)


class PackageNotFound(Exception):
    """
    """


class IndexProxy(object):

    def __init__(self, index=None):
        self.index = index or INDEX

    def updateBaseIndex(self, eggs_dir=EGGS_DIR):
        """Update base index.html
        """
        file_path = os.path.join(eggs_dir, 'index.html')
        html = open(file_path, 'w')

        # take care of the already cached eggs in repository:
        # union these packages with the remote packages
        local_package_names = [item for item in os.listdir(eggs_dir)
                if os.path.isdir(os.path.join(eggs_dir,item))]
        self.index.scan_all()
        package_names = list(set(self.index.package_pages.keys()).union(
            set(local_package_names)))
        package_names.sort()

        print >> html, "<html><head><title>Simple Index</title></head><body>"
        for pack_name in package_names:
            print >> html, '<a href="%s/">%s</a><br/>' % (pack_name, pack_name)
        print >> html, '</body></html>'

        html.close()
        del html

    def _lookupPackage(self, package_name):
        requirement = Requirement.parse(package_name)
        self.index.find_packages(requirement)

    def updatePackageIndex(self, package_name, eggs_dir=EGGS_DIR):
        """Update info for a specific package
        """

        package_path = os.path.join(eggs_dir, package_name)
        local_eggs = {}
        if os.path.exists(package_path):
            for pkg in os.listdir(package_path):
                if pkg != "index.html":
                    local_eggs[pkg] = True

        self._lookupPackage(package_name)
        if not self.index[package_name] and len(local_eggs) == 0:
            raise PackageNotFound, "Package '%s' does not exists or has no " \
                    "eggs" % package_name

        if not os.path.exists(package_path):
            os.mkdir(package_path)
        html_path = os.path.join(package_path, 'index.html')
        dists = self.index[package_name]
        if not dists and os.path.exists(html_path):
            # We already have a cached index page and there are no dists.
            # Pypi is probably down, so we keep our existing one.
            return
        html = open(html_path, 'w')
        title = "Links for %s" % package_name
        print >> html, "<html><head><title>%s</title></head>" % package_name
        print >> html, "<body><h1>%s</h1>" % package_name
        for dist in dists:
            if getattr(dist, "module_path", None) is not None:
                # this is a module installed in system
                continue

            filename, md5 = egg_info_for_url(dist.location)
            print >> html, (
                '<a href="%s#%s" rel="download">%s</a><br />'
                % (filename, md5, filename)
                )
            if filename in local_eggs:
                del local_eggs[filename]
        for egg in local_eggs:
            print >> html, (
                '<a href="%s" rel="download">%s</a><br />'
                % (egg, egg)
                )

        print >> html, "</body></html>"
        html.close()
        del html

    def updateEggFor(self, package_name, eggname, eggs_dir=EGGS_DIR):
        """Download an egg for package_name
        """
        self._lookupPackage(package_name)
        file_path = os.path.join(eggs_dir, package_name, eggname)
        for dist in self.index[package_name]:
            if getattr(dist, "module_path", None) is not None:
                # this is a module installed in system (directory), we want
                # to download a fresh package
                continue

            filename, md5 = egg_info_for_url(dist.location)
            # There may be more than one filename that matches: if the first n
            # fail, we want to try until one works!
            if filename == eggname:
                tmp = tempfile.gettempdir()
                try:
                    tmp_location = self.index.download(dist.location, tmp)
                    sys.stderr.write('Downloaded %s\n' % dist.location)
                    shutil.move(tmp_location, file_path)
                    return
                except Exception, err:
                    sys.stderr.write('Error downloading %s: \n\t%s\n' % (dist.location, err))

        raise ValueError, "Egg '%s' not found in index" % eggname
