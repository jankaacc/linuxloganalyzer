
import argparse
import getpass
import re
import yaml

from crontab import CronTab
from os import listdir, getcwd, popen
from os.path import isfile, join
from time import sleep

import sys

print(sys.executable)

class LogAnalyzer:
    """
    class based log analyzer
    """

    def __init__(self, args):
        self.filename = args.file_name
        self.text = ''
        with open(self.filename, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
            if args.monitored_log_dirs:
                self.monitored_dirs = args.monitored_log_dirs
            else:
                self.monitored_dirs = cfg['monitored_log_dirs'].split()
            if args.list_log_files:
                self.list_log_files = args.list_log_files
                print(self.list_log_files)
            else:
                self.list_log_files = cfg['list_log_files'].split()
            if args.time_interval:
                self.time_interval = args.time_interval
            else:
                self.time_interval = cfg['time_interval']
            if args.search_patterns:
                self.search_patterns = args.search_patterns
            else:
                self.search_patterns = cfg['search_patterns']
            if args.output_location:
                self.output_location = args.output_location
            else:
                self.output_location = cfg['output_location']

    def __open_listed_files(self):
        for file in self.list_log_files:
            with open(file, 'r') as f:
                text = f.read()
                new_text = ['{} : {}'.format(file, line) for line in text.splitlines()]
                new_text = '\n'.join(new_text)
                self.text += new_text
                # print(self.text)

    def __open_listed_dirs(self):
        paths = []
        for dir in self.monitored_dirs:
            onlyfiles = [f for f in listdir(dir) if isfile(join(dir, f))]
            for file in onlyfiles:
                paths.append(join(dir, file))
        for path in paths:
            try:
                with open(path,'r') as f:
                    text = f.read()
                    new_text = ['{} : {}'.format(path, line) for line in text.splitlines()]
                    new_text = '\n'.join(new_text)
                    self.text += new_text
                    print("Opening file: {}".format(path))
            except:
                print("Bad File format")

    def __filter_logs(self):
        # print('{}'.format(self.search_patterns))
        pattern = re.compile(r'{}'.format(self.search_patterns))
        matches = pattern.findall(self.text)
        return matches

    def analyzer_evaluate(self):
        self.__open_listed_files()
        self.__open_listed_dirs()
        regex_matches = self.__filter_logs()
        filtered_content = '\n'.join(regex_matches)
        with open(self.output_location, 'w') as f:
            f.write(filtered_content)

    def run_repeatedly(self):

        my_cron = CronTab(user=getpass.getuser())
        found = False
        for job in my_cron:
            if job.comment == 'log_analyzer':
                job.minute.every(self.time_interval)
                my_cron.write()
                print('Cron job modified successfully')
                found = True
        if not found:
            # print(getcwd())
            job = my_cron.new(command='/usr/bin/python3.5 {}/{}'.format(getcwd(), 'linuxloganalyzer.py'), comment='log_analyzer')
            job.minute.every(self.time_interval)
            my_cron.write()
            print('Cron job created')


    def show(self):
        # print(self.time_interval.__class__)
        # print(self.monitored_dirs, self.list_log_files, self.time_interval, self.search_patterns, self.output_location)
        print(self.text)


def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-fn", "--file_name", help="name of config yaml to be read from file  eg. 'config.yaml'",
                        type=str, default="config.yaml")
    parser.add_argument("-mld", "--monitored_log_dirs", help="monitored directories", nargs='+',
                        type=str, default=None)
    parser.add_argument("-llf", "--list_log_files", help="log files to be read",  nargs='+',
                        type=str, default=None)
    parser.add_argument("-tu", "--time_interval", help="time interval to logs be checked",
                        type=str, default=None)
    parser.add_argument("-sp", "--search_patterns", help="search patterns in log files",
                        type=str, default=None)
    parser.add_argument("-ol", "--output_location", help="output_location of te searched patterns",
                        type=str, default=None)
    # Print version
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    # Parse arguments
    args = parser.parse_args()
    return args




if __name__ == '__main__':
    # Parse the arguments
    args = parseArguments()
    print(args)
    loganalyzer = LogAnalyzer(args)
    loganalyzer.analyzer_evaluate()
    loganalyzer.run_repeatedly()

