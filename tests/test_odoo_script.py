# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from __future__ import print_function
import os
import subprocess

from odoo_script import OdooEnvironment

here = os.path.abspath(os.path.dirname(__file__))


def test_odoo_env(odoo_venv):
    with OdooEnvironment(database=odoo_venv.dbname) as env:
        admin = env['res.users'].search([('id', '=', 1)])
        assert len(admin) == 1


def test_odoo_script(odoo_venv):
    """ Test simple access to env in script """
    script = os.path.join(here, 'scripts', 'script1.py')
    cmd = [
        'odoo-script',
        '-d', odoo_venv.dbname,
        '--log-level=error',
        script
    ]
    result = subprocess.check_output(cmd, universal_newlines=True)
    assert result == 'admin\n'


def test_odoo_script_args(odoo_venv):
    """ Test sys.argv in script """
    script = os.path.join(here, 'scripts', 'script2.py')
    cmd = [
        'odoo-script',
        '-d', odoo_venv.dbname,
        '--log-level=error',
        '--',
        script,
        'a', '-b',
    ]
    result = subprocess.check_output(cmd, universal_newlines=True)
    assert result == script + ' a -b\n'


def test_odoo_script_shebang(odoo_venv):
    """ Test simple access to env in script """
    script = os.path.join(here, 'scripts', 'script1.py')
    cmd = [
        script,
        '-d', odoo_venv.dbname,
        '--log-level=error',
    ]
    result = subprocess.check_output(cmd, universal_newlines=True)
    assert result == 'admin\n'


def test_odoo_script_shebang_args(odoo_venv):
    script = os.path.join(here, 'scripts', 'script2.py')
    cmd = [
        script,
        '-d', odoo_venv.dbname,
        '--log-level=error',
        '--',
        'a', '-b',
    ]
    result = subprocess.check_output(cmd, universal_newlines=True)
    assert result == script + ' a -b\n'
