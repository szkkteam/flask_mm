#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
from __future__ import unicode_literals

import re
import os.path as op

# Pip package imports
import uuid

# Internal package imports

class UuidNameGen(object):

    uuid_type = uuid.uuid1
    separator = "_sep_"
    thumb_name = "_thumb"
    wm_name ="_wm"

    @classmethod
    def generate_name(cls, filename):
        return str(cls.uuid_type()) + cls.separator + filename

    @classmethod
    def get_original_name(cls, name):
        """
            Use this function to get the user's original filename.
            Filename is concatenated with <UUID>_sep_<FILE NAME>, to avoid collisions.
            Use this function on your models on an aditional function
            ::
                class ProjectFiles(Base):
                    id = Column(Integer, primary_key=True)
                    file = Column(FileColumn, nullable=False)
                    def file_name(self):
                        return get_file_original_name(str(self.file))
            :param name:
                The file name from model
            :return:
                Returns the user's original filename removes <UUID>_sep_
        """
        re_match = re.findall(".*%s(.*)" % cls.separator, name)
        if re_match:
            return re_match[0]
        else:
            return "Not valid"

    @classmethod
    def original_name(cls, uuid_filename):
        return uuid_filename.split(cls.separator)[1]

    @classmethod
    def thumbgen_filename(cls, filename):
        name, ext = op.splitext(filename)
        return name + cls.thumb_name + ext

    @classmethod
    def watermark_filename(cls, filename):
        name, ext = op.splitext(filename)
        return name + cls.wm_name + ext