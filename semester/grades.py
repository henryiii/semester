#!/usr/bin/env python

'''
Set final grades
Henry Schreiner
Version 1.5

This requires Anaconda, or the following:
* Python 2.7 or 3.3+
* Numpy
* Scipy
* Matplotlib
* Pandas
* Six

Note: Most of the time, Python includes the
required graphical toolkit, Tkinter. However,
on some OS's, Python is separated and you may
need to add python-tkinter manually.

'''

from __future__ import division, print_function

import sys
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
from matplotlib.widgets import Button
import platform
import re
from six import string_types
import pandas as pd

from six.moves.tkinter import Tk
from six.moves.tkinter_tkfiledialog import askopenfilenames, askopenfilename, asksaveasfile

class Cutoffs(object):
    def __init__(self, students):
        self.gpacuts = np.array([60, 62, 68, 70, 72, 78, 80, 82, 88, 90, 92.])+.5
        self.gpanames = np.array(['F','D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A'])
        self.gpavalues = np.array([0, 1-1/3, 1,  1+1/3, 2-1/3, 2,   2+1/3, 3-1/3, 3,   3+1/3, 4-1/3, 4])
        self.student_list = students
        self.student_list.sort(['Score'],ascending=False,inplace=True)
        #self.totals = students['Score'].order(ascending=False)
        # Remove the following line to remove cut prediction
        self.gpacuts[:] = self.predict_cuts()

    @property
    def gpacutsfull(self):
        'Add 0 and 100 to the cuts'
        return np.append(0,np.append(self.gpacuts,100))

    @property
    def num_students(self):
        return len(self.student_list)

    def hist(self):
        return sp.histogram(self.student_list['Score'],self.gpacutsfull)[0]

    def check(self):
        return np.sum(self.hist()*self.gpavalues)/self.num_students

    def listhist(self):
        return ['{}:{}'.format(nm,hist) for hist, nm in zip(self.hist()[::-1],self.gpanames[::-1]) if hist > 0]

    def whatgrade(self,grade):
        return self.gpanames[abovewhich(self.gpacutsfull,grade)]

    def listcuts(self):
        return ['{}:{}'.format(self.gpacuts[-n-1],self.gpanames[-n-1]) for n in range(len(self.gpacuts))]

    def predict_cuts(self):
        cuts =  (predict_cuts(self.student_list['Score'])-.5).round()+.5
        return np.fmax(np.fmin(cuts,99.5),9.5)

    def itcuts(self):
        return [(self.gpanames[-n-1],self.gpacuts[-n-1]) for n in range(len(self.gpacuts))]

    def __repr__(self):
        return '{} students, Average GPA:{:.2f}'.format(self.num_students, self.check())
    def __str__(self):
        return repr(self)

    def gpastring(self):
        return 'GPA:{:.2f}'.format(self.check())

    def plot(self):
        self.max = max(self.student_list['Score'])+2
        self.min = min(x for x in self.student_list['Score'] if x > 5)-4

        fig = plt.figure(1,figsize=(16,8))
        ax = fig.add_subplot(111,
                             autoscale_on=False,
                             xlim=(0,self.num_students),
                             ylim=(self.min,self.max))

        fig.subplots_adjust(right=0.76, left=.05)

        # Set 1 line per %
        ax.yaxis.set_major_locator(plt.MultipleLocator(10.0))
        ax.yaxis.set_minor_locator(plt.MultipleLocator(1.0))
        ax.yaxis.grid(which='major', linewidth=0.75, linestyle='-', color='0.75')
        ax.yaxis.grid(which='minor', linewidth=0.25, linestyle='-', color='0.75')

        # Remove xaxis stuff
        ax.xaxis.set_ticks([])

        #set lines
        self.listlines = [plt.axhline(a,axes=ax,alpha=.3) for a in self.gpacuts]

        gpacutsforav = np.append(self.min,np.append(self.gpacuts,self.max))
        self.listlabels = [ax.annotate(let,
                                       (self.num_students-.7,(gpacutsforav[n]+gpacutsforav[n+1])/2),
                                       verticalalignment='center')
                           for n,let in enumerate(self.gpanames)]

        self.labelpoints = [ax.annotate(self.whatgrade(a),(loc+.5,a+.5),color='r',weight='medium',horizontalalignment='center')
                     for loc,a in enumerate(self.student_list['Score'])]
        self.label_state = 2

        for n in range(self.num_students):
                whatgrade = self.whatgrade(self.student_list.iloc[n]['Score'])
                self.student_list.loc[self.student_list.index[n],'Grades'] = whatgrade

        X = np.arange(self.num_students)

        # Main plots
        self.bar = ax.bar(X+.1,self.student_list['Score'].round(),alpha=.2,color='b')
        ax.scatter(X+.5,self.student_list['Score'],color='r')

        # Show average and stddev
        totalmean = self.student_list['Score'].mean()
        totalstd = self.student_list['Score'].std()
        ofsetbig = offset_copy(ax.transData,x=-25,units='dots')
        ofsetsm = offset_copy(ax.transData,x=-20,units='dots')
        ax.annotate("",
                    xy=(0,totalmean),
                    xytext=(0,totalmean),
                    xycoords=ax.transData,
                    textcoords=ofsetbig,
                    annotation_clip=False,
                    arrowprops=dict(arrowstyle="->",color='g'),
                    )
        ax.annotate("",
                    xy=(0,totalmean+totalstd),
                    xytext=(0,totalmean+totalstd),
                    xycoords=ax.transData,
                    textcoords=ofsetsm,
                    annotation_clip=False,
                    arrowprops=dict(arrowstyle="->",color='g',alpha=.8),
                    )
        ax.annotate("",
                    xy=(0,totalmean-totalstd),
                    xytext=(0,totalmean-totalstd),
                    xycoords=ax.transData,
                    textcoords=ofsetsm,
                    annotation_clip=False,
                    arrowprops=dict(arrowstyle="->",color='g',alpha=.8),
                    )

        # Title
        ax.set_title('Mean: {:.2f}, Median: {:.2f}, Stddev: {:.2f}'.format(totalmean, np.median(self.student_list['Score']),totalstd))

        # Label on the bottom
        self.lowlab = ax.text(.5, -0.01,
                        str(self),
                        horizontalalignment='center',
                        verticalalignment='top',
                        transform = ax.transAxes)

        self.lowlab.set_color(('g' if 2.95 < self.check() < 3.05 else 'r'))

        changer = LineChanger(self)
        changer.connect(fig, ax)

        togglestepax = plt.axes([0.89, 0.05, 0.09, 0.075])
        togglestep = Button(togglestepax, 'Toggle\nstepping')
        togglestep.on_clicked(changer.togglestepping)

        togglelabelax = plt.axes([0.89, 0.15, 0.09, 0.075])
        togglelabel = Button(togglelabelax, 'Toggle\nlabels')
        togglelabel.on_clicked(self._togglelabels)

        savecutsax = plt.axes([0.89, 0.25, 0.09, 0.075])
        savecuts = Button(savecutsax, 'Save Cuts')
        savecuts.on_clicked(self._savecuts)

        saveimportax = plt.axes([0.78, 0.35, 0.20, 0.075])
        saveimport = Button(saveimportax, 'Save Registrar import file')
        saveimport.on_clicked(self._saveimport)

        loadcutsax = plt.axes([0.78, 0.25, 0.09, 0.075])
        loadcuts = Button(loadcutsax, 'Load cuts')
        loadcuts.on_clicked(self._loadcuts)

        savegradessax = plt.axes([0.78, 0.15, 0.09, 0.075])
        savegrades = Button(savegradessax, 'Save Grades')
        savegrades.on_clicked(self._savegrades)

        self.histax = plt.axes([0.78, 0.50, 0.2, 0.4])
        self.sideplot = self.histax.bar(np.arange(len(self.gpanames))+.1,self.hist())
        self.histax.set_xbound(lower=0, upper=len(self.gpanames))
        self.histax.set_xticks(np.arange(1,len(self.gpanames)+1)-.5)
        self.histax.set_xticklabels(self.gpanames)
        self.histax.set_ybound(upper=max(self.hist())+.5)
        self._colorbars()

        plt.show(block=True)

    def _savegrades(self, event=None):
        sorted_students = self.student_list.sort(['Last','First'])
        print(sorted_students)
        root = Tk()
        root.withdraw()
        csvfile = asksaveasfile(mode='w',defaultextension='.csv',title='Choose a file to save grades to')
        root.destroy()
        if csvfile:

            sorted_students.to_csv(csvfile)

    def _savecuts(self, event=None):
        root = Tk()
        root.withdraw()
        csvfile = asksaveasfile(mode='w',defaultextension='.csv',title='Choose a file to save cuts to')
        root.destroy()
        if csvfile:
            pd.DataFrame(self.gpacuts).to_csv(csvfile)

    def _saveimport(self, event=None):
        root = Tk()
        root.withdraw()
        csvfile = asksaveasfile(mode='w',defaultextension='.csv',title='Choose a file to save registrar import to')
        root.destroy()
        if csvfile:
            sorted_students = self.student_list.sort(['Last','First'])
            finalgrades = pd.DataFrame()
            finalgrades['Name'] = sorted_students['Last'] + ', ' + sorted_students['First']
            finalgrades['Grade'] = sorted_students['Grades']
            finalgrades['Absences'] = ''
            finalgrades['Remarks'] = ''
            finalgrades['Unique'] = sorted_students['Class']
            finalgrades.to_csv(csvfile,sep='\t',index_label='EID',encoding='utf-8')

    def _loadcuts(self, event=None):
        filetypes = [
            ('Cuts file','*.csv'),
            ('Allfiles','*'),
            ]
        if platform.system() != 'Windows':
            filetypes.append(filetypes.pop(0)) # Reorder so the all gradefiles is selected first

        root = Tk()
        root.withdraw()
        csvfile = askopenfilename(filetypes=filetypes, title='Choose a file to load cuts from')
        root.destroy()

        if csvfile:
            cuts = pd.DataFrame.from_csv(csvfile).values.flatten()
            for i in range(len(cuts)):
                self._change(i,cuts[i])

    def _togglelabels(self,event=None):
        self.label_state = (self.label_state + 1) % 3
        for n, label in enumerate(self.labelpoints):
            label.set_visible(self.label_state != 0)
            if self.label_state != 0:
                label.set_text(self.student_list.iloc[n]['First'] + ' ' + self.student_list.iloc[n]['Last'][0] + '.'
                               if self.label_state == 1 else self.whatgrade(self.student_list.iloc[n]['Score']))

    def _updatesideplot(self):
        for bar,hi in zip(self.sideplot,self.hist()):
            bar.set_height(hi)
        self.histax.set_ybound(upper=max(self.hist())+.5)

    def _colorbars(self):
        for n,bar in enumerate(self.bar):
            if self.whatgrade(self.student_list.iloc[n]['Score']) == self.whatgrade(self.student_list['Score'].round()[n]):
                bar.set_color('b')
            else:
                bar.set_color('r')

    def _change(self,linenum,changeto):
        if self.gpacutsfull[linenum] < changeto < self.gpacutsfull[linenum+2] and self.gpacutsfull[linenum+1] != changeto:
            self.gpacuts[linenum] = changeto
            self.listlines[linenum].set_ydata([changeto, changeto])
            for n,label in enumerate(self.labelpoints):
                whatgrade = self.whatgrade(self.student_list.iloc[n]['Score'])
                if self.label_state == 2:
                    label.set_text(whatgrade)
                self.student_list.loc[self.student_list.index[n],'Grades'] = whatgrade
            self.lowlab.set_text(str(self))

            gpacutsforav = np.append(self.min,np.append(self.gpacuts,self.max))
            self.listlabels[linenum].xyann = (self.num_students-.7,(gpacutsforav[linenum]+gpacutsforav[linenum+1])/2)
            self.listlabels[linenum+1].xyann = (self.num_students-.7,(gpacutsforav[linenum+1]+gpacutsforav[linenum+2])/2)
            self.lowlab.set_color(('g' if 2.95 < self.check() < 3.05 else 'r'))
            self._colorbars()
            self._updatesideplot()
            return True
        else:
            return False


