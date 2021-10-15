import sys
import json
import pathlib
from typing import TextIO
import secrets
import time
import os


opt = sys.argv[2:]  # make list of options

for i in range(len(opt)):
    opt[i] = opt[i][1:]

MAIN_DIR_PATH = str(pathlib.Path(__file__).parent.resolve().parent.resolve())


def add(options):  # baf-add
    AllowableOptions = {  # options for baf-add
        'sum': {
            's': {
                type(float): 'sum'
            }
        },
        'tax': {
            't': {
                type(float): 'tax'
            }
        },
        'tax_type': {
            'tt': {
                'a': ' tax_after',
                'b': ' tax_before'
            }
        },
        'regularity': {
            'r': {
                'o': 'once',
                'd': 'day',
                'm': 'month',
            }
        },
        'interest': {
            'i': {
                type(float): 'interest'
            }
        },
        'length': {
            'l': {
                type(int): 'length'
            }
        },
        'type': {
            'type': {
                'si': 'simple income',
                'se': 'simple expense',
                'ri': 'regular income',
                're': 'regular expense',
                'an': 'annuity loan',
                'dn': 'differentiated loan',
                'd': 'deposit'
            }
        },
        'user_id': {
            'uid': {
                type(int): 'user id'
            }
        },
        'add_date': {
            'ad': {
                type(str): 'add date'
            }
        }
    }

    OptListBefore = []
    OptListAfter = []

    for i in options:
        OptionsList = []
        OptListBefore.append(i[:i.find('=')])  # letters before = in options
        OptListAfter.append(i[i.find('=') + 1:])  # letters after = in options
        for j in AllowableOptions:
            for k in AllowableOptions[j]:
                OptionsList.append(k)  # options that should be in command


    def validation():
        for i in options:  #checking for invalid options
            if i[:i.find('=')] not in OptionsList:
                print("baf-add: invalid option -- '" + i[:i.find('=')] + "'")
                return False

        if ('s' not in OptListBefore) or ('tt' not in OptListBefore) or ('t' not in OptListBefore) or ('type' not in OptListBefore) or ('uid' not in OptListBefore) or ('ad' not in OptListBefore): #checking for necessary options
            print('baf-add: some options are missing')
            return False
        
        elif OptListAfter[OptListBefore.index('type')] in ['an', 'dn', 'd']:
            if ('i' not in OptListBefore) or ('l' not in OptListBefore) or ('r' not in OptListBefore):
                print('baf-add: some options are missing')   #checking for necessary options for this type
                return False
            else:
                try:
                    int(OptListAfter[OptListBefore.index('l')])
                except:
                    print('baf-add: length should be a integer')  #checking for integer in length
                    return False

                OptListBefore.append('pd')
                OptListAfter.append(OptListAfter[OptListBefore.index('ad')][0:2])

                if not (set(OptListAfter[OptListBefore.index('r')]).issubset({'o', 'd', 'm'})):
                    print("baf-add: regularity can 'o' or 'd' or 'm' only")
                    return False

                try:
                    float(OptListAfter[OptListBefore.index('i')])
                except:
                    print('baf-add: invalid value for interest')  # checking for integer in length
                    return False

        elif OptListAfter[OptListBefore.index('type')] in ['re', 'ri']:
            if 'r' not in OptListBefore:
                print('baf-add: some options are missing')   #checking for necessary options for this type
                return False
            elif not (set(OptListAfter[OptListBefore.index('r')]).issubset({'o', 'd', 'm'})):
                print("baf-add: regularity can 'o' or 'd' or 'm' only")
                return False

            OptListBefore.append('pd')
            OptListAfter.append(OptListAfter[OptListBefore.index('ad')][0:2])

            try:
                float(OptListAfter[OptListBefore.index('i')])
            except:
                print('baf-add: invalid value for interest')  # checking for integer in length
                return False

        try:
            float(OptListAfter[OptListBefore.index('s')])   #checking for float in sum
        except:
            print('baf-add: sum should be a number')
            return False

        try:
            float(OptListAfter[OptListBefore.index('t')])   #checking for float in tax
        except:
            print('baf-add: tax should be a number')
            return False

        if not (set(OptListAfter[OptListBefore.index('tt')]).issubset({'a', 'b'})): #checking for a or b in tax type
            print("baf-add: tax type can 'a' or 'b' only")
            return False

        TypeSet = set()
        TypeSet.add(OptListAfter[OptListBefore.index('type')])

        if not (TypeSet.issubset({'si', 'se', 'ri', 're', 'an', 'dn', 'd'})):  #checking for correct types
            print("baf-add: invalid type, please read documentation for more information")
            return False

        try:
            int(OptListAfter[OptListBefore.index('uid')])   #checking for integer in user id
        except:
            print('baf-add: user id should be a integer')
            return False

        if len(OptListAfter[OptListBefore.index('ad')]) < 10: # add date length > 9
            print('baf-add: invalid value for add date')
            return False

        return True

    if not validation():  # checking validation
        exit()
    else:
        TransferData = {}

        for i in range(len(OptListBefore)):  # making TransferData
            TransferData[OptListBefore[i]] = OptListAfter[i]

        with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'r') as ToMainJSON:  # adding TransferData to bridge
            ToMainJSONRead = ToMainJSON.read()
            ToMainJSONReadDecoded = json.loads(ToMainJSONRead)
            ToMainJSONReadDecoded['add-in'].append(TransferData)
        with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'w') as ToMainJSONWrite:
            ToMainJSONWrite.write(json.dumps(ToMainJSONReadDecoded))


