import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid == 1.4',
    'pyramid_beaker',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'edauth',
    'edapi',
    'edworker',
    'edschema',
    'py-postgresql',
    'psycopg2',
    'pyramid_exclog',
    'pyyaml',
    'services',
    'python3-memcached']

docs_extras = [
    'Sphinx',
    'docutils',
    'repoze.sphinx.autointerface']

setup(name='smarter',
      version='0.1',
      description='smarter',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application", ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages() + ['config'],
      package_dir={'config': '../config'},
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=requires,
      extras_require={
          'docs': docs_extras, },
      entry_points="""\
      [paste.app_factory]
      main = smarter:main
      [console_scripts]
      initialize_smarter_db = smarter.scripts.initializedb:main
      """
      )
