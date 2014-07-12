#! /usr/bin/env python

from setuptools import setup, find_packages

setup(name="django-cache-by-user",
      version="1.0.0",
      author="Rory McCann",
      author_email="rory@technomancy.org",
      url='https://github.com/rory/django-cache-by-user',
      packages=['cache_by_user'],
      license='GPLv3',
      description=('Make your django site share a cache'
                   ' for all anonymous users, increasing cache hits'), )
