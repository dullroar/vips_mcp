#!/usr/bin/env python3
"""Compatibility command for scan_secrets.py.

Run me when: I use the previous name for the context secret scan.
"""
import sys

from scan_secrets import main


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
