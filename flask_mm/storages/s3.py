#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import errno
import hashlib
import os
import io
import shutil
from datetime import datetime

# Pip package imports
try:
    from boto import s3
    from boto.s3.prefix import Prefix
    from boto.s3.key import Key
except ImportError:
    s3 = None

from flask import send_from_directory

from werkzeug import cached_property
from werkzeug.datastructures import FileStorage

# Internal package imports
from flask_mm.storages import BaseStorage, as_unicode
from .. import files


class S3Storage(BaseStorage):

    def __init__(self, bucket_name, region, aws_access_key_id, aws_secret_access_key, *args, **kwargs):
        super(S3Storage, self).__init__(*args, **kwargs)

        # Optional parameters
        if not s3:
            raise ValueError('Could not import boto. You can install boto by '
                             'using pip install boto')

        connection = s3.connect_to_region(
            region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self._bucket = connection.get_bucket(bucket_name)
        self.separator = '/'

    @cached_property
    def bucket(self):
        return self._bucket

    @cached_property
    def root(self):
        return ''

    def _get_bucket_list_prefix(self, path):
        parts = path.split(self.separator)
        if len(parts) == 1:
            search = ''
        else:
            search = self.separator.join(parts[:-1]) + self.separator
        return search

    def _get_path_keys(self, path):
        search = self._get_bucket_list_prefix(path)
        return {key.name for key in self.bucket.list(search, self.separator)}

    def exists(self, filename):
        if filename == '':
            return True
        keys = self._get_path_keys(filename)
        return filename in keys or (filename + self.separator) in keys

    def ensure_path(self, filename):
        key = Key(self.bucket, filename)
        key.set_contents_from_string('')

    def open(self, filename, mode='r', encoding='utf8'):
        pass

    def read(self, filename):
        pass

    def write(self, filename, content):
        pass

    def delete(self, filename):
        pass

    def save(self, file_or_wfs, filename, **kwargs):
        headers = kwargs.get('header')
        self.ensure_path(filename)
        dest = self.path(filename)
        key = Key(self.bucket, dest)
        if isinstance(file_or_wfs, FileStorage):
            key.set_contents_from_stream(
                file_or_wfs.stream, headers=headers)
        else:
            with open(dest, 'wb') as out:
                try:
                    key.set_contents_from_file(out)
                except AttributeError:
                    file_or_wfs.save(out, **kwargs)
        return filename

    def copy(self, filename, target):
        pass

    def move(self, filename, target):
        pass

    def list_files(self):
        for dirpath, dirnames, filenames in os.walk(self.root):
            prefix = os.path.relpath(dirpath, self.root)
            for f in filenames:
                yield os.path.join(prefix, f) if prefix != '.' else f

    def path(self, filename):
        '''Return the full path for a given filename in the storage'''
        pass

    def serve(self, filename):
        '''Serve files for storages with direct file access'''
        return send_from_directory(self.root, filename)

    def get_metadata(self, filename):
        '''Fetch all available metadata'''
        pass