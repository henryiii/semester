#!/usr/bin/env python3

from __future__ import absolute_import

from plumbum import cli

from .assignments import Assignments
from .makefigures import MakeFigures
from .roster import Roster

class Semester(cli.Application):
    'Holds several semester cli tools'

Semester.subcommand("assignments", Assignments)
Semester.subcommand("makefigures", MakeFigures)
Semester.subcommand("roster", Roster)
