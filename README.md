# ynabkit

[![PyPI](https://img.shields.io/pypi/v/ynabkit.svg)](https://pypi.org/project/ynabkit/)
[![Changelog](https://img.shields.io/github/v/release/zmoog/ynabkit?include_prereleases&label=changelog)](https://github.com/zmoog/ynabkit/releases)
[![Tests](https://github.com/zmoog/ynabkit/workflows/Test/badge.svg)](https://github.com/zmoog/ynabkit/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/zmoog/ynabkit/blob/master/LICENSE)

YNAB Kit is a CLI tool to support data import and export from YNAB. It provides tools to convert data from Fineco and Satispay export files to YNAB CSV format.

## Installation

Install this tool using `pip`:

    pip install ynabkit

## Usage

For help, run:

    ynabkit --help

You can also use:

    python -m ynabkit --help

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd ynabkit
    python -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
