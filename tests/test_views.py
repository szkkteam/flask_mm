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
class TestUrls:

    def test_url(self, app_manager):
        st = mm.by_name()

        expected_url = url_for('mm.get_file', mm=st.name, filename='test.txt')
        assert st.url('test.txt') == expected_url

    def test_get_file(self, app_manager):
        st = mm.by_name()

        file_url = url_for('mm.get_file', mm='media', filename='file.test')
        response = app_manager.test_client().get(file_url, follow_redirects=True)
        print("respinse data:", response.data)
        #assert response.status_code == 200
        assert response.data == ''.encode('utf-8')

    def test_get_file_not_found(self, app_manager):
        st = mm.by_name()

        file_url = url_for('mm.get_file', mm='media', filename='not.found')

        response = app_manager.test_client().get(file_url)
        assert response.status_code == 404

    def test_get_file_no_storage(self, app_manager):
        st = mm.by_name()

        file_url = url_for('mm.get_file', mm='fake', filename='file.test')

        response = app_manager.test_client().get(file_url)
        assert response.status_code == 404

