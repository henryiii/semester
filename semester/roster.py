#!/usr/bin/env python
'''
This makes a printable grade list from a downloaded roster. Choose the
for grade submission roster to ensure all important fields are present.

To run:

.. code:bash
    $ ./makelist.py -s clips_nro4.WBY
    $ pdflatex list.tex
    $ evince list.pdf
'''
from __future__ import print_function

from plumbum import cli, local, FG
from plumbum.cmd import pdflatex
from plumbum.path.utils import delete

import functools as ft
from datetime import datetime
import pandas as pd

EID_NAME = 'EID'
STUDENT_NAME = 'Name'
ROSTER_FILE = 'roster.tex'
STUDENTS_FILE = 'students.tex'

START = r'''
\documentclass[letterpaper,12pt,article]{memoir}
\setulmarginsandblock{1in}{1in}{*}
\setlrmarginsandblock{.75in}{.75in}{*}
\checkandfixthelayout
\renewcommand\arraystretch{1.6}
\begin{document}
\pagestyle{empty}
'''

def TABLEHEAD(n) :
    lines = [r'}\\[2ex]', '', r'\begin{tabular}{rl*{'+str(n)+r'}{|p{.25in}}|}']
    lines.append('Name & EID & ' + ' & '.join(str(i+1) for i in range(n)) +  r' \\\hline')
    return '\n'.join(lines)

ROSTTABLEHEAD = r'''}\\[2ex]

\begin{tabular}{|rl|p{4in}|}
\hline
Name & EID & Present? \\\hline'''



class Roster(cli.Application):
    'This makes a printable grade list from a downloaded roster.'
    roster = cli.Flag(['-r', '--roster'], help='Makes a single column roster instead')
    number = cli.SwitchAttr(['-n', '--number'], cli.Range(1,12), default=11, help='Number of columns in gradesheet')
    _schedule = None

    @cli.switch(['-s', '--schedule'], cli.ExistingFile)
    def schedule(self, filename):
        'Read schedule file, in the std csv format.'
        self._schedule = filename

    def main(self, filename):
        filename = cli.ExistingFile(filename)
        outname = local.cwd / (ROSTER_FILE if self.roster else STUDENTS_FILE)

        date = datetime.now().date()
        semester = 'Spring' if date.month < 5 else 'Summer' if date.month < 8 else 'Fall'

        with open(str(outname),'w') as f:
            out = ft.partial(print,file=f)
            outtable = ft.partial(out,sep=' & ',end=' \\\\\\hline\n')

            students = pd.read_csv(str(filename),sep='\t')
            students = students[pd.notnull(students[EID_NAME])]

            out(START)

            lst = ['']*(1 if self.roster else self.number)
            printed = False

            def splitnames(row):
                row['Lastname'], row['Firstnames'] = row[STUDENT_NAME].title().split('; ')
                row['Firstname'] = row['Firstnames'].split()[0].strip()
                row['NiceName'] = row['Firstname'] + ' ' + row['Lastname']
                return row

            def printrow(row):
                outtable(row['NiceName'],row[EID_NAME],*lst)

            if self._schedule:
                labinfo = pd.read_csv(str(self._schedule),index_col=0)

            for val in sorted(set(students['Unique'])):
                if printed:
                    out(r'\newpage')
                else:
                    printed = True
                one_class = students[students['Unique']==val]
                class_header = '{} \quad {} {} -- {} students'.format(int(val), semester, date.year, len(one_class.index))
                if self._schedule:
                    info = labinfo.loc[int(val)]
                    class_header += ' \quad ' + info['weekday'].upper() + '@' + str(info['starting hour'])
                out(r'''
            \begin{center}

            {\bfseries\large''',class_header,(ROSTTABLEHEAD if self.roster else TABLEHEAD(self.number)))

                one_class = one_class.apply(splitnames,axis=1)
                one_class.apply(printrow,axis=1)

                out('''\\end{tabular}
            \end{center}''')

            out('''
            \end{document}
            ''')

        pdflatex[outname] & FG
        delete(outname,
               outname.with_suffix('.log'),
               outname.with_suffix('.aux'))
        print("Created", outname.with_suffix('.pdf'))

if __name__ == '__main__':
    Roster.run()

def main():
    Roster.run()
