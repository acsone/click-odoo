#!/usr/bin/env click-odoo

env = env  # noqa

print(env["res.users"].search([("login", "=", "admin")]).login)
