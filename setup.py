'''
Created on May 2, 2013

@author: ejen
'''
from distutils.core import setup
import subprocess

subprocess.call('cd ./scripts/; ./install_udl_requirements.sh', shell=True)

requires = ['celery(>=3.0.19)']

scripts = ['scripts/initialize_udl2_database.sh',
         'scripts/initialize_udl2_database_user.sh',
         'scripts/initialize_udl2_directories.sh',
         'scripts/start_rabbitmq.sh',
         'scripts/start_celery.sh',
         'scripts/start_udl.sh',
         'scripts/teardown_udl2_database.sh',
         'scripts/initialize_udl2_database_user.py',
         'scripts/start_rabbitmq.py',
         'scripts/start_celery.py',
         'scripts/driver.py',]

setup(name='udl2',
      version='0.1',
      description="Edware's Universal Data Loader",
      author="Amplify Insight Edware Team",
      author_email="edwaredev@wgen.net",
      packages=['edschema', 'fileloader', 'filesplitter', 'final_cleanup', 'move_to_integration', 
                'move_to_target', 'sfv', 'udl2', 'udl2_util', 'udl2_tests',],
      package_dir={'edschema':'src/edschema',
                   'fileloader':'src/fileloader',
                   'filesplitter':'src/filesplitter',
                   'final_cleanup':'src/final_cleanup',
                   'move_to_integration': 'src/move_to_integration',
                   'move_to_target': 'src/move_to_target',
                   'sfv': 'src/sfv',
                   'udl2':'src/udl2',
                   'udl2_util':'src/udl2_util',
                   'udl2_tests':'tests'
      },
      package_data={'udl2': ['datafiles/*.csv']},
      url='https://github.wgenhq.net/Ed-Ware-SBAC/edware-udl-2.0/',
      scripts=scripts,
      requires=requires,
      data_files=[('/var/log/wgen/edware-udl/logs', ['logs/udl2.audit.log', 'logs/udl2.error.log']),
                  ('/opt/wgen/edware-udl/etc', ['conf/udl2_conf.ini', 'conf/udl2_conf.cfg', 'conf/udl2_conf.py']),
                  ('/opt/wgen/edware-udl/zones/datafiles/', ['src/udl2/datafiles/seed.csv']),
                  ('/opt/wgen/edware-udl/zones/datafiles/',['tests/data/valid_csv.csv', 'tests/data/invalid_ext.xls']), ],
) 
