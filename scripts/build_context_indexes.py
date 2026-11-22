#!/usr/bin/env python3
"""Compatibility command for build_indexes.py.

Run me when: I use the previous name to rebuild or check indexes.
"""
import sys

from build_indexes import main


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
