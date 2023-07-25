# ynab

[![PyPI](https://img.shields.io/pypi/v/ynab.svg)](https://pypi.org/project/ynab/)
[![Changelog](https://img.shields.io/github/v/release/zmoog/ynab?include_prereleases&label=changelog)](https://github.com/zmoog/ynab/releases)
[![Tests](https://github.com/zmoog/ynab/workflows/Test/badge.svg)](https://github.com/zmoog/ynab/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/zmoog/ynab/blob/master/LICENSE)

YNAB Kit is a CLI tool to support data import and export from YNAB. It provides tools to convert data from Fineco and Satispay export files to YNAB CSV format.

## Installation

Install this tool using `pip`:

    pip install ynab

## Usage

For help, run:

    ynab --help

You can also use:

    python -m ynab --help

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd ynab
    python -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
