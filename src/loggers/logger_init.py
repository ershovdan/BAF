import os
import datetime
import json


def init(): # main logger initialization
    def AddToInitLog(text): # add text to log of logger init
        with open('../logs/init_log.log', 'a') as file:
            file.write(str(text) + '\n')


    with open('../logs/init_log.log', 'w') as file:  # create clean init_log.log
        file.write('')
    os.system('sudo chmod -R 777 ../logs/') # making logs available for all users and groups

    time = datetime.datetime.today()  # fix time
    time_str = str(datetime.datetime.today().date()) + '_' + str(datetime.datetime.today().time()) # string of fixed time with _ between date and time

    AddToInitLog('This logger init log, started at ' + time_str) # record to init_log.log
    AddToInitLog('=' * 59) # record to init_log.log

    with open('../logs/main/main_from_' + time_str + '.log', 'w+') as file: # creating new main log
        pass
    AddToInitLog(str(datetime.datetime.today()) + ' created main_from_' + time_str + '.log') # record to init_log.log
    os.system('sudo chmod -R 777 ../logs/main/') # making main logs available for all users and groups

    with open('../logs/currency/upc_' + time_str + '.log', 'w+') as file: # creating new currency rate updater log
        pass
    AddToInitLog(str(datetime.datetime.today()) + ' created main_from_' + time_str + '.log') # record to init_log.log
    os.system('sudo chmod -R 777 ../logs/currency/') # making currency rate updater logs available for all users and groups

    try: # checking journal for existence
        open('../logs/main/main.journal', 'r')
        AddToInitLog(str(datetime.datetime.today()) + ' main journal checked') # record to init_log.log
    except: # creating journal
        with open('../logs/main/main.journal', 'w+') as file:
            pass
        AddToInitLog(str(datetime.datetime.today()) + ' main journal not found, creating it') # record to init_log.log

    with open('../logs/use.json', 'w') as file: # writing used log names
        dict = {
            'main': 'main_from_' + time_str + '.log',
            'upc': 'upc_' + time_str + '.log'
        }

        file.write(json.dumps(dict))

    delta_time = (datetime.datetime.today() - time).microseconds * 0.001 # time between start and finish of log initialization
    AddToInitLog(str(datetime.datetime.today()) + ' completed at ' + str(delta_time) + ' milliseconds') # record to init_log.log
