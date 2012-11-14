# -*- coding: utf-8 -*-
import unittest


class TestWsgi(unittest.TestCase):

    def setUp(self):
        import tempfile
        from paste.fixture import TestApp
        from collective.eggproxy.wsgi import EggProxyApp
        from collective.eggproxy.config import config

        self.tempdir = tempfile.mkdtemp()
        config["eggs_directory"] = self.tempdir
        self.app = TestApp(EggProxyApp(config))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tempdir)

    def test_root_index(self):
        response = self.app.get('/')
        assert 'collective.eggproxy' in response, response

    def test_package_index(self):
        response = self.app.get('/collective.eggproxy')
        assert '<title>Links for collective.eggproxy</title>' in response, \
                response

    def test_package(self):
        # without trailing '/', paste.fixture.TestResponse click results in:
        # >>> urlparse.urljoin('/collective.eggproxy',
        #                      'collective.eggproxy-0.2.0.tar.gz')
        # '/collective.eggproxy-0.2.0.tar.gz'
        # actual url is: /collective.eggproxy/collective.eggproxy-0.2.0.tar.gz
        response = self.app.get('/collective.eggproxy/')
        response = response.click(index=0, verbose=True)
        assert ('Content-Encoding', 'gzip') in response.headers, \
                response.headers
