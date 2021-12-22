class MonthInfo:
    def __init__(self, year, month):
        self.year = f'{year:04d}'
        self.month = f'{month:02d}'
        self.start_day = f'{1:02d}'
        self.end_day = f'{self.days_in_month(year, month):02d}'

        self.start_date = f'{self.year}-{self.month}-{self.start_day}'
        self.end_date = f'{self.year}-{self.month}-{self.end_day}'
    
    def days_in_month(self, year, month):
        if year % 4 == 0:
            monthSwitch = {
                1: 31,
                2: 29,
                3: 31,
                4: 30,
                5: 31,
                6: 30,
                7: 31,
                8: 31,
                9: 30,
                10: 31,
                11: 30,
                12: 31,
            }
        else:
            monthSwitch = {
                1: 31,
                2: 28,
                3: 31,
                4: 30,
                5: 31,
                6: 30,
                7: 31,
                8: 31,
                9: 30,
                10: 31,
                11: 30,
                12: 31,
            }

        return monthSwitch.get(month, 0)
