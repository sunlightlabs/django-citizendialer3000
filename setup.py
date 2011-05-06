from citizendialer3000 import __version__
from setuptools import setup, find_packages
import os

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
readme = f.read()
f.close()

setup(
    name='django-citizendialer3000',
    version=__version__,
    description='A tool to help US citizens call their representatives in Congress',
    long_description=readme,
    author='Jeremy Carbaugh',
    author_email='jcarbaugh@sunlightfoundation.com',
    url='http://github.com/sunlightlabs/django-citizendialer3000/',
    packages=find_packages(),
    license='BSD License',
    platforms=["any"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
    ],
)
