import sys
import json
import pathlib
from typing import TextIO
import secrets
import time
import os
import random


opt = sys.argv[2:]  # make list of options

for i in range(len(opt)): # options from commands without values
    opt[i] = opt[i][1:]

MAIN_DIR_PATH = str(pathlib.Path(__file__).parent.resolve().parent.resolve()) # path to src/


def FVM_Choice(): # select one of 64 fvm bridges
    ret = 'front_validator-main-' + str(random.randint(0, 63)) + '.json'
    return ret


def add(options):  # baf-add
    NeedOptions = ['s', 't', 'tt', 'i', 'type', 'l', 'uid', 'ad', 'r']  # options allowed

    OptionsFromCommand = [] # options before =
    OptionsFromCommandValues = [] # options after =

    for i in options: # creating OptionsFromCommand and OptionsFromCommandValues
        OptionsFromCommand.append(i[:i.find('=')])
        OptionsFromCommandValues.append(i[i.find('=') + 1:])

    for i in OptionsFromCommand: # checking for unexpected options
        if i not in NeedOptions:
            print("baf-add: invalid option -- '" + i + "'")
            exit()

    if not set(NeedOptions).issubset(OptionsFromCommand): # checking for missing options
        print("baf-add: some options are missing")
        exit()

    try: # checking for sum is number
        float(OptionsFromCommandValues[OptionsFromCommand.index('s')])
    except:
        print("baf-add: sum should be number")
        exit()

    try: # checking for tax is number
        float(OptionsFromCommandValues[OptionsFromCommand.index('t')])
    except:
        print("baf-add: tax should be number")
        exit()

    if str(OptionsFromCommandValues[OptionsFromCommand.index('tt')]) not in ['a', 'b']: # checking for tax type is a(after) or b(before)
        print("baf-add: invalid tax type")
        exit()

    try: # checking for interest is number
        float(OptionsFromCommandValues[OptionsFromCommand.index('i')])
    except:
        print("baf-add: interest should be number")
        exit()

    if str(OptionsFromCommandValues[OptionsFromCommand.index('type')]) not in ['an', 'dn', 'si', 'se', 'ri', 're', 'd']: # checking for tax type is an or dn or se or si or re or ri or d
        print("baf-add: invalid type")
        exit()

    try: # checking for length is integer
        int(OptionsFromCommandValues[OptionsFromCommand.index('l')])
    except:
        print("baf-add: length should be integer")
        exit()

    try: # checking for user id is integer
        int(OptionsFromCommandValues[OptionsFromCommand.index('uid')])
    except:
        print("baf-add: invalid uid")
        exit()

    try: # checking for add date is DD.MM.YYYY
        time.strptime(OptionsFromCommandValues[OptionsFromCommand.index('ad')], '%d.%m.%Y')
    except ValueError:
        print("baf-add: invalid add date value")
        exit()

    if str(OptionsFromCommandValues[OptionsFromCommand.index('r')]) not in ['o', 'd', 'm']: # checking for regularity is o(once) or d(day) or m(month)
        print("baf-add: invalid regularity")
        exit()

    TransferData = {} # data to bridge
    for i in range(len(OptionsFromCommand)):
        TransferData[OptionsFromCommand[i]] = options[i][options[i].find('=') + 1:]

    TransferData['pd'] = TransferData['ad'][0:2] # pay date = add date

    Fvm = FVM_Choice() # number of fvm bridge

    with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'r') as ToMainJSON:  # adding TransferData to bridge
        ToMainJSONRead = ToMainJSON.read()
        ToMainJSONReadDecoded = json.loads(ToMainJSONRead)
        ToMainJSONReadDecoded['add-in'].append(TransferData)
    with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'w') as ToMainJSONWrite:
        ToMainJSONWrite.write(json.dumps(ToMainJSONReadDecoded))


