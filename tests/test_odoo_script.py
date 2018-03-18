# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from __future__ import print_function
import os
import subprocess

from click.testing import CliRunner

from odoo_script import OdooEnvironment
from odoo_script.cli import main
from odoo_script import console

here = os.path.abspath(os.path.dirname(__file__))

try:
    import odoo
    import odoo.api  # noqa
except ImportError:
    import openerp as odoo
    import openerp.api  # noqa

# see also scripts/install_odoo.py
dbname = 'odoo-script-test-%s-%s' % odoo.release.version_info[:2]


def test_odoo_env():
    with OdooEnvironment(database=dbname) as env:
        admin = env['res.users'].search([('id', '=', 1)])
        assert len(admin) == 1


def test_odoo_script():
    """ Test simple access to env in script """
    script = os.path.join(here, 'scripts', 'script1.py')
    cmd = [
        'odoo-script',
        '-d', dbname,
        '--log-level=error',
        script
    ]
    result = subprocess.check_output(cmd, universal_newlines=True)
    assert result == 'admin\n'


def test_cli_runner():
    """ Test simple access to env in script (through click CliRunner) """
    script = os.path.join(here, 'scripts', 'script1.py')
    runner = CliRunner()
    result = runner.invoke(main, [
        '-d', dbname,
        '--log-level=error',
        script
    ])
    assert result.exit_code == 0
    assert result.output == 'admin\n'


def test_odoo_script_args():
    """ Test sys.argv in script """
    script = os.path.join(here, 'scripts', 'script2.py')
    cmd = [
        'odoo-script',
        '-d', dbname,
        '--log-level=error',
        '--',
        script,
        'a', '-b', '-d',
    ]
    result = subprocess.check_output(cmd, universal_newlines=True)
    assert result == script + ' a -b -d\n'


def test_odoo_script_shebang():
    """ Test simple access to env in script """
    script = os.path.join(here, 'scripts', 'script1.py')
    cmd = [
        script,
        '-d', dbname,
        '--log-level=error',
    ]
    result = subprocess.check_output(cmd, universal_newlines=True)
    assert result == 'admin\n'


def test_odoo_script_shebang_args():
    script = os.path.join(here, 'scripts', 'script2.py')
    cmd = [
        script,
        '-d', dbname,
        '--log-level=error',
        '--',
        'a', '-b', '-d',
    ]
    result = subprocess.check_output(cmd, universal_newlines=True)
    assert result == script + ' a -b -d\n'


def test_interactive_no_script(mocker):
    mocker.patch.object(console.Shell, 'ipython')
    mocker.patch.object(console.Shell, 'python')
    mocker.patch.object(console, '_isatty', return_value=True)

    runner = CliRunner()
    result = runner.invoke(main, [
        '-d', dbname,
        '--log-level=error',
    ])
    assert result.exit_code == 0
    assert console.Shell.ipython.call_count == 1
    assert console.Shell.python.call_count == 0


def test_interactive_no_script_preferred_shell(mocker):
    mocker.patch.object(console.Shell, 'ipython')
    mocker.patch.object(console.Shell, 'python')
    mocker.patch.object(console, '_isatty', return_value=True)

    runner = CliRunner()
    result = runner.invoke(main, [
        '-d', dbname,
        '--log-level=error',
        '--shell-interface=python',
    ])
    assert result.exit_code == 0
    assert console.Shell.ipython.call_count == 0
    assert console.Shell.python.call_count == 1
