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
from flask import send_from_directory, abort

from werkzeug import cached_property
from werkzeug.datastructures import FileStorage

# Internal package imports
from flask_mm.storages import BaseStorage, as_unicode
from .. import files


CHUNK_SIZE = 2 ** 16

def sha1(file):
    hasher = hashlib.sha1()
    blk_size_to_read = hasher.block_size * CHUNK_SIZE
    while (True):
        read_data = file.read(blk_size_to_read)
        if not read_data:
            break
        hasher.update(read_data)
    return hasher.hexdigest()

class LocalStorage(BaseStorage):

    def __init__(self, root, *args, **kwargs):
        super(LocalStorage, self).__init__(*args, **kwargs)
        self.base_path = root

        # Optional parameters
        self.permission = kwargs.get('permission', 0o666)

        if not self.exists(self.base_path):
            self.ensure_path(self.base_path)
            #raise IOError('LocalStorage path "%s" does not exist or is not accessible' % self.base_path)

    @cached_property
    def root(self):
        return os.path.normpath(self.base_path)

    def exists(self, filename):
        dest = self.path(filename)
        return os.path.exists(dest)

    def ensure_path(self, filename):
        dirname = os.path.dirname(self.path(filename))
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname, self.permission | 0o111)
            except OSError as e:
                # Don't raise on race condition,
                # directory has been created elsewhere
                if e.errno != errno.EEXIST:
                    raise

    def open(self, filename, mode='r', encoding='utf8'):
        dest = self.path(filename)
        if 'w' in mode:
            self.ensure_path(filename)
        if 'b' in mode:
            return open(dest, mode)
        else:
            return io.open(dest, mode, encoding=encoding)

    def read(self, filename):
        with self.open(filename, 'rb') as f:
            return f.read()

    def write(self, filename, content):
        self.ensure_path(filename)
        with self.open(filename, 'wb') as f:
            return f.write(self.as_binary(content))

    def delete(self, filename):
        dest = self.path(filename)
        if os.path.isdir(dest):
            shutil.rmtree(dest, ignore_errors=True)
        else:
            os.remove(dest)

    def save(self, file_or_wfs, filename, **kwargs):
        self.ensure_path(filename)
        dest = self.path(filename)
        if isinstance(file_or_wfs, FileStorage):
            file_or_wfs.save(dest, **kwargs)
        else:
            with open(dest, 'wb') as out:
                try:
                    shutil.copyfileobj(file_or_wfs, out)
                except AttributeError:
                    file_or_wfs.save(out, **kwargs)
        return filename

    def copy(self, filename, target):
        src = self.path(filename)
        dest = self.path(target)
        self.ensure_path(target)
        shutil.copy2(src, dest)

    def move(self, filename, target):
        src = self.path(filename)
        dest = self.path(target)
        self.ensure_path(target)
        shutil.move(src, dest)

    def list_files(self):
        for dirpath, dirnames, filenames in os.walk(self.root):
            prefix = os.path.relpath(dirpath, self.root)
            for f in filenames:
                yield os.path.join(prefix, f) if prefix != '.' else f

    def path(self, filename):
        '''Return the full path for a given filename in the storage'''
        if callable(self.base_path):
            return os.path.join(self.base_path(), filename)
        return os.path.join(self.base_path, filename)

    def serve(self, filename):
        if not self.public_view:
            abort(400)
        '''Serve files for storages with direct file access'''
        return send_from_directory(self.root, filename)

    def get_metadata(self, filename):
        '''Fetch all available metadata'''
        dest = self.path(filename)
        with open(dest, 'rb', buffering=0) as f:
            checksum = 'sha1:{0}'.format(sha1(f))
        return {
            'checksum': checksum,
            'size': os.path.getsize(dest),
            'mime': files.mime(filename),
            'modified': datetime.fromtimestamp(os.path.getmtime(dest)),
        }