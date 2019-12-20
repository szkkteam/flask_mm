#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
from __future__ import unicode_literals

import os
import io
from PIL import Image

# Pip package imports
from flask import url_for

import pytest
# Internal package imports
import flask_mm as mm


@pytest.mark.parametrize("app_manager", [('local', 'image', {})], indirect=True)
class TestLocalImageManager:

    def test_save_from_file(self, app_manager, utils):
        st = mm.by_name()

        f = utils.file(Image.open('tests/flask.jpg'))

        filename = st.save(f, 'test.jpg')
        assert st.exists(filename)
        st.delete(filename)

    def test_save_from_filestorage(self, app_manager, utils):
        st = mm.by_name()

        with open('tests/flask.jpg', 'rb') as fp:
            f = utils.filestorage('flask.jpg', fp)
            filename = st.save(f)
            assert st.exists(filename)
            st.delete(filename)

    def test_save_from_filestorage_with_filename(self, app_manager, utils):
        st = mm.by_name()

        with open('tests/flask.jpg', 'rb') as fp:
            f = utils.filestorage(None, fp)
            filename = st.save(f, 'cica_flask.jpg')
            assert st.exists(filename)
            st.delete(filename)

    def test_save_from_filestorage_original_name(self, app_manager, utils):
        st = mm.by_name()

        with open('tests/flask.jpg', 'rb') as fp:
            f = utils.filestorage('flask.jpg', fp)
            filename = st.save(f, generate_name=False)
            assert filename == 'flask.jpg'
            assert st.exists(filename)
            st.delete(filename)

    def test_save_from_filestorage_with_filename_original_name(self, app_manager, utils):
        st = mm.by_name()

        with open('tests/flask.jpg', 'rb') as fp:
            f = utils.filestorage('flask.jpg', fp)
            filename = st.save(f, 'cicakutya.jpg', generate_name=False)
            assert filename == 'cicakutya.jpg'
            assert st.exists(filename)
            st.delete(filename)

