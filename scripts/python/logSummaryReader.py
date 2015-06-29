#!/bin/python

# file: logSummaryReader.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Collection of classes and functions to parse a given PETSc log summary.


import os
import re
import collections

import numpy
from matplotlib import pyplot

# load matplotlib style sheet
pyplot.style.use('./style/style_PetIBM.mplstyle')


class Phase(object):
    """Contains info related to a phase of an event."""
    def __init__(self, info):
        """Parses the info related to a phase.
        
        Parameters
        ----------
        info: list(str)
            Data related to the phase.
        """
        self.count = int(info[0])
        self.max_time = float(info[2])
        self.ratio_time = float(info[3])
        self.max_flops = float(info[4])
        self.ratio_flops = float(info[5])


class Event(object):
    """Contains info related to an event."""
    def __init__(self, info):
        """Parses general info about the event.
        
        Parameters
        ----------
        info: list(str)
            Data about the general info of the event.
        """
        self.index = int(info[0])
        self.name = info[1].strip()
        info = info[2].split()
        self.time = float(info[0])
        self.percent = float(info[1][:-1])
        self.flops = float(info[2])
    
    def parse_phases(self, info):
        """Gets info about all phases that occur during the event.
        
        Parameters
        ----------
        info: list(str)
            Data about all phases that occur during the event.
        """
        self.phases = collections.OrderedDict()
        for data in info:
            name = data[0]
            self.phases[name] = Phase(data[1:])
            
    def print_phase_names(self):
        """Prints the list of phases that occur during the event."""
        print('List of phases for event {}:'.format(self.name))
        for name in self.phases.keys():
            print('\t{}'.format(name))


class LogSummary(object):
    """Contains info about what is happening during a PetIBM run."""
    def __init__(self, file_path):
        """Parses the log file to get the execution time, 
        the number of processes involved,
        and info about the various event that occur during the run.
        
        Parameters
        ----------
        file_path: str
            Path of the the logging file.
        """
        self.file_path = file_path
        self.load()
        self.get_nprocs()
        self.get_execution_time()
        self.get_events()
    
    def load(self):
        """Loads the content of the file into a list."""
        with open(self.file_path, 'r') as infile:
            self.lines = infile.readlines()
    
    def get_nprocs(self):
        """Finds the number of processes involved."""
        pattern = 'processor'
        for line in self.lines:
            match = re.search(pattern, line)
            if match:
                data = line.split()
                self.nprocs = int([n for i, n in enumerate(data[:-1])
                                   if pattern in data[i+1]][0])
                break
                
    def get_execution_time(self):
        """Finds the execution-time of the simulation."""
        pattern = 'Time '
        for line in self.lines:
            match = re.search(pattern, line)
            if match:
                data = line.split()
                self.execution_time = float(data[2])
                break
                
    def get_events(self):
        """Gets info about each events that occur 
        during the simulation.
        """
        # create events with general info
        start = 0
        pattern = 'Summary '
        for i, line in enumerate(self.lines[start:]):
            match = re.search(pattern, line)
            if match:
                i += 2
                line = self.lines[start+i]
                self.events = collections.OrderedDict()
                while not re.match(r'^\s*$', line):
                    info = re.split(':', re.sub(' +', ' ', line))
                    name = info[1].strip()
                    self.events[name] = Event(info)
                    i += 1
                    line = self.lines[i]
                break
        start += i
        # grab the appropriate phases section
        for name, event in self.events.iteritems():
            for i, line in enumerate(self.lines[start:]):
                if event.name in line:
                    i +=2
                    line = self.lines[start+i]
                    phases_info = []
                    while not (re.match(r'^\s*$', line) or '---' in line):
                        data = line.strip().split()
                        for k, element in enumerate(data[1:]):
                            if len(element) > 10:
                                data[k+1:k+2] = element[:10], element[10:]
                        phases_info.append(data)
                        i += 1
                        line = self.lines[start+i]
                    self.events[name].parse_phases(phases_info)
                    start += i
                    break
    
    def print_event_names(self):
        """Prints the list of events that occur during the run."""
        print('List of events for {}:'.format(self.file_path))
        for name in self.events.keys():
            print('\t{}'.format(name))


class Series(object):
    def __init__(self, directory, nprocs=[]):
        self.directory = directory
        self.parse_logging_files(nprocs)
    
    def parse_logging_files(self, nprocs):
        if nprocs:
            self.logs = [LogSummary('{0}/n{1}/log_summary_n{1}.out'.format(self.directory, n)) 
                         for n in nprocs]
        else:
            self.logs = [LogSummary('{0}/{1}/log_summary_{1}.out'.format(self.directory, d)) 
                         for d in os.listdir(self.directory)
                         if os.path.isdir(d)]

