#!/usr/bin/env python

from setuptools import find_packages, setup

with open('README.md', encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="vvm",
    version="0.3.0",  # don't change this manually, use bumpversion instead
    description="Vyper version management tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ben Hauser",
    author_email="ben@hauser.id",
    url="https://github.com/vyperlang/vvm",
    include_package_data=True,
    py_modules=["vvm"],
    python_requires=">=3.8, <4",
    install_requires=["requests>=2.32.3,<3", "packaging>=24.1,<25"],
    license="MIT",
    zip_safe=False,
    keywords="ethereum vyper",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
