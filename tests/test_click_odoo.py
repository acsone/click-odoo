# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from __future__ import print_function
import logging
import os
import subprocess
import textwrap

import click
from click.testing import CliRunner

from click_odoo import OdooEnvironment, env_options
from click_odoo.cli import main
from click_odoo import console

here = os.path.abspath(os.path.dirname(__file__))

try:
    import odoo
    import odoo.api  # noqa
except ImportError:
    import openerp as odoo
    import openerp.api  # noqa

# see also scripts/install_odoo.py
dbname = 'click-odoo-test-%s-%s' % odoo.release.version_info[:2]


def test_odoo_env():
    with OdooEnvironment(database=dbname) as env:
        admin = env['res.users'].search([('id', '=', 1)])
        assert len(admin) == 1


def test_click_odoo():
    """ Test simple access to env in script """
    script = os.path.join(here, 'scripts', 'script1.py')
    cmd = [
        'click-odoo',
        '-d', dbname,
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
        script
    ])
    assert result.exit_code == 0
    assert result.output == 'admin\n'


def test_click_odoo_args():
    """ Test sys.argv in script """
    script = os.path.join(here, 'scripts', 'script2.py')
    cmd = [
        'click-odoo',
        '-d', dbname,
        '--',
        script,
        'a', '-b', '-d',
    ]
    result = subprocess.check_output(cmd, universal_newlines=True)
    assert result == textwrap.dedent("""\
        sys.argv = {} a -b -d
        __name__ = __main__
    """.format(script))


def test_click_odoo_shebang():
    """ Test simple access to env in script """
    script = os.path.join(here, 'scripts', 'script1.py')
    cmd = [
        script,
        '-d', dbname,
    ]
    result = subprocess.check_output(cmd, universal_newlines=True)
    assert result == 'admin\n'


def test_click_odoo_shebang_args():
    script = os.path.join(here, 'scripts', 'script2.py')
    cmd = [
        script,
        '-d', dbname,
        '--',
        'a', '-b', '-d',
    ]
    result = subprocess.check_output(cmd, universal_newlines=True)
    assert result == textwrap.dedent("""\
        sys.argv = {} a -b -d
        __name__ = __main__
    """.format(script))


def test_interactive_no_script(mocker):
    mocker.patch.object(console.Shell, 'ipython')
    mocker.patch.object(console.Shell, 'python')
    mocker.patch.object(console, '_isatty', return_value=True)

    runner = CliRunner()
    result = runner.invoke(main, [
        '-d', dbname,
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
        '--shell-interface=python',
    ])
    assert result.exit_code == 0
    assert console.Shell.ipython.call_count == 0
    assert console.Shell.python.call_count == 1


def test_logging_stderr(capfd):
    script = os.path.join(here, 'scripts', 'script3.py')
    cmd = [
        'click-odoo',
        '-d', dbname,
        '--',
        script,
    ]
    subprocess.check_call(cmd)
    out, err = capfd.readouterr()
    assert "Modules loaded" in err
    assert "hello from script3" in err


def test_logging_logfile(tmpdir):
    @click.command()
    @env_options()
    def testcmd(env):
        logging.getLogger(__name__).info("hello from testcmd")

    logfile = tmpdir.join('log')

    runner = CliRunner()
    result = runner.invoke(testcmd, [
        '-d', dbname,
        '--logfile', str(logfile),
    ])
    assert result.exit_code == 0
    logcontent = logfile.read()
    assert "Modules loaded" in logcontent
    assert "hello from testcmd" in logcontent
