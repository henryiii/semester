#!/usr/bin/env python
import os

from setuptools import setup, find_packages

HERE = os.path.dirname(__file__)

setup(
    name = "semester",
    version = "0.1.0",
    description = "Tools to help with running a semester based course",
    author = "Henry Schreiner",
    author_email = "henryiii@physics.utexas.edu",
    license = "MIT",
    url = "http://semester.readthedocs.org",
    packages = find_packages(),
    platforms = ["POSIX", "Windows"],
    provides = ["semester"],
    keywords = "classes, teaching, grading, exam, lab, course, school",
    long_description = open(os.path.join(HERE, "README.rst"), "r").read(),
    classifiers = [
         "Development Status :: 5 - Production/Stable",
         "License :: OSI Approved :: MIT License",
         "Operating System :: Microsoft :: Windows",
         "Operating System :: POSIX",
         "Programming Language :: Python :: 2.7",
         "Programming Language :: Python :: 3",
         "Programming Language :: Python :: 3.3",
         "Programming Language :: Python :: 3.4",
         "Topic :: Software Development :: Build Tools",
         "Topic :: System :: Systems Administration",
    ],
    entry_points={
        'console_scripts':[
            'semester = semester.__main__:Semester.run',
            'semester.assignments = semester.assignments:Assignments.run',
            'semester.figures = semester.figures:Figures.run',
            'semester.roster = semester.roster:Roster.run',
            ],
        'gui_scripts':[
            'semester.grades = semester.grades:main',
            'semester.gui.roster = semester.gui.roster:main'
            ]
        },
)
