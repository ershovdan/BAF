import json


class Currency:
    def __init__(self):
        self.type = 'currency'

    def convert(self, point, currnet, sum):
        with open('../cfg/currency_rate.json', 'r') as file:
            FileRead = file.read()
            JsonRead = json.loads(FileRead)

        money = sum / JsonRead[point] * JsonRead[currnet]

        return round(money, 2)
