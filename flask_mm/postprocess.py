#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import six

# Pip package imports
from PIL import Image, ImageEnhance

# Internal package imports

class Postprocess(object):

    def process(self, target, **kwargs):
        pass

class Watermarker(Postprocess):

    DEFAULT_POSITION = None
    DEFAULT_OPACITY = 0.5
    DEFAULT_TILE = False
    DEFAULT_SCALE = 1.0
    DEFAULT_GREYSCALE = False
    DEFAULT_ROTATION = 0
    DEFAULT_QUALITY = 0.85

    def __init__(self,
                 watermark_image,
                 position=Watermarker.DEFAULT_POSITION,
                 opacity=Watermarker.DEFAULT_OPACITY,
                 tile=Watermarker.DEFAULT_TILE,
                 scale=Watermarker.DEFAULT_SCALE,
                 greyscale=Watermarker.DEFAULT_GREYSCALE,
                 rotation=Watermarker.DEFAULT_ROTATION,
                 quality=Watermarker.DEFAULT_QUALITY):

        self.watermark_image = watermark_image
        self.position = position
        self.opacity = opacity
        self.tile = tile
        self.scale = scale
        self.greyscale = greyscale
        self.rotation = rotation
        self.quality = quality

    def process(self, target, **kwargs):
        if not isinstance(target, Image):
            target = Image.open(target)
        if not isinstance(self.watermark_image, Image):
            self.watermark_image = Image.open(self.watermark_image)

        # determine the actual value that the parameters provided will render
        scale = determine_scale(self.scale, target, self.watermark_image)
        watermark_image = self.watermark_image.resize(scale, resample=Image.ANTIALIAS)
        rotation = determine_rotation(self.rotation, watermark_image)
        position = determine_position(self.position, target, watermark_image)
        opacity = self.opacity
        greyscale = self.greyscale

        if opacity < 1:
            watermark_image = reduce_opacity(watermark_image, opacity)

        watermark_image = watermark_image.resize(scale, resample=Image.ANTIALIAS)

        if greyscale and watermark_image.mode != 'LA':
            watermark_image = watermark_image.convert('LA')

        if rotation != 0:
            # give some leeway for rotation overlapping
            new_w = int(watermark_image.size[0] * 1.5)
            new_h = int(watermark_image.size[1] * 1.5)

            new_mark = Image.new('RGBA', (new_w, new_h), (0,0,0,0))

            # center the watermark in the newly resized image
            new_l = int((new_w - mark.size[0]) / 2)
            new_t = int((new_h - mark.size[1]) / 2)
            new_mark.paste(watermark_image, (new_l, new_t))

            watermark_image = new_mark.rotate(rotation)

        if target.mode != 'RGBA':
            target = target.convert('RGBA')

        layer = Image.new('RGBA', target.size, (0, 0, 0, 0))
        if tile:
            first_y = int(position[1] % watermark_image.size[1] - watermark_image.size[1])
            first_x = int(position[0] % watermark_image.size[0] - watermark_image.size[0])

            for y in range(first_y, target.size[1], watermark_image.size[1]):
                for x in range(first_x, target.size[0], watermark_image.size[0]):
                    layer.paste(watermark_image, (x, y))
        else:
            layer.paste(watermark_image, position)

        # composite the watermark with the layer
        return Image.composite(layer, target, layer)

def reduce_opacity(img, opacity):
    """
    Returns an image with reduced opacity.
    """
    assert opacity >= 0 and opacity <= 1

    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    else:
        img = img.copy()

    alpha = img.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    img.putalpha(alpha)

    return img

def determine_scale(scale, img, mark):
    """
    Scales an image using a specified ratio, 'F' or 'R'. If `scale` is
    'F', the image is scaled to be as big as possible to fit in `img`
    without falling off the edges.  If `scale` is 'R', the watermark
    resizes to a percentage of minimum size of source image.  Returns
    the scaled `mark`.
    """
    if scale:
        try:
            scale = float(scale)
        except (ValueError, TypeError):
            pass

        if isinstance(scale, six.string_types) and scale.upper() == 'F':
            # scale watermark to full, but preserve the aspect ratio
            scale = min(
                float(img.size[0]) / mark.size[0],
                float(img.size[1]) / mark.size[1]
            )
        elif isinstance(scale, six.string_types) and scale.upper() == 'R':
            # scale watermark to % of source image and preserve the aspect ratio
            scale = min(
                float(img.size[0]) / mark.size[0],
                float(img.size[1]) / mark.size[1]
            ) / 100 * settings.WATERMARK_PERCENTAGE
        elif type(scale) not in (float, int):
            raise ValueError('Invalid scale value "%s"! Valid values are "F" '
                             'for ratio-preserving scaling, "R%%" for percantage aspect '
                             'ratio of source image and floating-point numbers and '
                             'integers greater than 0.' % scale)

        # determine the new width and height
        w = int(mark.size[0] * float(scale))
        h = int(mark.size[1] * float(scale))

        # apply the new width and height, and return the new `mark`
        return (w, h)
    else:
        return mark.size

def determine_rotation(rotation, mark):
    """
    Determines the number of degrees to rotate the watermark image.
    """
    if isinstance(rotation, six.string_types) and rotation.lower() == 'r':
        rotation = random.randint(0, 359)
    else:
        rotation = _int(rotation)

    return rotation

def determine_position(position, img, mark):
    """
    Options:
        TL: top-left
        TR: top-right
        BR: bottom-right
        BL: bottom-left
        C: centered
        R: random
        X%xY%: relative positioning on both the X and Y axes
        X%xY: relative positioning on the X axis and absolute positioning on the
              Y axis
        XxY%: absolute positioning on the X axis and relative positioning on the
              Y axis
        XxY: absolute positioning on both the X and Y axes
    """
    left = top = 0

    max_left = max(img.size[0] - mark.size[0], 0)
    max_top = max(img.size[1] - mark.size[1], 0)

    #Added a 10px margin from corners to apply watermark.
    margin = 10

    if not position:
        position = 'r'

    if isinstance(position, tuple):
        left, top = position
    elif isinstance(position, six.string_types):
        position = position.lower()

        # corner positioning
        if position in ['tl', 'tr', 'br', 'bl']:
            if 't' in position:
                top = margin
            elif 'b' in position:
                top = max_top - margin
            if 'l' in position:
                left = margin
            elif 'r' in position:
                left = max_left - margin

        # center positioning
        elif position == 'c':
            left = int(max_left / 2)
            top = int(max_top / 2)

        # relative or absolute positioning
        elif 'x' in position:
            left, top = position.split('x')

            if '%' in left:
                left = max_left * _percent(left)
            else:
                left = _int(left)

            if '%' in top:
                top = max_top * _percent(top)
            else:
                top = _int(top)

    return int(left), int(top)
