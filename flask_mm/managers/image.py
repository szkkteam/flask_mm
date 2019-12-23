#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import io
import os

# Pip package imports
from werkzeug.datastructures import FileStorage
from werkzeug import secure_filename

from PIL import Image, ImageOps

# Internal package imports
from . import BaseManager
from flask_mm.files import IMAGES, DEFAULTS
from flask_mm.files import lower_extension, extension

class ImageManager(BaseManager):

    def __init__(self, name, storage, *args, **kwargs):
        super(ImageManager, self).__init__(name, storage, *args, **kwargs)

        self.max_size = kwargs.get('max_size', None)
        self.thumbnail_size = kwargs.get('thumbnail_size', (200,200, True))
        allowed_extensions = kwargs.get('extensions', IMAGES)
        self.keep_image_formats = kwargs.get('keep_image_formats', ['PNG, JPG, JPEG'])
        self.image_quality = kwargs.get('image_quality', 95)

        if allowed_extensions == DEFAULTS:
            allowed_extensions = IMAGES
        self.allowed_extensions = allowed_extensions

    def url_thumbnail(self, filename):
        if isinstance(filename, FileStorage):
            return filename.filename
        return self.prefix + self.namegen.thumbgen_filename(filename)


    def delete(self, filename):
        super(ImageManager, self).delete(filename)
        self.delete_thumbnal(filename)

    def delete_thumbnal(self, filename):
        self.storage.delete(self.namegen.thumbgen_filename(filename))

    def save(self, file_or_wfs, filename=None, **kwargs):
        size = kwargs.pop('size', None)
        thumbnail_size = kwargs.pop('thumbnail_size', self.thumbnail_size)
        create_thumbnail = kwargs.pop('create_thumbnail', True)
        quality = kwargs.pop('image_quality', self.image_quality)
        generate_name = kwargs.pop('generate_name', True)
        print("KWARGS: ", kwargs)

        # Try to open the uploaded image file with PIL
        if file_or_wfs and isinstance(file_or_wfs, FileStorage):
            try:
                #image = Image.open(io.BytesIO(file_or_wfs.stream.read()))
                image = Image.open(file_or_wfs)
                filename = lower_extension(secure_filename(file_or_wfs.filename)) if not filename else filename
            except Exception as e:
                raise ValueError("Invalid image: %s" % e)
        else:
            try:
                image = Image.open(io.BytesIO(file_or_wfs))
            except TypeError:
                image = file_or_wfs

        # Filename will be extracted from FileStorage, otherwise it has to be provided.
        if not filename:
            raise ValueError('filename is required')

        # If Image max size is defined, resize the image if neccessery
        if image and size:
            image = self.resize(image, size)

        # Calcualte the save format for the image
        format_filename, format = self._get_save_format(filename, image)

        # If generate filename is requested, use the given name generator
        if generate_name:
            filename = self.generate_name(format_filename)

        # Save the image with the specified options
        filename = super(ImageManager, self).save(self._convert(image), filename, format=format, quality=quality, **kwargs)

        # If create thumbnail is requested, generate a thumbnail and save it
        if create_thumbnail and thumbnail_size:
            # Resize the thumbnail
            image = self.resize(image, thumbnail_size)
            # Save the thumbnail image
            super(ImageManager, self).save(self._convert(image), self.generate_thumbnail_name(filename), format=format, quality=quality, **kwargs)

        return filename

    def generate_thumbnail_name(self, filename_or_wfs):
        if isinstance(filename_or_wfs, FileStorage):
            return self.namegen.thumbgen_filename(filename_or_wfs.filename)
        return self.namegen.thumbgen_filename(filename_or_wfs)

    def _get_save_format(self, filename, image):
        if image.format not in self.keep_image_formats:
            name, ext = os.path.splitext(filename)
            filename = "%s.jpg" % name
            return filename, "JPEG"
        return filename, image.format

    def _convert(self, image):
        if image.mode not in ("RGB", "RGBA"):
            return image.convert("RGBA")
        return image

    def resize(self, image, size):
        """
            Resizes the image
            :param image: The image object
            :param size: size is PIL tuple (width, heigth, force) ex: (200,100,True)
        """
        (width, height, force) = size

        if image.size[0] > width or image.size[1] > height:
            if force:
                #return ImageOps.fit(image, (width, height), Image.ANTIALIAS)
                return image.resize((width, height), Image.ANTIALIAS)
            else:
                thumb = image.copy()
                thumb.thumbnail((width, height), Image.ANTIALIAS)
                return thumb

        return image