def user(options):
    if (options[0] != 'add') and (options[0] != 'chg') and (options[0] != 'gui'):  # only -add(add) or -chg(change) or -gui(get user id)
        print("baf-usr: invalid option -- '" + options[0] + "'")
        exit()

    Fvm = FVM_Choice() # number of fvm bridge

    if options[0] == 'gui':     # get user id by username
        if options[1][:options[1].find('=')] == 'un':  # only un(username) option
            with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'r') as ToMainJSON:  # adding username to bridge
                ToMainJSONRead = ToMainJSON.read()
                try:
                    ToMainJSONReadDecoded = json.loads(ToMainJSONRead)
                except:
                    print(ToMainJSONRead)
                    exit()

                ToMainJSONReadDecoded['usr-get-in'].append(options[1][options[1].find('=') + 1:])
            with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'w') as ToMainJSONWrite: # adding ToMainJSONReadDecoded to bridge
                ToMainJSONWrite.write(json.dumps(ToMainJSONReadDecoded))

            while True:  # waiting for response from core
                with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'r') as FromMainJSON:
                    FromMainJSONRead = FromMainJSON.read()

                if FromMainJSONRead != '':  # getting response
                    try:
                        print(json.loads(FromMainJSONRead)['usr-get-out'][options[1][options[1].find('=') + 1:]])
                        FromMainJSONReadNew = json.loads(FromMainJSONRead)
                        FromMainJSONReadNew['usr-get-out'].pop(options[1][options[1].find('=') + 1:])

                        with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'w') as FromMainJSONWrite: # deleting response from bridge
                            FromMainJSONWrite.write(json.dumps(FromMainJSONReadNew))

                        break
                    except KeyError:
                        pass
        else:
            print("baf-usr: invalid option -- '" + options[1][:options[1].find('=')] + "'")
            exit()

    elif options[0] == 'add':  #add user
        NeedOptions = ['un', 'cu', 'fd'] # options allowed

        OptionsFromCommand = []  # options before =
        OptionsFromCommandValues = []  # options after =

        for i in options:  # creating OptionsFromCommand and OptionsFromCommandValues
            if i != 'add':
                OptionsFromCommand.append(i[:i.find('=')])
                OptionsFromCommandValues.append(i[i.find('=') + 1:])

        for i in OptionsFromCommand:  # checking for unexpected options
            if i not in NeedOptions:
                print("baf-usr: invalid option -- '" + i + "'")
                exit()

        if not set(NeedOptions).issubset(OptionsFromCommand):  # checking for missing options
            print("baf-usr: some options are missing")
            exit()

        username = options[OptionsFromCommand.index('un') + 1][options[OptionsFromCommand.index('un') + 1].find('=') + 1:]
        currency = options[OptionsFromCommand.index('cu') + 1][options[OptionsFromCommand.index('cu') + 1].find('=') + 1:]
        first_day = options[OptionsFromCommand.index('fd') + 1][options[OptionsFromCommand.index('fd') + 1].find('=') + 1:]

        UserAddList = []
        UserAddList.append(currency)
        UserAddList.append(first_day)

        if currency not in ['rub', 'usd', 'eur']: # only rub, usd, eur
            print("baf-usr: invalid currency")
            exit()

        if first_day not in ['m', 's']: # only Monday or Sunday
            print("baf-usr: invalid first day of week")
            exit()

        with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'r') as FromMainJSON: # adding FromMainJSONReadDecoded to bridge
            FromMainJSONRead = FromMainJSON.read()

        if FromMainJSONRead != '':
            FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
            FromMainJSONReadDecoded['usr-add-in'].append({username: UserAddList})
            with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'w') as ToMainJSONWrite:
                ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))

    elif options[0] == 'chg': # change user
        NeedOptions = ['un', 'id', 'fd', 'ia', 'nu'] # allowed options
        OptionsFromCommand = [] # options before =

        if len(options) < 3: # minimum 3 options
            print("baf-usr: some options are missing")
            exit()

        for i in range(1, len(options)): # checking for invalid options
            if options[i][:options[i].find('=')] not in NeedOptions:
                print("baf-usr: invalid option -- '" + options[i] + "'")
                exit()
            else:
                OptionsFromCommand.append(options[i][:options[i].find('=')])

        if ('un' in OptionsFromCommand) and ('id' in OptionsFromCommand): # username xor user_id
            print("baf-usr: please select -- 'un' xor -- 'id'")
            exit()

        un_or_id = ''

        if 'un' in OptionsFromCommand:
            username_or_id = options[OptionsFromCommand.index('un') + 1][options[OptionsFromCommand.index('un') + 1].find('=') + 1:]
            un_or_id = 'un'

        if 'id' in OptionsFromCommand:
            username_or_id = options[OptionsFromCommand.index('id') + 1][options[OptionsFromCommand.index('id') + 1].find('=') + 1:]
            un_or_id = 'id'

        try: # checking for is_active is t(true) or f(false)
            is_active = options[OptionsFromCommand.index('ia') + 1][options[OptionsFromCommand.index('ia') + 1].find('=') + 1:]

            if is_active not in ['t', 'f']: # only true of false
                print("baf-usr: invalid user activity")
                exit()
        except ValueError:
            is_active = ''

        try: # checking for first day of week is m(Monday) or s(Sunday)
            first_day = options[OptionsFromCommand.index('fd') + 1][options[OptionsFromCommand.index('fd') + 1].find('=') + 1:]

            if first_day not in ['m', 's']: # only Monday or Sunday
                print("baf-usr: invalid first day of week")
                exit()
        except ValueError:
            first_day = ''

        try:
            new_username = options[OptionsFromCommand.index('nu') + 1][options[OptionsFromCommand.index('nu') + 1].find('=') + 1:]
        except ValueError:
            new_username = ''

        with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'r') as FromMainJSON: # adding FromMainJSONReadDecoded to bridge
            FromMainJSONRead = FromMainJSON.read()

        if FromMainJSONRead != '':
            FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
            FromMainJSONReadDecoded['usr-chg-in'].append({username_or_id: [un_or_id, is_active, first_day, new_username]})
            with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'w') as ToMainJSONWrite:
                ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))


