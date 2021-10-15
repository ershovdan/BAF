import json
import sys
from loggers.logger import Upc


if len(sys.argv) > 4:
    print("baf-upc: too many options")
    exit()
elif len(sys.argv) < 4:
    print("baf-upc: some options are missing")
    exit()
elif len(sys.argv) == 4:
    OptionsFromCommand = []
    OptionsFromCommandValues = []

    options = sys.argv[1:]

    type = None

    Cur = {'rub', 'usd', 'eur'}

    for i in options:  # creating OptionsFromCommand
        OptionsFromCommand.append(i[:i.find('=')][1:])
        OptionsFromCommandValues.append(i[i.find('=') + 1:])

    if set(OptionsFromCommand).issubset(Cur):

        for i in OptionsFromCommandValues:
            try:
                float(i)
            except:
                print("baf-upc: invalid JSON input")
                exit()

        dict = {OptionsFromCommand[0]: float(OptionsFromCommandValues[0]), OptionsFromCommand[1]: float(OptionsFromCommandValues[1]), OptionsFromCommand[2]: float(OptionsFromCommandValues[2])}

        Upc().info('update: ' + str(dict))

        with open('../cfg/currency_rate.json', 'w') as file:
            JsonDict = json.dumps(dict)
            file.write(JsonDict)
    else:
        print("baf-upc: invalid JSON input")
        exit()
