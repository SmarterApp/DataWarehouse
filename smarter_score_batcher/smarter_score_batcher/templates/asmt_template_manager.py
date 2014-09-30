'''
Created on Sep 19, 2014

@author: agrebneva
'''
from smarter_score_batcher.celery import conf
import os
import json
from zope import interface, component
from zope.interface.declarations import implementer
import fnmatch
from beaker.cache import cache_region
from smarter_score_batcher.utils.merge import deep_merge
from smarter_score_batcher.error.exceptions import MetadataException
from smarter_score_batcher.error.error_codes import ErrorSource
import logging


logger = logging.getLogger("smarter_score_batcher")


class MetadataTemplate:
    '''
    A single template for an asmt
    '''
    def __init__(self, asmt_data_json):
        self.asmt_data_json = asmt_data_json

    def get_asmt_metadata_template(self):
        return self.asmt_data_json

    def get_asmt_subject(self):
        return self.asmt_data_json['Identification']['Subject']


class IMetadataTemplateManager(interface.Interface):
    def get_template(self, key):
        pass


def get_template_key(year, asmt_type, grade, subject):
    return '_'.join([str(year), asmt_type, str(grade), subject])


class MetadataTemplateManager:
    '''
    Loads and manages asmt templates by asmt SUBJECT
    '''
    def __init__(self, asmt_meta_dir=None):
        self.templates = {}
        self.asmt_meta_location = self._get_template_location(asmt_meta_dir)

    def _load_templates(self, path, pattern='.static_asmt_metadata.json'):
        '''
        Load templates for a specific path matching the pattern
        :param path - root for the templates
        :param pattern - pattern to match template names
        '''
        templates = []
        for root, _, filenames in os.walk(path):
            for file in fnmatch.filter(filenames, pattern):
                full_path = os.path.join(root, file)
                with open(full_path, 'r+') as f:
                    template = MetadataTemplate(json.load(f))
                    templates.append(template)
        return templates

    def get_key(self, path, metadata_template):
        '''
        Get cache key for path and template
        :return cache key
        '''
        return metadata_template.get_asmt_subject().lower()

    def _get_template_location(self, asmt_meta_location=None):
        '''
        Figure out location of the templates. If not provided, use default
        :param asmt_meta_location: optional specified root location of the templates
        '''
        if asmt_meta_location is not None and os.path.isabs(asmt_meta_location):
            return asmt_meta_location
        here = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(here, self._get_configured_path() if asmt_meta_location is None else asmt_meta_location)

    def _get_configured_path(self):
        return conf.get('smarter_score_batcher.metadata.static', '../../resources/meta/static')

    def _load_template(self, key, path=None):
        '''
        load individual static template
        :param key: key of the template to load
        :param path: optional relative path where to look for the template
        :return template for the key
        '''
        location = self.asmt_meta_location if path is None else os.path.join(self.asmt_meta_location, path.lower())
        templates = [template for template in self._load_templates(location, pattern='*.json') if template.get_asmt_subject().lower() == key.lower()]
        if len(templates) == 0:
            raise MetadataException('Unable to load metadata for key {0} from location {1}'.format(key, location))
        if len(templates) > 1:
            raise MetadataException('Too many templates for key {0} from location {1}'.format(key, location))
        return templates.pop()

    @cache_region('public.shortlived', 'metadata.templates')
    def get_template(self, key):
        '''
        lazy load template
        :param key: key to load template for
        :return template for the key
        '''
        logger.info('Loading template for key {0}'.format(key))
        sm = self._load_template(key)
        if sm is None:
            raise MetadataException("Unable to load metadata for key {0} from ".format(key), err_source=ErrorSource.METADATATEMPLATEMANAGER_GET_TEMPLATE)
        return sm.get_asmt_metadata_template().copy()


@implementer(IMetadataTemplateManager)
class PerfMetadataTemplateManager(MetadataTemplateManager):
    '''
    Loads and manages performance templates by academic year, asmt type, grade, and subject
    '''
    def __init__(self, asmt_meta_dir=None, static_asmt_meta_dir=None):
        self.templates = {}
        self.asmt_meta_location = self._get_template_location(asmt_meta_dir)
        self.meta_template_mgr = MetadataTemplateManager(asmt_meta_dir=static_asmt_meta_dir)

    def get_key(self, path, metadata_template):
        '''
        create key by provided path of the template file
        :param path: path to the template, which will be included into the key
        :param metadata_template: template to get the key for
        :return cache key
        '''
        key = path[len(self.asmt_meta_location) + 1:].replace(os.path.sep, '_') if path.startswith(self.asmt_meta_location) else path
        key = key + '_' + metadata_template.get_asmt_subject()
        return key.lower()

    def _load_template(self, key):
        '''
        load individual template and merge it with static template
        :param key - key to load template for
        :return combined static and perfomance templates
        '''
        keys = key.split('_')
        subject = keys.pop()
        path = os.path.sep.join(keys)
        custom_template = self._load_custom_template(subject, path)
        standard_template = self.meta_template_mgr.get_template(subject)
        return MetadataTemplate(deep_merge(standard_template, custom_template))

    def _load_custom_template(self, subject, path):
        tmpl = super()._load_template(subject, path=path)
        return tmpl.get_asmt_metadata_template()

    def _get_configured_path(self):
        return conf.get('smarter_score_batcher.metadata.performance', '../../resources/meta/performance')

component.provideUtility(PerfMetadataTemplateManager(), IMetadataTemplateManager)
