#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import errno
from contextlib import contextmanager
import os
import mimetypes
import io
import zipfile
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

    def __init__(self, bucket_name, aws_region, aws_access_key, aws_secret_access_key, *args, **kwargs):
        super(S3Storage, self).__init__(*args, **kwargs)

        # Optional parameters
        self.base_path = kwargs.get('root')
        self.policy = kwargs.get('policy')

        if not s3:
            raise ValueError('Could not import boto. You can install boto by '
                             'using pip install boto')

        connection = s3.connect_to_region(
            aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_access_key,
        )
        # TODO: Get config if can create bucket, create if can
        self._bucket = connection.get_bucket(bucket_name)
        self.separator = '/'
        self.base_path = kwargs.get('root')

    @cached_property
    def bucket(self):
        return self._bucket

    @cached_property
    def root(self):
        return ''

    def _generate_key(self, filename, headers=None):
        if self.base_path:
            filename = '%s/%s' % (self.base_path, filename)

        k = self.bucket.new_key(filename)
        if not headers or 'Content-Type' not in headers:
            ct = mimetypes.guess_type(filename)[0]
            if ct:
                k.set_metadata('Content-Type', ct)

        return k

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
        # TOOD: Maybe remove this function?
        key = Key(self.bucket, filename)
        key.set_contents_from_string('')

    @contextmanager
    def open(self, filename, mode='r', encoding='utf8'):
        full_filename = self.path(filename)
        if mode == 'w':
            # TODO: Overwrite file
            pass
        if mode == 'b':
            # TODO: What to do here?
            pass
        else:
            k = self.bucket.get_key(full_filename)
            if not k:
                raise FileNotFoundError('File does not exist: {0}'.format(filename))
            return io.BytesIO(k.read())

    def read(self, filename):
        filename = self.path(filename)
        k = self.bucket.get_key(filename)
        if not k:
            return None
        return k.read()

    def write(self, filename, content):
        key = self._generate_key(self.path(filename))
        return key.set_contents_from_string(content, policy=self.policy)
        pass

    def delete(self, filename):
        filename = self.path(filename)
        self.bucket.delete_key(filename)

    def save(self, file_or_wfs, filename, **kwargs):
        headers = kwargs.get('header')
        dest = self.path(filename)
        key = self._generate_key(dest)
        if isinstance(file_or_wfs, FileStorage):
            key.set_contents_from_stream(
                file_or_wfs.stream, headers=headers, policy=self.policy)
        else:
            with open(dest, 'wb') as out:
                key.set_contents_from_file(out)
        return filename

    def archive_files(self, out_filename, filenames, *args, **kwargs):
        if not isinstance(filenames, (tuple, list)):
            filenames = [filenames]

        zf = zipfile.ZipFile(io.BytesIO(), 'w', zipfile.ZIP_DEFLATED)
        try:
            for filename in filenames:
                zf.write(self.read(filename))
            self.write(out_filename, zf.read())
        except Exception as e:
            print(e)
        finally:
            zf.close()

        return out_filename

    def copy(self, filename, target):
        # TODO: Implement copy
        raise NotImplementedError('Copy operation is not implemented')

    def move(self, filename, target):
        # TODO: Implement move. Does it make sense? This storage handle only 1 bucket
        raise NotImplementedError('Move operation is not implemented')

    def list_files(self):
        for file in self.bucket.objects.all():
            yield file

    def path(self, filename):
        '''Return the full path for a given filename in the storage'''
        if self.base_path:
            return self.base_path + self.separator + filename
        return filename

    def serve(self, filename):
        '''Serve files for storages with direct file access'''
        key = self.bucket.get_key(self.path(filename))
        if key is None:
            raise ValueError()
        return key.generate_url(3600)

    def get_metadata(self, filename):
        '''Fetch all available metadata'''
        pass