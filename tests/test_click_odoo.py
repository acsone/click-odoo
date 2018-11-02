# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from __future__ import print_function

import os
import subprocess
import textwrap

import click
import psycopg2
import pytest
from click.testing import CliRunner

import click_odoo
from click_odoo import OdooEnvironment, console, odoo, odoo_bin
from click_odoo.cli import main

here = os.path.abspath(os.path.dirname(__file__))

# This hack is necessary because the way CliRunner patches
# stdout is not compatible with the Odoo logging initialization
# mechanism. Logging is therefore tested with subprocesses.
odoo.netsvc._logger_init = True


def _init_odoo_db(dbname):
    subprocess.check_call(["createdb", dbname])
    subprocess.check_call([odoo_bin, "-d", dbname, "-i", "base", "--stop-after-init"])


def _drop_db(dbname):
    subprocess.check_call(["dropdb", "--if-exists", dbname])


@pytest.fixture(scope="session")
def odoodb():
    if "CLICK_ODOO_TEST_DB" in os.environ:
        yield os.environ["CLICK_ODOO_TEST_DB"]
    else:
        dbname = "click-odoo-test-" + odoo.release.version.replace(".", "-")
        try:
            _init_odoo_db(dbname)
            yield dbname
        finally:
            _drop_db(dbname)


def test_odoo_env(odoodb):
    with OdooEnvironment(database=odoodb) as env:
        admin = env["res.users"].search([("login", "=", "admin")])
        assert len(admin) == 1


def test_click_odoo(odoodb):
    """ Test simple access to env in script """
    script = os.path.join(here, "scripts", "script1.py")
    cmd = ["click-odoo", "-d", odoodb, script]
    result = subprocess.check_output(cmd, universal_newlines=True)
    assert result == "admin\n"


def test_cli_runner(odoodb):
    """ Test simple access to env in script (through click CliRunner) """
    script = os.path.join(here, "scripts", "script1.py")
    runner = CliRunner()
    result = runner.invoke(main, ["-d", odoodb, script])
    assert result.exit_code == 0
    assert result.output == "admin\n"


def test_click_odoo_args(odoodb):
    """ Test sys.argv in script """
    script = os.path.join(here, "scripts", "script2.py")
    cmd = ["click-odoo", "-d", odoodb, "--", script, "a", "-b", "-d"]
    result = subprocess.check_output(cmd, universal_newlines=True)
    assert result == textwrap.dedent(
        """\
        sys.argv = {} a -b -d
        __name__ = __main__
    """.format(
            script
        )
    )


def test_click_odoo_shebang(odoodb):
    """ Test simple access to env in script with click-odoo shebang """
    script = os.path.join(here, "scripts", "script1.py")
    cmd = [script, "-d", odoodb]
    result = subprocess.check_output(cmd, universal_newlines=True)
    assert result == "admin\n"


def test_click_odoo_shebang_args(odoodb):
    """ Test script arguments (with click-odoo shebang) """
    script = os.path.join(here, "scripts", "script2.py")
    cmd = [script, "-d", odoodb, "--", "a", "-b", "-d"]
    result = subprocess.check_output(cmd, universal_newlines=True)
    assert result == textwrap.dedent(
        """\
        sys.argv = {} a -b -d
        __name__ = __main__
    """.format(
            script
        )
    )


def test_interactive_no_script(mocker, odoodb):
    mocker.patch.object(console.Shell, "ipython")
    mocker.patch.object(console.Shell, "python")
    mocker.patch.object(console, "_isatty", return_value=True)

    runner = CliRunner()
    result = runner.invoke(main, ["-d", odoodb])
    assert result.exit_code == 0
    assert console.Shell.ipython.call_count == 1
    assert console.Shell.python.call_count == 0


def test_interactive_no_script_preferred_shell(mocker, odoodb):
    mocker.patch.object(console.Shell, "ipython")
    mocker.patch.object(console.Shell, "python")
    mocker.patch.object(console, "_isatty", return_value=True)

    runner = CliRunner()
    result = runner.invoke(main, ["-d", odoodb, "--shell-interface=python"])
    assert result.exit_code == 0
    assert console.Shell.ipython.call_count == 0
    assert console.Shell.python.call_count == 1


def test_logging_stderr(capfd, odoodb):
    script = os.path.join(here, "scripts", "script3.py")
    cmd = ["click-odoo", "-d", odoodb, "--", script]
    subprocess.check_call(cmd)
    out, err = capfd.readouterr()
    assert not out
    assert "Modules loaded" in err
    assert "hello from script3" in err


