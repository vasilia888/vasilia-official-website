import re
import xml.etree.ElementTree as ET
from pathlib import Path


def collect_cjk_strings_with_refs(xml_path: Path, module: str) -> dict[str, set[str]]:
    cjk_re = re.compile(r"[\u4e00-\u9fff]")
    root = ET.fromstring(xml_path.read_text(encoding="utf-8"))
    out: dict[str, set[str]] = {}

    def add(s: str, current_ref: str | None) -> None:
        s = s.strip()
        if not s:
            return
        if not cjk_re.search(s):
            return
        if s not in out:
            out[s] = set()
        if current_ref:
            out[s].add(current_ref)

    def walk(e: ET.Element, current_ref: str | None) -> None:
        # Switch context when entering a template with id.
        if e.tag == "template" and e.attrib.get("id"):
            current_ref = f"{module}.{e.attrib['id']}"

        if e.text:
            add(e.text, current_ref)
        if e.tail:
            add(e.tail, current_ref)

        for k, v in e.attrib.items():
            # Typical user-facing attrs which Odoo extracts into translations.
            if k in {"aria-label", "placeholder", "alt", "title"}:
                add(v, current_ref)

        for ch in list(e):
            walk(ch, current_ref)

    walk(root, None)
    return out


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    module = "vasilia_website_base"

    views = [
        base / "views" / "header.xml",
        base / "views" / "footer.xml",
        base / "views" / "pages.xml",
    ]

    locations: dict[str, set[str]] = {}
    for vf in views:
        per_file = collect_cjk_strings_with_refs(vf, module)
        for s, refs in per_file.items():
            locations.setdefault(s, set()).update(refs)

    strings = set(locations.keys())

    # Manual translation table for all current CN literals in templates.
    # Keep it explicit to avoid producing incorrect English silently.
    T: dict[str, str] = {
        "Vasilia 首页": "Vasilia home",
        "主导航": "Main navigation",
        "产品系列": "Collections",
        "新品专区": "New Arrivals",
        "礼盒套装": "Gift Sets",
        "品牌故事": "Our Story",
        "客户服务": "Customer Service",
        "美妆资讯": "Beauty Journal",
        "肌肤测评": "Skin Quiz",
        "联系我们": "Contact",
        "英文": "English",
        "购物袋": "Shopping Bag",
        "打开菜单": "Open menu",
        "移动菜单": "Mobile menu",
        "关闭菜单": "Close menu",
        "移动导航": "Mobile navigation",
        "微博": "Weibo",
        "微信": "WeChat",
        "小红书": "Xiaohongshu",
        "购物": "Shop",
        "关于": "About",
        "服务": "Service",
        "护肤服务": "Skincare services",
        "常见问题": "FAQ",
        "加入vasilia尊享会": "Join the vasilia Circle",
        "第一时间获取新品发布和美妆资讯": "Exclusive access to new launches and beauty insights",
        "输入您的邮箱": "Enter your email",
        "© 2024 vasilia. 保留所有权利。": "© 2024 vasilia. All rights reserved.",
        "隐私政策": "Privacy Policy",
        "服务条款": "Terms of Service",
        "探索系列": "Explore Collection",
        "返回顶部": "Back to top",
        "Vasilia | 奢华美妆与护肤": "Vasilia | Luxury Skincare and Beauty",
        "遇见你的自然之美": "Discover Your Natural Radiance",
        "源自珍稀植物精粹，融合诺贝尔奖级科研技术 — 唤醒肌肤本真光采，绽放自信魅力 — 为追求卓越的您，打造专属奢华护肤体验": "Born from rare botanical extracts, powered by Nobel-winning science — Awaken your skin's innate radiance and confidence",
        "品牌承诺": "Our Promise",
        "纯净成分、科学精准、可持续美妆。": "Clean ingredients, science-led precision, sustainable beauty.",
        "配图": "Image",
        "天然成分": "Natural Ingredients",
        "源自最优质的自然产地。": "Sourced from the finest natural origins.",
        "科学精准": "Scientific precision",
        "以前沿科研为支撑。": "Supported by leading research.",
        "可持续美妆": "Sustainable beauty",
        "致力于环境保护责任。": "Dedicated to environmental responsibility.",
        "满意顾客": "Happy Customers",
        "年科研经验": "Years of research",
        "零动物测试": "Cruelty Free",
        "科学": "Science",
        "科学研发": "Scientific R&D",
        "以科研为基底，打造兼具触感与功效的奢护体验。": "Built on research, crafted for both sensorial luxury and results.",
        "了解更多": "Learn More",
        "科研": "Research",
        "精选": "Featured",
        "精选系列": "Featured Collection",
        "我们的配方融合了大自然最优质的成分与前沿科技": "Our formulations combine nature's finest ingredients with cutting-edge science",
        "新品": "New",
        "畅销": "Best Seller",
        "查看全部": "View All",
        "用爱与科学打造": "Crafted with Love & Science",
        "vasilia创立于2013年，源于一个简单的信念：每个人都值得对自己的肌肤充满自信。我们的皮肤科医生和化妆品科学家团队不懈努力，创造出在保证安全和可持续性的同时能带来显著效果的配方。": "Founded in 2013, vasilia was born from a simple belief: everyone deserves to feel confident in their own skin. Our team of dermatologists and cosmetic scientists work tirelessly to create formulations that deliver visible results without compromising on safety or sustainability.",
        "为您的独特需求而精心打造": "Crafted for your unique needs",
        "筛选": "Filter",
        "清除筛选": "Clear filters",
        "产品分类": "Category",
        "护肤": "Skincare",
        "彩妆": "Makeup",
        "护发": "Hair Care",
        "健康": "Health",
        "价格区间": "Price Range",
        "全部价格": "All Prices",
        "$250以上": "Over $250",
        "款产品": " products",
        "排序：": "Sort by:",
        "最热门": "Most Popular",
        "最新上架": "New Arrivals",
        "价格从低到高": "Price: Low to High",
        "价格从高到低": "Price: High to Low",
        "最新上新，优先体验": "The newest drops—experience them first",
    }

    missing = sorted(strings - set(T.keys()))
    if missing:
        raise SystemExit(
            "Missing translations for these strings:\n- "
            + "\n- ".join(repr(s) for s in missing)
        )

    ordered = sorted(strings)

    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')

    out: list[str] = []
    out.append(
        "# Translation of vasilia_website_base (English). Source (msgid) is Simplified Chinese from views.\n"
    )
    out.append("#\n")
    out.append('msgid ""\n')
    out.append('msgstr ""\n')
    out.append('"Project-Id-Version: Odoo Server 18.0\\n"\n')
    out.append('"Report-Msgid-Bugs-To: \\n"\n')
    out.append('"POT-Creation-Date: 2026-04-25 00:00+0000\\n"\n')
    out.append('"PO-Revision-Date: 2026-04-25 00:00+0000\\n"\n')
    out.append('"Last-Translator: \\n"\n')
    out.append('"Language-Team: English\\n"\n')
    out.append('"Language: en_US\\n"\n')
    out.append('"MIME-Version: 1.0\\n"\n')
    out.append('"Content-Type: text/plain; charset=UTF-8\\n"\n')
    out.append('"Content-Transfer-Encoding: 8bit\\n"\n')
    out.append('"Plural-Forms: nplurals=2; plural=(n != 1);\\n"\n\n')

    for s in ordered:
        out.append(f"#. module: {module}\n")
        for ref in sorted(locations[s]):
            out.append(f"#: model_terms:ir.ui.view,arch_db:{ref}\n")
        out.append(f'msgid "{esc(s)}"\n')
        out.append(f'msgstr "{esc(T[s])}"\n\n')

    po_path = base / "i18n" / "en_US.po"
    po_path.write_text("".join(out), encoding="utf-8")

    print(f"Generated {po_path} with {len(ordered)} entries.")


if __name__ == "__main__":
    main()

