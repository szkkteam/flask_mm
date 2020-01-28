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
from flask_mm.postprocess import Postprocess

class ImageManager(BaseManager):

    def __init__(self, app, name, storage, *args, **kwargs):
        super(ImageManager, self).__init__(app, name, storage, *args, **kwargs)

        self.max_size = kwargs.get('max_size', None)
        self.thumbnail_size = kwargs.get('thumbnail_size', (200,200, True))
        allowed_extensions = kwargs.get('extensions', IMAGES)
        self.keep_image_formats = kwargs.get('keep_image_formats', ['PNG', 'JPG', 'JPEG'])
        self.image_quality = kwargs.get('image_quality', 90)
        self.crop_type = kwargs.get('crop_type', 'TOP')
        self.preprocess = kwargs.pop('preprocess', None)
        self.postprocess = kwargs.pop('postprocess', None)

        if allowed_extensions == DEFAULTS:
            allowed_extensions = IMAGES
        self.allowed_extensions = allowed_extensions

    def url_thumbnail(self, filename):
        if isinstance(filename, FileStorage):
            return filename.filename
        return self.namegen.thumbgen_filename(filename)


    def delete(self, filename):
        super(ImageManager, self).delete(filename)
        self.delete_thumbnail(filename)

    def get_thumbnail(self, filename):
        return self.namegen.thumbgen_filename(filename)

    def delete_thumbnail(self, filename):
        self.storage.delete(self.namegen.thumbgen_filename(filename))

    def save(self, file_or_wfs, filename=None, **kwargs):
        size = kwargs.pop('size', self.max_size)
        thumbnail_size = kwargs.pop('thumbnail_size', self.thumbnail_size)
        create_thumbnail = kwargs.pop('create_thumbnail', True)
        quality = kwargs.pop('image_quality', self.image_quality)
        generate_name = kwargs.pop('generate_name', True)

        # TODO: Implement preprocess
        preprocess = kwargs.pop('preprocess', self.preprocess)
        postprocess = kwargs.pop('postprocess', self.postprocess)

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
        print("Format: ", format)

        # If generate filename is requested, use the given name generator
        if generate_name:
            filename = self.generate_name(format_filename)

        # TODO: Implement preprocessing of the image

        # If create thumbnail is requested, generate a thumbnail and save it
        if create_thumbnail and thumbnail_size:
            # Resize the thumbnail
            image_thumb = self.resize(image, thumbnail_size)
            # Save the thumbnail image
            super(ImageManager, self).save(self._convert(image_thumb, format), self.generate_thumbnail_name(filename),
                                           format=format, quality=quality, **kwargs)
        # Perform the postprocess if defined
        if postprocess:
            assert isinstance(postprocess,
                              Postprocess), "Postprocess must be a subclass of flask_mm.postrocess.Postprocess"
            image = postprocess.process(image)

        # Save the image with the specified options
        filename = super(ImageManager, self).save(self._convert(image, format), filename, format=format, quality=quality, **kwargs)

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

    def _convert(self, image, format):
        if image.mode not in ("RGB", "RGBA"):
            image =  image.convert("RGBA")

        if image.mode == "RGBA" and format in ['JPG', 'JPEG']:
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])  # 3 is the alpha channel
            return background

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
                return resize_and_crop(image, width, height, self.crop_type.lower())
            else:
                thumb = image.copy()
                thumb.thumbnail((width, height), Image.ANTIALIAS)
                return thumb

        return image

def resize_and_crop(image, width, height, crop_type='middle'):
    # Get current and desired ratio for the images
    img_ratio = image.size[0] / float(image.size[1])
    ratio = width / float(height)
    # The image is scaled/cropped vertically or horizontally depending on the ratio
    if ratio > img_ratio:
        #img = image.copy()
        #img.thumbnail( (width, int(height * image.size[1] / image.size[0])), Image.ANTIALIAS )
        img = image.resize((width, int(height * image.size[1] / image.size[0])), Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, img.size[0], height)
        elif crop_type == 'middle':
            box = (0, (img.size[1] - height) / 2, img.size[0], (img.size[1] + height) / 2)
        elif crop_type == 'bottom':
            box = (0, img.size[1] - height, img.size[0], img.size[1])
        else:
            raise ValueError('ERROR: invalid value for crop_type')
        return img.crop(box)
    elif ratio < img_ratio:
        img = image.resize((int(height * image.size[0] / image.size[1]), height), Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, width, img.size[1])
        elif crop_type == 'middle':
            box = ((img.size[0] - width) / 2, 0, (img.size[0] + width) / 2, img.size[1])
        elif crop_type == 'bottom':
            box = (img.size[0] - width, 0, img.size[0], img.size[1])
        else:
            raise ValueError('ERROR: invalid value for crop_type')
        return img.crop(box)
    else:
        return image.resize((width, height),
                         Image.ANTIALIAS)
