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


logger_init.init()


def GetStrDate():
    time_str = str(datetime.datetime.today().date()) + '_' + str(datetime.datetime.today().time())
    return time_str

MAIN_DIR_PATH = str(pathlib.Path(__file__).parent.resolve().parent.resolve()) # main dir

MainLogger().info('core started')

with open(MAIN_DIR_PATH + '/src/logs/main/main.journal', 'a') as file:
    file.write(GetStrDate() + ' core started\n')

with open(MAIN_DIR_PATH + '/src/cfg/baf_cfg.json', 'r') as CfgFile:
    CfgFileRead = json.loads(CfgFile.read())

with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'w') as bridge: # set bridge from const
    with open(MAIN_DIR_PATH + '/src/consts/bridges/front_validator-main.const', 'r') as const:
        ConstRead = const.read()
        bridge.write(ConstRead)

try:  #connect to db
    connection = psycopg2.connect(user=CfgFileRead['psql_user'], database='baf', password=CfgFileRead['psql_password'], host=CfgFileRead['psql_host'], port=CfgFileRead['psql_port'])
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    MainLogger().info('connected to DB')
except Exception as error:
    print('DB error')

    MainLogger().fatal('error due to DB')

    with open('logs/main/main.journal', 'a') as file:
        file.write(GetStrDate() + ' core crash due to DB error\n\n')


def AddToDB(dict):
    cursor.execute("INSERT INTO operations (user_id, sum, tax_type, tax, type, interest, length, add_date, pay_date, regularity) VALUES ('" + dict['uid'] + "', '" + dict['s'] + "', '" + dict['tt'] + "', '" + dict['t'] + "',  '" + dict['type'] + "',  '" + dict['i'] + "',  '" + dict['l'] + "',  '" + dict['ad'] + "', '" + dict['pd'] + "', '" + dict['r'] + "');")


def GetUserIDByUserName(username):
    cursor.execute("SELECT user_id FROM users WHERE username = '" + username + "'")
    try:
        return cursor.fetchone()[0]
    except TypeError:
        return 'null'


def AddUser(dict):
    username = next(iter(dict))
    currency = dict[username][0]
    first_day = dict[username][1]

    cursor.execute("INSERT INTO  users (username, first_day_of_week, is_active) VALUES ('" + username + "', '" + first_day + "', '" + "t" + "') ON CONFLICT DO NOTHING;")

    cursor.execute("SELECT user_id FROM users WHERE username = '" + username + "';")
    user_id = str(cursor.fetchone()[0])

    cursor.execute("INSERT INTO currency (user_id, currency_point, current_currency) VALUES ('" + user_id + "', '" + currency + "', '" + currency + "') ON CONFLICT DO NOTHING;")


def ChangeUser(dict):
    username = next(iter(dict))
    username_or_id = dict[username][0]
    is_active = dict[username][1]
    first_day = dict[username][2]
    new_username = dict[username][3]

    if username_or_id == 'un':
        if is_active != '':
            try:
                cursor.execute("SELECT username FROM users WHERE username = '" + username + "';")
                cursor.execute("UPDATE users SET is_active = '" + is_active + "' WHERE username = '" + username + "';")
            except:
                pass

        if first_day != '':
            try:
                cursor.execute("SELECT username FROM users WHERE username = '" + username + "';")
                cursor.execute("UPDATE users SET first_day_of_week = '" + first_day + "' WHERE username = '" + username + "';")
            except:
                pass

        if new_username != '':
            try:
                cursor.execute("SELECT username FROM users WHERE username = '" + username + "';")
                cursor.execute("UPDATE users SET username = '" + new_username + "' WHERE username = '" + username + "';")
            except:
                pass

        MainLogger().info('CHANGE_USER by username new_username=' + new_username)

    if username_or_id == 'id':
        if is_active != '':
            try:
                cursor.execute("SELECT username FROM users WHERE user_id = '" + username + "';")
                cursor.execute("UPDATE users SET is_active = '" + is_active + "' WHERE user_id = " + username + ";")
            except:
                pass

        if first_day != '':
            try:
                cursor.execute("SELECT username FROM users WHERE user_id = '" + username + "';")
                cursor.execute("UPDATE users SET first_day_of_week = '" + first_day + "' WHERE user_id = " + username + ";")
            except:
                pass

        if new_username != '':
            try:
                cursor.execute("SELECT username FROM users WHERE user_id = '" + username + "';")
                cursor.execute("UPDATE users SET username = '" + new_username + "' WHERE user_id = " + username + ";")
            except:
                pass

        MainLogger().info('CHANGE_USER by username new_username=' + new_username)


