'''
 * Copyright (C) James Robert Albert III - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by James Albert <jamesrobertalbert@gmail.com>, March 2015
'''

from openpyxl import load_workbook

class Spreadsheet(object):
    def __init__(self, path):
        self.wb = load_workbook(filename=path)
        self.nav = self.wb.active
        self.columns = self.nav.columns
        self.rows = self.nav.rows
        self.col_count = len(self.nav.columns)
        self.row_count = len(self.nav.rows)

    def get(self, col, row):
        col = col.upper()
        row = str(row)
        key = col + row
        return self.nav[key].value

    def toDict(self):
        key_row = list(self.nav.rows).pop(0)
        cols = [cell.value for cell in key_row]
        orders = []
        for row in self.rows[1:]:
            orders.append({})
            for col, cell in zip(cols, row):
                if col in ['Ship To Zip', 'Phone'] and not isinstance(col, unicode):
                    '''
                    5-digit zip codes and phone numbers
                    get treated as numbers and a '.0' is appended to them.
                    this cuts off the trailing '.0'.
                    '''
                    cell.value = str(cell.value)[:-2]
                if cell.value is None:
                    cell.value = str()
                orders[-1][col] = '%s' % cell.value or str()

        return orders