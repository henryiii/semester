#!/usr/bin/env python
import os

from setuptools import setup, find_packages

HERE = os.path.dirname(__file__)

setup(
    name = "semester",
    version = "0.1.1",
    description = "Tools to help with running a semester based course",
    author = "Henry Schreiner",
    author_email = "henryschreineriii@gmail.com",
    license = "MIT",
    url = "http://semester.readthedocs.org",
    packages = find_packages(),
    platforms = ["POSIX", "Windows"],
    provides = ["semester"],
    keywords = "classes, teaching, grading, exam, lab, course, school",
    long_description = open(os.path.join(HERE, "README.rst"), "r").read(),
    python_requires = ">=3.7",
    install_requires = [
        "plumbum>=1.5",
        "numpy",
        "scipy",
        "matplotlib",
        "six",
    ],
    classifiers = [
         "Development Status :: 2 - Pre-Alpha",
         "License :: OSI Approved :: MIT License",
         "Operating System :: Microsoft :: Windows",
         "Operating System :: POSIX",
         "Programming Language :: Python :: 3",
         "Topic :: Software Development :: Build Tools",
         "Topic :: System :: Systems Administration",
    ],
    entry_points={
        'console_scripts':[
            'semester = semester.__main__:main',
            'semester.assignments = semester.assignments:main',
            'semester.canvas = semester.utils.canvasgrader:main',
            'semester.figures = semester.figures:main',
            'semester.roster = semester.roster:main',
            ],
        'gui_scripts':[
            'semester.grades = semester.grades:main',
            'semester.gui.roster = semester.gui.roster:main'
            ]
        },
)
