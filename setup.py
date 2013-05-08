from distutils.core import setup
import subprocess

subprocess.call('cd ./scripts/; ./install_udl_requirements.sh', shell=True)

requires=['celery(>=3.0.19)']

scripts=['scripts/initialize_udl_database.sh',
         'scripts/start_rabbitmq.sh',
         'scripts/start_udl.sh',
         'scripts/initialize_udl_database.py',
         'scripts/start_rabbitmq.py',
         'scripts/start_udl.py']

setup(name='udl2', 
      version='0.1',
      description="Edware's Universal Data Loader",
      author="Amplify Insight Edware Team",
      author_email="edwaredev@wgen.net",
      packages=['udl2', 'elastic_csv', 'fileloader', 'filesplitter',],
      package_dir={'udl2':'src/udl2', 
                   'elastic_csv':'src/elastic_csv',
                   'fileloader':'src/fileloader',
                   'filesplitter':'src/filesplitter',},
      package_data={'udl2': ['datafiles/*.csv']},
      url='https://github.wgenhq.net/Ed-Ware-SBAC/edware-udl-2.0/',
      scripts=scripts,
      requires=requires,
      data_files=[('/opt/wgen/edware-udl/logs', ['logs/udl2.audit.log', 'logs/udl2.error.log']),
                  ('/opt/wgen/edware-udl/etc', ['conf/udl2.ini', 'conf/udl2.cfg', 'conf/udl2.py']),],
) 