def change(options):
    NeedOptions = ['oid', 'uid', 's', 't', 'tt', 'i', 'r', 'l', 'type', 'ad', 'ns', 'nt', 'ntt', 'ni', 'nr', 'nl', 'nad'] # options allowed
    OptionsForSelect = ['uid', 's', 't', 'tt', 'i', 'r', 'l', 'type', 'ad',] # options for uid
    NewOptions = ['oid', 'ns', 'nt', 'ntt', 'ni', 'nr', 'nl', 'nad'] # options for oid
    OptionsFromCommand = []  # options before =
    OptionsFromCommandValues = []  # options after =

    for i in options:  # creating OptionsFromCommand and OptionsFromCommandValues
        OptionsFromCommand.append(i[:i.find('=')])
        OptionsFromCommandValues.append(i[i.find('=') + 1:])

    Fvm = FVM_Choice() # number of fvm bridge

    types = ['si', 'se', 'ri', 're', 'dn', 'an', 'd'] # allowed operations types

    if ('oid' in OptionsFromCommand) and ('uid' in OptionsFromCommand): # oid xor uid
        print("baf-chg: please select -- 'oid' xor -- 'uid'")
        exit()

    if 'oid' not in OptionsFromCommand: # by user id
        if len(options) < 11:  # minimum 11 options
            print("baf-chg: some options are missing")
            exit()

        for i in OptionsFromCommand: # checking for unexpected options
            if i not in NeedOptions:
                print("baf-chg: invalid option -- '" + i + "'")
                exit()

        for i in OptionsForSelect: # checking for missing options
            if i not in OptionsFromCommand:
                print("baf-chg: some options are missing")
                exit()

        try: # checking for user id is integer
            int(OptionsFromCommandValues[OptionsFromCommand.index('uid')])
        except:
            print("baf-chg: user id should be integer")

        try:  # checking for sum is number
            float(OptionsFromCommandValues[OptionsFromCommand.index('s')])
        except:
            print("baf-chg: sum should be number")
            exit()

        try:  # checking for tax is number
            float(OptionsFromCommandValues[OptionsFromCommand.index('t')])
        except:
            print("baf-chg: tax should be number")
            exit()

        if str(OptionsFromCommandValues[OptionsFromCommand.index('tt')]) not in ['a',
                                                                                 'b']:  # checking for tax type is a(after) or b(before)
            print("baf-chg: invalid tax type")
            exit()

        try:  # checking for interest is number
            float(OptionsFromCommandValues[OptionsFromCommand.index('i')])
        except:
            print("baf-chg: interest should be number")
            exit()

        if str(OptionsFromCommandValues[OptionsFromCommand.index('type')]) not in ['an', 'dn', 'si', 'se', 'ri', 're', 'd']:  # checking for tax type is an or dn or se or si or re or ri or d
            print("baf-chg: invalid type")
            exit()

        try:  # checking for length is integer
            int(OptionsFromCommandValues[OptionsFromCommand.index('l')])
        except:
            print("baf-chg: length should be integer")
            exit()

        try:  # checking for add date is DD.MM.YYYY
            time.strptime(OptionsFromCommandValues[OptionsFromCommand.index('ad')], '%d.%m.%Y')
        except ValueError:
            print("baf-chg: invalid add date value")
            exit()

        if str(OptionsFromCommandValues[OptionsFromCommand.index('r')]) not in ['o', 'd', 'm']:  # checking for regularity is o(once) or d(day) or m(month)
            print("baf-chg: invalid regularity")
            exit()


    else: # by operation id
        for i in OptionsFromCommand: # checking for unexpected options
            if i not in NewOptions:
                print("baf-chg: invalid option -- '" + i + "'")
                exit()

        try:
            a = OptionsFromCommandValues[OptionsFromCommand.index('oid')]
        except:
            print("baf-chg: some options are missing")

        try: # checking for operation id is integer
            int(OptionsFromCommandValues[OptionsFromCommand.index('oid')])
        except:
            print("baf-chg: operation id should be integer")

    try: # checking for new sum is number
        if options[OptionsFromCommand.index('ns')][options[OptionsFromCommand.index('ns')].find('=') + 1:] != '':
            try:
                int(options[OptionsFromCommand.index('ns')][options[OptionsFromCommand.index('ns')].find('=') + 1:])
            except:
                print("baf-chg: new sum should be integer")
                exit()
    except ValueError:
        pass

    try: # checking for new tax is number
        if options[OptionsFromCommand.index('nt')][options[OptionsFromCommand.index('nt')].find('=') + 1:] != '':
            try:
                float(options[OptionsFromCommand.index('nt')][options[OptionsFromCommand.index('nt')].find('=') + 1:])
            except:
                print("baf-chg: new tax should be number")
                exit()
    except ValueError:
        pass

    try: # checking for new tax type is a or b
        if options[OptionsFromCommand.index('ntt')][options[OptionsFromCommand.index('ntt')].find('=') + 1:] != '':
            if options[OptionsFromCommand.index('ntt')][options[OptionsFromCommand.index('ntt')].find('=') + 1:] not in ['a', 'b']:
                print("baf-chg: invalid new tax type")
                exit()
    except ValueError:
        pass

    try: # checking for new interest is number
        if options[OptionsFromCommand.index('ni')][options[OptionsFromCommand.index('ni')].find('=') + 1:] != '':
            try:
                float(options[OptionsFromCommand.index('ni')][options[OptionsFromCommand.index('ni')].find('=') + 1:])
            except:
                print("baf-chg: new interest should be number")
                exit()
    except ValueError:
        pass

    try: # checking for new regularity is o or d or m
        if options[OptionsFromCommand.index('nr')][options[OptionsFromCommand.index('nr')].find('=') + 1:] != '':
            if options[OptionsFromCommand.index('nr')][options[OptionsFromCommand.index('nr')].find('=') + 1:] not in ['o', 'd', 'm']:
                print("baf-chg: invalid new regularity type")
                exit()
    except ValueError:
        pass

    try: # checking for new add date is DD.MM.YYYY
        if options[OptionsFromCommand.index('nad')][options[OptionsFromCommand.index('nad')].find('=') + 1:] != '':
            try:
                time.strptime(OptionsFromCommandValues[OptionsFromCommand.index('nad')], '%d.%m.%Y')
            except:
                print("baf-chg: invalid new add date")
                exit()
    except ValueError:
        pass

    try: # checking for new length is integer
        if options[OptionsFromCommand.index('nl')][options[OptionsFromCommand.index('nl')].find('=') + 1:] != '':
            try:
                float(options[OptionsFromCommand.index('nl')][options[OptionsFromCommand.index('nl')].find('=') + 1:])
            except:
                print("baf-chg: new length should be integer")
                exit()
    except ValueError:
        pass

    TransferData = {} # data to bridge
    for i in range(len(OptionsFromCommand)):
        TransferData[OptionsFromCommand[i]] = options[i][options[i].find('=') + 1:]

    TransferData['pd'] = TransferData['ad'][0:2] # adding pay date to transfer data
    try:
        TransferData['npd'] = TransferData['nad'][0:2]
    except:
        pass

    with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'r') as FromMainJSON: # adding TransferData to bridge
        FromMainJSONRead = FromMainJSON.read()

    if FromMainJSONRead != '':
        FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
        FromMainJSONReadDecoded['chg-in'].append(TransferData)
        with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'w') as ToMainJSONWrite:
            ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))


