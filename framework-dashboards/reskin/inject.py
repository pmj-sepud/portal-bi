"""Injeta (ou substitui) um <style id="bi-reskin"> antes de </head> numa pagina do portal."""
import re
import sys
from pathlib import Path

PORTAL = Path(r"C:\Users\Usuário\Desktop\Dashboards HTML\portal-bi")


def inject(rel, css):
    p = PORTAL / rel
    html = p.read_text(encoding="utf-8")
    block = f'<style id="bi-reskin">\n{css}\n</style>'
    if 'id="bi-reskin"' in html:
        html = re.sub(r'<style id="bi-reskin">.*?</style>', block, html, flags=re.DOTALL)
    else:
        html = html.replace("</head>", block + "\n</head>", 1)
    p.write_text(html, encoding="utf-8")
    print("injected ->", rel, f"({len(css)} chars)")


if __name__ == "__main__":
    rel = sys.argv[1]
    css = Path(sys.argv[2]).read_text(encoding="utf-8")
    inject(rel, css)
