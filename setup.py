#!/usr/bin/env python3
#
# Copyright (c) 2018 Tatu Ylonen.  See LICENSE and https://ylonen.org

from setuptools import setup, Extension

with open("README.md", "r") as f:
    long_description = f.read()

setup(name="tokentree",
      version="0.1.0",
      description="Optimized tree of integer tokens with counts and data",
      long_description=long_description,
      long_description_content_type="text/markdown",
      author="Tatu Ylonen",
      author_email="ylo@clausal.com",
      url="https://ylonen.org",
      license="MIT",
      download_url="https://github.com/tatuylonen/tokentree",
      packages=["tokentree"],
      setup_requires=["cython",
                      "setuptools>=18.0"],
      ext_modules=[Extension("tokentree.ctokentree",
                             sources=["tokentree/ctokentree.pyx"])],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3 :: Only",
          ])