def get(options):
    OptionsFromCommand = []  # options before =
    OptionsFromCommandValues = []  # options after =

    type = None # default type

    Fvm = FVM_Choice() # number of fvm bridge

    GetTypes = ['oid', 'afd'] # allowed types

    for i in options: # creating OptionsFromCommand
        OptionsFromCommand.append(i[:i.find('=')])
        OptionsFromCommandValues.append(i[i.find('=') + 1:])

    try: # checking for get type in options
        if OptionsFromCommandValues[OptionsFromCommand.index('gt')] not in GetTypes: # invalid type
            print("baf-get: invalid get type '" + OptionsFromCommandValues[OptionsFromCommand.index('gt')] + "'")
            exit()
        else: # get type in options
            type = OptionsFromCommandValues[OptionsFromCommand.index('gt')]
    except ValueError:
        print("baf-get: some options are missing")
        exit()

    if type == 'oid': # get operation id
        OidOptions = ['gt', 'uid', 's', 't', 'tt', 'i', 'r', 'l', 'type', 'ad'] # allowed options

        for i in OptionsFromCommand: # checking for unexpected options
            if i not in OidOptions:
                print("baf-get: invalid option -- '" + i + "'")
                exit()

        if not set(OidOptions).issubset(OptionsFromCommand): # checking for missing options
            print("baf-get: some options are missing")
            exit()

        try: # checking for user id is integer
            int(OptionsFromCommandValues[OptionsFromCommand.index('uid')])
        except:
            print("baf-get: user id should be integer")

        try:  # checking for sum is number
            float(OptionsFromCommandValues[OptionsFromCommand.index('s')])
        except:
            print("baf-get: sum should be number")
            exit()

        try:  # checking for tax is number
            float(OptionsFromCommandValues[OptionsFromCommand.index('t')])
        except:
            print("baf-get: tax should be number")
            exit()

        if str(OptionsFromCommandValues[OptionsFromCommand.index('tt')]) not in ['a', 'b']:  # checking for tax type is a(after) or b(before)
            print("baf-get: invalid tax type")
            exit()

        try:  # checking for interest is number
            float(OptionsFromCommandValues[OptionsFromCommand.index('i')])
        except:
            print("baf-get: interest should be number")
            exit()

        if str(OptionsFromCommandValues[OptionsFromCommand.index('type')]) not in ['an', 'dn', 'si', 'se', 'ri', 're', 'd']:  # checking for tax type is an or dn or se or si or re or ri or d
            print("baf-get: invalid type")
            exit()

        try:  # checking for length is integer
            int(OptionsFromCommandValues[OptionsFromCommand.index('l')])
        except:
            print("baf-get: length should be integer")
            exit()

        try:  # checking for add date is DD.MM.YYYY
            time.strptime(OptionsFromCommandValues[OptionsFromCommand.index('ad')], '%d.%m.%Y')
        except ValueError:
            print("baf-get: invalid add date value")
            exit()

        if str(OptionsFromCommandValues[OptionsFromCommand.index('r')]) not in ['o', 'd', 'm']:  # checking for regularity is o(once) or d(day) or m(month)
            print("baf-get: invalid regularity")
            exit()

        code = secrets.token_hex(16) # code to fvm bridge

        TransferData = {'code': code} # adding code to transfer data
        for i in range(len(OptionsFromCommand)):
            TransferData[OptionsFromCommand[i]] = OptionsFromCommandValues[i]

        with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'r') as FromMainJSON:
            FromMainJSONRead = FromMainJSON.read()

        TransferData['pd'] = TransferData['ad'][0:2] # adding pay date to transfer data

        if FromMainJSONRead != '':  # adding TransferData to bridge
            FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
            FromMainJSONReadDecoded['get-oid-in'].append(TransferData)
            with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'w') as ToMainJSONWrite:
                ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))

        while True:  # waiting for response
            with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'r') as FromMainJSON:
                FromMainJSONRead = FromMainJSON.read()

            if FromMainJSONRead != '':  # we got response
                try:
                    print(json.loads(FromMainJSONRead)['get-oid-out'][code])
                    FromMainJSONReadNew = json.loads(FromMainJSONRead)
                    FromMainJSONReadNew['get-oid-out'].pop(code)

                    with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'w') as FromMainJSONWrite:  # deleting response from bridge
                        FromMainJSONWrite.write(json.dumps(FromMainJSONReadNew))

                    break
                except KeyError:
                    pass

    elif type == 'afd': # all for date
        AfdOptions = ['gt', 'uid', 'd'] # allowed operations

        for i in OptionsFromCommand: # checking for unexpected options
            if i not in AfdOptions:
                print("baf-get: invalid option -- '" + i + "'")
                exit()

        if not set(AfdOptions).issubset(OptionsFromCommand): # checking for missing options
            print("baf-get: some options are missing")
            exit()

        try: # checking for date is DD.MM.YYYY
            time.strptime(OptionsFromCommandValues[OptionsFromCommand.index('d')], '%d.%m.%Y')
        except ValueError:
            print("baf-get: invalid date value")
            exit()

        try: # checking for user id is integer
            int(OptionsFromCommandValues[OptionsFromCommand.index('uid')])
        except:
            print("baf-get: user id should be integer")

        code = secrets.token_hex(16) # code to fvm bridge

        TransferData = {'code': code} # adding code to transfer data
        for i in range(len(OptionsFromCommand)):
            TransferData[OptionsFromCommand[i]] = OptionsFromCommandValues[i]

        with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'r') as FromMainJSON:
            FromMainJSONRead = FromMainJSON.read()

        if FromMainJSONRead != '':  # adding TransferData to bridge
            FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
            FromMainJSONReadDecoded['get-afd-in'].append(TransferData)
            with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'w') as ToMainJSONWrite:
                ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))

        while True:  # waiting for response
            with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'r') as FromMainJSON:
                FromMainJSONRead = FromMainJSON.read()

            if FromMainJSONRead != '':  # we got response
                try:
                    print(json.loads(FromMainJSONRead)['get-afd-out'][code])
                    FromMainJSONReadNew = json.loads(FromMainJSONRead)
                    FromMainJSONReadNew['get-afd-out'].pop(code)

                    with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'w') as FromMainJSONWrite:  # deleting response from bridge
                        FromMainJSONWrite.write(json.dumps(FromMainJSONReadNew))

                    break
                except KeyError:
                    pass


