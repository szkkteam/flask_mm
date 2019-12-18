#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
from __future__ import unicode_literals

import os

# Pip package imports
from flask import url_for

import pytest
# Internal package imports
import flask_mm as mm

def test_default_configuration(app, init_mm):
    app.Configure()
    init_mm.init_app(app)
    assert 'media' in app.extensions['mediamanager']
    st = init_mm.by_name()
    assert st.storage.root == os.path.join(app.instance_path, 'media')

def test_single_dict_configuration(app, init_mm):
    app.Configure(
        MEDIA_MANAGER = {
            'URL': '',
            'PREFIX': '/media',
            'STORAGE': 'local',
            'MANAGER': 'file',
            'ROOT': os.path.join(app.instance_path, 'media')}
    )
    init_mm.init_app(app)
    assert 'media' in app.extensions['mediamanager']
    st = init_mm.by_name()
    assert st.storage.root == os.path.join(app.instance_path, 'media')

def test_signle_dict_multiple_configuration(app, init_mm):
    app.Configure(
        MEDIA_MANAGER = {
            'PHOTO': {
                'URL': '',
                'PREFIX': '/media',
                'STORAGE': 'local',
                'MANAGER': 'file',
                'ROOT': os.path.join(app.instance_path, 'photo')
            },
            'VIDEO': {
                'URL': '',
                'PREFIX': '/media',
                'STORAGE': 'local',
                'MANAGER': 'file',
                'ROOT': os.path.join(app.instance_path, 'video')
            }
        }
    )
    init_mm.init_app(app)
    assert 'photo' in app.extensions['mediamanager']
    assert 'video' in app.extensions['mediamanager']
    photo = init_mm.by_name('photo')
    video = init_mm.by_name('video')
    assert photo.storage.root == os.path.join(app.instance_path, 'photo')
    assert video.storage.root == os.path.join(app.instance_path, 'video')

def test_multiple_dict_single_configuration(app, init_mm):
    app.Configure(
            MM_PHOTO = {
                'URL': '',
                'PREFIX': '/media',
                'STORAGE': 'local',
                'MANAGER': 'file',
                'ROOT': os.path.join(app.instance_path, 'photo')
            },
            MM_VIDEO = {
                'URL': '',
                'PREFIX': '/media',
                'STORAGE': 'local',
                'MANAGER': 'file',
                'ROOT': os.path.join(app.instance_path, 'video')
            }
    )
    init_mm.init_app(app)
    assert 'photo' in app.extensions['mediamanager']
    assert 'video' in app.extensions['mediamanager']
    photo = init_mm.by_name('photo')
    video = init_mm.by_name('video')
    assert photo.storage.root == os.path.join(app.instance_path, 'photo')
    assert video.storage.root == os.path.join(app.instance_path, 'video')

def test_single_configuration(app, init_mm):
    app.Configure(
            MM_PHOTO_URL = '',
            MM_PHOTO_PREFIX = '/media',
            MM_PHOTO_STORAGE = 'local',
            MM_PHOTO_MANAGER  = 'file',
            MM_PHOTO_ROOT = os.path.join(app.instance_path, 'photo'),
            MM_VIDEO_URL='',
            MM_VIDEO_PREFIX='/media',
            MM_VIDEO_STORAGE='local',
            MM_VIDEO_MANAGER='file',
            MM_VIDEO_ROOT=os.path.join(app.instance_path, 'video'),
    )
    init_mm.init_app(app)
    assert 'photo' in app.extensions['mediamanager']
    assert 'video' in app.extensions['mediamanager']
    photo = init_mm.by_name('photo')
    video = init_mm.by_name('video')
    assert photo.storage.root == os.path.join(app.instance_path, 'photo')
    assert video.storage.root == os.path.join(app.instance_path, 'video')

def test_single_configuration_mix_global(app, init_mm):
    app.Configure(
        MM_PHOTO_URL='',
        MM_PHOTO_PREFIX='/media',
        MM_VIDEO_URL='',
        MM_VIDEO_PREFIX='/media',
        MM_STORAGE = 'local',
        MM_MANAGER = 'file',
        MM_ROOT = os.path.join(app.instance_path, 'test')
    )
    init_mm.init_app(app)
    assert 'photo' in app.extensions['mediamanager']
    assert 'video' in app.extensions['mediamanager']
    photo = init_mm.by_name('photo')
    video = init_mm.by_name('video')
    assert photo.storage.root == os.path.join(app.instance_path, 'test')
    assert video.storage.root == os.path.join(app.instance_path, 'test')

def test_configuration_global(app, init_mm):
    app.Configure(
        MM_URL = '',
        MM_PREFIX = '/media',
        MM_SOTRAGE = 'local',
        MM_MANAGER = 'file',
        MM_ROOT = os.path.join(app.instance_path, 'test')
    )

    init_mm.init_app(app)
    assert 'media' in app.extensions['mediamanager']
    st = init_mm.by_name()
    print(st.storage.root)
    assert st.storage.root == os.path.join(app.instance_path, 'test')

def test_signle_dict_multiple_configuration_mix_global(app, init_mm):
    app.Configure(
        MEDIA_MANAGER = {
            'PHOTO': {
                'URL': '',
                'PREFIX': '/media',
                'STORAGE': 'local',
                'MANAGER': 'file',
            },
            'VIDEO': {
                'URL': '',
                'PREFIX': '/media',
                'STORAGE': 'local',
                'MANAGER': 'file',
            },
            'ROOT': os.path.join(app.instance_path, 'test')
        }
    )
    init_mm.init_app(app)
    assert 'photo' in app.extensions['mediamanager']
    assert 'video' in app.extensions['mediamanager']
    photo = init_mm.by_name('photo')
    video = init_mm.by_name('video')
    assert photo.storage.root == os.path.join(app.instance_path, 'test')
    assert video.storage.root == os.path.join(app.instance_path, 'test')

def test_multiple_dict_single_configuration_mix_global(app, init_mm):
    app.Configure(
            MM_PHOTO = {
                'URL': '',
                'PREFIX': '/media',
                'STORAGE': 'local',
                'MANAGER': 'file',
            },
            MM_VIDEO = {
                'URL': '',
                'PREFIX': '/media',
                'STORAGE': 'local',
                'MANAGER': 'file',
            },
            MM_ROOT=os.path.join(app.instance_path, 'test')
    )
    init_mm.init_app(app)
    assert 'photo' in app.extensions['mediamanager']
    assert 'video' in app.extensions['mediamanager']
    photo = init_mm.by_name('photo')
    video = init_mm.by_name('video')
    assert photo.storage.root == os.path.join(app.instance_path, 'test')
    assert video.storage.root == os.path.join(app.instance_path, 'test')

def test_multiple_config_get_by_without_name(app, init_mm):
    app.Configure(
        MM_PHOTO_URL='',
        MM_PHOTO_PREFIX='/media',
        MM_VIDEO_URL='',
        MM_VIDEO_PREFIX='/media',
        MM_STORAGE = 'local',
        MM_MANAGER = 'file',
        MM_ROOT = os.path.join(app.instance_path, 'test')
    )
    init_mm.init_app(app)
    assert 'photo' in app.extensions['mediamanager']
    assert 'video' in app.extensions['mediamanager']
    with pytest.raises(KeyError):
        photo = init_mm.by_name()
    with pytest.raises(KeyError):
        video = init_mm.by_name()
