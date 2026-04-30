from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from ..product_seed import CATEGORY_LABELS, LWEB_PRODUCTS


class LWebController(WebsiteSale):
    def _image_url(self, product_tmpl, size="image_512"):
        stamp = int(product_tmpl.write_date.timestamp()) if product_tmpl.write_date else product_tmpl.id
        return f"/web/image/product.template/{product_tmpl.id}/{size}?unique={stamp}"

    def _category_key_from_product(self, product_tmpl):
        reverse_labels = {label: key for key, label in CATEGORY_LABELS.items()}
        for categ in product_tmpl.public_categ_ids:
            if categ.name in reverse_labels:
                return reverse_labels[categ.name]
        if product_tmpl.categ_id and product_tmpl.categ_id.name in reverse_labels:
            return reverse_labels[product_tmpl.categ_id.name]
        return "skincare"

    def _fallback_products(self):
        fallback = []
        for index, item in enumerate(LWEB_PRODUCTS, start=1):
            fallback.append(
                {
                    "id": index,
                    "name_cn": item["name"],
                    "price": item["price"],
                    "rating": item["rating"],
                    "reviews": item["reviews"],
                    "image": item["image"],
                    "tag": item.get("tag") or "",
                    "category": item["category"],
                }
            )
        return fallback

    def _get_website_products(self):
        templates = (
            request.env["product.template"]
            .sudo()
            .search([("is_published", "=", True), ("sale_ok", "=", True)], order="id asc")
        )
        if not templates:
            return self._fallback_products()

        products = []
        for item in templates:
            products.append(
                {
                    "id": item.id,
                    "name_cn": item.name,
                    "price": item.list_price,
                    "rating": getattr(item, "rating_avg", 0.0) or 0.0,
                    "reviews": getattr(item, "rating_count", 0) or 0,
                    "image": self._image_url(item, "image_512"),
                    "tag": (item.website_ribbon_id.name or "").lower() if item.website_ribbon_id else "",
                    "category": self._category_key_from_product(item),
                }
            )
        return products

    @http.route(
        ["/", "/home", "/page/homepage", "/lweb"],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
        priority=100,
    )
    def lweb_home(self, **kwargs):
        products = self._get_website_products()
        return request.render(
            "vasilia_website_base.lweb_homepage",
            {
                "featured_products": products[:4],
            },
        )

    @http.route(
        [
            "/shop",
            "/shop/page/<int:page>",
            "/shop/category/<model('product.public.category'):category>",
            "/shop/category/<model('product.public.category'):category>/page/<int:page>",
            "/lweb/products",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def shop(self, page=0, category=None, search="", **kwargs):
        products = self._get_website_products()
        return request.render("vasilia_website_base.lweb_products", {"products": products})

    @http.route(
        ["/new-arrivals", "/shop/new-arrivals", "/lweb/new-arrivals"],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
        priority=210,
    )
    def lweb_new_arrivals(self, **kwargs):
        products = [p for p in self._get_website_products() if p.get("tag") in ("new", "hot")]
        return request.render("vasilia_website_base.lweb_new_arrivals", {"products": products})


