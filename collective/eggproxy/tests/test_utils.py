# -*- coding: utf-8 -*-
import unittest
import os


class TestUtils(unittest.TestCase):

    def setUp(self):
        import tempfile
        from collective.eggproxy.utils import IndexProxy
        from collective.eggproxy.config import config

        self.tempdir = tempfile.mkdtemp()
        self.base_index = os.path.join(self.tempdir, 'index.html')
        config["eggs_directory"] = self.tempdir
        self.index = IndexProxy(config)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tempdir)

    def test_index(self):
        # assume non-existence
        assert os.path.isfile(self.base_index) is False

        self.index.updateBaseIndex(self.tempdir)

        # assume existence
        assert os.path.isfile(self.base_index) is True

        page = open(self.base_index).read()

        # check case
        assert 'PasteDeploy' in page

    def test_local_index(self):
        dirname = os.path.join(self.tempdir, 'my.eggproxy.test.package')
        os.mkdir(dirname)

        self.index.updateBaseIndex(self.tempdir)

        page = open(self.base_index).read()
        assert '<a href="my.eggproxy.test.package/">' \
                'my.eggproxy.test.package</a>' in page

    def test_package(self):
        self.index.updatePackageIndex('collective.eggproxy', self.tempdir)
        dirname = os.path.join(self.tempdir, 'collective.eggproxy')

        assert os.path.isdir(dirname) is True

        assert os.listdir(dirname) == ['index.html']
        ['index.html']

        page = open(os.path.join(dirname, 'index.html')).read()
        assert '<html><head><title>Links for collective.eggproxy' \
                '</title></head>' in page

    def test_local_packages(self):
        dirname = os.path.join(self.tempdir, 'collective.eggproxy')
        os.mkdir(dirname)
        dummy = open(
                os.path.join(dirname, 'collective.eggproxy-0.0.0.tar.gz'), 'w')
        dummy.write('')
        dummy.close()

        self.index.updatePackageIndex('collective.eggproxy', self.tempdir)

        page = open(os.path.join(dirname, 'index.html')).read()
        assert '<a href="collective.eggproxy-0.0.0.tar.gz" rel="download">' \
                'collective.eggproxy-0.0.0.tar.gz</a>' in page

    def test_package_case_sensitive(self):
        self.index.updatePackageIndex('Paste', self.tempdir)
        dirname = os.path.join(self.tempdir, 'Paste')

        assert os.path.isdir(dirname) is True

        assert os.listdir(dirname) == ['index.html']
        ['index.html']

        page = open(os.path.join(dirname, 'index.html')).read()
        assert '<html><head><title>Links for Paste</title></head>' in page
