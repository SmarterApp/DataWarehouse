from setuptools import setup, find_packages

requires = ['mock']

tests_require = requires + [
    'nose >= 1.2.1',
    'coverage', ]

setup(name='Henshin',
      version='0.1',
      description='Transform assessment DataGen data to landing zone format',
      classifiers=[
          "Programming Language :: Python", ],
      author='',
      author_email='',
      url='',
      keywords='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=requires,
      tests_require=tests_require,
      entry_points="""\
      """,
      )