def user(options):
    if (options[0] != 'add') and (options[0] != 'chg') and (options[0] != 'gui'):  # only -add or -chg or -gui
        print("baf-usr: invalid option -- '" + options[0] + "'")
        exit()

    if options[0] == 'gui':     # get user id by username
        if options[1][:options[1].find('=')] == 'un':  # necessary option
            with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'r') as ToMainJSON:  # adding username to bridge
                ToMainJSONRead = ToMainJSON.read()
                try:
                    ToMainJSONReadDecoded = json.loads(ToMainJSONRead)
                except:
                    print(ToMainJSONRead)
                    exit()

                ToMainJSONReadDecoded['usr-get-in'].append(options[1][options[1].find('=') + 1:])
            with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'w') as ToMainJSONWrite: # adding ToMainJSONReadDecoded to bridge
                ToMainJSONWrite.write(json.dumps(ToMainJSONReadDecoded))

            while True:  # waiting for response
                with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'r') as FromMainJSON:
                    FromMainJSONRead = FromMainJSON.read()

                if FromMainJSONRead != '':  # we got response
                    try:
                        print(json.loads(FromMainJSONRead)['usr-get-out'][options[1][options[1].find('=') + 1:]])
                        FromMainJSONReadNew = json.loads(FromMainJSONRead)
                        FromMainJSONReadNew['usr-get-out'].pop(options[1][options[1].find('=') + 1:])

                        with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'w') as FromMainJSONWrite: # deleting response from bridge
                            FromMainJSONWrite.write(json.dumps(FromMainJSONReadNew))

                        break
                    except KeyError:
                        pass
        else:
            print("baf-usr: invalid option -- '" + options[1][:options[1].find('=')] + "'")
            exit()

    elif options[0] == 'add':  #add user
        NeedOptions = ['un', 'cu', 'fd']
        OptionsFromCommand = []

        if len(options) < 4:  # minimum 3 options
            print("baf-usr: some options are missing")
            exit()

        for i in range(1, 4): # checking for invalid options
            if options[i][:options[i].find('=')] not in NeedOptions:
                print("baf-usr: invalid option -- '" + options[i] + "'")
                exit()
            else:
                OptionsFromCommand.append(options[i][:options[i].find('=')])

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

        with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'r') as FromMainJSON:
            FromMainJSONRead = FromMainJSON.read()

        if FromMainJSONRead != '':  # adding FromMainJSONReadDecoded to bridge
            FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
            FromMainJSONReadDecoded['usr-add-in'].append({username: UserAddList})
            with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'w') as ToMainJSONWrite:
                ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))

    elif options[0] == 'chg': # change user
        NeedOptionsList = ['un', 'id', 'fd', 'ia', 'nu']
        OptionsFromCommand = []

        if len(options) < 3: # minimum 3 options
            print("baf-usr: some options are missing")
            exit()

        for i in range(1, len(options)): # checking for invalid options
            if options[i][:options[i].find('=')] not in NeedOptionsList:
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

        try:
            is_active = options[OptionsFromCommand.index('ia') + 1][options[OptionsFromCommand.index('ia') + 1].find('=') + 1:]

            if is_active not in ['t', 'f']: # only true of false
                print("baf-usr: invalid user activity")
                exit()
        except ValueError:
            is_active = ''

        try:
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

        with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'r') as FromMainJSON:
            FromMainJSONRead = FromMainJSON.read()

        if FromMainJSONRead != '':  # adding FromMainJSONReadDecoded to bridge
            FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
            FromMainJSONReadDecoded['usr-chg-in'].append({username_or_id: [un_or_id, is_active, first_day, new_username]})
            with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'w') as ToMainJSONWrite:
                ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))


