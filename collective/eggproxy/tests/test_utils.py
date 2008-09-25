# -*- coding: utf-8 -*-
from collective.eggproxy.utils import IndexProxy
from nose import with_setup
import tempfile
import shutil
import os

index = IndexProxy()
tempdir = os.path.join(tempfile.gettempdir(), 'eggs')

def setup_func():
    if os.path.isdir(tempdir):
        shutil.rmtree(tempdir)
    os.mkdir(tempdir)

def teardown_func():
    if os.path.isdir(tempdir):
        shutil.rmtree(tempdir)

@with_setup(setup_func, teardown_func)
def test_index():
    # assume non-existence
    assert os.path.isfile(os.path.join(tempdir, 'index.html')) == False

    index.updateBaseIndex(tempdir)

    # assume existence
    assert os.path.isfile(os.path.join(tempdir, 'index.html')) == True

    page = open(os.path.join(tempdir, 'index.html')).read()

    # check case
    assert 'ZODB3' in page

@with_setup(setup_func, teardown_func)
def test_package():
    index.updatePackageIndex('collective.eggproxy', tempdir)
    dirname = os.path.join(tempdir, 'collective.eggproxy')

    assert os.path.isdir(dirname) == True

    assert os.listdir(dirname) == ['index.html']
    ['index.html']

    page = open(os.path.join(dirname, 'index.html')).read()
    assert '<html><head><title>collective.eggproxy</title></head>' in page
