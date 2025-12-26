import sys
import yaml
import datetime
import click

from .fineco.inputs import AccountTransactionsInput, CreditCardTransactionsInput
from .fineco.outputs import CreditCardTransactionsOutput, AccountTransactionsOutput
from .satispay.inputs import TransactionsInput
from .satispay.outputs import TransactionsOutput
from .n26.inputs import TransactionsInput as N26TransactionsInput
from .n26.outputs import TransactionsOutput as N26TransactionsOutput
from . import payee


@click.group()
@click.version_option()
@click.option(
    "-p",
    "--payees-file",
    help="YAML file containing payee mappings",
    type=click.Path(exists=True),
    default="payees.yml",
)
@click.option(
    "--payee-output-format",
    help="Format for unknown payees output (list or yaml)",
    type=click.Choice(["list", "yaml"]),
    default="list",
)
@click.option(
    "-s",
    "--start-date",
    help="Start date",
    type=click.DateTime(),
    default=None,
)
@click.option(
    "-e",
    "--end-date",
    help="End date",
    type=click.DateTime(),
    default=None,
)
@click.pass_context
def cli(ctx: click.Context, payees_file: str, payee_output_format: str = "list", start_date: datetime.datetime = None, end_date: datetime.datetime = None):
    "CLI tool to support data import and export from YNAB"
    try:
        with open(payees_file, "r") as f:
            mappings = yaml.safe_load(f)

            payee_resolver = payee.PayeeResolver()
            payee_resolver.load_mappings(mappings)

            ctx.ensure_object(dict)
            ctx.obj["payee_resolver"] = payee_resolver
            ctx.obj["payee_output_format"] = payee_output_format
            ctx.obj["start_date"] = start_date
            ctx.obj["end_date"] = end_date

    except Exception as e:
        raise click.BadParameter(
            f"Error loading payee mappings from {payees_file}: {e}",
            param=ctx.params.get("payees_file"),
            param_hint="payees-file",
        ) from e

@cli.group()
def fineco():
    "Fineco related commands"


@cli.group()
def satispay():
    "Satispay related commands"


@cli.group()
def n26():
    "N26 related commands"


@cli.group()
@click.pass_context
def payees(ctx: click.Context):
    "Payees management commands"
    # Store payees_file in the group context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["payees_file"] = ctx.parent.params.get("payees_file", "payees.yml")


