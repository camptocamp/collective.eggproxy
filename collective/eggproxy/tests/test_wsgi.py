# -*- coding: utf-8 -*-
from collective.eggproxy.wsgi import EggProxyApp
from collective.eggproxy.tests import *
from paste.fixture import TestApp

app = TestApp(EggProxyApp('http://pypi.python.org/simple', eggs_dir=tempdir))

@with_setup(setup_func, teardown_func)
def test_root_index():
    response = app.get('/')
    assert 'collective.eggproxy' in response, response

@with_setup(setup_func, teardown_func)
def test_package_index():
    response = app.get('/collective.eggproxy')
    assert 'collective.eggproxy' in response, response

@with_setup(setup_func, teardown_func)
def test_package():
    response = app.get('/collective.eggproxy')
    response = app.get('/collective.eggproxy/collective.eggproxy-0.2.0.tar.gz')
    assert ('Content-Encoding', 'gzip') in response.headers, response.headers

