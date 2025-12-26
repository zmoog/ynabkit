from click.testing import CliRunner
from unittest.mock import Mock, patch
import datetime
import yaml
import tempfile
import os
from ynabkit.cli import cli, describe
from ynabkit.fineco.models import AccountTransaction
from ynabkit import payee


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("cli, version ")


def test_describe_date_filtering():
    """Test that the describe function properly filters transactions by start and end dates."""
    
    # Create mock transactions with different dates
    transactions = [
        AccountTransaction(
            date=datetime.datetime(2023, 1, 15),
            amount=100.0,
            description="Transaction 1",
            description_full="Transaction 1 Full",
            state="completed",
            moneymap_category="category1",
            payee="Payee 1"
        ),
        AccountTransaction(
            date=datetime.datetime(2023, 2, 15),
            amount=200.0,
            description="Transaction 2", 
            description_full="Transaction 2 Full",
            state="completed",
            moneymap_category="category2",
            payee="Payee 2"
        ),
        AccountTransaction(
            date=datetime.datetime(2023, 3, 15),
            amount=300.0,
            description="Transaction 3",
            description_full="Transaction 3 Full", 
            state="completed",
            moneymap_category="category3",
            payee="Payee 3"
        ),
    ]
    
    # Create mock input and output objects
    mock_input = Mock()
    mock_input.read.return_value = transactions
    
    mock_output = Mock()
    mock_output.table.return_value = "mocked table output"
    
    # Create mock payee resolver
    mock_payee_resolver = Mock(spec=payee.PayeeResolver)
    mock_payee_resolver.unresolved = []
    
    # Test 1: No date filtering - should return all transactions
    with patch('ynabkit.cli.click.echo') as mock_echo:
        describe(mock_input, mock_output, mock_payee_resolver, "table", None, None)
        mock_output.table.assert_called_once()
        filtered_transactions = mock_output.table.call_args[0][0]
        assert len(filtered_transactions) == 3
    
    # Reset mocks
    mock_output.reset_mock()
    
    # Test 2: Start date filtering - should return transactions from Feb 1st onwards
    start_date = datetime.datetime(2023, 2, 1)
    with patch('ynabkit.cli.click.echo') as mock_echo:
        describe(mock_input, mock_output, mock_payee_resolver, "table", start_date, None)
        filtered_transactions = mock_output.table.call_args[0][0]
        assert len(filtered_transactions) == 2
        assert all(t.timestamp >= start_date for t in filtered_transactions)
    
    # Reset mocks  
    mock_output.reset_mock()
    
    # Test 3: End date filtering - should return transactions up to Feb 28th
    end_date = datetime.datetime(2023, 2, 28)
    with patch('ynabkit.cli.click.echo') as mock_echo:
        describe(mock_input, mock_output, mock_payee_resolver, "table", None, end_date)
        filtered_transactions = mock_output.table.call_args[0][0]
        assert len(filtered_transactions) == 2
        assert all(t.timestamp <= end_date for t in filtered_transactions)
    
    # Reset mocks
    mock_output.reset_mock()
    
    # Test 4: Both start and end date filtering - should return only Feb transaction
    start_date = datetime.datetime(2023, 2, 1)
    end_date = datetime.datetime(2023, 2, 28)
    with patch('ynabkit.cli.click.echo') as mock_echo:
        describe(mock_input, mock_output, mock_payee_resolver, "table", start_date, end_date)
        filtered_transactions = mock_output.table.call_args[0][0]
        assert len(filtered_transactions) == 1
        assert filtered_transactions[0].timestamp >= start_date
        assert filtered_transactions[0].timestamp <= end_date
        assert filtered_transactions[0].description == "Transaction 2"
    
    # Reset mocks
    mock_output.reset_mock()
    
    # Test 5: Date range with no matching transactions
    start_date = datetime.datetime(2023, 4, 1)
    end_date = datetime.datetime(2023, 4, 30)
    with patch('ynabkit.cli.click.echo') as mock_echo:
        describe(mock_input, mock_output, mock_payee_resolver, "table", start_date, end_date)
        filtered_transactions = mock_output.table.call_args[0][0]
        assert len(filtered_transactions) == 0


