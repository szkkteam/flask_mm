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
def binfile():
    return PNG_FILE


@pytest.fixture
def pngfile():
    return PNG_FILE


@pytest.fixture
def jpgfile():
    return JPG_FILE