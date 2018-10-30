# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import click


# Wrapper options
config_opt = click.option(
    '--config', '-c', envvar=['ODOO_RC', 'OPENERP_SERVER'],
    type=click.Path(exists=True, dir_okay=False),
    help="Specify the Odoo configuration file. Other "
         "ways to provide it are with the ODOO_RC or "
         "OPENERP_SERVER environment variables, "
         "or ~/.odoorc (Odoo >= 10) "
         "or ~/.openerp_serverrc."
)

db_opt = click.option(
    '--database', '-d', envvar=['PGDATABASE'],
    help="Specify the database name. If present, this "
         "parameter takes precedence over the database "
         "provided in the Odoo configuration file."
)

log_level_opt = lambda default_log_level: click.option(
    '--log-level', default=default_log_level, show_default=True,
    help="Specify the logging level. Accepted values depend "
         "on the Odoo version, and include debug, info, "
          "warn, error."
)

logfile_opt = click.option(
    '--logfile', type=click.Path(dir_okay=False),
    help="Specify the log file."
)

rollback_opt = click.option(
    '--rollback', is_flag=True,
    help="Rollback the transaction even if the script "
         "does not raise an exception. Note that if the "
         "script itself commits, this option has no effect. "
         "This is why it is not named dry run. This option "
         "is implied when an interactive console is "
         "started."
)

# Main options
interactive_opt = click.option(
    '--interactive/--no-interactive', '-i',
    help="Inspect interactively after running the script."
)

shell_interface_opt = click.option(
    '--shell-interface',
    help="Preferred shell interface for interactive mode. Accepted "
         "values are ipython, ptpython, bpython, python. If not "
         "provided they are tried in this order."
)

script_arg = click.argument(
    'script', required=False, type=click.Path(exists=True, dir_okay=False)
)

script_args_arg = click.argument('script-args', nargs=-1)