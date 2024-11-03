from setuptools import setup
import os

VERSION = "0.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="ynabkit",
    description="CLI tool to support data import and export from YNAB",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Maurizio Branca",
    url="https://github.com/zmoog/ynabkit",
    project_urls={
        "Issues": "https://github.com/zmoog/ynabkit/issues",
        "CI": "https://github.com/zmoog/ynabkit/actions",
        "Changelog": "https://github.com/zmoog/ynabkit/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["ynabkit"],
    entry_points="""
        [console_scripts]
        ynabkit=ynabkit.cli:cli
    """,
    install_requires=["click"],
    extras_require={
        "test": [
            "openpyxl",  # Required to read .xlsx files
            "pytest",
            "rich",
            "xlrd",  # Required to read .xls files
        ]
    },
    python_requires=">=3.7",
)