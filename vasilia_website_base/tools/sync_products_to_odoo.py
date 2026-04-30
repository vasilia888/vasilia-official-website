#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import base64
import os


def _load_odoo(config_path, db_name):
    import odoo
    from odoo import api, SUPERUSER_ID

    odoo.tools.config.parse_config(["-c", config_path, "-d", db_name])
    odoo.service.server.load_server_wide_modules()
    registry = odoo.modules.registry.Registry(db_name)
    return odoo, api, SUPERUSER_ID, registry


def _sync(env):
    from odoo.modules.module import get_module_path
    from odoo.addons.vasilia_website_base.product_seed import CATEGORY_LABELS, LWEB_PRODUCTS

    ProductTemplate = env["product.template"].sudo()
    PublicCategory = env["product.public.category"].sudo()
    ProductCategory = env["product.category"].sudo()
    ProductRibbon = env["product.ribbon"].sudo()
    module_path = get_module_path("vasilia_website_base")

    public_categ_map = {}
    product_categ_map = {}
    for key, label in CATEGORY_LABELS.items():
        public_categ = PublicCategory.search([("name", "=", label)], limit=1)
        if not public_categ:
            public_categ = PublicCategory.create({"name": label})
        public_categ_map[key] = public_categ.id

        product_categ = ProductCategory.search([("name", "=", label)], limit=1)
        if not product_categ:
            product_categ = ProductCategory.create({"name": label})
        product_categ_map[key] = product_categ.id

    ribbon_map = {}
    for tag_name, bg_color in (("new", "#4A90E2"), ("hot", "#E74C3C")):
        ribbon = ProductRibbon.search([("name", "=", tag_name.upper())], limit=1)
        if not ribbon:
            ribbon = ProductRibbon.create(
                {
                    "name": tag_name.upper(),
                    "bg_color": bg_color,
                    "text_color": "#FFFFFF",
                    "position": "left",
                }
            )
        ribbon_map[tag_name] = ribbon.id

    for item in LWEB_PRODUCTS:
        rel_image_path = item["image"].replace("/vasilia_website_base/", "", 1)
        image_full_path = os.path.join(module_path, rel_image_path)
        image_data = False
        if os.path.exists(image_full_path):
            with open(image_full_path, "rb") as file_obj:
                image_data = base64.b64encode(file_obj.read())

        vals = {
            "name": item["name"],
            "default_code": item["code"],
            "list_price": item["price"],
            "sale_ok": True,
            "is_published": True,
            "categ_id": product_categ_map[item["category"]],
            "public_categ_ids": [(6, 0, [public_categ_map[item["category"]]])],
        }
        tag = item.get("tag") or ""
        vals["website_ribbon_id"] = ribbon_map.get(tag) or False
        if image_data:
            vals["image_1920"] = image_data

        product_tmpl = ProductTemplate.search([("default_code", "=", item["code"])], limit=1)
        if product_tmpl:
            product_tmpl.write(vals)
        else:
            ProductTemplate.create(vals)


def main():
    parser = argparse.ArgumentParser(description="Sync LWeb products to Odoo product.template.")
    parser.add_argument("--config", default="/mnt/etc/odoo.conf", help="Path to odoo.conf")
    parser.add_argument("--db", default="1234", help="Database name")
    args = parser.parse_args()

    _, api, superuser_id, registry = _load_odoo(args.config, args.db)
    with registry.cursor() as cr:
        env = api.Environment(cr, superuser_id, {})
        _sync(env)
        cr.commit()
    print(f"LWeb products synced into database '{args.db}'.")


if __name__ == "__main__":
    main()
