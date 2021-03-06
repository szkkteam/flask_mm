#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
from __future__ import unicode_literals

import six
import zipfile
import zlib
# Pip package imports

# Internal package imports
from flask_mm import files

DEFAULT_STORAGE = 'local'

class BaseStorage(object):

    root = None
    DEFAULT_MIME = 'application/octet-stream'

    def __init__(self, *args, **kwargs):
        self.public_view = kwargs.get('public_view', True)

    @property
    def has_url(self):
        return False

    @property
    def base_url(self):
        return None

    def exists(self, filename):
        raise NotImplementedError('Existance checking is not implemented')

    def open(self, filename, *args, **kwargs):
        raise NotImplementedError('Open operation is not implemented')

    def read(self, filename):
        raise NotImplementedError('Read operation is not implemented')

    def write(self, filename, content):
        raise NotImplementedError('Write operation is not implemented')

    def delete(self, filename):
        raise NotImplementedError('Delete operation is not implemented')

    def copy(self, filename, target):
        raise NotImplementedError('Copy operation is not implemented')

    def move(self, filename, target):
        self.copy(filename, target)
        self.delete(filename)

    def save(self, file_or_wfs, filename, **kwargs):
        self.write(filename, file_or_wfs.read())
        return filename

    def metadata(self, filename):
        meta = self.get_metadata(filename)
        # Fix backend mime misdetection
        meta['mime'] = meta.get('mime') or files.mime(filename, self.DEFAULT_MIME)
        return meta

    def archive_files(self, out_filename, filenames, *args, **kwargs):
        if not isinstance(filenames, (tuple, list)):
            filenames = [filenames]
        with zipfile.ZipFile(self.path(out_filename), 'w', zipfile.ZIP_DEFLATED) as zipper:
            for filename in filenames:
                zipper.write(self.path(filename), filename)

        return out_filename

    def get_metadata(self, filename):
        raise NotImplementedError('Copy operation is not implemented')

    def serve(self, filename):
        raise NotImplementedError('serve operation is not implemented')

    def path(self, filename):
        raise NotImplementedError('path operation is not implemented')

    def as_binary(self, content, encoding='utf8'):
        if hasattr(content, 'read'):
            return content.read()
        elif isinstance(content, six.text_type):
            return content.encode(encoding)
        else:
            return content

    def list_file(self):
        raise NotImplementedError('list_files operation is not implemented')

def as_unicode(s):
    if isinstance(s, bytes):
        return s.decode('utf-8')

    return str(s)