class LineChanger(object):
    'This handles moving lines by dragging'
    def __init__(self,cutinst):
        self.cuts = cutinst
        self.pressed = False
        self.curline = None
        self.stepping = True

    def on_press(self,event):
        try:
            self.curline = closest(self.cuts.gpacuts,event.ydata)
            self.pressed = True
        except TypeError:
            pass

    def on_release(self,event):
        self.pressed = False
        self.curline = None

    def on_motion(self,event):
        if self.pressed and event.inaxes == self.ax:
            newval = (np.round(event.ydata-.5)+.5 if self.stepping else event.ydata)
            if self.cuts._change(self.curline,newval):
                self.fig.canvas.draw()

    def togglestepping(self, event):
        self.stepping = not self.stepping

    def connect(self,figure,ax):
        'Connect to figure'
        self.fig = figure
        self.ax = ax
        self.cidpress = figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def disconnect(self):
        'Disconnect all the stored connection ids'
        self.rect.figure.canvas.mpl_disconnect(self.cidpress)
        self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
        self.rect.figure.canvas.mpl_disconnect(self.cidmotion)


def abovewhich(arr,val):
    listoflocs = np.append(np.where(arr>val)[0]-1,-1)
    return listoflocs[0]


def closest(arr,val):
    dist = np.abs(arr-val)
    return np.where(dist==min(dist))[0][0]


