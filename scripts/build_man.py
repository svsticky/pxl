#!/usr/bin/env python
import sys

sys.path.append(".")

from click_man import core
from pxl import cli


core.write_man_pages(name="pxl", cli=cli.cli, target_dir="docs/man")
