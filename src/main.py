'''
    Welcome to Bourne Again Ferrum core.
    ershovdan, 2021
'''


import threading
import time
import psycopg2
from psycopg2 import Error
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
import pathlib
import handlers.operation_handler as OperationHandler
import loggers.logger_init as logger_init
from loggers.logger import MainLogger
import os
import handlers.currency as CurrencyHandler


logger_init.init() # initialization log initializer


def GetStrDate(): # time before core start
    time_str = str(datetime.datetime.today().date()) + '_' + str(datetime.datetime.today().time())
    return time_str

MAIN_DIR_PATH = str(pathlib.Path(__file__).parent.resolve().parent.resolve()) # finding main dir

MainLogger().info('core started') # record main log

with open(MAIN_DIR_PATH + '/src/cfg/run', 'w') as file: # run status "true"
    file.write('"true"')

with open(MAIN_DIR_PATH + '/src/logs/main/main.journal', 'a') as file: # record to journal
    file.write(GetStrDate() + ' core started\n')

with open(MAIN_DIR_PATH + '/src/cfg/baf_cfg.json', 'r') as CfgFile: # getting configuration
    CfgFileRead = json.loads(CfgFile.read())

for i in range(64): # annulling 64 fvm bridges (or creating if they aren't existing)
    with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main-' + str(i) + '.json', 'w+') as file:
        with open(MAIN_DIR_PATH + '/src/consts/bridges/front_validator-main.const', 'r') as const:
            ConstRead = const.read()
            file.write(ConstRead)

os.system('sudo chmod -R 777 ../bridges/') # making bridges available for all users and groups
with open(MAIN_DIR_PATH + '/src/logs/main/main.journal', 'a') as file:
    file.write(GetStrDate() + ' create fv-m bridges\n')


try:  #connect to db
    connection = psycopg2.connect(user=CfgFileRead['psql_user'], database='baf', password=CfgFileRead['psql_password'], host=CfgFileRead['psql_host'], port=CfgFileRead['psql_port'])
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    MainLogger().info('connected to DB') # record to main log
except Exception as error: # something went wrong
    MainLogger().fatal('error due to DB') # record to main log

    with open('logs/main/main.journal', 'a') as file: # record to journal about crash
        file.write(GetStrDate() + ' core crash due to DB error\n\n')


def AddToDB(dict): # add operation (INSERT)
    cursor.execute("INSERT INTO operations (user_id, sum, tax_type, tax, type, interest, length, add_date, pay_date, regularity) VALUES ('" + dict['uid'] + "', '" + dict['s'] + "', '" + dict['tt'] + "', '" + dict['t'] + "',  '" + dict['type'] + "',  '" + dict['i'] + "',  '" + dict['l'] + "',  '" + dict['ad'] + "', '" + dict['pd'] + "', '" + dict['r'] + "');") # add to operations table
    MainLogger().info('ADD, user_id=' + str(dict['uid'])) # record main log


def GetUserIDByUserName(username): # get user by user id
    cursor.execute("SELECT user_id FROM users WHERE username = '" + username + "'")
    try:
        uid = cursor.fetchone()[0]
        MainLogger().info('GET USER successful, uid=' + str(uid)) # record main log
        return uid
    except TypeError:
        MainLogger().info('GET USER not successful') # record main log
        return 'null'


def AddUser(dict): # add new user
    username = next(iter(dict))
    currency = dict[username][0]
    first_day = dict[username][1]

    cursor.execute("INSERT INTO  users (username, first_day_of_week, is_active) VALUES ('" + username + "', '" + first_day + "', '" + "t" + "') ON CONFLICT DO NOTHING;") # if user already exist do nothing (add to users table)

    cursor.execute("SELECT user_id FROM users WHERE username = '" + username + "';")
    user_id = str(cursor.fetchone()[0])

    cursor.execute("INSERT INTO currency (user_id, currency_point, current_currency) VALUES ('" + user_id + "', '" + currency + "', '" + currency + "') ON CONFLICT DO NOTHING;") # add to currency table

    MainLogger().info('ADD USER, username=' + str(username)) # record main log


