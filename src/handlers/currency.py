import json


class Currency:
    def __init__(self):
        self.type = 'currency'

    def convert(self, point, currency, sum):
        with open('../cfg/currency_rate.json', 'r') as file: # reading currency rate file
            FileRead = file.read()
            JsonRead = json.loads(FileRead)

        money = sum / JsonRead[point] * JsonRead[currency] # sum in new currency

        return round(money, 2)
