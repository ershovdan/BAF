import os
import datetime
import json


def init():
    def AddToInitLog(text):   # add text to log of logger init
        with open('../logs/init_log.log', 'a') as file:
            file.write(str(text) + '\n')


    with open('../logs/init_log.log', 'w') as file:  # create clean init_log.log
        file.write('')
    os.system('sudo chmod -R 777 ../logs/')

    time = datetime.datetime.today()  # fix time
    time_str = str(datetime.datetime.today().date()) + '_' + str(datetime.datetime.today().time()) # string of fixed time with _ between date and time

    AddToInitLog('This logger init log, started at ' + time_str)
    AddToInitLog('=' * 59)


    with open('../logs/main/main_from_' + time_str + '.log', 'w+') as file:
        pass
    AddToInitLog(str(datetime.datetime.today()) + ' created main_from_' + time_str + '.log')
    os.system('sudo chmod -R 777 ../logs/main/')

    with open('../logs/currency/upc_' + time_str + '.log', 'w+') as file:
        pass
    AddToInitLog(str(datetime.datetime.today()) + ' created main_from_' + time_str + '.log')
    os.system('sudo chmod -R 777 ../logs/currency/')

    try:
        open('../logs/main/main.journal', 'r')
        AddToInitLog(str(datetime.datetime.today()) + ' main journal checked')
    except:
        with open('../logs/main/main.journal', 'w+') as file:
            pass
        AddToInitLog(str(datetime.datetime.today()) + ' main journal not found, creating it')

    with open('../logs/use.json', 'w') as file:
        dict = {
            'main': 'main_from_' + time_str + '.log',
            'upc': 'upc_' + time_str + '.log'
        }

        file.write(json.dumps(dict))


    delta_time = (datetime.datetime.today() - time).microseconds * 0.001
    AddToInitLog(str(datetime.datetime.today()) + ' completed at ' + str(delta_time) + ' milliseconds') # completed