def ChangeUser(dict): # change existing user
    username = next(iter(dict))
    username_or_id = dict[username][0]
    is_active = dict[username][1]
    first_day = dict[username][2]
    new_username = dict[username][3]

    if username_or_id == 'un': # by username
        if is_active != '':
            try:
                cursor.execute("SELECT username FROM users WHERE username = '" + username + "';") # if user is existing
                cursor.execute("UPDATE users SET is_active = '" + is_active + "' WHERE username = '" + username + "';") # change is active status
            except:
                pass

        if first_day != '':
            try:
                cursor.execute("SELECT username FROM users WHERE username = '" + username + "';") # if user is existing
                cursor.execute("UPDATE users SET first_day_of_week = '" + first_day + "' WHERE username = '" + username + "';") # change first day
            except:
                pass

        if new_username != '':
            try:
                cursor.execute("SELECT username FROM users WHERE username = '" + username + "';") # if user is existing
                cursor.execute("UPDATE users SET username = '" + new_username + "' WHERE username = '" + username + "';") # change username
            except:
                pass

        MainLogger().info('CHANGE_USER by username, new_username=' + new_username) # record main log

    if username_or_id == 'id': # by user id
        if is_active != '':
            try:
                cursor.execute("SELECT username FROM users WHERE user_id = '" + username + "';") # if user is existing
                cursor.execute("UPDATE users SET is_active = '" + is_active + "' WHERE user_id = " + username + ";") # change is active status
            except:
                pass

        if first_day != '':
            try:
                cursor.execute("SELECT username FROM users WHERE user_id = '" + username + "';") # if user is existing
                cursor.execute("UPDATE users SET first_day_of_week = '" + first_day + "' WHERE user_id = " + username + ";") # change first day
            except:
                pass

        if new_username != '':
            try:
                cursor.execute("SELECT username FROM users WHERE user_id = '" + username + "';") # if user is existing
                cursor.execute("UPDATE users SET username = '" + new_username + "' WHERE user_id = " + username + ";") # change username
            except:
                pass

        MainLogger().info('CHANGE_USER by username, new_username=' + new_username) # record main log


