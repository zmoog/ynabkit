from typing import List, Callable
from .models import Transaction
import io
import json
from rich.console import Console
from rich.table import Table


class TransactionsOutput:
    def __init__(self, transactions: List[Transaction], payee_resolver: Callable[[str], str]):
        self.transactions = transactions
        self.payee_resolver = payee_resolver

    def table(self) -> str:
        """Output a table with the transactions"""
        console = Console(file=io.StringIO())
        
        console.print(f"Found {len(self.transactions)} transactions")

        # Create a new table
        table = Table(
            title="N26 transactions",
        )

        # Add columns
        table.add_column("booking_date")
        table.add_column("value_date")
        table.add_column("partner_name")
        table.add_column("partner_iban")
        table.add_column("type")
        table.add_column("payment_reference")
        table.add_column("account_name")
        table.add_column("amount_eur")
        table.add_column("original_amount")
        table.add_column("original_currency")
        table.add_column("exchange_rate")   

        for transaction in self.transactions:
            table.add_row(
                str(transaction.booking_date.strftime("%Y-%m-%d")),
                str(transaction.value_date.strftime("%Y-%m-%d")),
                transaction.partner_name,
                transaction.partner_iban,
                transaction.type,
                transaction.payment_reference,
                transaction.account_name,
                str(transaction.amount_eur),
                str(transaction.original_amount),
                transaction.original_currency,
                str(transaction.exchange_rate),
            )

        # turn table into a string using the Console
        console.print(table)

        return console.file.getvalue()

    def csv(self) -> str:
        """Output a CSV string with the transactions.
        
        It produces CSV using the YNAB format. See https://docs.youneedabudget.com/article/921-formatting-csv-file
        to learn more about the format.
        """

        import csv
        output = io.StringIO()
        
        writer = csv.writer(output)
        writer.writerow(["Date", "Payee", "Memo", "Amount"])
        for transaction in self.transactions:
            writer.writerow([
                transaction.booking_date.strftime("%m/%d/%Y"),
                self.payee_resolver(transaction.partner_name) if self.payee_resolver else "",
                transaction.partner_name,
                str(transaction.amount_eur),
            ])
        
        return output.getvalue()        

    def json(self) -> str:
        """Output the transactions as a JSON string"""
        return json.dumps(self.transactions, cls=TransactionEncoder, indent=4)
\
class TransactionEncoder(json.JSONEncoder):
    def default(self, obj):
        return {
            "booking_date": obj.booking_date.isoformat(),
            "value_date": obj.value_date.isoformat(),
            "partner_name": obj.partner_name,
            "partner_iban": obj.partner_iban,
            "type": obj.type,
            "payment_reference": obj.payment_reference,
            "account_name": obj.account_name,
            "amount_eur": obj.amount_eur,
            "original_amount": obj.original_amount,
            "original_currency": obj.original_currency,
            "exchange_rate": obj.exchange_rate,
        }   