import re
from typing import Dict, List


class PayeeResolver:
    def load_mappings(self, mappings: List[Dict[str, List[str]]]):
        self.mappings = [
            dict(
                name=payee["payee"],
                patterns=[re.compile(pattern, re.IGNORECASE) for pattern in payee["patterns"]]
            )
            for payee in mappings
        ]

    def __call__(self, memo: str) -> str:
        """Resolve a memo to a payee name"""
        # print(self.mappings)
        for payee in self.mappings:
            # print(memo, payee)
            if any(pattern.search(memo) for pattern in payee["patterns"]):
                return payee["name"]
        return ""
