#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is a class to work with templated LaTeX

from __future__ import division, print_function

import datetime
import re
import os

START = r'''
\newcommand{\pytem}[1]{%
    \ifcsname pytem@#1\endcsname%
        \csname pytem@#1\endcsname%
    \else%
        \texttt{[#1]}%
    \fi%
}

'''
HEADER = '%pytem.sty {0}, generated on {1}\n'
COMMAND = '\\newcommand\\pytem@{0}{{{1}}}\n\n'
DATEFMT = "%B %d, %Y at %I:%M %p"

class Template(object):
    '''This makes and prints a template file for LaTeX.

    To use, you can initialize with a dictionary, or use the class like
    a dictionary.

    >>> tmpl = Template('sampletemplate',dict(one='this', two='that'))
    >>> tmpl['three'] = 'other'
    >>> tmpl.validate('template.tex')
    True
    >>> tmpl.writetofile()

    Args:
        name: The name to label the file header with
        dictionary: An optional dictionary to initialize the class with
    '''
    def __init__(self, name, dictionary=None):
        self._name = name
        if dictionary is None:
            self._dict = dict()
        else:
            self._dict = dictionary

    def __setitem__(self,key,item):
        self._dict[key] = item

    def validate(self, filename):
        '''Check filename to see if all the template entries are accounted for.'''
        allthere = True
        listk = listkeys(filename)
        for item in listk:
            if item not in self._dict:
                print(item, 'missing!')
                allthere = False
        return allthere

    def writetofile(self,styname='pytem.sty'):
        '''Write the style file for importing into LaTeX.'''
        with open(styname, 'w') as f:
            f.write(HEADER.format(self._name,datetime.datetime.now().strftime(DATEFMT)))
            f.write(START)
            for key in self._dict:
                if isinstance(self._dict[key],list):
                    f.write(COMMAND.format(key,', '.join(self._dict[key])))
                else:
                    f.write(COMMAND.format(key,self._dict[key]))

    def compiletofile(self,texfile,styfile='pytem.sty'):
        '''Write and compile ``.tex`` file, in current directory.'''
        self.writetofile(styfile)
        compileLaTeX(os.path.abspath(os.path.curdir),os.path.abspath(os.path.curdir),texfile)

def listkeys(filename):
    with open(filename) as f:
        txt = f.read()
    repattern = re.compile(r'\\pytem{([^}]*)}')
    grplist = repattern.findall(txt)
    return grplist

class DidNotCompileError(Exception):
    'This is thrown if compilation fails'

def compileLaTeX(sourcedir, finaldir, filename,newname=None):
    if newname is None:
        newname = filename
    filename = os.path.splitext(filename)[0]
    newname = os.path.splitext(newname)[0]
    curdir = os.path.abspath('.')
    os.chdir(sourcedir)
    if os.system('pdflatex '+filename+'.tex') == 0:
        try:
            os.unlink(os.path.join(finaldir,newname+'.pdf'))
        except OSError:
            pass
        final_output = os.path.join(finaldir,newname+'.pdf')
        os.rename(os.path.join(sourcedir,filename+'.pdf'), final_output)
        os.unlink(filename+'.log')
        os.unlink(filename+'.aux')
    else:
        os.chdir(curdir)
        raise DidNotCompileError()
    os.chdir(curdir)
    return final_output

def make_latex_table(title,listoflist):
    output = r'\begin{tabular}{r'
    output += 'l'*(len(listoflist[0])-1)
    output += '}\n'
    output += '{\\bfseries ' + '} & {\\bfseries '.join(title) + '}\\\\\n \\hline\n'
    for line in listoflist:
        output += ' & '.join(line)
        output += '\\\\\n'
    output += r'\end{tabular}'
    return output
