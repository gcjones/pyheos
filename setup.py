"""pyheos"""

import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join("README.md"), 'r') as fh:
    long_description = fh.read()

const = {}
with open(os.path.join('pyheos', 'const.py'), 'r') as fp:
    exec(fp.read(), const)

setup(name=const['__title__'],
      version=const['__version__'],
      description='A python library for interacting with HEOS devices using the CLI and asyncio.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/andrewsayre/pyheos',
      author='Andrew Sayre',
      author_email='andrew@sayre.net',
      license='MIT',
      packages=find_packages(),
      install_requires=[],
      tests_require=['tox>=3.5.0,<4.0.0'],
      platforms=['any'],
      keywords="heos",
      zip_safe=False,
      classifiers=[
          "Development Status :: 1 - Planning",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Topic :: Software Development :: Libraries",
          "Topic :: Home Automation",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          ])