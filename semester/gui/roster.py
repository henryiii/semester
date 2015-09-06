#!/usr/bin/env python3

from sandals import *
from semester.roster import Roster
import webbrowser

with window("Make roster"):
    label("Roster should be downloaded in\nCLIPs Grade Submission format")

    with stack(borderwidth=1, relief=tkinter.SUNKEN):
        file_label = editBox("", width=50)
        @button("Pick roster file")
        def pick_file():
            with askOpenFile() as f:
                file_label.text = f.name

    with stack(borderwidth=1, relief=tkinter.SUNKEN):
        times_label = editBox("", width=50)

        @button("Pick times file (optional)")
        def pick_times():
            with askOpenFile() as f:
                times_label.text = f.name

    with flow():
        label = label("The number of assignments for columns roster:")

        @spinBox(default=11, values=list(range(2,13)), width=4)
        def spin(value):
            pass

    @button("Make columns roster")
    def make_roster():
        if not file_label.text:
            print("Must have a filename")
            return
        if times_label.text:
            Roster.invoke(file_label.text, number=int(spin.value), schedule=times_label.text)
            webbrowser.open('students.pdf')
        else:
            Roster.invoke(file_label.text, number=int(spin.value))
            webbrowser.open('roster.pdf')

    @button("Make sign in sheet")
    def make_signin():
        if not file_label.text:
            print("Must have a filename")
            return
        if times_label.text:
            Roster.invoke(file_label.text, number=int(spin.value), schedule=times_label.text, roster=True)
            webbrowser.open('students.pdf')
        else:
            Roster.invoke(file_label.text, number=int(spin.value), roster=True)
            webbrowser.open('roster.pdf')
