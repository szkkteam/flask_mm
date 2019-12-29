#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import abort, Blueprint

# Internal package imports
from . import by_name

mm_bp = Blueprint('mm', __name__)

@mm_bp.route('/<string:mm>/<path:filename>')
def get_file(mm, filename):
    try:
        print("MM: ", mm)
        storage = by_name(mm)
        print(storage)
    except KeyError:
        abort(404)
    else:
        return storage.serve(filename)