from __future__ import annotations

import shutil
import sys
from pathlib import Path

import nox

ALL_PYTHONS = ["3.7", "3.8", "3.9", "3.10"]

nox.options.sessions = ["lint", "tests"]


DIR = Path(__file__).parent.resolve()


@nox.session(reuse_venv=True)
def lint(session):
    """
    Run the linter.
    """
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(python=ALL_PYTHONS, reuse_venv=True)
def tests(session):
    """
    Run the unit and regular tests.
    """
    session.install("-e", ".[test]")
    session.run("pytest", *session.posargs)


@nox.session
def build(session):
    """
    Build an SDist and wheel.
    """
    session.install("build")
    session.run("python", "-m", "build")