def change(options):
    NeedOptions = ['oid', 'uid', 's', 't', 'tt', 'i', 'r', 'l', 'type', 'ad', 'ns', 'nt', 'ntt', 'ni', 'nr', 'nl', 'nad'] # options allowed
    OptionsForSelect = ['uid', 's', 't', 'tt', 'i', 'r', 'l', 'type', 'ad'] # options for uid
    NewOptions = ['oid', 'ns', 'nt', 'ntt', 'ni', 'nr', 'nl', 'nad'] # options for oid
    OptionsFromCommand = []

    types = ['si', 'se', 'ri', 're', 'dn', 'an', 'd']

    for i in options: # creating OptionsFromCommand
        OptionsFromCommand.append(i[:i.find('=')])

    if ('oid' in OptionsFromCommand) and ('uid' in OptionsFromCommand): # oid xor uid
        print("baf-usr: please select -- 'oid' xor -- 'uid'")
        exit()

    if 'oid' not in OptionsFromCommand: # oid
        if len(options) < 10:  # minimum 3 options
            print("baf-usr: some options are missing")
            exit()

        for i in OptionsFromCommand:
            if i not in NeedOptions:
                print("baf-usr: invalid option -- '" + i + "'")
                exit()

        for i in OptionsForSelect:
            if i not in OptionsFromCommand:
                print("baf-usr: some options are missing")
                exit()

    else: # uid
        for i in OptionsFromCommand:
            if i in OptionsForSelect:
                print("baf-usr: invalid option -- '" + i + "'")
                exit()

        for i in OptionsFromCommand:
            if i not in NewOptions:
                print("baf-usr: invalid option -- '" + i + "'")
                exit()

    try:
        if options[OptionsFromCommand.index('ns')][options[OptionsFromCommand.index('ns')].find('=') + 1:] != '':
            try:
                int(options[OptionsFromCommand.index('ns')][options[OptionsFromCommand.index('ns')].find('=') + 1:])
            except:
                print("baf-usr: sum should be integer")
                exit()
    except ValueError:
        pass

    try:
        if options[OptionsFromCommand.index('nt')][options[OptionsFromCommand.index('nt')].find('=') + 1:] != '':
            try:
                float(options[OptionsFromCommand.index('nt')][options[OptionsFromCommand.index('nt')].find('=') + 1:])
            except:
                print("baf-usr: process id should be number")
                exit()
    except ValueError:
        pass

    try:
        if options[OptionsFromCommand.index('ntt')][options[OptionsFromCommand.index('ntt')].find('=') + 1:] != '':
            if options[OptionsFromCommand.index('ntt')][options[OptionsFromCommand.index('ntt')].find('=') + 1:] not in ['a', 'b']:
                print("baf-usr: invalid tax type")
                exit()
    except ValueError:
        pass

    try:
        if options[OptionsFromCommand.index('ni')][options[OptionsFromCommand.index('ni')].find('=') + 1:] != '':
            try:
                float(options[OptionsFromCommand.index('ni')][options[OptionsFromCommand.index('ni')].find('=') + 1:])
            except:
                print("baf-usr: interest should be number")
                exit()
    except ValueError:
        pass

    try:
        if options[OptionsFromCommand.index('nr')][options[OptionsFromCommand.index('nr')].find('=') + 1:] != '':
            if options[OptionsFromCommand.index('nr')][options[OptionsFromCommand.index('nr')].find('=') + 1:] not in ['o', 'd', 'm']:
                print("baf-usr: invalid regularity type")
                exit()
    except ValueError:
        pass

    try:
        if options[OptionsFromCommand.index('nad')][options[OptionsFromCommand.index('nad')].find('=') + 1:] != '':
            if len(options[OptionsFromCommand.index('nad')][options[OptionsFromCommand.index('nad')].find('=') + 1:]) < 10:
                print("baf-usr: invalid add date")
                exit()
    except ValueError:
        pass

    try:
        if options[OptionsFromCommand.index('ni')][options[OptionsFromCommand.index('ni')].find('=') + 1:] != '':
            try:
                float(options[OptionsFromCommand.index('nl')][options[OptionsFromCommand.index('nl')].find('=') + 1:])
            except:
                print("baf-usr: length should be integer")
                exit()
    except ValueError:
        pass

    TransferData = {}
    for i in range(len(OptionsFromCommand)):
        TransferData[OptionsFromCommand[i]] = options[i][options[i].find('=') + 1:]

    TransferData['pd'] = TransferData['ad'][0:2]
    try:
        TransferData['npd'] = TransferData['nad'][0:2]
    except:
        pass

    with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'r') as FromMainJSON:
        FromMainJSONRead = FromMainJSON.read()

    if FromMainJSONRead != '':  # adding TransferData to bridge
        FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
        FromMainJSONReadDecoded['chg-in'].append(TransferData)
        with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'w') as ToMainJSONWrite:
            ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))


