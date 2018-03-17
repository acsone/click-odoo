#!/usr/bin/env python
import os
import subprocess
import sys


try:
    import odoo  # noqa
    sys.exit(0)
except ImportError:
    # odoo < 10
    try:
        import openerp  # noqa
        sys.exit(0)
    except ImportError:
        # odoo not installed
        pass


odoo_dir = os.path.join(os.environ['VIRTUAL_ENV'], 'src', 'odoo')
odoo_series = os.environ['ODOO_SCRIPT_TEST_SERIES']

if not os.path.exists(odoo_dir):
    subprocess.check_call([
        'git', 'clone',
        '--depth=1',
        '-b', odoo_series,
        'https://github.com/odoo/odoo',
        odoo_dir,
    ])


subprocess.check_call([
    'pip', 'install',
    '-e', odoo_dir,
])
