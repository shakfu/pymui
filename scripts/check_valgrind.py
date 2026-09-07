#!/usr/bin/env python3
"""Gate a Valgrind memcheck log on leaks attributable to pymui.

CPython leaks hundreds of KB of interpreter statics by design, so the log's
global "definitely lost" total says nothing about this extension. A record
counts only when one of its stack frames sits in the pymui extension object.

Usage:
    python scripts/check_valgrind.py valgrind_output.log
"""

import re
import sys

# microui is linked into the extension, so both share this object file.
EXTENSION = re.compile(r"pymui\.cpython-[^/\s]*\.so")
HEADING = re.compile(
    r"^\s*[\d,]+ bytes in [\d,]+ blocks are (definitely|indirectly|possibly) lost"
)
PREFIX = re.compile(r"^==\d+==\s?")


def records(text):
    """Yield (kind, lines) for each leak record in the log."""
    block = []
    for raw in text.splitlines():
        if not PREFIX.match(raw):
            continue
        line = PREFIX.sub("", raw)
        # A heading always starts a record, even where the log gives no
        # blank separator before it.
        if line.strip() and not HEADING.match(line):
            block.append(line)
            continue
        if block:
            match = HEADING.match(block[0])
            if match:
                yield match.group(1), block
        block = [line] if line.strip() else []
    if block and HEADING.match(block[0]):
        yield HEADING.match(block[0]).group(1), block


def main(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    if "HEAP SUMMARY" not in text:
        print(f"FAIL: {path} has no HEAP SUMMARY; Valgrind did not finish")
        return 1

    lost = {"definitely": [], "indirectly": [], "possibly": []}
    for kind, block in records(text):
        if any(EXTENSION.search(line) for line in block):
            lost[kind].append(block)

    for line in text.splitlines():
        if re.search(r"(lost|reachable|suppressed):|ERROR SUMMARY", line):
            print(line)
    print()

    if lost["possibly"]:
        # Cython holds module-level code objects via interior pointers, which
        # memcheck cannot distinguish from a leak. Report, do not fail.
        print(f"WARNING: {len(lost['possibly'])} possibly-lost records in pymui")
        print()

    hard = lost["definitely"] + lost["indirectly"]
    if hard:
        for block in hard:
            print("\n".join(block))
            print()
        print(f"FAIL: {len(hard)} leak records attributable to pymui")
        return 1

    print("OK: no definitely/indirectly lost blocks attributable to pymui")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: check_valgrind.py <valgrind log>")
    sys.exit(main(sys.argv[1]))