def test_payees_add():
    """Test the payees add command."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create a temporary payees file
        payees_file = "test_payees.yml"
        initial_payees = [
            {"name": "Existing Payee", "patterns": ["EXISTING"]}
        ]
        with open(payees_file, "w") as f:
            yaml.dump(initial_payees, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Test adding a new payee
        result = runner.invoke(
            cli,
            ["-p", payees_file, "payees", "add"],
            input="New Store\nNEW STORE PATTERN 1\nNEW STORE PATTERN 2\n\n"
        )

        assert result.exit_code == 0
        assert "✓ Added payee 'New Store' with 2 pattern(s)" in result.output

        # Verify the payee was added
        with open(payees_file, "r") as f:
            payees = yaml.safe_load(f)

        assert len(payees) == 2
        assert payees[0]["name"] == "Existing Payee"
        assert payees[1]["name"] == "New Store"
        assert payees[1]["patterns"] == ["NEW STORE PATTERN 1", "NEW STORE PATTERN 2"]


def test_payees_add_no_patterns():
    """Test the payees add command with no patterns (should abort)."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create a temporary payees file
        payees_file = "test_payees.yml"
        initial_payees = [
            {"name": "Existing Payee", "patterns": ["EXISTING"]}
        ]
        with open(payees_file, "w") as f:
            yaml.dump(initial_payees, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Test adding a payee with no patterns (just press enter for name, then enter for pattern)
        result = runner.invoke(
            cli,
            ["-p", payees_file, "payees", "add"],
            input="New Store\n\n"
        )

        assert result.exit_code == 0
        assert "No patterns entered. Aborting." in result.output

        # Verify no payee was added
        with open(payees_file, "r") as f:
            payees = yaml.safe_load(f)

        assert len(payees) == 1
        assert payees[0]["name"] == "Existing Payee"


def test_payees_lint():
    """Test the payees lint command."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create a temporary payees file with unsorted payees
        payees_file = "test_payees.yml"
        unsorted_payees = [
            {"name": "Zebra Store", "patterns": ["ZEBRA"]},
            {"name": "Apple Store", "patterns": ["APPLE"]},
            {"name": "Microsoft", "patterns": ["MSFT"]},
            {"name": "Amazon", "patterns": ["AMZN"]},
        ]
        with open(payees_file, "w") as f:
            yaml.dump(unsorted_payees, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Run lint command
        result = runner.invoke(cli, ["-p", payees_file, "payees", "lint"])

        assert result.exit_code == 0
        assert "✓ Sorted 4 payees" in result.output

        # Verify payees are sorted
        with open(payees_file, "r") as f:
            payees = yaml.safe_load(f)

        names = [p["name"] for p in payees]
        assert names == ["Amazon", "Apple Store", "Microsoft", "Zebra Store"]
        assert names == sorted(names, key=str.lower)


def test_payees_lint_case_insensitive():
    """Test that payees lint sorts case-insensitively."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create a temporary payees file with mixed case names
        payees_file = "test_payees.yml"
        unsorted_payees = [
            {"name": "zebra", "patterns": ["ZEBRA"]},
            {"name": "Apple", "patterns": ["APPLE"]},
            {"name": "MICROSOFT", "patterns": ["MSFT"]},
            {"name": "amazon", "patterns": ["AMZN"]},
        ]
        with open(payees_file, "w") as f:
            yaml.dump(unsorted_payees, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Run lint command
        result = runner.invoke(cli, ["-p", payees_file, "payees", "lint"])

        assert result.exit_code == 0

        # Verify payees are sorted case-insensitively
        with open(payees_file, "r") as f:
            payees = yaml.safe_load(f)

        names = [p["name"] for p in payees]
        assert names == ["amazon", "Apple", "MICROSOFT", "zebra"]


def test_payees_lint_empty_file():
    """Test that payees lint handles empty list gracefully."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create a payees file with an empty list
        payees_file = "test_payees.yml"
        with open(payees_file, "w") as f:
            yaml.dump([], f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Run lint command
        result = runner.invoke(cli, ["-p", payees_file, "payees", "lint"])

        assert result.exit_code == 0
        assert "✓ Sorted 0 payees" in result.output