def get(options):
    OptionsFromCommand = []
    OptionsFromCommandValues = []

    type = None

    GetTypes = ['oid', 'afd']

    for i in options: # creating OptionsFromCommand
        OptionsFromCommand.append(i[:i.find('=')])
        OptionsFromCommandValues.append(i[i.find('=') + 1:])

    try:
        if OptionsFromCommandValues[OptionsFromCommand.index('gt')] not in GetTypes:
            print("baf-get: invalid get type '" + OptionsFromCommandValues[OptionsFromCommand.index('gt')] + "'")
            exit()
        else:
            type = OptionsFromCommandValues[OptionsFromCommand.index('gt')]
    except ValueError:
        print("baf-get: some options are missing")
        exit()

    if type == 'oid':
        OidOptions = ['gt', 'uid', 's', 't', 'tt', 'i', 'r', 'l', 'type', 'ad']

        for i in OptionsFromCommand:
            if i not in OidOptions:
                print("baf-get: invalid option -- '" + i + "'")
                exit()

        if not set(OidOptions).issubset(OptionsFromCommand):
            print("baf-get: some options are missing")
            exit()

        code = secrets.token_hex(16)

        TransferData = {'code': code}
        for i in range(len(OptionsFromCommand)):
            TransferData[OptionsFromCommand[i]] = OptionsFromCommandValues[i]

        with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'r') as FromMainJSON:
            FromMainJSONRead = FromMainJSON.read()

        TransferData['pd'] = TransferData['ad'][0:2]

        if FromMainJSONRead != '':  # adding TransferData to bridge
            FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
            FromMainJSONReadDecoded['get-oid-in'].append(TransferData)
            with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'w') as ToMainJSONWrite:
                ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))

        while True:  # waiting for response
            with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'r') as FromMainJSON:
                FromMainJSONRead = FromMainJSON.read()

            if FromMainJSONRead != '':  # we got response
                try:
                    print(json.loads(FromMainJSONRead)['get-oid-out'][code])
                    FromMainJSONReadNew = json.loads(FromMainJSONRead)
                    FromMainJSONReadNew['get-oid-out'].pop(code)

                    with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'w') as FromMainJSONWrite:  # deleting response from bridge
                        FromMainJSONWrite.write(json.dumps(FromMainJSONReadNew))

                    break
                except KeyError:
                    pass

    elif type == 'afd':
        AfdOptions = ['gt', 'uid', 'd']

        for i in OptionsFromCommand:
            if i not in AfdOptions:
                print("baf-get: invalid option -- '" + i + "'")
                exit()

        if not set(AfdOptions).issubset(OptionsFromCommand):
            print("baf-get: some options are missing")
            exit()

        try:
            time.strptime(OptionsFromCommandValues[OptionsFromCommand.index('d')], '%d.%m.%Y')
        except ValueError:
            print("baf-get: invalid date value")
            exit()

        code = secrets.token_hex(16)

        TransferData = {'code': code}
        for i in range(len(OptionsFromCommand)):
            TransferData[OptionsFromCommand[i]] = OptionsFromCommandValues[i]

        with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'r') as FromMainJSON:
            FromMainJSONRead = FromMainJSON.read()

        if FromMainJSONRead != '':  # adding TransferData to bridge
            FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
            FromMainJSONReadDecoded['get-afd-in'].append(TransferData)
            with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'w') as ToMainJSONWrite:
                ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))

        while True:  # waiting for response
            with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'r') as FromMainJSON:
                FromMainJSONRead = FromMainJSON.read()

            if FromMainJSONRead != '':  # we got response
                try:
                    print(json.loads(FromMainJSONRead)['get-afd-out'][code])
                    FromMainJSONReadNew = json.loads(FromMainJSONRead)
                    FromMainJSONReadNew['get-afd-out'].pop(code)

                    with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json',
                              'w') as FromMainJSONWrite:  # deleting response from bridge
                        FromMainJSONWrite.write(json.dumps(FromMainJSONReadNew))

                    break
                except KeyError:
                    pass


