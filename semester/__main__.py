#!/usr/bin/env python3

from __future__ import absolute_import

from plumbum import cli

from .assignments import Assignments
from .figures import Figures
from .roster import Roster
from .grades import process

class Semester(cli.Application):
    'Holds several semester cli tools'

Semester.subcommand("assignments", Assignments)
Semester.subcommand("figures", Figures)
Semester.subcommand("roster", Roster)

@Semester.subcommand("grades")
class Grades(cli.Application):
    "Sets the grades using a gui application."

    def main(self, *filenames):
        for f in filenames:
            cli.ExistingFile(f) # Just checking for errors, result not used

@Semester.subcommand("canvas")
class Canvas(cli.Application):
    "Helps run through empty grade files."

    def main(self):
        from .util.canvasgrader import main
        main()

if __name__ == '__main__':
    Semester.run()

def main():
    Semester.run()
