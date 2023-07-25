from typing import List
import datetime

import xlrd

from .models import CreditCardTransaction


class CreditCardTransactionsInput:

    def __init__(self, excel_file: str, circuit: str = None):
        self.excel_file = excel_file
        self.circuit = circuit

    def read(self) -> List[CreditCardTransaction]:
        """Read a credit card statement and output a list of CreditCardTransaction objects"""
        # Open the workbook
        workbook = xlrd.open_workbook(self.excel_file)

        # Select the first sheet (index 0) from the workbook
        sheet = workbook.sheet_by_index(0)

        transactions = []

        # Read data from cells with data
        for row in range(3, sheet.nrows):

            cell_value = sheet.cell_value(row, 1)
            if cell_value == "":
                continue
                
            owner = sheet.cell_value(row, 1)
            card_number = sheet.cell_value(row, 2)

            transaction_date = datetime.datetime(*xlrd.xldate_as_tuple(sheet.cell_value(row, 3), workbook.datemode))
            registration_date = datetime.datetime(*xlrd.xldate_as_tuple(sheet.cell_value(row, 4), workbook.datemode))

            description = sheet.cell_value(row, 5)
            operation_state = sheet.cell_value(row, 6)
            operation_type = sheet.cell_value(row, 7)
            circuit = sheet.cell_value(row, 8)
            transaction_type = sheet.cell_value(row, 9)
            amount = sheet.cell_value(row, 10)

            # print(f"{owner} {card_number} {transaction_date} {registration_date} {description} {operation_state} {circuit} {transaction_type} [{amount}]")
            # print(f"{owner} {card_number} {transaction_date} {registration_date} {description} {operation_type} {circuit} {transaction_type} [{amount}]")
            # print(f"{transaction_date} {description} [{amount}] ({circuit})")

            # for col in range(1, sheet.ncols):
            #     cell_value = sheet.cell_value(row, col)
            #         print(cell_value)

            if self.circuit != "ALL" and circuit != self.circuit:
                continue

            transaction = CreditCardTransaction(
                owner=owner,
                card_number=card_number,
                transaction_date=transaction_date,
                registration_date=registration_date,
                description=description,
                operation_state=operation_state,
                operation_type=operation_type,
                circuit=circuit,
                transaction_type=transaction_type,
                amount=amount,
            )

            transactions.append(transaction)
        
        return transactions