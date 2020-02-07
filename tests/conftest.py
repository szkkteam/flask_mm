#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
from __future__ import unicode_literals

import io
import os
import six

# Pip package imports
from flask import Flask
from werkzeug.datastructures import FileStorage

import pytest

# Internal package imports
import flask_mm as mm

PNG_FILE = os.path.join(os.path.dirname(__file__), 'flask.png')
JPG_FILE = os.path.join(os.path.dirname(__file__), 'flask.jpg')

TEST_CONFIGS = {
    'local' : {
        'STORAGE': 'local',
        'ROOT': os.path.abspath(os.path.join(os.path.dirname(__file__),'test')),
    },
    'file' : {
        'MANAGER': 'file'
    },
    'image': {
        'MANAGER': 'image',
        'THUMBNAIL_SIZE': (100,100, False)
    },
    's3': {
        'STORAGE': 's3',
        'AWS_ACCESS_KEY': os.environ.get('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        'AWS_REGION': os.environ.get('AWS_REGION'),
        'BUCKET_NAME': 'fairy-light',
        'ROOT': 'test',
    }
}

class TestConfig:
    TESTING = True

class TestFlaskConfig(Flask):
    def Configure(self, **configs):
        for key, value in configs.items():
            self.config[key] = value

@pytest.fixture
def init_mm():
    ext = mm.MediaManager()
    return ext

@pytest.fixture(autouse=True)
def app(init_mm):
    app = TestFlaskConfig('flask-mm-tests')
    app.config.from_object(TestConfig)
    ctx = app.test_request_context()
    ctx.push()
    yield app
    ctx.pop()

@pytest.fixture
def app_manager(request, app, init_mm):
    mark = request.param
    if mark is not None:
        storage = mark[0]
        manager = mark[1]
        try:
            conf = mark[2]
        except IndexError:
            conf = {}

        tmp_conf = { **TEST_CONFIGS[storage], **TEST_CONFIGS[manager] }
        tmp_conf = { **tmp_conf, **conf }

        app.Configure(
            MEDIA_MANAGER = tmp_conf
        )
        init_mm.init_app(app)
    return app

class Utils(object):

    def filestorage(self, filename, content, content_type=None):
        return FileStorage(
            self.file(content),
            filename,
            content_type=content_type
        )
    def file(self, content):
        if isinstance(content, six.binary_type):
            return io.BytesIO(content)
        elif isinstance(content, six.string_types):
            return io.BytesIO(content.encode('utf-8'))
        else:
            return content

@pytest.fixture
def utils():
    return Utils()

@pytest.fixture
def binfile():
    return PNG_FILE


@pytest.fixture
def pngfile():
    return PNG_FILE


@pytest.fixture
def jpgfile():
    return JPG_FILE