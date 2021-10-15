import datetime
import json, os


def AddToFile(file_name, text):
    with open('../logs/' + str(file_name), 'a') as file:
        file.write(str(text) + '\n')


def GetStrDate():
    time_str = str(datetime.datetime.today().date()) + '_' + str(datetime.datetime.today().time())
    return time_str


class MainLogger:
    def __init__(self):
        self.type = 'for main'

        with open('../logs/use.json', 'r') as file:
            JsonRead = json.loads(file.read())
            self.file = 'main/' + JsonRead['main']

    def info(self, text):
        AddToFile(self.file, GetStrDate() + ' ' + str(text) + '\n')

    def warn(self, text):
        AddToFile(self.file, GetStrDate() + ' Warning: ' + str(text) + '\n')

    def error(self, text):
        AddToFile(self.file, GetStrDate() + ' Error: ' + str(text) + '\n')

    def fatal(self, text):
        AddToFile(self.file, GetStrDate() + ' Fatal: ' + str(text) + '\n')


class Upc:
    def __init__(self):
        self.type = 'for upc'

        with open('../logs/use.json', 'r') as file:
            JsonRead = json.loads(file.read())
            self.file = 'currency/' + JsonRead['upc']

    def info(self, text):
        AddToFile(self.file, GetStrDate() + ' ' + str(text) + '\n')

    def warn(self, text):
        AddToFile(self.file, GetStrDate() + ' Warning: ' + str(text) + '\n')

    def error(self, text):
        AddToFile(self.file, GetStrDate() + ' Error: ' + str(text) + '\n')

    def fatal(self, text):
        AddToFile(self.file, GetStrDate() + ' Fatal: ' + str(text) + '\n')

