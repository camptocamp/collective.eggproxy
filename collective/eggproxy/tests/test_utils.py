# -*- coding: utf-8 -*-
from collective.eggproxy.utils import IndexProxy
from collective.eggproxy.tests import *

index = IndexProxy()

@with_setup(setup_func, teardown_func)
def test_index():
    # assume non-existence
    assert os.path.isfile(os.path.join(tempdir, 'index.html')) == False

    index.updateBaseIndex(tempdir)

    # assume existence
    assert os.path.isfile(os.path.join(tempdir, 'index.html')) == True

    page = open(os.path.join(tempdir, 'index.html')).read()

    # check case
    assert 'PasteDeploy' in page

@with_setup(setup_func, teardown_func)
def test_package():
    index.updatePackageIndex('collective.eggproxy', tempdir)
    dirname = os.path.join(tempdir, 'collective.eggproxy')

    assert os.path.isdir(dirname) == True

    assert os.listdir(dirname) == ['index.html']
    ['index.html']

    page = open(os.path.join(dirname, 'index.html')).read()
    assert '<html><head><title>collective.eggproxy</title></head>' in page

@with_setup(setup_func, teardown_func)
def test_package_case_sensitive():
    index.updatePackageIndex('Paste', tempdir)
    dirname = os.path.join(tempdir, 'Paste')

    assert os.path.isdir(dirname) == True

    assert os.listdir(dirname) == ['index.html']
    ['index.html']

    page = open(os.path.join(dirname, 'index.html')).read()
    assert '<html><head><title>Paste</title></head>' in page