def delete(options):
    OptionsFromCommand = []
    OptionsFromCommandValues = []

    type = None

    for i in options:  # creating OptionsFromCommand
        OptionsFromCommand.append(i[:i.find('=')])
        OptionsFromCommandValues.append(i[i.find('=') + 1:])

    OidOptions = ['oid']

    for i in OptionsFromCommand:
        if i not in OidOptions:
            print("baf-del: invalid option -- '" + i + "'")
            exit()

    if not set(OidOptions).issubset(OptionsFromCommand):
        print("baf-del: some options are missing")
        exit()

    code = secrets.token_hex(16)

    try:
        int(OptionsFromCommandValues[OptionsFromCommand.index('oid')])
    except:
        print("baf-del: invalid value for operation id")
        exit()

    TransferData = {'code': code}
    for i in range(len(OptionsFromCommand)):
        TransferData[OptionsFromCommand[i]] = OptionsFromCommandValues[i]

    with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'r') as FromMainJSON:
        FromMainJSONRead = FromMainJSON.read()

    if FromMainJSONRead != '':  # adding TransferData to bridge
        FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
        FromMainJSONReadDecoded['del-in'].append(TransferData)
        with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'w') as ToMainJSONWrite:
            ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))

    while True:  # waiting for response
        with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'r') as FromMainJSON:
            FromMainJSONRead = FromMainJSON.read()

        if FromMainJSONRead != '':  # we got response
            try:
                FromMainJSONReadNew = json.loads(FromMainJSONRead)
                FromMainJSONReadNew['del-out'].pop(code)

                with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'w') as FromMainJSONWrite:  # deleting response from bridge
                    FromMainJSONWrite.write(json.dumps(FromMainJSONReadNew))

                break
            except KeyError:
                pass


