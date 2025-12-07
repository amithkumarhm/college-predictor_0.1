#!/usr/bin/env python3
"""
Setup script for College Predictor Application
"""

from setuptools import setup, find_packages
import os

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="college-predictor",
    version="0.1.0",
    author="College Predictor Team",
    author_email="support@collegepredictor.com",
    description="AI-powered college admission prediction system for Karnataka PGCET",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amithkumarhm/college-predictor",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['datasets/*.csv', 'templates/*.html', 'static/*', 'static/css/*', 'static/js/*'],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'college-predictor=app:main',
        ],
    },
)