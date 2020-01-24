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


class TestGetByName:

    def test_by_name_default(self, app, init_mm):
        init_mm.init_app(app)
        assert init_mm.by_name() == mm.by_name() == app.extensions['mediamanager']['media']

@pytest.mark.parametrize("app_manager", [('local', 'file', {})], indirect=True)
class TestLocalFileManager:

    def test_path(self, app_manager):
        st = mm.by_name()
        assert st.path('file.test') == os.path.abspath(os.path.join(os.path.dirname(__file__),'test', 'file.test'))

    def test_root(self, app_manager):
        st = mm.by_name()
        assert st.storage.root == os.path.abspath(os.path.join(os.path.dirname(__file__),'test'))

    def test_exists(self, app_manager):
        st = mm.by_name()
        assert st.exists('file.test')
        assert not st.exists('notexists')

    def test_file_open(self, app_manager):
        st = mm.by_name()
        with st.open('file.test') as f:
            assert f.read() == ""

    def test_open_write_new_file(self, app_manager):
        st = mm.by_name()
        with st.open('file.test', 'w') as f:
            f.write('')

    def test_open_read_not_found(self, app_manager):
        st = mm.by_name()
        with pytest.raises(FileNotFoundError):
            with st.open('file.not.found') as f:
                pass

    def test_read(self, app_manager):
        st = mm.by_name()
        assert st.read('file.test') == b''

    def test_read_not_found(self, app_manager):
        st = mm.by_name()
        with pytest.raises(FileNotFoundError):
            st.read('file.not.found')

    def test_write_overwrite(self, app_manager):
        st = mm.by_name()
        st.write('file.test', '', overwrite=True)

    def test_write_not_overwrite(self, app_manager):
        st = mm.by_name()
        with pytest.raises(FileExistsError):
            st.write('file.test', '')

    def test_save_from_file(self, app_manager, utils):
        st = mm.by_name()

        f = utils.file(b'test')

        filename = st.save(f, 'test.png')
        assert st.exists(filename)
        st.delete(filename)

    def test_save_from_filestorage(self, app_manager, utils):
        st = mm.by_name()

        f = utils.filestorage('test.png', 'test')

        filename = st.save(f)
        assert st.exists(filename)
        st.delete(filename)

    def test_save_from_filestorage_with_filename(self, app_manager, utils):
        st = mm.by_name()

        f = utils.filestorage('test.png', 'test')
        filename = st.save(f, st.generate_name(f))
        assert st.exists(filename)
        st.delete(filename)

    def test_save_from_filestorage_original_name(self, app_manager, utils):
        st = mm.by_name()

        f = utils.filestorage('test.png', 'test')

        filename = st.save(f)
        assert filename == 'test.png'
        assert st.exists(filename)
        st.delete(filename)

    def test_save_from_filestorage_with_filename_original_name(self, app_manager, utils):
        st = mm.by_name()

        f = utils.filestorage('test.png', 'test')

        filename = st.save(f, 'cicakutya.png')
        assert filename == 'cicakutya.png'
        assert st.exists(filename)
        st.delete(filename)

    def test_compress_files_file(self, app_manager, utils):
        st = mm.by_name()

        f1 = utils.file(b'test')
        f2 = utils.file(b'test')

        filename1 = st.save(f1, 'test1.png')
        filename2 = st.save(f2, 'test2.png')

        archive = st.archive_files(st.generate_name('compressed.zip'), [filename1, filename2])

        assert st.exists(archive)

        st.delete(filename1)
        st.delete(filename2)
        st.delete(archive)

    def test_compress_files_filestorage(self, app_manager, utils):
        st = mm.by_name()

        f1 = utils.filestorage('test.png', 'test')
        f2 = utils.filestorage('test.png', 'test')

        filename1 = st.save(f1, st.generate_name(f1))
        filename2 = st.save(f2, st.generate_name(f2))

        archive = st.archive_files(st.generate_name('compressed.zip'), [filename1, filename2])

        assert st.exists(archive)

        st.delete(filename1)
        st.delete(filename2)
        st.delete(archive)