def test_logging_logfile(tmpdir, capfd, odoodb):
    script = os.path.join(here, "scripts", "script3.py")
    logfile = tmpdir.join("mylogfile")
    cmd = ["click-odoo", "-d", odoodb, "--logfile", str(logfile), "--", script]
    subprocess.check_call(cmd)
    out, err = capfd.readouterr()
    assert not out
    logcontent = logfile.read()
    assert "Modules loaded" in logcontent
    assert "hello from script3" in logcontent


def test_env_options_withdb(odoodb, tmpdir):
    @click.command()
    @click_odoo.env_options()
    def testcmd(env):
        login = env["res.users"].search([("login", "=", "admin")]).login
        click.echo("login={}".format(login))

    # database from command line
    runner = CliRunner()
    result = runner.invoke(testcmd, ["-d", odoodb])
    assert result.exit_code == 0
    assert "login=admin\n" in result.output
    # database in config
    odoocfg1 = tmpdir / "odoo1.cfg"
    odoocfg1.write(
        textwrap.dedent(
            """\
        [options]
        db_name={}
    """.format(
                odoodb
            )
        )
    )
    result = runner.invoke(testcmd, ["-c", str(odoocfg1)])
    assert result.exit_code == 0
    assert "login=admin\n" in result.output
    # database -d has priority over db_name in config
    odoocfg2 = tmpdir / "odoo2.cfg"
    odoocfg2.write(
        textwrap.dedent(
            """\
        [options]
        db_name=notadb
    """
        )
    )
    result = runner.invoke(testcmd, ["-c", str(odoocfg2), "-d", odoodb])
    assert result.exit_code == 0
    assert "login=admin\n" in result.output
    # no -d, error
    result = runner.invoke(testcmd, [])
    assert result.exit_code != 0
    assert "No database provided" in result.output


def test_env_options_nodb(odoodb, tmpdir):
    @click.command()
    @click_odoo.env_options(with_database=False)
    def testcmd(env):
        assert not env

    # no database
    runner = CliRunner()
    result = runner.invoke(testcmd, [])
    assert result.exit_code == 0
    # -d not allowed
    result = runner.invoke(testcmd, ["-d", odoodb])
    assert result.exit_code != 0
    assert "no such option: -d" in result.output
    # db_name in config ignored
    odoocfg1 = tmpdir / "odoo1.cfg"
    odoocfg1.write(
        textwrap.dedent(
            """\
        [options]
        db_name={}
    """.format(
                odoodb
            )
        )
    )
    result = runner.invoke(testcmd, ["-c", str(odoocfg1)])
    assert result.exit_code == 0


def test_env_options_optionaldb(odoodb, tmpdir):
    @click.command()
    @click_odoo.env_options(database_required=False)
    def testcmd(env):
        if env:
            print("with env")
        else:
            print("without env")

    # no database
    runner = CliRunner()
    result = runner.invoke(testcmd, [])
    assert result.exit_code == 0
    assert "without env" in result.output
    # with database
    runner = CliRunner()
    result = runner.invoke(testcmd, ["-d", odoodb])
    assert result.exit_code == 0
    assert "with env" in result.output
    # database in config
    odoocfg1 = tmpdir / "odoo1.cfg"
    odoocfg1.write(
        textwrap.dedent(
            """\
        [options]
        db_name={}
    """.format(
                odoodb
            )
        )
    )
    result = runner.invoke(testcmd, ["-c", str(odoocfg1)])
    assert result.exit_code == 0
    assert "with env" in result.output


def test_env_options_database_must_exist(odoodb):
    @click.command()
    @click_odoo.env_options(database_must_exist=False)
    def testcmd(env):
        if env:
            print("with env")
        else:
            print("without env")

    # no database, must not exist, no env
    runner = CliRunner()
    result = runner.invoke(testcmd, ["-d", "dbthatdoesnotexist"])
    assert result.exit_code == 0
    assert "without env" in result.output

    # database exists, must not exist, env ok
    runner = CliRunner()
    result = runner.invoke(testcmd, ["-d", odoodb])
    assert result.exit_code == 0
    assert "with env" in result.output


def _cleanup_testparam(dbname):
    with psycopg2.connect(dbname=dbname) as conn:
        with conn.cursor() as cr:
            cr.execute("DELETE FROM ir_config_parameter " "WHERE key='testparam'")
            conn.commit()
    conn.close()


