import json
import sys
from loggers.logger import Upc


options = sys.argv[1:] # json string

if len(options) > 6: # checking input json string
    print("baf-upc: too many options")
    exit()
elif len(options) < 6: # checking input json string
    print("baf-upc: some options are missing")
    exit()
elif len(options) == 6: # json input string is right format (e.g. ["usd": 0.0, "usd": 0.0, "rub": 0.0])
    CurrenciesFromCommand = [] # currencies from json string
    CurrenciesFromCommandValues = [] # currency rates from json string

    Cur = {'rub', 'usd', 'eur'} # available currencies

    for i in range(len(options)): # creating CurrenciesFromCommand
        if i % 2 == 0:
            string = options[i]
            new_string = ''

            for j in range(len(string)):
                if (string[j] != ' ') and (string[j] != '[') and (string[j] != ']') and (string[j] != ':') and (string[j] != ','):
                    new_string += string[j]

            CurrenciesFromCommand.append(new_string)
        else:
            string = options[i]
            new_string = ''

            for j in range(len(string)):
                if (string[j] != ' ') and (string[j] != '[') and (string[j] != ']') and (string[j] != ':') and (string[j] != ','):
                    new_string += string[j]

            CurrenciesFromCommandValues.append(new_string)

    if set(CurrenciesFromCommand).issubset(Cur): # checking json for unexpected currencies
        for i in CurrenciesFromCommandValues:
            try:
                float(i)
            except:
                print("baf-upc: invalid JSON input")
                exit()

        dict = {CurrenciesFromCommand[0]: float(CurrenciesFromCommandValues[0]), CurrenciesFromCommand[1]: float(CurrenciesFromCommandValues[1]), CurrenciesFromCommand[2]: float(CurrenciesFromCommandValues[2])} # updating currency rate
        Upc().info('update: ' + str(dict))

        with open('../cfg/currency_rate.json', 'w') as file:
            JsonDict = json.dumps(dict)
            file.write(JsonDict)
    else:
        print("baf-upc: invalid JSON input")
        exit()