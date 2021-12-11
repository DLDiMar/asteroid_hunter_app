class monthInfo:
    def __init__(self, year, month):
        self.year = f'{year:04d}'
        self.month = f'{month:02d}'
        self.startDay = f'{1:02d}'
        self.endDay = f'{self.daysInMonth(year, month):02d}'

        self.startDate = f'{self.year}-{self.month}-{self.startDay}'
        self.endDate = f'{self.year}-{self.month}-{self.endDay}'
    
    def daysInMonth(self, year, month):
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
