'''
Entry point for edapi

'''
EDAPI_REPORTS_PLACEHOLDER = 'edapi_reports'

# directive used to save report_config decorators to Pyramid Configurator's registry
def add_report_config(self, delegate, **kwargs):
    settings = kwargs.copy()
    settings['reference'] = delegate
    if self.registry.get(EDAPI_REPORTS_PLACEHOLDER) is None:
        self.registry[EDAPI_REPORTS_PLACEHOLDER] = {}
    
    # Only process decorators with a name defined
    if settings.get('name') is not None:
        self.registry[EDAPI_REPORTS_PLACEHOLDER][settings['name']] = settings

# this is automatically called by consumer of edapi when it calls config.include(edapi)     
def includeme(config):
    # routing for retrieving list of report names with GET
    config.add_route('list_of_reports', '/data')
    
    # routing for the GET, POST, OPTIONS verbs
    config.add_route('report_get_option_post', '/data/{name}')
    
    # directive to handle report_config decorators
    config.add_directive('add_report_config', add_report_config)
    
    # scans edapi, ignoring test package
    config.scan(ignore='edapi.test')
