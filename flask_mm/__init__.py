#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
from os.path import join
import pkg_resources

# Pip package imports
from flask import current_app, Blueprint



# Internal package imports
from .__about__ import __version__, __description__  # noqa: Facade pattern

# :Import Storages
from .storages import (
    DEFAULT_STORAGE
)
# :Import Managers
from .managers import (
    DEFAULT_MANAGER
)
# :Import default file extensions
from .files import (
    DEFAULTS
)

CONF_PREFIX = 'MM_'
PREFIX = '{0}_MM_'
MANAGER_PREFIX = 'MM_{0}_'
STORAGE_PREFIX = 'MM_{0}_'

MANAGERS = dict((ep.name, ep) for ep in pkg_resources.iter_entry_points('mm.managers'))
STORAGES = dict((ep.name, ep) for ep in pkg_resources.iter_entry_points('mm.storages'))

def _config_from_dict(app, name, config):
    # Override global configuration
    manager = config.pop('MANAGER')
    storage = config.pop('STORAGE')

    manager_class = MANAGERS[manager].load()
    storage_class = STORAGES[storage].load()

    config = {k.lower(): v for k, v in config.items()}

    return manager_class(app, name, storage=storage_class(**config), **config)

def by_name(name=''):
    if len(name) == 0 and len(current_app.extensions[MediaManager.key].keys()) == 1:
        name = list(current_app.extensions[MediaManager.key].keys())[0]
    try:
        return current_app.extensions[MediaManager.key][name.lower()]
    except KeyError:
        msg = "Input argument: %s must one of %s" % (name, current_app.extensions[MediaManager.key].keys())
        raise KeyError(msg)

class MediaManager(object):

    allowed_configs = [
        # Common configuration values
        'URL',
        'ROOT',
        'MANAGER',
        'STORAGE',
        'EXTENSIONS',
        'PUBLIC_VIEW'
        # Image Manager related configuration values
        'MAX_SIZE',
        'THUMBNAIL_SIZE',
        'KEEP_IMAGE_FORMATS',
        'IMAGE_QUALITY',
        'CROP_TYPE'
        'PREPROCESS',
        'POSTPROCESS',
        # Local Storage related configuration values
        'PERMISSION',
        # Amazon S3 Storage related configuration values
        'AWS_ACCESS_KEY',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_REGION',
        'BUCKET_NAME',
        'OBJECT_ACL'
    ]

    key = 'mediamanager'
    name = 'media'

    default_storage = 'local'
    default_manager = 'file'
    default_prefix = '/media'
    default_url = None

    def __init__(self, app=None, *args, **kwargs):
        self.app = app
        if app is not None:
            self.init_app(app, *args, **kwargs)

    def init_app(self, app, *args, **kwargs):
        self.instances = self.configure(app)
        app.extensions = getattr(app, 'extensions', {})
        app.extensions[self.key] = self.instances


    def by_name(self, name=''):
        try:
            if len(name) == 0 and len(current_app.extensions[MediaManager.key].keys()) == 1:
                name = list(current_app.extensions[MediaManager.key].keys())[0]
            return current_app.extensions[self.key][name.lower()]
        except RuntimeError:
            if len(name) == 0 and len(self.instances.keys()) == 1:
                name = list(self.instances.keys())[0]
            return self.instances[name.lower()]
        except KeyError:
            msg = "Input argument: \'%s\' must one of %s" % (name, self.instances.keys())
            raise KeyError(msg)

    def configure(self, app):

        def get_name_config(pattern):
            for element in self.allowed_configs:
                if pattern.endswith(element):
                    l = pattern.replace('_' + element, '')
                    if l.startswith(CONF_PREFIX):
                        name = l.replace(CONF_PREFIX, '')
                    else:
                        name = None
                    return name, element
            return '', ''


        mm = app.config.get('MEDIA_MANAGER', None)
        mm_instances = {}
        # Media Manager configuration is not exists, try to parse app.config to search for named configuration elements
        global_config = {
            'URL' : self.default_url,
            'ROOT': join(app.instance_path, 'media'),
            'PREFIX': self.default_prefix,
            'EXTENSIONS': DEFAULTS,
            'MANAGER': MediaManager.default_manager,
            'STORAGE': MediaManager.default_storage,
            'PUBLIC_VIEW': True
        }
        if mm is None:
            mm = {}
            # Search for individual dict config for different managers
            for key, value in app.config.items():
                if key.startswith(CONF_PREFIX):
                    if key.endswith(tuple(self.allowed_configs)):
                        name, conf_element = get_name_config(key)
                        if name is not None:
                            """ Example:
                                MM_PHOTO_MEDIA_URL = # configuration
                            """
                            if name in mm:
                                mm[name][conf_element] = value
                            else:
                                mm[name] = {}
                        else:
                            """ Example:
                                MM_URL = # configuration
                            """
                            _, conf_element = get_name_config(key)
                            global_config[conf_element] = value

        for key, value in app.config.items():
            if key.startswith(CONF_PREFIX):
                if isinstance(value, dict):
                    """ Example:
                        MM_PHOTO_MEDIA = {
                            # configuration
                        }
                    """
                    name = key.replace(CONF_PREFIX, '').lower()
                    mm_instances[name] = _config_from_dict(app, name, { **global_config, **value } )

        # Media manager configuration(s) can be encapsulated in a dictionary
        if isinstance(mm, dict):
            # If Media Manager instance(s) defined as key = name, value = config_dict
            for conf, value in mm.items():
                """ Example:
                    MEDIA_MANAGER = {
                        # configuration
                    }
                """
                if not isinstance(value, dict):
                    global_config[conf] = value

            for name, config in mm.items():
                """ Example:
                    MEDIA_MANAGER = {
                        'PHOTO': {
                            # Local configuration
                        },
                        'FILES':{
                            # Local configuration
                        },
                        'URL': # Global configuration
                    }
                """
                if not isinstance(config, dict):
                    continue
                name = name.lower()
                mm_instances[name] = _config_from_dict(app, name, { **global_config, **config } )

        if len(mm_instances.keys()) == 0:
            mm_instances[self.name] = _config_from_dict(app, self.name, global_config)

        from .views import mm_bp
        app.register_blueprint(mm_bp, url_prefix=global_config.get('PREFIX'))

        return mm_instances









