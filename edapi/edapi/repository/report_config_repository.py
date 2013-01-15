'''
Created on Jan 11, 2013

@author: dip
'''
import venusian

class report_config(object):
    def __init__(self, **kwargs):
        #TODO ensure certain keywords exist?
        self.__dict__.update(kwargs)
        
    def __call__(self, original_func):
        settings = self.__dict__.copy()
        
        def callback(scanner, name, obj):
            def wrapper(*args, wrapper, **kwargs):
                print ("Arguments were: %s, %s" % (args, kwargs))
                return original_func(self, *args, **kwargs)
            scanner.registry.add((obj,original_func), **settings)
        venusian.attach(original_func, callback, category='edapi')
        return original_func
           
class ReportConfigRepository: 
    '''A repository of report configs'''
    #TODO temp class var?
    registered = {}
    
    def __init__(self):
        # __registered = {}
        pass
    
    def add(self, delegate, **kwargs):
        settings = kwargs.copy()
        settings['reference'] = delegate
        ReportConfigRepository.registered[settings['alias']] = settings
    
    def get_report_config(self, name):
        report = ReportConfigRepository.registered.get(name, None)
        if (report is None):
            return None
        return report['params']
    
    def get_report_delegate(self, name):
        return ReportConfigRepository.registered[name]['reference']
    
    
    