def delete(options):
    OptionsFromCommand = []  # options before =
    OptionsFromCommandValues = []  # options after =

    Fvm = FVM_Choice() # number of fvm bridge

    for i in options:  # creating OptionsFromCommand
        OptionsFromCommand.append(i[:i.find('=')])
        OptionsFromCommandValues.append(i[i.find('=') + 1:])

    DelOptions = ['oid'] # allowed options

    for i in OptionsFromCommand: # checking for unexpected options
        if i not in DelOptions:
            print("baf-del: invalid option -- '" + i + "'")
            exit()

    if not set(DelOptions).issubset(OptionsFromCommand): # checking for missing options
        print("baf-del: some options are missing")
        exit()

    try: # checking for operation id is integer
        int(OptionsFromCommandValues[OptionsFromCommand.index('oid')])
    except:
        print("baf-del: operation id should be integer")
        exit()

    TransferData = {}
    for i in range(len(OptionsFromCommand)):
        TransferData[OptionsFromCommand[i]] = OptionsFromCommandValues[i]

    with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'r') as FromMainJSON:
        FromMainJSONRead = FromMainJSON.read()

    if FromMainJSONRead != '':  # adding TransferData to bridge
        FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
        FromMainJSONReadDecoded['del-in'].append(TransferData)
        with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'w') as ToMainJSONWrite:
            ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))