def plot_execution_time(series_list, save=None):
    """Plots the excution-time versus the process count 
    for each series.
    
    Parameters
    ----------
    series_list: list(Series)
        List of series to plot.
    save: str
        Name of the .png file to be saved; default: None (does not save).
    """
    # set up figure
    fig, ax = pyplot.subplots(figsize=(8, 6))
    ax.yaxis.grid(zorder=0)
    pyplot.xlabel('process count', fontsize=16)
    pyplot.ylabel('wall-time (s)', fontsize=16)
    # get info common to all series
    nprocs = numpy.array([log.nprocs for log in series_list[0].logs])
    # plot execution time for each series
    for num, series in enumerate(series_list):
        times = [log.execution_time for log in series.logs]
        pyplot.plot(nprocs, times,
                    label='run {}'.format(num+1),
                    marker='o', zorder=10)
    # ideal scaling for last series
    pyplot.plot(nprocs, times[0]/nprocs, 
                label='ideal scaling',
                color='k', ls='--', zorder=10)
    # set plot parameters
    pyplot.legend(loc='best', fontsize=14)
    pyplot.xscale('log')
    pyplot.yscale('log')
    pyplot.xlim(0, 128);
    if save:
        pyplot.savefig('./images/{}.png'.format(save))


def plot_phases_event(logs, 
                      event_name, variable_name,
                      phase_names=[],
                      xlabel='process count', ylabel='time (s)',
                      save=None):
    """Plots info about the phases of a given event.
    
    Parameters
    ----------
    logs: list(LogSummary)
        List of parsed logging file.
    event_name: str
        Name of the event to plot.
    variable_name: str
        Name of the variable of the phase to consider.
    phase_names: list(str)
        List of phase names to consider; default [] (all phases).
    xlabel: str
        x-label; default: 'process count'.
    ylabel: str
        y-label; default: 'time (s)'.
    save: str
        name of the .png file to be save; default: None (does not save).
    """
    fig, ax = pyplot.subplots(figsize=(8, 6))
    ax.yaxis.grid(zorder=0)
    pyplot.xlabel(xlabel, fontsize=16)
    pyplot.ylabel(ylabel, fontsize=16)
    pyplot.title(event_name)
    nprocs = [log.nprocs for log in logs]
    data = collections.OrderedDict()
    index = 0
    if not phase_names:
        phase_names = logs[0].events[event_name].phases.keys()
    for name in phase_names:
        index += 1
        marker = ('o' if index <=7 else 's')
        data[name] = []
        for log in logs:
            data[name].append(getattr(log.events[event_name].phases[name],
                                      variable_name))
        pyplot.plot(nprocs, data[name],
                    label=name,
                    marker=marker, zorder=10)
    pyplot.xscale('log')
    if 'max' in variable_name:
        pyplot.yscale('log')
    pyplot.xlim(min(nprocs), max(nprocs))
    pyplot.legend(loc='best', fontsize=14, 
                  bbox_to_anchor=(1.0, 1.0), frameon=False)
    if save:
        pyplot.savefig('./images/{}.png'.format(save))


def plot_phases_event_average(series_list, 
                              event_name, variable_name,
                              phase_names=[],
                              xlabel='process count', 
                              ylabel='time (s)',
                              save=None):
    """Plots info about the phases of a given event.
    
    Parameters
    ----------
    series_list: list(Series)
        List of of series, 
        each element of a series being a parsed log file.
    event_name: str
        Name of the event to plot.
    variable_name: str
        Name of the variable of the phase to consider.
    phase_names: list(str)
        List of phase names to consider; default [] (all phases).
    xlabel: str
        x-label; default: 'process count'.
    ylabel: str
        y-label; default: 'time (s)'.
    save: str
        name of the .png file to be save; default: None (does not save).
    """
    # grab info common to all series
    series_model = series_list[0]
    nprocs = [log.nprocs for log in series_model.logs]
    if not phase_names:
        phase_names = series_model.logs[0].events[event_name].phases.keys()
    # set up fure parameters
    fig, ax = pyplot.subplots(figsize=(8, 6))
    ax.yaxis.grid(zorder=0)
    pyplot.xlabel(xlabel, fontsize=16)
    pyplot.ylabel(ylabel, fontsize=16)
    pyplot.title(event_name)
    # get data to plot
    data = collections.OrderedDict()
    index = 0
    for name in phase_names:
        index += 1
        marker = ('o' if index <=7 else 's')
        data[name] = [0]*len(series_model.logs)
        # average data over all series in list
        for series in series_list:
            for i, log in enumerate(series.logs):
                data[name][i] += getattr(log.events[event_name].phases[name],
                                         variable_name)
        data[name] = numpy.array(data[name])/len(series_list)
        # plot data
        pyplot.plot(nprocs, data[name],
                    label=name,
                    marker=marker, zorder=10)
    pyplot.xscale('log')
    pyplot.xlim(min(nprocs), max(nprocs))
    if 'max' in variable_name:
        pyplot.yscale('log')
    pyplot.legend(loc='best', fontsize=14, 
                  bbox_to_anchor=(1.0, 1.0), frameon=False)
    if save:
        pyplot.savefig('./images/{}.png'.format(save))