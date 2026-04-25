# -*- coding: utf-8 -*-
# Part of vasilia_website_base. See LICENSE file.

def post_init_hook(env):
    """首次安裝後載入 vasilia_website_base 的 i18n/*.po 到 ir.translation（與手動升級模組等效）。"""
    mod = env["ir.module.module"].search([("name", "=", "vasilia_website_base")], limit=1)
    if mod:
        # We want view-level translations to be fully in sync with i18n/*.po.
        # Without overwrite, old msgid-based entries may linger and cause mixed languages.
        mod._update_translations(overwrite=True)
