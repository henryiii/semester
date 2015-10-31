#!/usr/bin/env python3
from __future__ import print_function, unicode_literals
import re
from plumbum import local, cli, CommandNotFound
# Required plumbum > 1.4.2

INPUTEXT = 'mkd'
INPUTFORM = 'markdown+escaped_line_breaks+implicit_figures'

RE_STARREDLINES = re.compile(r'^\s*\*.*?$', re.MULTILINE)
RE_POINTS = re.compile(r'\((\d+)\)')

# Add options for figures if recognised format
IMG_FORMATS = dict(
    pdf='--default-image-extension=pdf',
    docx='--default-image-extension=svg',
    html='--default-image-extension=png',
)

# The following helps find pandoc on Windows if it is not in the path
POSPATHS = (
    'pandoc',
    'pandoc.exe',
    local.path('~/AppData/Local/Pandoc/pandoc.exe'),
    local.path('/Program Files/Pandoc/pandoc.exe'),
    local.path('/Program Files (x86)/Pandoc/pandoc.exe'),
    )


def get_path(possibles):
    for loc in possibles:
        try:
            return local[loc]
        except CommandNotFound:
            pass
    raise CommandNotFound(possibles[0], POSPATHS)

pandoc = get_path(POSPATHS)


def main(filename, outext, ans, prepend=None):
    name = filename.with_suffix('').basename.replace('_', ' ').title()
    outname = filename.with_suffix('.ans' if ans else '').with_suffix('.'+outext, 0)
    out_opts = IMG_FORMATS.get(outext, '')

    if prepend is None:
        heading = ''
    else:
        with open(str(prepend)) as f:
            heading = f.read().format(name=name)

    with open(str(filename)) as f:
        txt = f.read().strip()

    studenttxt = heading + RE_STARREDLINES.sub('', txt)

    pts = RE_POINTS.findall(txt)
    pts = sum(int(p) for p in pts)
    ansheading = '#{0} Rubric. Points: {1}\n\n'.format(name, pts)
    txt = txt.replace('(1)', '**(1 point)**')
    txt = ansheading + RE_POINTS.sub(r'**(\g<1> points)**', txt)

    (pandoc['-V','geometry:margin=1in','-f', INPUTFORM, '-o', str(outname), out_opts]
     << (txt if ans else studenttxt).encode('ascii'))()


class Assignments(cli.Application):
    DESCRIPTION = '''Makes assignments for pandoc. Needs pandoc in the path. \
Processes all *.{0} if no file given.'''.format(INPUTEXT)
    answer = cli.Flag(['-a', '--answer'],
            help="Produce an answer version")

    _prepend = None

    @cli.switch(['-p', '--prepend'], cli.ExistingFile)
    def prepend(self, filename):
        'File to prepend to each assignment'
        self._prepend = filename


    output = cli.SwitchAttr(['-o', '--output'],
            cli.Set('pdf', 'docx', 'html', 'odt'),
            list=True,
            help='Sets the output format...')

    def main(self, *files):
        if not files:
            print("Searching", local.cwd, "for files.")
        if self._prepend is None:
            try:
                self._prepend = cli.ExistingFile('prepend.rst')
            except ValueError:
                pass

        items = list(map(cli.ExistingFile, files)) if files else local.cwd // ('*.'+INPUTEXT)
        try:
            items.remove(self._prepend)
        except ValueError:
            pass

        for item in items:
            if self.output:
                for output in self.output:
                    print(item.basename + '...', end=' ')
                    main(item, output, self.answer, self._prepend)
                    print('\b\b\b\b -> {1}{0} done.'.format(output, 'answers ' if self.answer else ''))

            else:
                for output in IMG_FORMATS:
                    print(item.basename + '...', end=' ')
                    main(item, output, False, self._prepend)
                    print('\b\b\b\b -> {0} done.'.format(output))
                print(item.basename + '...', end=' ')
                main(item, 'pdf', True, self._prepend)
                print('\b\b\b\b -> answers pdf done.')



if __name__ == '__main__':
    Assignments.run()


def main():
    Assignments.run()
