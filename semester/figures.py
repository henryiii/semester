#!/usr/bin/env python3
from __future__ import print_function, unicode_literals

from plumbum.cmd import pdflatex, convert
from plumbum import local, cli, FG
from plumbum.path.utils import delete
# Required plumbum > 1.4.2

def image_comp(item):
    pdflatex['-shell-escape', item] & FG
    print('Converting', item)
    convert[item.with_suffix('.svg'),
            item.with_suffix('.png')] & FG

    delete(item.with_suffix('.log'),
           item.with_suffix('.aux'),
           )


class Figures(cli.Application):
    'Creates figures from source files, in several useful formats.'
    def main(self, *srcfiles):
        items = map(cli.ExistingFile, srcfiles) if srcfiles else local.cwd // '*.tex'
        for item in items:
            image_comp(item)


if __name__ == '__main__':
    Figures.run()

def main():
    Figures.run()
