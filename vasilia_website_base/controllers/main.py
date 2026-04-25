from odoo import http
from odoo.http import request


class LWebController(http.Controller):
    def _demo_products(self):
        return [
            {"id": 1, "name_cn": "晶透焕亮精华液", "price": 189, "rating": 4.8, "reviews": 342, "image": "/vasilia_website_base/static/src/source/images/jinghuaye/bushui/Rectangle-463.jpg", "tag": "hot", "category": "skincare"},
            {"id": 2, "name_cn": "安瓶焕亮修护精华", "price": 129, "rating": 4.9, "reviews": 298, "image": "/vasilia_website_base/static/src/source/images/jinghuaye/bushui/Rectangle-464.jpg", "tag": "new", "category": "skincare"},
            {"id": 3, "name_cn": "水光鲜妍精华", "price": 156, "rating": 4.7, "reviews": 489, "image": "/vasilia_website_base/static/src/source/images/jinghuaye/bushui/Rectangle-466.jpg", "tag": "new", "category": "skincare"},
            {"id": 4, "name_cn": "海蓝水光精华", "price": 168, "rating": 4.7, "reviews": 242, "image": "/vasilia_website_base/static/src/source/images/jinghuaye/bushui/Rectangle-465.jpg", "tag": "", "category": "skincare"},
            {"id": 5, "name_cn": "唇雾丝绒小方管", "price": 68, "rating": 4.8, "reviews": 156, "image": "/vasilia_website_base/static/src/source/images/meizhuang/1.jpg", "tag": "new", "category": "makeup"},
            {"id": 6, "name_cn": "大地色眼影九宫格", "price": 238, "rating": 4.8, "reviews": 224, "image": "/vasilia_website_base/static/src/source/images/yanyingpang/dap/Rectangle-461.jpg", "tag": "new", "category": "makeup"},
            {"id": 7, "name_cn": "亮肤遮瑕粉底液", "price": 186, "rating": 4.7, "reviews": 200, "image": "/vasilia_website_base/static/src/source/images/fengdi/bushui/1.jpg", "tag": "hot", "category": "makeup"},
            {"id": 8, "name_cn": "晶透高光修容盘", "price": 229, "rating": 4.7, "reviews": 198, "image": "/vasilia_website_base/static/src/source/images/yanyingpang/dap/Rectangle-462.jpg", "tag": "", "category": "makeup"},
            {"id": 9, "name_cn": "光感隔离妆前乳", "price": 149, "rating": 4.6, "reviews": 233, "image": "/vasilia_website_base/static/src/source/images/yanshuang/1/2.jpg", "tag": "new", "category": "health"},
            {"id": 10, "name_cn": "四色矿物眼影盘", "price": 168, "rating": 4.8, "reviews": 214, "image": "/vasilia_website_base/static/src/source/images/yanyingpang/danse/5.jpg", "tag": "new", "category": "health"},
            {"id": 11, "name_cn": "草本修护面膜", "price": 128, "rating": 4.8, "reviews": 274, "image": "/vasilia_website_base/static/src/source/images/hufas/shenhuli/Rectangle-469.jpg", "tag": "", "category": "skincare"},
            {"id": 12, "name_cn": "修护精华喷雾", "price": 132, "rating": 4.8, "reviews": 221, "image": "/vasilia_website_base/static/src/source/images/hufas/shenhuli/Rectangle-466.jpg", "tag": "", "category": "haircare"},
            {"id": 13, "name_cn": "密集睫毛膏", "price": 128, "rating": 4.8, "reviews": 324, "image": "/vasilia_website_base/static/src/source/images/hufuyi/yan/13.jpg", "tag": "new", "category": "haircare"},
            {"id": 14, "name_cn": "纤长睫毛膏", "price": 128, "rating": 4.8, "reviews": 279, "image": "/vasilia_website_base/static/src/source/images/hufuyi/yan/14.jpg", "tag": "", "category": "haircare"},
            {"id": 15, "name_cn": "双头防水睫毛膏", "price": 136, "rating": 4.7, "reviews": 197, "image": "/vasilia_website_base/static/src/source/images/hufuyi/yan/15.jpg", "tag": "", "category": "haircare"},
            {"id": 16, "name_cn": "丝绒哑光口红", "price": 108, "rating": 4.7, "reviews": 201, "image": "/vasilia_website_base/static/src/source/images/hufuyi/ri/2.jpg", "tag": "new", "category": "makeup"},
        ]

    @http.route(
        ["/", "/home", "/page/homepage", "/lweb"],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
        priority=100,
    )
    def lweb_home(self, **kwargs):
        products = self._demo_products()
        return request.render(
            "vasilia_website_base.lweb_homepage",
            {
                "featured_products": products[:4],
            },
        )

    @http.route(
        ["/shop", "/shop/page/<int:page>", "/lweb/products"],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
        priority=200,
    )
    def lweb_products(self, **kwargs):
        products = self._demo_products()
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
        products = [p for p in self._demo_products() if p.get("tag") in ("new", "hot")]
        return request.render("vasilia_website_base.lweb_new_arrivals", {"products": products})

