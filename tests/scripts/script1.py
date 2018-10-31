#!/usr/bin/env click-odoo
from __future__ import print_function

env = env  # noqa

print(env["res.users"].search([("login", "=", "admin")]).login)