def currency(options):
    OptionsFromCommand = []  # options before =
    OptionsFromCommandValues = []  # options after =

    type = None # default type

    CurrencyTypes = ['cp', 'cc'] # allowed types

    Fvm = FVM_Choice() # number of fvm bridge

    for i in options:  # creating OptionsFromCommand
        OptionsFromCommand.append(i[:i.find('=')])
        OptionsFromCommandValues.append(i[i.find('=') + 1:])

    try: # checking for currency type in options
        if OptionsFromCommandValues[OptionsFromCommand.index('ct')] not in CurrencyTypes: # invalid type
            print("baf-cur: invalid get type '" + OptionsFromCommandValues[OptionsFromCommand.index('ct')] + "'")
            exit()
        else: # currency type in options
            type = OptionsFromCommandValues[OptionsFromCommand.index('ct')]
    except ValueError:
        print("baf-cur: some options are missing")
        exit()

    if type == 'cp': # currency point
        OidOptions = ['uid', 'nc', 'ct'] # allowed options

        for i in OptionsFromCommand: # checking for unexpected options
            if i not in OidOptions:
                print("baf-cur: invalid option -- '" + i + "'")
                exit()

        if not set(OidOptions).issubset(OptionsFromCommand): # checking for missing options
            print("baf-cur: some options are missing")
            exit()

        try: # checking for user id is integer
            int(OptionsFromCommandValues[OptionsFromCommand.index('uid')])
        except:
            print("baf-cur: invalid value for operation id")
            exit()

        if OptionsFromCommandValues[OptionsFromCommand.index('nc')] not in ['rub', 'usd', 'eur']: # checking for new currency is valid
            print("baf-cur: invalid value for new currency")
            exit()

        TransferData = {} # data to fvm bridge
        for i in range(len(OptionsFromCommand)):
            TransferData[OptionsFromCommand[i]] = OptionsFromCommandValues[i]

        with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'r') as FromMainJSON: # adding TransferData to bridge
            FromMainJSONRead = FromMainJSON.read()

        if FromMainJSONRead != '':
            FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
            FromMainJSONReadDecoded['cur-in'].append(TransferData)
            with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'w') as ToMainJSONWrite:
                ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))

    elif type == 'cc': # current currency
        OidOptions = ['uid', 'nc', 'ct'] # allowed options

        for i in OptionsFromCommand: # checking for unexpected options
            if i not in OidOptions:
                print("baf-cur: invalid option -- '" + i + "'")
                exit()

        if not set(OidOptions).issubset(OptionsFromCommand): # checking for missing options
            print("baf-cur: some options are missing")
            exit()

        try: # checking for user id is integer
            int(OptionsFromCommandValues[OptionsFromCommand.index('uid')])
        except:
            print("baf-cur: invalid value for operation id")
            exit()

        if OptionsFromCommandValues[OptionsFromCommand.index('nc')] not in ['rub', 'usd', 'eur']: # checking for new currency is valid
            print("baf-cur: invalid value for new currency")
            exit()

        TransferData = {} # data to fvm
        for i in range(len(OptionsFromCommand)):
            TransferData[OptionsFromCommand[i]] = OptionsFromCommandValues[i]

        with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'r') as FromMainJSON: # adding TransferData to bridge
            FromMainJSONRead = FromMainJSON.read()

        if FromMainJSONRead != '':
            FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
            FromMainJSONReadDecoded['cur-in'].append(TransferData)
            with open(MAIN_DIR_PATH + '/src/bridges/' + Fvm, 'w') as ToMainJSONWrite:
                ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))


# selecting function
if sys.argv[1] == '-add': # add
    add(opt)
elif sys.argv[1] == '-usr': # user
    user(opt)
elif sys.argv[1] == '-chg': # change
    change(opt)
elif sys.argv[1] == '-get': # get
    get(opt)
elif sys.argv[1] == '-del': # delete
    delete(opt)
elif sys.argv[1] == '-cur': # currency
    currency(opt)
