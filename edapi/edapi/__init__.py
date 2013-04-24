'''
Entry point for edapi

'''
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy


EDAPI_REPORTS_PLACEHOLDER = 'edapi_reports'


def add_report_config(self, delegate, **kwargs):
    '''
    directive used to save report_config decorators to Pyramid Configurator's registry

    @param delegate: a delegate to the wrapped function
    '''
    settings = kwargs.copy()
    settings['reference'] = delegate
    if self.registry.get(EDAPI_REPORTS_PLACEHOLDER) is None:
        self.registry[EDAPI_REPORTS_PLACEHOLDER] = {}

    # Only process decorators with a name defined
    if settings.get('name') is not None:
        self.registry[EDAPI_REPORTS_PLACEHOLDER][settings['name']] = settings


class ContentTypePredicate(object):
    '''
    custom predicate for routing by content-type
    '''
    def __init__(self, content_type, config):
        self.content_type = content_type.lower()

    @staticmethod
    def default_content_type():
        return "application/json"

    def text(self):
        return 'content_type = %s' % (self.content_type,)

    phash = text

    def __call__(self, context, request):
        content_type = getattr(request, 'content_type', None)
        if not content_type or len(content_type) == 0:
            content_type = ContentTypePredicate.default_content_type()
        return content_type.lower() == self.content_type


def includeme(config):
    '''
    this is automatically called by consumer of edapi when it calls config.include(edapi)
    '''

    # routing for retrieving list of report names with GET
    config.add_route('list_of_reports', '/data')

    # routing for the GET, POST, OPTIONS verbs
    config.add_route('report_get_option_post', '/data/{name}')

    # directive to handle report_config decorators
    config.add_directive('add_report_config', add_report_config)

    config.add_view_predicate('content_type', ContentTypePredicate)

    # scans edapi, ignoring test package
    config.scan(ignore='edapi.test')
