"""A collection for arbitrary objects, that indexes them based on (a given subset of) their properties.

but keeps track of the given props values, so you can use multiple different kinds of indexing to find an object again at a later time.
"""

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

long_description = ''
with(open(path.join(here, 'README.md'), encoding='utf-8')) as f:
    long_descruption = f.read()

setup(
    name='multi_indexed_collection',
    py_modules=['multi_indexed_collection'],
    version='1.1.0',
    description='A collection for arbitrary objects, that indexes them based on (a given subset of) their properties.',
    long_description=long_description,
    url='https://github.com/Qqwy/python-multiple_indexed_collection',
    author='Qqwy/Wiebe-Marten Wijnja',
    author_email='qqwy@gmx.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
    python_requires='>=3',
)
