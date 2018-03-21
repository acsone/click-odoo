# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import code
import logging
import os

_logger = logging.getLogger(__name__)


class Shell(object):

    shells = ['ipython', 'ptpython', 'bpython', 'python']

    @classmethod
    def python(cls, local_vars):
        console = code.InteractiveConsole(locals=local_vars)
        import rlcompleter  # noqa
        import readline
        readline.parse_and_bind("tab: complete")
        console.interact()

    @classmethod
    def ipython(cls, local_vars):
        from IPython import start_ipython
        start_ipython(argv=[], user_ns=local_vars)

    @classmethod
    def ptpython(cls, local_vars):
        from ptpython.repl import embed
        embed({}, local_vars)

    @classmethod
    def bpython(cls, local_vars):
        from bpython import embed
        embed(local_vars)

    @classmethod
    def interact(cls, local_vars, preferred_shell=None):
        if preferred_shell:
            shells_to_try = [preferred_shell] + Shell.shells
        else:
            shells_to_try = Shell.shells

        for shell in shells_to_try:
            try:
                return getattr(cls, shell)(local_vars)
            except ImportError:
                pass
            except Exception:
                _logger.error("Could not start '%s' shell.", shell)
                _logger.debug("Shell error:", exc_info=True)

        _logger.error("Could not start any shell.")


def _isatty(stream):
    try:
        return os.isatty(stream.fileno())
    except Exception:
        return False
