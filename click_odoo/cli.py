#!/usr/bin/env python
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import runpy
import sys

import click

from . import console
from .env_options import env_options

_logger = logging.getLogger(__name__)


@click.command(
    help="Execute a python script in an initialized Odoo "
    "environment. The script has access to a 'env' global "
    "variable which is an odoo.api.Environment "
    "initialized for the given database. If no script is "
    "provided, the script is read from stdin or an "
    "interactive console is started if stdin appears "
    "to be a terminal."
)
@env_options(database_required=False, with_addons_path=True)
@click.option(
    "--interactive/--no-interactive",
    "-i",
    help="Inspect interactively after running the script.",
)
@click.option(
    "--shell-interface",
    help="Preferred shell interface for interactive mode. Accepted "
    "values are ipython, ptpython, bpython, python. If not "
    "provided they are tried in this order.",
)
@click.argument("script", required=False, type=click.Path(exists=True, dir_okay=False))
@click.argument("script-args", nargs=-1)
def main(env, interactive, shell_interface, script, script_args):
    global_vars = {"env": env}
    if script:
        sys.argv[1:] = script_args
        global_vars = runpy.run_path(
            script, init_globals=global_vars, run_name="__main__"
        )
    if not script or interactive:
        if console._isatty(sys.stdin):
            if not env:
                _logger.info("No environment set, use `-d dbname` to get one.")
            console.Shell.interact(global_vars, shell_interface)
            if env:
                env.cr.rollback()
        else:
            sys.argv[:] = [""]
            global_vars["__name__"] = "__main__"
            exec(sys.stdin.read(), global_vars)
