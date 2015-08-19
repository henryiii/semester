#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 17:26:59 2015

@author: henryiii
"""

from . import pytem
import os
import pandas as pd
from datetime import date
from bs4 import BeautifulSoup
import sys

SOURCE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.normpath(os.path.join(SOURCE,os.path.pardir))
FINAL = os.path.join(MAIN,'output')
WEB = os.path.normpath(os.path.join(MAIN,os.path.pardir,'web'))



FILE_TA = os.path.join(MAIN,'tainfo.csv')
FILE_SCHED = os.path.join(MAIN,'schedinfo.csv')
FILE_TIMES = os.path.join(MAIN,'labinfo.csv')

OUT_TALIST_HTML = os.path.join(FINAL,'talist.html')
OUT_TALIST_EMAIL = os.path.join(FINAL,'talist.txt')
OUT_CLASSLIST_HTML = os.path.join(FINAL,'classlist.html')

PYTEM_STY = os.path.join(SOURCE,'pytem.sty')
PAGE_TABLE_HEADER = '''
                <tr>
                        <td><p>Name</p></td>
                        <td><p>Classes</p></td>
                        <td><p>Office Location</p></td>
                        <td><p>Office Hours</p></td>
                        <td><p>Email</p></td>
                </tr>
'''
PAGE = '''
                <tr>
                        <td><p>{0}</p></td>
                        <td><p>{1}</p></td>
                        <td><p>{2}</p></td>
                        <td><p>{3}</p></td>
                        <td><p><a href="{4}">{4}</a>{5}</p></td>
                </tr>
'''
SIMPLE = '''
Name: {0}
Sections: {1}
Office: {2}
Date: {3}
Email: {4}
Phone: {5}
'''

TEXHEADER = 'Name & Labs & Email'
TEXPAGE = '''{0} & {1} & {4}'''

TABLEHEADER = 'section\tday and time      \teid   \tname\n' + 54*'-' + '\n'
TABLE = '{section}\t{day}\t{eid}\t{name}\n'
SECTABLE = '''
                <tr>
                        <td>{section}</td>
                        <td>{day}</td>
                        <td>{name}</td>
                </tr>'''

WEEK = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Monday/Wednesday','Tuesday/Thursday']
SWEEK = ['U','M','T','W','R','F','S','MW','TR']

TAF = ['eid','name','sections','officeloc','officehours','emailstu','emailother','phone']
LABF = ['class','weekday','hour']
SF = ['date', 'lab']

if WEB not in sys.path:
    sys.path.insert(0, WEB)
import send as send_web

def current_semester():
    'This outputs the current semster. Comment out and put a hard coded semester if you must have a different one.'
    today = date.today()
    month = today.month + today.day / 31.
    year = today.year + (1 if month > 11.5 else 0)
    if month>11.5 or month < 5.1:
        semester = 'Spring'
    elif month < 7:
        semester = 'Summer'
    else:
        semester = 'Fall'
    return '{} {}'.format(semester,year)
    #return 'Summer 2015'


def to12(hour):
    return (hour - (0 if hour <= 12 else 12),('AM' if hour < 12 else 'PM'))

def loadTimesList( filename=FILE_TIMES):
    return pd.read_csv(filename,dtype=str,skipinitialspace=True).set_index('class')

class Time(object):
    'Interpret a pandas row as a time'
    def __init__(self,row):
        '1 is monday, etc.'
        try:
            self.day = SWEEK.index(row['weekday'].upper())
        except (AttributeError, ValueError):
            self.day = row['weekday']
        self.hour = int(row['starting hour'])
    def make_day(self):
        hour,ampm = to12(self.hour)
        return '{0:<9} {1:2}:00 {2}'.format(WEEK[self.day],hour,ampm)
    def make_day_simple(self):
        return '{0}{1}'.format(SWEEK[self.day],self.hour)

    def make_day_range(self):
        return '{0} {1}00 to {2}00'.format(SWEEK[self.day],self.hour,self.hour + 2)



def loadTAList( filename=FILE_TA):
    talist = pd.read_csv(filename, index_col='EID', dtype=str, skipinitialspace=True)
    talist['Classes'].fillna('None',inplace=True)
    talist.fillna('NA',inplace=True)
    return talist


class TA(object):
    def __init__(self, row):
        self.eid = row.name
        self.name = row['Name']
        self.sections = row['Classes'].split(',')
        if '*' in row['Office location']:
            office,self.mail = row['Office location'].split('*')
        else:
            self.mail = 'mailbox is on 5th floor RLM, all the way down the hall'
            office =  row['Office location']
        self.office = office
        self.date = row['Office hours'].split(',')
        self.email = row['Email (students)']
        if row["Email (other TA's)"]:
            self.otheremail = row["Email (other TA's)"]
        else:
            self.otheremail =row["Email (students)"]
        self.phone = row['Phone']

    @classmethod
    def notavailable(cls):
        row = pd.DataFrame(index=[u'Name', u'Classes', u'Office location', u'Office hours', u'Email (students)', u"Email (other TA's)", u'Phone'])
        row['Name']['------']='Not assigned'
        return cls(row)

    def make_web(self, times):
        date = "<br/>".join(self.date).replace('--','-')
        sections = "<br/>".join(a + ' ' + Time(times.ix[a]).make_day() for a in self.sections)
        #phone = ("<br/>" + self.phone if self.phone else "")
        phone = ''
        return PAGE.format(
                 self.name.replace('\\"u','&uuml;'),
                 sections,
                 self.office,
                 date,
                 self.email,
                 phone)

    def make_tex(self, times):

        sections = ", ".join((a + ' ' + Time(times.ix[a]).make_day_simple() for a in self.sections))
        return ( self.name,
                 sections,
                 self.email,
                 self.phone)

    def make_email(self, lab, labtime):
        return TABLE.format(section=lab,day=labtime,eid=self.eid,name=self.name.replace('\\"u','ue'))

    def make_web_section(self, lab, labtime):
        return SECTABLE.format(section=lab,day=labtime,name=self.name)

    def __repr__(self):
        return SIMPLE.format(*self.as_list())

    @staticmethod
    def header():
        return 'Eid', 'Name', 'Sections', "Office", "Date", "Email", "Other email", "Phone"




def loadScheduleList(filename=FILE_SCHED):
   return pd.read_csv(filename, skipinitialspace=True)

class Schedule(object):
    def __init__(self, row):
        self.date = row['date']
        self.name = row['lab']



class AllInfo(object):
    def __init__(self):
        self.semestertext = current_semester()
        self.tmpl = None

    def talistload(self, filename=FILE_TA):
        self.talist = loadTAList(filename)

    def talistsave(self,filename=FILE_TA):
        self.talist.to_csv(filename, )

    def schedulelistload(self, filename=FILE_SCHED):
        self.schedulelist = loadScheduleList(filename)

    def schedulelistsave(self, filename=FILE_SCHED):
        self.schedulelist.to_csv(filename,index=False)

    def lablistload(self, filename=FILE_TIMES):
        self.lablist = loadTimesList(filename)

    def lablistsave(self, filename=FILE_TIMES):
        self.lablist.to_csv(filename)

    def init_template(self, forced_recreate=False):
        if forced_recreate or self.tmpl is None:
            schedules = self.schedulelist.apply(Schedule, axis=1)
            tas = self.talist.apply(TA, axis=1)
            self.tmpl = pytem.Template('lab102m')
            added_red = [[item.date,item.name]
                         if 'no lab' not in item.name.lower() else
                         ['\emph{'+item.date+'}','\emph{'+item.name+'}'] for item in schedules]
            self.tmpl['firstlab'] = schedules[0].date if 'no lab' not in schedules[0].name.lower() else schedules[1].date
            self.tmpl['semester'] = self.semestertext
            self.tmpl['labtable'] = pytem.make_latex_table(['Date','Lab'],added_red)
            self.tmpl['headta'] = tas[0].name
            self.set_ta(tas[0])

            talist =  [ta.make_tex(self.lablist) for ta in tas]
            self.tmpl['tatable'] = pytem.make_latex_table(['Name','Sections','Email','Phone'],talist)

    def set_ta(self,ta):
        self.tmpl['currentname'] = ta.name
        self.tmpl['currentemail'] = ta.email
        self.tmpl['currentofficeloc'] = ta.office
        self.tmpl['currentofficehours'] = ta.date
        self.tmpl['currentmailbox'] = ta.mail

    def write_html_talist(self):
        self.init_template()
        tas = self.talist.apply(TA, axis=1)
        with open(OUT_TALIST_HTML,'w') as f:
            f.write(PAGE_TABLE_HEADER)
            for ta in tas:
                f.write(ta.make_web(self.lablist))

    def write_html_classlist(self):
        self.init_template()
        tas = self.talist.apply(TA, axis=1)
        with open(OUT_CLASSLIST_HTML,'w') as f:
            for section in sorted(self.lablist.index):
                section_found = False
                for ta in tas:
                    if section in ta.sections:
                        f.write(ta.make_web_section(section, Time(self.lablist.ix[section]).make_day()))
                        section_found = True
                        break
                if not section_found:
                    f.write(TA.notavailable().make_web_section(section, Time(self.lablist.ix[section]).make_day()))

    def write_email_talist(self):
        self.init_template()
        tas = self.talist.apply(TA, axis=1)
        with open(OUT_TALIST_EMAIL,'w') as f:
            f.write('This is the assignment of the TAs in the lab sections for 102M:\n\n')
            f.write(TABLEHEADER)
            for section in sorted(self.lablist.index):
                section_found = False
                for ta in tas:
                    if section in ta.sections:
                        f.write(ta.make_email(section, Time(self.lablist.ix[section]).make_day()))
                        section_found = True
                        break
                if not section_found:
                    f.write(TA.notavailable().make_email(section, Time(self.lablist.ix[section]).make_day()))
        return OUT_TALIST_EMAIL

    def write_latex_template(self,filename = PYTEM_STY):
        self.init_template()
        self.tmpl.writetofile(filename)

    def make_latex_tarequirements(self):
        self.init_template()
        return pytem.compileLaTeX(SOURCE,FINAL,'tareqirements')


    def make_latex_schedule(self):
        print('Creating schedule')
        self.init_template()
        return pytem.compileLaTeX(SOURCE,FINAL,'schedule')

    def make_latex_handout(self):
        print('Creating handout')
        self.init_template()
        return pytem.compileLaTeX(SOURCE,FINAL,'handout')

    def make_latex_syllabi(self, filename = PYTEM_STY):
        self.init_template()
        tas = self.talist.index
        return [self.make_latex_syllabus(taeid, filename) for taeid in reversed(tas)]

    def make_latex_syllabus(self, taeid, filename = PYTEM_STY):
        ta = TA(self.talist.ix[taeid])
        self.set_ta(ta)
        self.write_latex_template(filename)
        return pytem.compileLaTeX(SOURCE,FINAL,'syllabus','Syllabus_102M_'+ta.name.replace(' ','_').replace('\\"u','ue'))


def copy_web_files():
    TAFILE = (os.path.join(WEB,"personnel.html"), os.path.join(FINAL,"talist.html"))
    CFILE = (os.path.join(WEB,"classes.html"), os.path.join(FINAL,"classlist.html"))

    for file_o, file_s in (TAFILE, CFILE):
        with open(file_o) as f:
            soup = BeautifulSoup(f)
        with open(file_s) as f:
            add_table = '<table border="1" cellpadding="2" cellspacing="2" class="content_table">' + f.read() + r'</table>'
        tatable = BeautifulSoup(add_table)
        soup.table.replace_with(tatable.table)
        with open(file_o,'w') as f:
            f.write(soup.prettify())


def send_web_files():
    send_web.main()

def main():
    info = AllInfo()

    info.talistload()
    info.schedulelistload()
    info.lablistload()

    info.write_latex_template()

    info.write_html_talist()
    info.write_email_talist()
    info.write_html_classlist()
    info.make_latex_tarequirements()
    info.make_latex_schedule()
    info.make_latex_handout()
    info.make_latex_syllabi()

if __name__ == '__main__':
    main()
