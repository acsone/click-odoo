#!/usr/bin/env click-odoo
from __future__ import print_function

import sys

env = env  # noqa

res = " ".join(sys.argv)
print("sys.argv =", res)
print("__name__ =", __name__)
