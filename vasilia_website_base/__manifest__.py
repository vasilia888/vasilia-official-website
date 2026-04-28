{
    "name": "Vasilia Website Base",
    "version": "18.0.1.1.0",
    "category": "Website",
    "summary": "Vasilia-style homepage, products and new arrivals pages",
    "author": "Grit",
    "website": "https://ifangtech.com",
    "depends": ["website"],
    "data": [
        "views/header.xml",
        "views/footer.xml",
        "views/pages.xml",
    ],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "post_init_hook": "post_init_hook",
}

