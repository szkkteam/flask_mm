#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from six.moves.urllib.parse import urljoin

from flask import url_for, request, abort

from werkzeug import secure_filename, FileStorage, cached_property

# Internal package imports
from flask_mm.utils import UuidNameGen
from flask_mm.files import extension, lower_extension
from flask_mm.storages import BaseStorage

DEFAULT_MANAGER = 'file'

class BaseManager(object):

    def __init__(self, app, name, storage, *args, **kwargs):
        self.name = name
        assert isinstance(storage, BaseStorage), "Storage object must be a subclass of BaseStorage"
        self.storage = storage

        # Optional parameters
        self.allowed_extensions = kwargs.get('extensions', None)
        self.namegen = kwargs.get('name_gen', UuidNameGen)

    def _clean_url(self, url):
        if not url.startswith('http://') and not url.startswith('https://'):
            url = ('https://' if request.is_secure else 'http://') + url
        if not url.endswith('/'):
            url += '/'
        return url

    def url(self, filename, external=False):
        if isinstance(filename, FileStorage):
            filename = filename.filename
        if filename.startswith('/'):
            filename = filename[1:]
        if self.storage.has_url:
            # TODO: Clean url or not?
            return urljoin(self._clean_url(self.storage.base_url), self.storage.path(filename))
        else:
            return url_for('mm.get_file', mm=self.name, filename=filename, _external=external)

    def is_file_allowed(self, filename):
        if not self.allowed_extensions:
            return True
        return (extension(filename) in self.allowed_extensions)

    def generate_name(self, filename_or_wfs):
        if isinstance(filename_or_wfs, FileStorage):
            return self.namegen.generate_name(filename_or_wfs.filename)
        return self.namegen.generate_name(filename_or_wfs)

    def path(self, filename):
        if not hasattr(self.storage, 'path'):
            raise RuntimeError("Direct file access is not supported by " + self.storage.__class__.__name__)
        return self.storage.path(filename)

    def archive_files(self, out_filename, files, *args, **kwargs):
        return self.storage.archive_files(out_filename, files, *args, **kwargs)

    def exists(self, filename):
        return self.storage.exists(filename)

    def is_allowed(self, filename):
        return self.is_file_allowed(filename)

    def read(self, filename):
        if not self.exists(filename):
            raise FileNotFoundError(filename)
        return self.storage.read(filename)

    def open(self, filename, mode='r', **kwargs):
        if 'r' in mode and not self.storage.exists(filename):
            raise FileNotFoundError(filename)
        return self.storage.open(filename, mode, **kwargs)

    def write(self, filename, content, overwrite=False):
        if not overwrite and self.exists(filename):
            raise FileExistsError(filename)
        return self.storage.write(filename, content)

    def delete(self, filename):
        return self.storage.delete(filename)

    def save(self, file_or_wfs, filename=None, **kwargs):
        if not filename and isinstance(file_or_wfs, FileStorage):
            filename = lower_extension(secure_filename(file_or_wfs.filename))
        if not filename:
            raise ValueError('filename is required')

        if not self.is_allowed(filename):
            raise ValueError('File type is not allowed.')

        self.storage.save(file_or_wfs, filename, **kwargs)
        return filename

    def list_files(self):
        return self.storage.list_file()

    def metadata(self, filename):
        metadata = self.storage.metadata(filename)
        metadata['filename'] = os.path.basename(filename)
        # TODO: Impelement url getter
        #metadata['url'] = self.url

    def serve(self, filename):
        '''Serve a file given its filename'''
        if not self.exists(filename):
            abort(404)
        return self.storage.serve(filename)