def readcsv(name):
    'Canvas only'
    print("Reading:", name)
    students = pd.read_csv(name, index_col=3, skiprows=[1]) # Making some assumptions about the Canvas format
    students['Student']
    names = students['Student'].str.title().str.split(', ').apply(pd.Series)

    student_list = pd.DataFrame()
    student_list['First'] = names[1]
    student_list['Last'] = names[0]
    student_list['Score'] = students['Final Score']
    classes = students['Section'].str.extract(r'(\d{5})')
    try:
        student_list['Class'] = classes.apply(int)  # This fails on older pandas version (works on 0.15)
    except ValueError:
        student_list['Class'] = students['Section']
    student_list['Grades'] = ''

    return student_list


def predict_cuts(arr):
    av = arr.mean()
    std = arr.std()
    mini = std*.15
    std = max(std,3)
    mini = max(mini,1)
    ab, bc, cd, df = av+std*.5, av-std*.5, av-std*1.5, av-std*2.5
    return np.array([df,df+mini,cd-mini,cd,cd+mini,bc-mini,bc,bc+mini,ab-mini,ab,ab+mini])


def ask_filenames():
    filetypes = [
            ('Allfiles','*'),
            ('Canvas grade file','*.csv'),
            ]
    if platform.system() != 'Windows':
        filetypes.append(filetypes.pop(0)) # Reorder so the all gradefiles is selected first

    root = Tk()
    root.withdraw()
    filenames = askopenfilenames(filetypes=filetypes,
                             title='Select a file or files to open')
    root.destroy()

    # Fix for broken Windows Tk
    if isinstance(filenames,string_types):
        filenames_extra = re.findall('\{(.*?)\}',filenames)
        filenames = re.sub('\{(.*?)\}','',filenames)
        filenames = filenames.split() + filenames_extra

    return filenames



if __name__ == '__main__':
    main()

def main():
    process(sys.argv[1:])


def process(filenames=()):
    if not filenames:
        filenames = ask_filenames()

    if filenames:
        student_list = pd.concat(readcsv(name) for name in filenames)
        cuts = Cutoffs(student_list)
        cuts.plot()