def currency(options):
    OptionsFromCommand = []
    OptionsFromCommandValues = []

    type = None

    CurrencyTypes = ['cp', 'cc']

    for i in options:  # creating OptionsFromCommand
        OptionsFromCommand.append(i[:i.find('=')])
        OptionsFromCommandValues.append(i[i.find('=') + 1:])

    try:
        if OptionsFromCommandValues[OptionsFromCommand.index('ct')] not in CurrencyTypes:
            print("baf-cur: invalid get type '" + OptionsFromCommandValues[OptionsFromCommand.index('ct')] + "'")
            exit()
        else:
            type = OptionsFromCommandValues[OptionsFromCommand.index('ct')]
    except ValueError:
        print("baf-cur: some options are missing")
        exit()

    if type == 'cp':
        OidOptions = ['uid', 'nc', 'ct']

        for i in OptionsFromCommand:
            if i not in OidOptions:
                print("baf-cur: invalid option -- '" + i + "'")
                exit()

        if not set(OidOptions).issubset(OptionsFromCommand):
            print("baf-cur: some options are missing")
            exit()

        try:
            int(OptionsFromCommandValues[OptionsFromCommand.index('uid')])
        except:
            print("baf-cur: invalid value for operation id")
            exit()

        if OptionsFromCommandValues[OptionsFromCommand.index('nc')] not in ['rub', 'usd', 'eur']:
            print("baf-cur: invalid value for new currency")
            exit()

        TransferData = {}
        for i in range(len(OptionsFromCommand)):
            TransferData[OptionsFromCommand[i]] = OptionsFromCommandValues[i]

        with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'r') as FromMainJSON:
            FromMainJSONRead = FromMainJSON.read()

        if FromMainJSONRead != '':  # adding TransferData to bridge
            FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
            FromMainJSONReadDecoded['cur-in'].append(TransferData)
            with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'w') as ToMainJSONWrite:
                ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))

    elif type == 'cc':
        OidOptions = ['uid', 'nc', 'ct']

        for i in OptionsFromCommand:
            if i not in OidOptions:
                print("baf-cur: invalid option -- '" + i + "'")
                exit()

        if not set(OidOptions).issubset(OptionsFromCommand):
            print("baf-cur: some options are missing")
            exit()

        try:
            int(OptionsFromCommandValues[OptionsFromCommand.index('uid')])
        except:
            print("baf-cur: invalid value for operation id")
            exit()

        if OptionsFromCommandValues[OptionsFromCommand.index('nc')] not in ['rub', 'usd', 'eur']:
            print("baf-cur: invalid value for new currency")
            exit()

        TransferData = {}
        for i in range(len(OptionsFromCommand)):
            TransferData[OptionsFromCommand[i]] = OptionsFromCommandValues[i]

        with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'r') as FromMainJSON:
            FromMainJSONRead = FromMainJSON.read()

        if FromMainJSONRead != '':  # adding TransferData to bridge
            FromMainJSONReadDecoded = json.loads(FromMainJSONRead)
            FromMainJSONReadDecoded['cur-in'].append(TransferData)
            with open(MAIN_DIR_PATH + '/src/bridges/front_validator-main.json', 'w') as ToMainJSONWrite:
                ToMainJSONWrite.write(json.dumps(FromMainJSONReadDecoded))


if sys.argv[1] == '-add':
    add(opt)
elif sys.argv[1] == '-usr':
    user(opt)
elif sys.argv[1] == '-chg':
    change(opt)
elif sys.argv[1] == '-get':
    get(opt)
elif sys.argv[1] == '-del':
    delete(opt)
elif sys.argv[1] == '-cur':
    currency(opt)