def _assert_testparam_present(dbname, expected):
    with psycopg2.connect(dbname=dbname) as conn:
        with conn.cursor() as cr:
            cr.execute("SELECT value FROM ir_config_parameter " "WHERE key='testparam'")
            r = cr.fetchall()
            assert len(r) == 1
            assert r[0][0] == expected
    conn.close()


def _assert_testparam_absent(dbname):
    with psycopg2.connect(dbname=dbname) as conn:
        with conn.cursor() as cr:
            cr.execute("SELECT value FROM ir_config_parameter " "WHERE key='testparam'")
            r = cr.fetchall()
            assert len(r) == 0
    conn.close()


def test_write_commit(odoodb):
    """ test commit in script """
    _cleanup_testparam(odoodb)
    script = os.path.join(here, "scripts", "script4.py")
    cmd = ["click-odoo", "-d", odoodb, "--", script, "commit"]
    subprocess.check_call(cmd)
    _assert_testparam_present(odoodb, "testvalue")


def test_write_rollback(odoodb):
    """ test rollback in script """
    _cleanup_testparam(odoodb)
    script = os.path.join(here, "scripts", "script4.py")
    cmd = ["click-odoo", "-d", odoodb, "--", script, "rollback"]
    subprocess.check_call(cmd)
    _assert_testparam_absent(odoodb)


def test_write_defaulttx(odoodb):
    """ test click-odoo commits itself """
    _cleanup_testparam(odoodb)
    script = os.path.join(here, "scripts", "script4.py")
    cmd = ["click-odoo", "-d", odoodb, "--", script]
    subprocess.check_call(cmd)
    _assert_testparam_present(odoodb, "testvalue")


def test_write_interactive_defaulttx(mocker, odoodb):
    """ test click-odoo rollbacks in interactive mode """
    mocker.patch.object(console.Shell, "python")
    mocker.patch.object(console, "_isatty", return_value=True)

    _cleanup_testparam(odoodb)
    runner = CliRunner()
    script = os.path.join(here, "scripts", "script4.py")
    cmd = ["-d", odoodb, "--interactive", "--", script]
    result = runner.invoke(main, cmd)
    assert result.exit_code == 0
    _assert_testparam_absent(odoodb)


def test_write_stdin_defaulttx(odoodb):
    _cleanup_testparam(odoodb)
    script = os.path.join(here, "scripts", "script4.py")
    cmd = ["click-odoo", "-d", odoodb, "<", script]
    subprocess.check_call(" ".join(cmd), shell=True)
    _assert_testparam_present(odoodb, "testvalue")


def test_write_raise(tmpdir, capfd, odoodb):
    """ test nothing is committed if the script raises """
    _cleanup_testparam(odoodb)
    script = os.path.join(here, "scripts", "script4.py")
    logfile = tmpdir.join("mylogfile")
    cmd = ["click-odoo", "-d", odoodb, "--logfile", str(logfile), "--", script, "raise"]
    r = subprocess.call(cmd)
    assert r != 0
    logcontent = logfile.read()
    assert "testerror" in logcontent
    out, err = capfd.readouterr()
    assert "testerror" in err
    _assert_testparam_absent(odoodb)


def test_env_cache(odoodb):
    """ test a new environment does not reuse cache """
    _cleanup_testparam(odoodb)
    with OdooEnvironment(database=odoodb) as env:
        env["ir.config_parameter"].set_param("testparam", "testvalue")
        value = env["ir.config_parameter"].get_param("testparam")
        assert value == "testvalue"
        env.cr.commit()
    _assert_testparam_present(odoodb, "testvalue")
    _cleanup_testparam(odoodb)
    _assert_testparam_absent(odoodb)
    with OdooEnvironment(database=odoodb) as env:
        value = env["ir.config_parameter"].get_param("testparam")
        assert not value


def test_env_options_addons_path():
    script = os.path.join(here, "scripts", "script5.py")

    cmd = ["click-odoo", "--", script]
    r = subprocess.call(cmd)
    assert r != 0  # addon1 not found in addons path

    addons_path = ",".join(
        [
            os.path.join(odoo.__path__[0], "addons"),
            os.path.join(os.path.dirname(__file__), "data", "addons"),
        ]
    )

    cmd = ["click-odoo", "--addons-path", addons_path, "--", script]
    r = subprocess.call(cmd)
    assert r == 0
