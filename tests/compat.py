from click_odoo import odoo


def set_param(env, key: str, value: str) -> None:
    if odoo.release.version_info >= (20, 0):
        env["ir.config_parameter"].set_str(key, value)
    else:
        env["ir.config_parameter"].set_param(key, value)


def get_param(env, key: str) -> str:
    if odoo.release.version_info >= (20, 0):
        return env["ir.config_parameter"].get_str(key)
    else:
        return env["ir.config_parameter"].get_param(key)