def Change(dict):
    oid = ''
    oid_or_uid = ''

    try:
        oid_or_uid = dict['uid']
        oid_or_uid = 'uid'
    except:
        oid = dict['oid']

    if oid_or_uid == 'uid':
        try:
            cursor.execute("SELECT operation_id FROM operations WHERE sum = '" + dict['s'] + "' and tax = '" + dict['t'] + "' and tax_type = '" + dict['tt'] + "' and interest = '" + dict['i'] + "' and regularity = '" + dict['r'] + "' and length = '" + dict['l'] + "' and type = '" + dict['type'] + "' and add_date = '" + dict['ad'] + "' and pay_date = '" + dict['pd'] + "';")
            oid = str(cursor.fetchone()[0])
        except:
            pass

    try:
        if dict['ns'] != '':
            cursor.execute("UPDATE operations SET sum = '" + dict['ns'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass

    try:
        if dict['nt'] != '':
            cursor.execute("UPDATE operations SET tax = '" + dict['nt'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass

    try:
        if dict['ntt'] != '':
            cursor.execute("UPDATE operations SET tax_type = '" + dict['ntt'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass

    try:
        if dict['nr'] != '':
            cursor.execute("UPDATE operations SET regularity = '" + dict['nr'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass

    try:
        if dict['ni'] != '':
            cursor.execute("UPDATE operations SET interest = '" + dict['ni'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass

    try:
        if dict['nl'] != '':
            cursor.execute("UPDATE operations SET length = '" + dict['nl'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass

    try:
        if dict['nad'] != '':
            cursor.execute("UPDATE operations SET add_date = '" + dict['nad'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass

    try:
        if dict['npd'] != '':
            cursor.execute("UPDATE operations SET pay_date = '" + dict['npd'] + "' WHERE operation_id = '" + oid + "';")
    except:
        pass


def Get(dict):
    type = dict['gt']

    if type == 'oid':
        oid = 'null'

        try:
            cursor.execute("SELECT operation_id FROM operations WHERE sum = '" + dict['s'] + "' and tax = '" + dict['t'] + "' and tax_type = '" + dict['tt'] + "' and interest = '" + dict['i'] + "' and regularity = '" + dict['r'] + "' and length = '" + dict['l'] + "' and type = '" + dict['type'] + "' and add_date = '" + dict['ad'] + "' and pay_date = '" + dict['pd'] + "' and user_id = '" + dict['uid'] + "';")
            oid = str(cursor.fetchone()[0])
        except:
            pass
        return oid
    elif type == 'afd':
        cursor.execute("SELECT * FROM operations WHERE user_id = '" + dict['uid'] + "';")
        select = cursor.fetchall()

        SelectList = []

        user_id = dict['uid']

        cursor.execute("SELECT * FROM currency WHERE user_id = '" + dict['uid'] + "';")
        select_cur = cursor.fetchall()

        cur_point = select_cur[0][1][0:3]
        cur_currency = select_cur[0][2][0:3]

        DictDate = date(int(dict['d'][6:10]), int(dict['d'][3:5]), int(dict['d'][0:2]))

        CurHandler = CurrencyHandler.Currency()

        for i in select:
            SubList = []

            for j in i:
                SubList.append(j)

            DateSubList = date(int(SubList[9][6:10]), int(SubList[9][3:5]), int(SubList[9][0:2]))

            if DateSubList <= DictDate:
                if (str(SubList[11][0]) == 'm') and (str(DictDate.day) == str(SubList[10])) and (DictDate <= DateSubList + relativedelta(months=SubList[8])):
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

                elif (str(SubList[11][0]) == 'd') and (DictDate <= DateSubList + relativedelta(days=SubList[8])):
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
                elif (str(SubList[11][0]) == 'o') and (DictDate == DateSubList):
                    pass

        return str(SelectList)


def Delete(dict):
    cursor.execute("DELETE FROM operations WHERE operation_id = '" + dict['oid'] + "';")
    return 'True'


def Currency(dict):
    type = dict['ct']
    user_id = dict['uid']

    with open('../cfg/currency_rate.json', 'r') as file:
        FileRead = file.read()
        JsonRead = json.loads(FileRead)

    if type == 'cc':
        cursor.execute("UPDATE currency SET current_currency = '" + dict['nc'] + "' WHERE user_id = '" + user_id + "';")
    elif type == 'cp':
        cursor.execute("SELECT currency_point FROM currency WHERE user_id = '" + dict['uid'] + "';")
        select_cur = cursor.fetchall()

        old_currency_point = select_cur[0][0][0:3]

        cursor.execute("UPDATE currency SET currency_point = '" + dict['nc'] + "' WHERE user_id = '" + user_id + "';")

        cursor.execute("SELECT * FROM operations WHERE user_id = '" + user_id + "';")
        select_cur = cursor.fetchall()

        for i in select_cur:
            sum = i[3]

            operation_id = i[0]

            new_sum = round(sum / JsonRead[str(old_currency_point)] * JsonRead[dict['nc']], 2)

            cursor.execute("UPDATE operations SET sum = '" + str(new_sum) + "' WHERE operation_id = '" + str(operation_id) + "';")

    return 'True'


WorkStatus = True

with open(MAIN_DIR_PATH + '/src/logs/main/main.journal', 'a') as file:
    file.write(GetStrDate() + ' core init completed, entry central timer\n\n')

def CentralTimer():
    FrontValidatorMainIsReady = False

    with open('/home/ershovdan/My projects/baf/src/bridges/front_validator-main.json', 'r') as FrontValidatorJSON:
        try:
            DataFromFrontValidator = json.loads(FrontValidatorJSON.read())
            FrontValidatorMainIsReady = True
        except:
            FrontValidatorMainIsReady = False

        if FrontValidatorMainIsReady == True:
            if DataFromFrontValidator['add-in'] != []:
                AddToDB(DataFromFrontValidator['add-in'][0])
                data = DataFromFrontValidator['add-in'][0]
                DataFromFrontValidator['add-in'].pop(0)
                MainLogger().info('ADD data=' + str(data))

            if DataFromFrontValidator['usr-get-in'] != []:
                GetUserIDByUserName(DataFromFrontValidator['usr-get-in'][0])
                DataFromFrontValidator['usr-get-out'][DataFromFrontValidator['usr-get-in'][0]] = GetUserIDByUserName(DataFromFrontValidator['usr-get-in'][0])
                DataFromFrontValidator['usr-get-in'].pop(0)
                MainLogger().info('GET_USER return=' + GetUserIDByUserName(DataFromFrontValidator['usr-get-in'][0]))

            if DataFromFrontValidator['usr-add-in'] != []:
                AddUser(DataFromFrontValidator['usr-add-in'][0])
                data = DataFromFrontValidator['usr-add-in'][0]
                DataFromFrontValidator['usr-add-in'].pop(0)
                MainLogger().info('ADD_USER data=' + str(data))

            if DataFromFrontValidator['usr-chg-in'] != []:
                ChangeUser(DataFromFrontValidator['usr-chg-in'][0])
                data = DataFromFrontValidator['usr-chg-in'][0]
                DataFromFrontValidator['usr-chg-in'].pop(0)
                MainLogger().info('CHANGE_USER by username data=' + str(data))

            if DataFromFrontValidator['chg-in'] != []:
                Change(DataFromFrontValidator['chg-in'][0])
                data = DataFromFrontValidator['chg-in'][0]
                DataFromFrontValidator['chg-in'].pop(0)
                MainLogger().info('CHANGE data=' + str(data))

            if DataFromFrontValidator['get-oid-in'] != []:
                DataFromFrontValidator['get-oid-out'][DataFromFrontValidator['get-oid-in'][0]['code']] = Get(DataFromFrontValidator['get-oid-in'][0])
                MainLogger().info('GET operation id return=' + str(Get(DataFromFrontValidator['get-oid-in'][0])))
                DataFromFrontValidator['get-oid-in'].pop(0)

            if DataFromFrontValidator['get-afd-in'] != []:
                DataFromFrontValidator['get-afd-out'][DataFromFrontValidator['get-afd-in'][0]['code']] = Get(DataFromFrontValidator['get-afd-in'][0])
                MainLogger().info('GET all for date return=' + str(Get(DataFromFrontValidator['get-afd-in'][0])))
                DataFromFrontValidator['get-afd-in'].pop(0)

            if DataFromFrontValidator['del-in'] != []:
                Delete(DataFromFrontValidator['del-in'][0])
                MainLogger().info('DELETE')
                DataFromFrontValidator['del-in'].pop(0)

            if DataFromFrontValidator['cur-in'] != []:
                Currency(DataFromFrontValidator['cur-in'][0])
                MainLogger().info('CURRENCY')
                DataFromFrontValidator['cur-in'].pop(0)

            with open('/home/ershovdan/My projects/baf/src/bridges/front_validator-main.json', 'w') as FrontValidatorJSON:
                FrontValidatorJSON.write(json.dumps(DataFromFrontValidator))

        if WorkStatus == True:
            threading.Timer(interval=0.001, function=CentralTimer).start()
        else:
            MainLogger().info('main stopped')
            exit()


threading.Timer(interval=0.001, function=CentralTimer).start()

