#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="vvm",
    version="0.0.2",  # don't change this manually, use bumpversion instead
    description="Vyper version management tool",
    long_description_markdown_filename="README.md",
    author="Ben Hauser",
    author_email="ben@hauser.id",
    url="https://github.com/vyperlang/vvm",
    include_package_data=True,
    py_modules=["vvm"],
    setup_requires=["setuptools-markdown"],
    python_requires=">=3.6, <4",
    install_requires=["requests>=2.19.0,<3", "semantic_version>=2.8.1,<3"],
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
    ],
)