@payees.command(name="add")
@click.pass_context
def payees_add(ctx: click.Context):
    "Interactively add a new payee to the payees file"
    payees_file = ctx.obj.get("payees_file", "payees.yml")

    # Prompt for payee name
    name = click.prompt("Payee name")

    # Prompt for patterns (can add multiple)
    patterns = []
    click.echo("Enter patterns (one per line, empty line to finish):")
    while True:
        pattern = click.prompt("Pattern", default="", show_default=False)
        if not pattern:
            break
        patterns.append(pattern)

    if not patterns:
        click.echo("No patterns entered. Aborting.", err=True)
        return

    # Create new payee entry
    new_payee = {
        "name": name,
        "patterns": patterns
    }

    # Read existing payees
    with open(payees_file, "r") as f:
        existing_payees = yaml.safe_load(f) or []

    # Add new payee
    existing_payees.append(new_payee)

    # Write back
    with open(payees_file, "w") as f:
        yaml.dump(existing_payees, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    click.echo(f"✓ Added payee '{name}' with {len(patterns)} pattern(s) to {payees_file}")


@payees.command(name="lint")
@click.pass_context
def payees_lint(ctx: click.Context):
    "Sort payees by name in the payees file"
    payees_file = ctx.obj.get("payees_file", "payees.yml")

    # Read existing payees
    with open(payees_file, "r") as f:
        payees_list = yaml.safe_load(f) or []

    # Sort by name (case-insensitive)
    payees_list.sort(key=lambda p: p["name"].lower())

    # Write back
    with open(payees_file, "w") as f:
        yaml.dump(payees_list, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    click.echo(f"✓ Sorted {len(payees_list)} payees in {payees_file}")


@fineco.command(name="describe-account-transactions")
@click.argument(
    "excel-file-name",
)
@click.option(
    "-o",
    "--output-format",
    help="Output format",
    type=click.Choice(["table", "csv", "json"]),
    default="table",
)
@click.option(
    "-m",
    "--min-row",
    help="Minimum row to start reading from",
    type=int,
    default=11,
)
@click.option(
    "-c",
    "--max-col",
    help="Maximum column to read to",
    type=int,
    default=8,
)
@click.pass_context
def describe_account_transactions(ctx: click.Context, excel_file_name: str, output_format: str, min_row: int, max_col: int):
    "Read an .xlsx file containing bank account transactions and output the in a table, CSV or JSON file"
    payee_resolver = ctx.obj["payee_resolver"]
    describe(
        AccountTransactionsInput(excel_file_name, payee_resolver, min_row, max_col),
        AccountTransactionsOutput(),
        payee_resolver,
        output_format,
        ctx.obj.get("start_date"),
        ctx.obj.get("end_date"),
        ctx.obj.get("payee_output_format"),
    )


@fineco.command(name="describe-card-transactions")
@click.argument(
    "excel-file-name",
)
@click.option(
    "-o",
    "--output-format",
    help="Output format",
    type=click.Choice(["table", "csv", "json"]),
    default="table",
)
@click.option(
    "-c",
    "--circuit",
    help="Credit card circuit",
    type=click.Choice(["ALL", "BANCOMAT", "VISA", "MASTERCARD"]),
    default="ALL",
)
@click.pass_context
def describe_card_transactions(ctx: click.Context, excel_file_name: str, output_format: str, circuit: str):
    "Read an .xlsx file containing credit card transactions and output the in a table or a CSV file"
    payee_resolver = ctx.obj["payee_resolver"]
    describe(
        CreditCardTransactionsInput(excel_file_name, payee_resolver, circuit=circuit),
        CreditCardTransactionsOutput(),
        payee_resolver,
        output_format,
        ctx.obj.get("start_date"),
        ctx.obj.get("end_date"),
        ctx.obj.get("payee_output_format"),
    )

@satispay.command(name="describe-transactions")
@click.argument(
    "excel-file-name",
)
@click.option(
    "-o",
    "--output-format",
    help="Output format",
    type=click.Choice(["table", "csv", "json"]),
    default="table",
)
@click.option(
    "-e",
    "--exclude-kinds",
    help="Exclude kinds",
    type=click.Choice([
        "🏦 From Bank",
        "🏬 to a Store",
        "👤 to Person",
        "👤 from Person",
        "📱 Mobile Top-up",
    ]),
    default=None,
)
@click.pass_context
def describe_transactions(ctx: click.Context, excel_file_name: str, output_format: str, exclude_kinds: str):
    "Read an .xlsx file containing credit card transactions and output the in a table or a CSV file"
    payee_resolver = ctx.obj["payee_resolver"]
    describe(
        TransactionsInput(
            excel_file_name,
            exclude_kinds=exclude_kinds,
            payee_resolver=payee_resolver
        ),
        TransactionsOutput(),
        payee_resolver,
        output_format,
        ctx.obj.get("start_date"),
        ctx.obj.get("end_date"),
        ctx.obj.get("payee_output_format"),
    )

@n26.command(name="describe-transactions")
@click.argument(
    "csv-file-name",
)
@click.option(
    "-s",
    "--skip-header",
    help="Skip the header row",
    default=True,
)
@click.option(
    "-o",
    "--output-format",
    help="Output format",
    type=click.Choice(["table", "csv", "json"]),
    default="table",
)
@click.pass_context
def describe_n26_transactions(ctx: click.Context, csv_file_name: str, skip_header: bool, output_format: str):
    "Read an .csv file containing N26 transactions and output the in a table or a CSV file"
    payee_resolver = ctx.obj["payee_resolver"]
    describe(
        N26TransactionsInput(
            csv_file_name,
            skip_header=skip_header,
            payee_resolver=payee_resolver
        ),
        N26TransactionsOutput(),
        payee_resolver,
        output_format,
        ctx.obj.get("start_date"),
        ctx.obj.get("end_date"),
        ctx.obj.get("payee_output_format"),
    )


def describe(input, output, payee_resolver: payee.PayeeResolver, output_format: str, start_date: datetime.datetime = None, end_date: datetime.datetime = None, payee_output_format: str = "list"):
    """Read from input and write to output in the specified format."""
    transactions = input.read()

    if start_date:
        transactions = [t for t in transactions if t.timestamp >= start_date]
    if end_date:
        transactions = [t for t in transactions if t.timestamp <= end_date]

    if output_format == "table":
        click.echo(output.table(transactions))
    elif output_format == "csv":
        click.echo(output.csv(transactions))
    elif output_format == "json":
        click.echo(output.json(transactions))

    if payee_resolver.unresolved:
        if payee_output_format == "yaml":
            # Output as YAML format that can be appended to payees.yml
            unresolved_payees = []
            for memo in sorted(payee_resolver.unresolved):
                unresolved_payees.append({
                    "name": f"FIXME - {memo}",
                    "patterns": [memo]
                })
            click.echo(
                yaml.dump(unresolved_payees, default_flow_style=False, allow_unicode=True, sort_keys=False),
                file=sys.stderr,
                nl=False,

            )
        else:
            # Default list format
            click.echo(f"There are {len(payee_resolver.unresolved)} unresolved memos:", file=sys.stderr)
            for memo in payee_resolver.unresolved:
                click.echo(f"  - {memo}", file=sys.stderr)
