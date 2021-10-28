import datetime
import json, os


def AddToFile(file_name, text): # open file and write something
    with open('../logs/' + str(file_name), 'a') as file:
        file.write(str(text) + '\n')


def GetStrDate(): # get date and time
    time_str = str(datetime.datetime.today().date()) + '_' + str(datetime.datetime.today().time())
    return time_str


class MainLogger: # for main
    def __init__(self):
        self.type = 'for main'

        with open('../logs/use.json', 'r') as file: # log name from use.json
            JsonRead = json.loads(file.read())
            self.file = 'main/' + JsonRead['main']

    def info(self, text): # information
        AddToFile(self.file, GetStrDate() + ' ' + str(text) + '\n')

    def warn(self, text): # waring
        AddToFile(self.file, GetStrDate() + ' Warning: ' + str(text) + '\n')

    def error(self, text): # error
        AddToFile(self.file, GetStrDate() + ' Error: ' + str(text) + '\n')

    def fatal(self, text): # fatal error
        AddToFile(self.file, GetStrDate() + ' Fatal: ' + str(text) + '\n')


class Upc: # for currency rate updater
    def __init__(self):
        self.type = 'for upc'

        with open('../logs/use.json', 'r') as file: # log name from use.json
            JsonRead = json.loads(file.read())
            self.file = 'currency/' + JsonRead['upc']

    def info(self, text): # information
        AddToFile(self.file, GetStrDate() + ' ' + str(text) + '\n')

    def warn(self, text): # waring
        AddToFile(self.file, GetStrDate() + ' Warning: ' + str(text) + '\n')

    def error(self, text): # error
        AddToFile(self.file, GetStrDate() + ' Error: ' + str(text) + '\n')

    def fatal(self, text): # fatal error
        AddToFile(self.file, GetStrDate() + ' Fatal: ' + str(text) + '\n')
