import json
import datetime
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
from getpass import getpass
import pathlib


def GetStrDate():
    time_str = str(datetime.datetime.today().date()) + '_' + str(datetime.datetime.today().time())
    return time_str


if sys.argv[1:] != []:  #selecting config option
    print("baf-cfg: invalid option -- '" + sys.argv[1].replace('-', '') + "'")
else:
    print('Select option:')
    print('1. Update core')
    print('2. Install or reset core')
    print('3. Cancel')

    InputOpt = input()

    if (InputOpt != '1') and (InputOpt != '2'):  # not 1 or 2
        print()
        exit()

    if InputOpt == '1': # update
        print()

        try:  # create tables
            MAIN_DIR_PATH = str(pathlib.Path(__file__).parent.resolve().parent.resolve())

            with open(MAIN_DIR_PATH + '/src/cfg/baf_cfg.json', 'r') as CfgFile:
                CfgFileRead = json.loads(CfgFile.read())

            if CfgFileRead['psql_host'] == 'NULL':
                print('baf-cfg: core not installed')
                exit()


            connection = psycopg2.connect(user=CfgFileRead['psql_user'], database='baf', password=CfgFileRead['psql_password'], host=CfgFileRead['psql_host'], port=CfgFileRead['psql_port'])
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = connection.cursor()

            cursor.execute('ALTER TABLE operations '
                           'ADD COLUMN IF NOT EXISTS user_id INTEGER NOT NULL, '
                           'ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT NOW(), '
                           'ADD COLUMN IF NOT EXISTS sum FLOAT NOT NULL, '
                           'ADD COLUMN IF NOT EXISTS tax_type CHAR NOT NULL, '
                           'ADD COLUMN IF NOT EXISTS tax FLOAT NOT NULL, '
                           'ADD COLUMN IF NOT EXISTS type CHAR(8), '
                           'ADD COLUMN IF NOT EXISTS interest INTEGER, '
                           'ADD COLUMN IF NOT EXISTS length INTEGER, '
                           'ADD COLUMN IF NOT EXISTS add_date CHAR(10), '
                           'ADD COLUMN IF NOT EXISTS pay_date INTEGER,'
                           'ADD COLUMN IF NOT EXISTS regularity CHAR(2)'
                           ';')

            cursor.execute('ALTER TABLE currency '
                           'ADD COLUMN IF NOT EXISTS user_id INTEGER UNIQUE NOT NULL, '
                           'ADD COLUMN IF NOT EXISTS currency_point CHAR(5), '
                           'ADD COLUMN IF NOT EXISTS current_currency CHAR(5)'
                           ';')

            cursor.execute('ALTER TABLE users '
                           'ADD COLUMN IF NOT EXISTS username CHAR(150) UNIQUE, '
                           'ADD COLUMN IF NOT EXISTS first_day_of_week CHAR, '
                           'ADD COLUMN IF NOT EXISTS is_active CHAR'
                           ';')

            print('Tables updated...')

            cursor.close()
            connection.close()

            with open('logs/main/main.journal', 'a') as file:
                file.write(GetStrDate() + ' core updated\n\n')

        except Exception as error:
            print('baf-cfg: Something went wrong')
            exit()

        print('Completed')

    else:         # reinstall
        print()

        print('=== PostgreSQL settings ===')
        username = input('Username: ')
        password = getpass()
        host = input('host: ')
        port = input('port: ')

        print()

        try:  # connect to db
            connection = psycopg2.connect(user=username, database='postgres', password=password, host=host, port=port)
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = connection.cursor()

            cursor.execute('DROP DATABASE IF EXISTS baf;')
            cursor.execute('CREATE DATABASE baf;')

            print('DB dropped...')

        except Exception as error:
            print('baf-cfg: Something went wrong')
            exit()

        try:  # create tables
            connection = psycopg2.connect(user=username, database='baf', password=password, host=host, port=port)
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = connection.cursor()

            cursor.execute('CREATE TABLE operations ('
                           'operation_id SERIAL UNIQUE PRIMARY KEY, '
                           'user_id INTEGER NOT NULL, '
                           'timestamp TIMESTAMP DEFAULT NOW(), '
                           'sum FLOAT NOT NULL, '
                           'tax_type CHAR NOT NULL, '
                           'tax FLOAT NOT NULL, '
                           'type CHAR(8), '
                           'interest INTEGER, '
                           'length INTEGER, '
                           'add_date CHAR(10), '
                           'pay_date INTEGER,'
                           'regularity CHAR(2)'
                           ');')

            cursor.execute('CREATE TABLE currency ('
                           'user_id INTEGER UNIQUE NOT NULL, '
                           'currency_point CHAR(5), '
                           'current_currency CHAR(5)'
                           ');')

            cursor.execute('CREATE TABLE users ('
                           'user_id SERIAL UNIQUE PRIMARY KEY, '
                           'username CHAR(150) UNIQUE, '
                           'first_day_of_week CHAR, '
                           'is_active CHAR' 
                           ');')

            print('Tables created...')

            MAIN_DIR_PATH = str(pathlib.Path(__file__).parent.resolve().parent.resolve())

            print(MAIN_DIR_PATH + '/src/cfg/baf_cfg.json')

            with open(MAIN_DIR_PATH + '/src/cfg/baf_cfg.json', 'r') as CfgFile:
                CfgFileRead = json.loads(CfgFile.read())

            CfgFileRead['version'] = '0.1'
            CfgFileRead['main_dir_path'] = MAIN_DIR_PATH
            CfgFileRead['psql_user'] = username
            CfgFileRead['psql_password'] = password
            CfgFileRead['psql_host'] = host
            CfgFileRead['psql_port'] = port

            with open(MAIN_DIR_PATH + '/src/cfg/baf_cfg.json', 'w') as CfgFile:
                CfgFile.write(json.dumps(CfgFileRead))

            with open(MAIN_DIR_PATH + '/src/bash/baf-run', 'w'):
                pass

            with open(MAIN_DIR_PATH + '/src/bash/baf-add', 'w'):
                pass

            with open(MAIN_DIR_PATH + '/src/bash/baf-chg', 'w'):
                pass

            with open(MAIN_DIR_PATH + '/src/bash/baf-get', 'w'):
                pass

            with open(MAIN_DIR_PATH + '/src/bash/baf-usr', 'w'):
                pass

            with open(MAIN_DIR_PATH + '/src/bash/baf-run', 'a') as file:
                file.write('#!/bin/bash\n')
                file.write('\n')
                file.write('cd "' + str(MAIN_DIR_PATH) + '/src/bash/"\n')
                file.write('\n')
                file.write('sudo "../../venv/bin/python3" "../main.py"')

            with open(MAIN_DIR_PATH + '/src/bash/baf-add', 'a') as file:
                file.write('#!/bin/bash\n')
                file.write('\n')
                file.write('cd "' + str(MAIN_DIR_PATH) + '/src/bash/"\n')
                file.write('\n')
                file.write('"../../venv/bin/python3" "../front_validator.py" -add $1 $2 $3 $4 $5 $6 $7 $8 $9 ${10}')

            with open(MAIN_DIR_PATH + '/src/bash/baf-chg', 'a') as file:
                file.write('#!/bin/bash\n')
                file.write('\n')
                file.write('cd "' + str(MAIN_DIR_PATH) + '/src/bash/"\n')
                file.write('\n')
                file.write('"../../venv/bin/python3" "../front_validator.py" -chg $1 $2 $3 $4 $5 $6 $7 $8 $9 ${10} ${11} ${12} ${13} ${14} ${15} ${16}')

            with open(MAIN_DIR_PATH + '/src/bash/baf-get', 'a') as file:
                file.write('#!/bin/bash\n')
                file.write('\n')
                file.write('cd "' + str(MAIN_DIR_PATH) + '/src/bash/"\n')
                file.write('\n')
                file.write('# shellcheck disable=SC2068')
                file.write('"../../venv/bin/python3" "../front_validator.py" -get $@')

            with open(MAIN_DIR_PATH + '/src/bash/baf-usr', 'a') as file:
                file.write('#!/bin/bash\n')
                file.write('\n')
                file.write('cd "' + str(MAIN_DIR_PATH) + '/src/bash/"\n')
                file.write('\n')
                file.write('"../../venv/bin/python3" "../front_validator.py" -usr $1 $2 $3 $4 $5')

            print('Configured...')

            cursor.close()
            connection.close()

            with open(MAIN_DIR_PATH + '/src/logs/main/main.journal', 'w') as file:
                file.write(GetStrDate() + ' core installed\n\n')

        except Exception as error:
            print('baf-cfg: Something went wrong')
            exit()

        print('Completed')

