"""A collection that works like a set/dictionary,

but keeps track of the given props values, so you can use multiple different kinds of indexing to find an object again at a later time.
"""

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with(open(path.join(here, 'README.md'), encoding='utf-8')) as f:
    long_descruption = f.read()

setup(
    name='multi_indexed_dict',
    version='0.0.1',
    description='Multiple Indexed Dictionary',
    long_description=long_description,
    # url='https://github.com/Qqwy/TODO',
    author='Qqwy/Wiebe-Marten Wijnja',
    author_email='qqwy@gmx.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',

        'Programming Language :: Python 3',
        'Locense :: OSI Approved :: MIT Liccense',
    ],
)
