========
semester
========


A package of scripts and tools to make running a class or lab easier.


Description
===========

This package contains several tools that greatly ease starting a new semester. It
was written for a lab course at the University of Texas at Austin, but most of the
components should be general enough to use for other systems. Contributions
to generalize the system are welcome.

Installation
============

This is a standard python package and can be installed using pip. From
Pypi, this is `pip install semster`, and from the repository, simply
use `pip install -e .` to install (will still be editable). The `requirements.txt`
file contains the Python requirements, like `plumbum`. The easiest way to 
get the requirements on Mac, Linux, or Windows is to install Anaconda.
If you are familiar with Conda's
`env` tool, you can use the `environment.yml` file to instally prepare a virtual
enviroment for semester.

Other requirements: this needs `pandoc` (for creating different output formats) and
`ImageMagick` (for the figure conversion). Currently these are required. Optional
components include `PyQT` (for some of the guis).

Tools
=====

The main program is a command line laucher for the scripts. Simply run `semester` or
`python -m semester` to
see a list of the programs. All the programs have a shortcut, too, so this is just for
convinence. Shortcuts are added to the python path for the programs (or the the `python -m`
runable module syntax can be used).

Assignments
-----------

This can be run as `semester assignments` or `semester.assignments`. Makes assignments
from markdown files using pandoc. Processes all `*.mkd` files if no file fiven. Options include
`-a` to make an answer key, `-o` to set the output format(s), and `-p` to prepend a file to each
markdown file. Will try to prepend `prepend.rst` if no file given.

The format of the `.rst` files should be as follows:
A numbered list indicating questions
A stared sublist denoting answers, with values in parenthesis
For example:

.. code-block:: markdown

    1. First question
        * First part of answer (2)
        * Answers can have multiple parts(3)

The prepend file goes at the beginning, and can contain `{name}`, which will be based on the filename.
If you name your files `postlab1.mkd` or `homework1.mkd`, they will be nicely typeset here.


Figures
-------

The problem with these assignments, while they support latex math and markdown formating, putting images in can be hard. The `semester figures` command allows you to create the required copies of a .tex image written in Tikz to insert into an assignment. See the examples folder.

Roster
------

This allows you to take a CLIPs roster and make a printable roster that you can use to grade with.

A gui.roster option allows simple usage from a GUI.


Init
----

A package for creating new semester files, such as syllabii, teaching guidelines, schedule handouts. Has an optional GUI.

.. note:: Coming soon!

Grades
------

This allows you to grade a set of canvas classes (1 or more) with a powerful gui. Download the file(s) from Canvas export and then open them
with this program (if you open the program without an argument, it will ask you for a file with a GUI).

Once open, you can drag to set grades and there arer buttons to save files in different formats.

Canvas
------

A small utility to assist grading in Canvas when yo set a 0 point question (for just in time teaching style, for example).

.. note:: Coming soon!



.. code-block:: bash

    $ semester