def Change(dict): # change operation
    oid = ''
    oid_or_uid = ''

    try:
        oid_or_uid = dict['uid']
        oid_or_uid = 'uid'
    except:
        oid = dict['oid']

    if oid_or_uid == 'uid': # getting operation id by user id
        try:
            cursor.execute("SELECT operation_id FROM operations WHERE sum = '" + dict['s'] + "' and tax = '" + dict['t'] + "' and tax_type = '" + dict['tt'] + "' and interest = '" + dict['i'] + "' and regularity = '" + dict['r'] + "' and length = '" + dict['l'] + "' and type = '" + dict['type'] + "' and add_date = '" + dict['ad'] + "' and pay_date = '" + dict['pd'] + "';")
            oid = str(cursor.fetchone()[0])
        except:
            pass

    try: # updating sum
        if dict['ns'] != '':
            cursor.execute("UPDATE operations SET sum = '" + dict['ns'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass

    try: # updating tax
        if dict['nt'] != '':
            cursor.execute("UPDATE operations SET tax = '" + dict['nt'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass

    try: # updating tax type
        if dict['ntt'] != '':
            cursor.execute("UPDATE operations SET tax_type = '" + dict['ntt'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass

    try: # updating regularity
        if dict['nr'] != '':
            cursor.execute("UPDATE operations SET regularity = '" + dict['nr'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass

    try: # updating interest
        if dict['ni'] != '':
            cursor.execute("UPDATE operations SET interest = '" + dict['ni'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass

    try: # updating length
        if dict['nl'] != '':
            cursor.execute("UPDATE operations SET length = '" + dict['nl'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass

    try: # updating add_date
        if dict['nad'] != '':
            cursor.execute("UPDATE operations SET add_date = '" + dict['nad'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass

    try: # updating pay_date
        if dict['npd'] != '':
            cursor.execute("UPDATE operations SET pay_date = '" + dict['npd'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass

    MainLogger().info('CHANGE, operation_id=' + str(oid)) # record main log


def Get(dict): # get operation
    type = dict['gt']

    if type == 'oid': # operation id
        oid = 'null'

        try: # finding operation id
            cursor.execute("SELECT operation_id FROM operations WHERE sum = '" + dict['s'] + "' and tax = '" + dict['t'] + "' and tax_type = '" + dict['tt'] + "' and interest = '" + dict['i'] + "' and regularity = '" + dict['r'] + "' and length = '" + dict['l'] + "' and type = '" + dict['type'] + "' and add_date = '" + dict['ad'] + "' and pay_date = '" + dict['pd'] + "' and user_id = '" + dict['uid'] + "';")
            oid = str(cursor.fetchone()[0])
        except:
            pass

        MainLogger().info('GET operation id, oid=' + str(oid))  # record main log
        return oid

    elif type == 'afd': # all for date
        cursor.execute("SELECT * FROM operations WHERE user_id = '" + dict['uid'] + "';") # finding all operations by user id
        select = cursor.fetchall()

        SelectList = []

        user_id = dict['uid']

        cursor.execute("SELECT * FROM currency WHERE user_id = '" + dict['uid'] + "';") # currency of user
        select_cur = cursor.fetchall()

        cur_point = select_cur[0][1][0:3]
        cur_currency = select_cur[0][2][0:3]

        DictDate = date(int(dict['d'][6:10]), int(dict['d'][3:5]), int(dict['d'][0:2]))

        CurHandler = CurrencyHandler.Currency()

        for i in select: # selecting operations with needed date
            SubList = []

            for j in i:
                SubList.append(j)

            DateSubList = date(int(SubList[9][6:10]), int(SubList[9][3:5]), int(SubList[9][0:2]))

            if DateSubList <= DictDate:
                if (str(SubList[11][0]) == 'm') and (str(DictDate.day) == str(SubList[10])) and (DictDate <= DateSubList + relativedelta(months=SubList[8])): # monthly regularity
                    if SubList[6][0:2] == 'an':
                        SelectList.append(CurHandler.convert(cur_point, cur_currency, OperationHandler.Tax().simple(OperationHandler.Loan().mannuity(int(SubList[3]), int(SubList[7]), int(SubList[8]), SubList[9], dict['d']), SubList[5], SubList[4])))
                    elif SubList[6][0:2] == 'dn':
                        SelectList.append(CurHandler.convert(cur_point, cur_currency, OperationHandler.Tax().simple(OperationHandler.Loan().mdifferentiated(int(SubList[3]), int(SubList[7]), int(SubList[8]), SubList[9], dict['d']), SubList[5], SubList[4])))
                    elif SubList[6][0:2] == 'si':
                        if OperationHandler.Income().simple(int(SubList[3]), SubList[9], dict['d']) != float('inf'):
                            SelectList.append(CurHandler.convert(cur_point, cur_currency, OperationHandler.Tax().simple(OperationHandler.Income().simple(int(SubList[3]), SubList[9], dict['d']), SubList[5], SubList[4])))
                    elif SubList[6][0:2] == 'se':
                        if OperationHandler.Expense().simple(int(SubList[3]), SubList[9], dict['d']) != float('inf'):
                            SelectList.append(CurHandler.convert(cur_point, cur_currency, OperationHandler.Tax().simple(OperationHandler.Expense().simple(int(SubList[3]), SubList[9], dict['d']), SubList[5], SubList[4])))
                    elif SubList[6][0:2] == 'ri':
                        SelectList.append(CurHandler.convert(cur_point, cur_currency, OperationHandler.Tax().simple(OperationHandler.Income().regular(int(SubList[3]), SubList[9], dict['d']), SubList[5], SubList[4])))
                    elif SubList[6][0:2] == 're':
                        SelectList.append(CurHandler.convert(cur_point, cur_currency, OperationHandler.Tax().simple(OperationHandler.Expense().regular(int(SubList[3]), SubList[9], dict['d']), SubList[5], SubList[4])))
                    elif SubList[6][0:1] == 'd':
                        SelectList.append(CurHandler.convert(cur_point, cur_currency, OperationHandler.Tax().simple(OperationHandler.Deposit().classic(int(SubList[3]), SubList[9], dict['d'], int(SubList[7])), SubList[5], SubList[4])))

                elif (str(SubList[11][0]) == 'd') and (DictDate <= DateSubList + relativedelta(days=SubList[8])): # daily regularity
                    if SubList[6][0:2] == 'an':
                        SelectList.append(CurHandler.convert(cur_point, cur_currency, OperationHandler.Tax().simple(OperationHandler.Loan().dannuity(int(SubList[3]), int(SubList[7]), int(SubList[8]), SubList[9], dict['d']), SubList[5], SubList[4])))
                    elif SubList[6][0:2] == 'dn':
                        SelectList.append(CurHandler.convert(cur_point, cur_currency, OperationHandler.Tax().simple(OperationHandler.Loan().ddifferentiated(int(SubList[3]), int(SubList[7]), int(SubList[8]), SubList[9], dict['d']), SubList[5], SubList[4])))
                    elif SubList[6][0:2] == 'si':
                        if OperationHandler.Income().simple(int(SubList[3]), SubList[9], dict['d']) != float('inf'):
                            SelectList.append(CurHandler.convert(cur_point, cur_currency, OperationHandler.Tax().simple(OperationHandler.Income().simple(int(SubList[3]), SubList[9], dict['d']), SubList[5], SubList[4])))
                    elif SubList[6][0:2] == 'se':
                        if OperationHandler.Expense().simple(int(SubList[3]), SubList[9], dict['d']) != float('inf'):
                            SelectList.append(CurHandler.convert(cur_point, cur_currency, OperationHandler.Tax().simple(OperationHandler.Expense().simple(int(SubList[3]), SubList[9], dict['d']), SubList[5], SubList[4])))
                    elif SubList[6][0:2] == 'ri':
                        SelectList.append(CurHandler.convert(cur_point, cur_currency, OperationHandler.Tax().simple(OperationHandler.Income().regular(int(SubList[3]), SubList[9], dict['d']), SubList[5], SubList[4])))
                    elif SubList[6][0:2] == 're':
                        SelectList.append(CurHandler.convert(cur_point, cur_currency, OperationHandler.Tax().simple(OperationHandler.Expense().regular(int(SubList[3]), SubList[9], dict['d']), SubList[5], SubList[4])))
                elif (str(SubList[11][0]) == 'o') and (DictDate == DateSubList): # once regularity
                    pass

        MainLogger().info('GET all for date, user_id=' + str(dict['uid'])) # record main log
        return str(SelectList)


def Delete(dict): # delete operation
    cursor.execute("DELETE FROM operations WHERE operation_id = '" + dict['oid'] + "';") # deleting operations
    MainLogger().info('DELETE, oid=' + str(dict['oid'])) # record main log


def Currency(dict): # currency settings
    type = dict['ct']
    user_id = dict['uid']

    with open('../cfg/currency_rate.json', 'r') as file:
        FileRead = file.read()
        JsonRead = json.loads(FileRead)

    if type == 'cc': # current currency
        cursor.execute("UPDATE currency SET current_currency = '" + dict['nc'] + "' WHERE user_id = '" + user_id + "';") # updating current currency
        MainLogger().info('CURRENCY, current currency uid=' + str(user_id))  # record main log
    elif type == 'cp': # currency point
        cursor.execute("SELECT currency_point FROM currency WHERE user_id = '" + dict['uid'] + "';")
        select_cur = cursor.fetchall()

        old_currency_point = select_cur[0][0][0:3]

        cursor.execute("UPDATE currency SET currency_point = '" + dict['nc'] + "' WHERE user_id = '" + user_id + "';") # updating currency point

        cursor.execute("SELECT * FROM operations WHERE user_id = '" + user_id + "';")
        select_cur = cursor.fetchall()

        for i in select_cur: # updating all sums for user
            sum = i[3]

            operation_id = i[0]

            new_sum = round(sum / JsonRead[str(old_currency_point)] * JsonRead[dict['nc']], 2)

            cursor.execute("UPDATE operations SET sum = '" + str(new_sum) + "' WHERE operation_id = '" + str(operation_id) + "';")

        MainLogger().info('CURRENCY, currency point uid=' + str(user_id))  # record main log


with open(MAIN_DIR_PATH + '/src/logs/main/main.journal', 'a') as file: # record to journal
    file.write(GetStrDate() + ' core init completed, entry central timer\n\n')


def CentralTimer():
    WorkStatus = True
    FrontValidatorMainIsReady = False

    with open(MAIN_DIR_PATH + '/src/cfg/run', 'r') as file: # checking run status
        StatusRead = file.read()
        if StatusRead == '"false"\n':
            WorkStatus = False

    for i in range(64): # checking all fvm bridges
        with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main-' + str(i) + '.json', 'r') as FrontValidatorJSON:
            try:
                DataFromFrontValidator = json.loads(FrontValidatorJSON.read())
                FrontValidatorMainIsReady = True
            except:
                FrontValidatorMainIsReady = False

            if FrontValidatorMainIsReady == True:
                if DataFromFrontValidator['add-in'] != []: # add
                    AddToDB(DataFromFrontValidator['add-in'][0])
                    data = DataFromFrontValidator['add-in'][0]
                    DataFromFrontValidator['add-in'].pop(0)

                if DataFromFrontValidator['usr-get-in'] != []: #get user
                    GetUserIDByUserName(DataFromFrontValidator['usr-get-in'][0])
                    DataFromFrontValidator['usr-get-out'][DataFromFrontValidator['usr-get-in'][0]] = GetUserIDByUserName(DataFromFrontValidator['usr-get-in'][0])
                    DataFromFrontValidator['usr-get-in'].pop(0)

                if DataFromFrontValidator['usr-add-in'] != []: # add user
                    AddUser(DataFromFrontValidator['usr-add-in'][0])
                    data = DataFromFrontValidator['usr-add-in'][0]
                    DataFromFrontValidator['usr-add-in'].pop(0)

                if DataFromFrontValidator['usr-chg-in'] != []: # change user
                    ChangeUser(DataFromFrontValidator['usr-chg-in'][0])
                    data = DataFromFrontValidator['usr-chg-in'][0]
                    DataFromFrontValidator['usr-chg-in'].pop(0)

                if DataFromFrontValidator['chg-in'] != []: # change
                    Change(DataFromFrontValidator['chg-in'][0])
                    data = DataFromFrontValidator['chg-in'][0]
                    DataFromFrontValidator['chg-in'].pop(0)

                if DataFromFrontValidator['get-oid-in'] != []: # get operation id
                    DataFromFrontValidator['get-oid-out'][DataFromFrontValidator['get-oid-in'][0]['code']] = Get(DataFromFrontValidator['get-oid-in'][0])
                    DataFromFrontValidator['get-oid-in'].pop(0)

                if DataFromFrontValidator['get-afd-in'] != []: # get all for
                    DataFromFrontValidator['get-afd-out'][DataFromFrontValidator['get-afd-in'][0]['code']] = Get(DataFromFrontValidator['get-afd-in'][0])
                    DataFromFrontValidator['get-afd-in'].pop(0)

                if DataFromFrontValidator['del-in'] != []: # delete
                    Delete(DataFromFrontValidator['del-in'][0])
                    DataFromFrontValidator['del-in'].pop(0)

                if DataFromFrontValidator['cur-in'] != []: # currency
                    Currency(DataFromFrontValidator['cur-in'][0])
                    DataFromFrontValidator['cur-in'].pop(0)

                with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main-' + str(i) + '.json', 'w') as FrontValidatorJSON: # update fvm bridges
                    FrontValidatorJSON.write(json.dumps(DataFromFrontValidator))

    if WorkStatus == True: # status for run
        threading.Timer(interval=0.01, function=CentralTimer).start()
    else: # status not for run
        MainLogger().info('main stopped') # record main log

        with open(MAIN_DIR_PATH + '/src/logs/main/main.journal', 'a') as file:  # record to journal
            file.write(GetStrDate() + ' core stopped\n')

        exit()


threading.Timer(interval=0.01, function=CentralTimer).start() # starting central timer

