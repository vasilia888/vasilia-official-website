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
        if e.tag == "template" and e.attrib.get("id"):
            current_ref = f"{module}.{e.attrib['id']}"

        if e.text:
            add(e.text, current_ref)
        if e.tail:
            add(e.tail, current_ref)

        for k, v in e.attrib.items():
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

    ordered = sorted(locations.keys())

    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')

    out: list[str] = []
    out.append(
        "# Translation of vasilia_website_base (Chinese Simplified). Source (msgid) is Simplified Chinese from views.\n"
    )
    out.append("#\n")
    out.append('msgid ""\n')
    out.append('msgstr ""\n')
    out.append('"Project-Id-Version: Odoo Server 18.0\\n"\n')
    out.append('"Report-Msgid-Bugs-To: \\n"\n')
    out.append('"POT-Creation-Date: 2026-04-25 00:00+0000\\n"\n')
    out.append('"PO-Revision-Date: 2026-04-25 00:00+0000\\n"\n')
    out.append('"Last-Translator: \\n"\n')
    out.append('"Language-Team: Chinese (Simplified)\\n"\n')
    out.append('"Language: zh_CN\\n"\n')
    out.append('"MIME-Version: 1.0\\n"\n')
    out.append('"Content-Type: text/plain; charset=UTF-8\\n"\n')
    out.append('"Content-Transfer-Encoding: 8bit\\n"\n')
    out.append('"Plural-Forms: nplurals=1; plural=0;\\n"\n\n')

    for s in ordered:
        out.append(f"#. module: {module}\n")
        for ref in sorted(locations[s]):
            out.append(f"#: model_terms:ir.ui.view,arch_db:{ref}\n")
        out.append(f'msgid "{esc(s)}"\n')
        out.append(f'msgstr "{esc(s)}"\n\n')

    po_path = base / "i18n" / "zh_CN.po"
    po_path.write_text("".join(out), encoding="utf-8")
    print(f"Generated {po_path} with {len(ordered)} entries.")


if __name__ == "__main__":
    main()

