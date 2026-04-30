import json

from odoo import http
from odoo.http import Response, request
from ..product_seed import CATEGORY_LABELS


class LWebProductApiController(http.Controller):
    def _image_url(self, product_tmpl, size="image_1920"):
        stamp = int(product_tmpl.write_date.timestamp()) if product_tmpl.write_date else product_tmpl.id
        return f"/web/image/product.template/{product_tmpl.id}/{size}?unique={stamp}"

    def _get_category_key(self, product_tmpl):
        reverse_labels = {label: key for key, label in CATEGORY_LABELS.items()}
        for categ in product_tmpl.public_categ_ids:
            if categ.name in reverse_labels:
                return reverse_labels[categ.name]
        if product_tmpl.categ_id and product_tmpl.categ_id.name in reverse_labels:
            return reverse_labels[product_tmpl.categ_id.name]
        return ""

    def _get_tag(self, product_tmpl):
        tag = (product_tmpl.website_ribbon_id.name or "").strip().lower() if product_tmpl.website_ribbon_id else ""
        return tag if tag in ("new", "hot") else ""

    def _serialize_product(self, product_tmpl):
        return {
            "id": product_tmpl.id,
            "name": product_tmpl.name,
            "default_code": product_tmpl.default_code,
            "list_price": product_tmpl.list_price,
            "sale_ok": product_tmpl.sale_ok,
            "is_published": product_tmpl.is_published,
            "categ_id": product_tmpl.categ_id.id if product_tmpl.categ_id else False,
            "categ_name": product_tmpl.categ_id.name if product_tmpl.categ_id else "",
            "image_url": self._image_url(product_tmpl, "image_1920"),
            "rating_avg": getattr(product_tmpl, "rating_avg", 0.0) or 0.0,
            "rating_count": getattr(product_tmpl, "rating_count", 0) or 0,
            "tag": self._get_tag(product_tmpl),
            "category_key": self._get_category_key(product_tmpl),
            "public_categ_ids": product_tmpl.public_categ_ids.ids,
            "public_categ_names": product_tmpl.public_categ_ids.mapped("name"),
        }

    @http.route("/lweb/api/v1/products", type="http", auth="public", website=True, csrf=False, methods=["GET"])
    def lweb_products_http(self, **kwargs):
        domain = [("is_published", "=", True), ("sale_ok", "=", True)]
        if kwargs.get("default_code"):
            domain.append(("default_code", "=", kwargs["default_code"]))

        products = request.env["product.template"].sudo().search(domain, order="id asc")
        if kwargs.get("category_key"):
            products = products.filtered(lambda p: self._get_category_key(p) == kwargs["category_key"])
        if kwargs.get("tag"):
            target_tag = kwargs["tag"].strip().lower()
            products = products.filtered(lambda p: self._get_tag(p) == target_tag)

        items = [self._serialize_product(product) for product in products]
        body = json.dumps({"count": len(items), "items": items}, ensure_ascii=False)
        return Response(body, content_type="application/json;charset=utf-8", status=200)
