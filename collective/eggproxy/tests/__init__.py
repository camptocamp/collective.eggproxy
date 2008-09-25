from nose import with_setup
import tempfile
import shutil
import os

tempdir = os.path.join(tempfile.gettempdir(), 'eggs')

def setup_func():
    if os.path.isdir(tempdir):
        shutil.rmtree(tempdir)
    os.mkdir(tempdir)

def teardown_func():
    if os.path.isdir(tempdir):
        shutil.rmtree(tempdir)


