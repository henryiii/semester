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
get the requirements is to install Anaconda.

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

.. note::

   There is a graphical tool for creating assignments from `.mkd` files. It was created using `tKinter`
   and `sandals.py`.

Figures
-------

The problem with these assignments, while they support latex math and markdown formating, putting images in can be hard. The `semester figures` command allows you to create the required copies of a .tex image written in Tikz to insert into an assignment. See the examples folder.

Roster
------



Init
----



Grades
------


Canvas
------





.. code-block:: bash

    $ semester




