import io
import json
import sys
from typing import Callable, List

from rich.console import Console
from rich.table import Table

from .models import AccountTransaction, CreditCardTransaction

class AccountTransactionsOutput:
    """Output a list of AccountTransaction objects in a table or a CSV file"""

    def __init__(self, transactions: List[AccountTransaction], payee_resolver: Callable[[str], str] = None):
        self.transactions = transactions
        self.payee_resolver = payee_resolver

    def table(self) -> str:
        """Output a table with the transactions"""
        console = Console(file=io.StringIO())
        
        console.print(f"Found {len(self.transactions)} transactions")

        # Create a new table
        table = Table(
            title="Account transactions",
            # box=box.SIMPLE,
        )

        # Add columns
        table.add_column("Date")
        table.add_column("Amount")
        table.add_column("Description")
        table.add_column("Description full")
        table.add_column("State")
        table.add_column("MoneyMap category")

        # Add rows
        for transaction in self.transactions:
            table.add_row(
                str(transaction.date),
                str(transaction.amount),
                transaction.description,
                transaction.description_full,
                transaction.state,
                transaction.moneymap_category,
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
        
        missing_payees = set()

        for transaction in self.transactions:
            memo = f"{transaction.description}: {transaction.description_full}"
            payee = self.resolve_payee(memo) if self.resolve_payee else None
            if not payee:
                missing_payees.add(memo)
            writer.writerow([
                str(transaction.date),
                payee,
                memo,
                str(transaction.amount),
                # transaction.description,
                # transaction.description_full,
                # transaction.state,
                # transaction.moneymap_category,
            ])
        
        if missing_payees:
            print(f"No payee found for {len(missing_payees)} transactions", file=sys.stderr)
            for memo in missing_payees:
                print(f"  - {memo} ", file=sys.stderr)
            
        return output.getvalue()
    
    def json(self) -> str:
        """Renders the transactions as a JSON string."""
        return json.dumps(self.transactions, cls=AccountTransactionsEncoder, indent=4)

class CreditCardTransactionsOutput:
    """Output a list of CreditCardTransaction objects in a table or a CSV file"""

    def __init__(self, transactions: List[CreditCardTransaction], payee_resolver: Callable[[str], str] = None):
        self.transactions = transactions
        self.payee_resolver = payee_resolver

    def table(self) -> str:
        """Output a table with the transactions"""
        console = Console(file=io.StringIO())
        
        console.print(f"Found {len(self.transactions)} transactions")

        # Create a new table
        table = Table(
            title="Credit card transactions",
            # box=box.SIMPLE,
        )

        # Add columns
        table.add_column("owner")
        table.add_column("card_number")
        table.add_column("transaction_date")
        table.add_column("registration_date")
        table.add_column("description")
        table.add_column("operation_state")
        table.add_column("operation_type")
        table.add_column("circuit")
        table.add_column("transaction_type")
        table.add_column("amount")

        # Add rows
        for transaction in self.transactions:
            table.add_row(
                transaction.owner,
                transaction.card_number,
                str(transaction.transaction_date),
                str(transaction.registration_date),
                transaction.description,
                transaction.operation_state,
                transaction.operation_type,
                transaction.circuit,
                transaction.transaction_type,
                str(transaction.amount),
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
                # formate the datetime as MM/DD/YYYY
                # transaction.transaction_date.strftime("%m/%d/%Y"),
                transaction.registration_date.strftime("%m/%d/%Y"),
                # transaction.transaction_date,
                self.resolve_payee(transaction.description) if self.resolve_payee else "",
                transaction.description,
                str(transaction.amount),
            ])
        
        return output.getvalue()
    
    def json(self) -> str:
        """Renders the transactions as a JSON string."""
        return json.dumps(self.transactions, cls=CreditCardTransactionEncoder, indent=4)

class AccountTransactionsEncoder(json.JSONEncoder):
    def default(self, obj):
        return {
            "date": obj.date.isoformat(),
            "amount": obj.amount,
            "description": obj.description,
            "description_full": obj.description_full,
            "state": obj.state,
            "moneymap_category": obj.moneymap_category,
        }

class CreditCardTransactionEncoder(json.JSONEncoder):
    def default(self, obj):
        return {
            "owner": obj.owner, 
            "card_number": obj.card_number,
            "transaction_date": obj.transaction_date.isoformat(),
            "registration_date": obj.registration_date.isoformat(),
            "description": obj.description,
            "operation_state": obj.operation_state,
            "operation_type": obj.operation_type,
            "circuit": obj.circuit,
            "transaction_type": obj.transaction_type,
            "amount": obj.amount,
        }   
