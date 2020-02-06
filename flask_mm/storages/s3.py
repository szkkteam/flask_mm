#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import errno
from contextlib import contextmanager
import os
import mimetypes
import io
import zipfile
import codecs

# Pip package imports
import boto3
from botocore.exceptions import ClientError
from flask import send_from_directory

from werkzeug import cached_property
from werkzeug.datastructures import FileStorage

# Internal package imports
from flask_mm.storages import BaseStorage, as_unicode
from .. import files


class S3Storage(BaseStorage):

    def __init__(self, bucket_name, aws_region, aws_access_key, aws_secret_access_key, *args, **kwargs):
        super(S3Storage, self).__init__(*args, **kwargs)

        self.session = boto3.session.Session()
        self.s3config = boto3.session.Config(signature_version='s3v4')
        # Optional parameters
        self.base_path = kwargs.get('root')
        self.policy = kwargs.get('policy')

        self.s3 = self.session.resource('s3',
                                        config=self.s3config,
                                        #endpoint_url='', #TODO: Get url
                                        region_name=aws_region,
                                        aws_access_key_id=aws_access_key,
                                        aws_secret_access_key=aws_secret_access_key)

        # TODO: Get config if can create bucket, create if can
        self.bucket = self.s3.Bucket(bucket_name)
        try:
            self.bucket.create()
        except (self.s3.meta.client.exceptions.BucketAlreadyOwnedByYou, ClientError):
            pass

        self.separator = '/'
        self.base_path = kwargs.get('root')

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
        try:
            self.bucket.Object(filename).load()
        except ClientError:
            return False
        return True

    @contextmanager
    def open(self, filename, mode='r', encoding='utf8'):
        obj = self.bucket.Object(filename)
        if 'r' in mode:
            f = obj.get()['Body']
            yield f if 'b' in mode else codecs.getreader(encoding)(f)
        else:  # mode == 'w'
            f = io.BytesIO() if 'b' in mode else io.StringIO()
            yield f
            obj.put(Body=f.getvalue())

    def read(self, filename):
        obj = self.bucket.Object(filename).get()
        return obj['Body'].read()

    def write(self, filename, content):
        return self.bucket.put_object(Key=filename, Body=self.as_binary(content))

    def delete(self, filename):
        for obj in self.bucket.objects.filter(Prefix=filename):
            obj.delete()

    def save(self, file_or_wfs, filename, **kwargs):
        if isinstance(file_or_wfs, FileStorage):
            self.bucket.put_object(
                Body=file_or_wfs,
                Key=filename if filename else file_or_wfs.filename,
                # ContentType=?? TODO: How to get the content type?
            )
        else:
            if isinstance(file_or_wfs, io.BytesIO):
                file_or_wfs.seek(0)
                self.bucket.put_object(
                    Body=file_or_wfs,
                    Key=filename,
                    # ContentType=?? TODO: How to get the content type?
                )
            else:
                with open(filename, 'wb') as out:
                    self.bucket.put_object(
                        Body=self.as_binary(out),
                        Key=filename,
                        # ContentType=?? TODO: How to get the content type?
                    )
        return filename

    def archive_files(self, out_filename, filenames, *args, **kwargs):
        if not isinstance(filenames, (tuple, list)):
            filenames = [filenames]

        zf = zipfile.ZipFile(io.BytesIO(), 'w', zipfile.ZIP_DEFLATED)
        try:
            for filename in filenames:
                print("Filename: ", filename)
                d = self.read(filename)
                print("Data: ", d)
                zf.writestr(filename, d)
            self.write(out_filename, zf)
        except Exception as e:
            print("Error occured: ", e)
        finally:
            zf.close()

        return out_filename

    def copy(self, filename, target):
        src = {
            'Bucket': self.bucket.name,
            'Key': filename,
        }
        self.bucket.copy(src, target)

    def move(self, filename, target):
        # TODO: Implement move. Does it make sense? This storage handle only 1 bucket
        raise NotImplementedError('Move operation is not implemented')

    def list_files(self):
        for f in self.bucket.objects.all():
            yield f.key

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
        '''Fetch all availabe metadata'''
        obj = self.bucket.Object(filename)
        checksum = 'md5:{0}'.format(obj.e_tag[1:-1])
        mime = obj.content_type.split(';', 1)[0] if obj.content_type else None
        return {
            'checksum': checksum,
            'size': obj.content_length,
            'mime': mime,
            'modified': obj.last_modified,
        }