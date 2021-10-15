from datetime import date


class Loan:
    def __init__(self):
        self.HandlerType = 'loan'

    def mannuity(self, sum, interest, length, add_date, today):
        payment = sum * (interest / 12 / 100 / (1 - (1 + interest / 12 / 100) ** -length))
        return round(-payment, 2)

    def mdifferentiated(self, sum, interest, length, add_date, today):
        AddDate = date(int(add_date[6:10]), int(add_date[3:5]), int(add_date[0:2]))
        TodayDate = date(int(today[6:10]), int(today[3:5]), int(today[0:2]))
        DateDiff = TodayDate - AddDate

        SumIter = sum
        InterestIter = 0
        MainDebt = sum / length

        for i in range(round(DateDiff.days / 30.4166666667) + 1):
            InterestIter = SumIter * interest / 12 / 100
            SumIter -= MainDebt

        payment = InterestIter + MainDebt

        return round(-payment, 2)

    def once(self, sum, interest):
        return round(-(sum + sum * interest / 100), 2)

    def dannuity(self, sum, interest, length, add_date, today):
        payment = sum * (interest / 365 / 100 / (1 - (1 + interest / 365 / 100) ** -length))
        return round(-payment, 2)

    def ddifferentiated(self, sum, interest, length, add_date, today):
        AddDate = date(int(add_date[6:10]), int(add_date[3:5]), int(add_date[0:2]))
        TodayDate = date(int(today[6:10]), int(today[3:5]), int(today[0:2]))
        DateDiff = TodayDate - AddDate

        SumIter = sum
        InterestIter = 0
        MainDebt = sum / length

        for i in range(DateDiff.days + 1):
            InterestIter = SumIter * interest / 365 / 100
            SumIter -= MainDebt

        payment = InterestIter + MainDebt

        return round(-payment, 2)


class Income:
    def __init__(self):
        self.HandlerType = 'income'

    def simple(self, sum, add_date, today):
        AddDate = date(int(add_date[6:10]), int(add_date[3:5]), int(add_date[0:2]))
        TodayDate = date(int(today[6:10]), int(today[3:5]), int(today[0:2]))

        if AddDate == TodayDate:
            return sum
        else:
            return float('inf')

    def regular(self, sum, add_date, today):
        AddDate = date(int(add_date[6:10]), int(add_date[3:5]), int(add_date[0:2]))
        TodayDate = date(int(today[6:10]), int(today[3:5]), int(today[0:2]))

        return sum


class Expense:
    def __init__(self):
        self.HandlerType = 'expense'

    def simple(self, sum, add_date, today):
        AddDate = date(int(add_date[6:10]), int(add_date[3:5]), int(add_date[0:2]))
        TodayDate = date(int(today[6:10]), int(today[3:5]), int(today[0:2]))

        if AddDate == TodayDate:
            return -sum
        else:
            return float('inf')

    def regular(self, sum, add_date, today):
        AddDate = date(int(add_date[6:10]), int(add_date[3:5]), int(add_date[0:2]))
        TodayDate = date(int(today[6:10]), int(today[3:5]), int(today[0:2]))

        return -sum


class Deposit:
    def __init__(self):
        self.HandlerType = 'deposit'

    def classic(self, sum, add_date, today, interest):
        AddDate = date(int(add_date[6:10]), int(add_date[3:5]), int(add_date[0:2]))
        TodayDate = date(int(today[6:10]), int(today[3:5]), int(today[0:2]))
        DateDiff = TodayDate - AddDate

        SumIter = sum
        AddedSumIter = 0

        for i in range(round(DateDiff.days / 30.4166666667) + 1):
            AddedSumIter = SumIter * interest / 100
            SumIter += SumIter * interest / 100

        return AddedSumIter


class Tax:
    def __init__(self):
        self.type = 'tax'

    def simple(self, sum, tax, tax_type):
        if tax_type == 'a':
            return round(sum, 2)
        elif tax_type == 'b':
            return round(sum + sum * tax / 100, 2)