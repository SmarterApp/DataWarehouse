import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid == 1.4',
    'pyramid_beaker==0.8',
    'SQLAlchemy==0.8.3',
    'transaction==1.4.1',
    'pyramid_tm==0.7',
    'pyramid_debugtoolbar==1.0.8',
    'zope.sqlalchemy==0.7.3',
    'waitress==0.8.7',
    'lxml==3.3.5',
    'config',
    'edcore',
    'edschema',
    'edapi',
    'edauth',
    'edworker',
    'smarter_common',
    'pyramid_exclog==0.7',
    'py-postgresql==1.1.0',
    'psycopg2==2.5.1',
    'python3-memcached == 1.51']

docs_extras = [
    'Sphinx',
    'docutils']

setup(name='smarter_score_batcher',
      version='0.1',
      description='smarter_score_batcher',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application", ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      extras_require={
          'docs': docs_extras, },
      test_suite="smarter_score_batcher",
      entry_points="""\
      [paste.app_factory]
      main = smarter_score_batcher:main
      """,
      )
