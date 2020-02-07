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
from flask_mm.postprocess import Watermarker

THUMB_WIDTH = 253
THUMB_HEIGHT = 220

POSTPROCESS_PARAMS = Watermarker("tests/flask.png", opacity=0.08, scale=0.2, position="c")

@pytest.mark.parametrize("app_manager", [('local', 'image', { 'POSTPROCESS': POSTPROCESS_PARAMS })], indirect=True)
class TestLocalImageManagerPostprocessWatermark:
    @pytest.mark.parametrize("image", [("tests/flask.jpg"), ("tests/flask.png")])
    def test_basic_postprocess_watermark(self, app_manager, image, utils):
        st = mm.by_name()

        with open(image, 'rb') as fp:
            f = utils.filestorage('horse.jpg', fp)
            filename = st.save(f)
            assert st.exists(filename)
            st.delete(filename)

@pytest.mark.parametrize("app_manager", [('local', 'image', {})], indirect=True)
class TestLocalImageManagerPostprocess:
    @pytest.mark.parametrize("image", [("tests/flask.jpg"), ("tests/flask.png")])
    def test_basic_watermark(self, app_manager, image, utils):

        st = mm.by_name()

        with open(image, 'rb') as fp:
            f = utils.filestorage('flask.jpg', fp)
            filename = st.save(f, postprocess=POSTPROCESS_PARAMS)
            assert st.exists(filename)
            st.delete(filename)


@pytest.mark.parametrize("app_manager", [('local', 'image', { 'THUMBNAIL_SIZE': (THUMB_WIDTH,THUMB_HEIGHT,True) })], indirect=True)
class TestLocalImageManagerThumbnailForced:

    #@pytest.mark.parametrize("image", [("tests/snow_terrain1.jpg"), ("tests/horse1.jpg"), ("tests/mogyi2.jpg")])
    @pytest.mark.parametrize("image", [("tests/flask.jpg"), ("tests/flask.png")])
    def test_save_thumbnail(self, app_manager, image, utils):
        st = mm.by_name()

        f = utils.file(Image.open(image))

        filename = st.save(f, 'test.jpg')
        assert st.exists(filename)
        assert st.exists(st.generate_thumbnail_name(filename))
        st.delete(filename)

    #@pytest.mark.parametrize("image", [("tests/snow_terrain1.jpg"), ("tests/horse1.jpg"), ("tests/mogyi2.jpg")])
    @pytest.mark.parametrize("image", [("tests/flask.jpg"), ("tests/flask.png")])
    def test_size_thumbnail(self, app_manager, image, utils):
        st = mm.by_name()

        f = utils.file(Image.open(image))

        filename = st.save(f, 'test.jpg')
        assert st.exists(st.generate_thumbnail_name(filename))
        thumb = Image.open(os.path.join('tests', 'test', st.generate_thumbnail_name(filename)))
        assert thumb.size[0] == THUMB_WIDTH
        assert thumb.size[1] == THUMB_HEIGHT

        st.delete(filename)

@pytest.mark.parametrize("app_manager", [('local', 'image', {}), ('s3', 'image', {})], indirect=True)
class TestImageManager:

    @pytest.mark.parametrize("image", [("tests/flask.jpg"), ("tests/flask.png")])
    def test_save_from_file(self, app_manager, image, utils):
        st = mm.by_name()

        f = utils.file(Image.open(image))

        filename = st.save(f, 'test.jpg')
        assert st.exists(filename)
        st.delete(filename)

    @pytest.mark.parametrize("image", [("tests/flask.jpg"), ("tests/flask.png")])
    def test_save_from_filestorage(self, app_manager, image, utils):
        st = mm.by_name()

        with open(image, 'rb') as fp:
            f = utils.filestorage('flask.jpg', fp)
            filename = st.save(f)
            assert st.exists(filename)
            st.delete(filename)

    @pytest.mark.parametrize("image", [("tests/flask.jpg"), ("tests/flask.png")])
    def test_save_from_filestorage_with_filename(self, app_manager, image, utils):
        st = mm.by_name()

        with open(image, 'rb') as fp:
            f = utils.filestorage(None, fp)
            filename = st.save(f, 'cica_flask.jpg')
            assert st.exists(filename)
            st.delete(filename)

    @pytest.mark.parametrize("image", [("tests/flask.jpg"), ("tests/flask.png")])
    def test_save_from_filestorage_original_name(self, app_manager, image, utils):
        st = mm.by_name()

        with open(image, 'rb') as fp:
            f = utils.filestorage('flask.jpg', fp)
            filename = st.save(f, generate_name=False)
            assert filename == 'flask.jpg'
            assert st.exists(filename)
            st.delete(filename)

    @pytest.mark.parametrize("image", [("tests/flask.jpg"), ("tests/flask.png")])
    def test_save_from_filestorage_with_filename_original_name(self, app_manager, image, utils):
        st = mm.by_name()

        with open(image, 'rb') as fp:
            f = utils.filestorage('flask.jpg', fp)
            filename = st.save(f, 'cicakutya.jpg', generate_name=False)
            assert filename == 'cicakutya.jpg'
            assert st.exists(filename)
            st.delete(filename)

