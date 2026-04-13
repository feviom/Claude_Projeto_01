#!/usr/bin/env python3
"""
AGE Informa — Script de publicação no GitHub Pages
Uso: python agent/publicar.py
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "agent" / "config.json"
EDICOES_DIR = BASE_DIR / "age-informa" / "edicoes"
PORTAL_INDEX = BASE_DIR / "age-informa" / "index.html"

def listar_edicoes():
    """Lista todos os boletins HTML publicados."""
    edicoes = sorted(EDICOES_DIR.glob("age-informa-*-[0-9][0-9][0-9][0-9].html"),
                     reverse=True)
    return edicoes

def atualizar_portal(edicoes: list):
    """Atualiza o index.html do portal com a lista de edições."""

    cards_html = ""
    for edicao in edicoes:
        nome = edicao.stem  # age-informa-01-2026
        partes = nome.split("-")
        num = partes[2]
        ano = partes[3]
        cards_html += f"""
        <a href="edicoes/{edicao.name}" class="edicao-card">
          <div class="edicao-numero">Nº {num}/{ano}</div>
          <div class="edicao-nome">AGE Informa</div>
          <div class="edicao-link">Acessar edição →</div>
        </a>"""

    portal_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AGE Informa — Todas as edições</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Sans+3:wght@300;400;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --azul: #002D72; --vermelho: #C0111E;
    --dourado: #C8A84B; --texto: #2C2C2A;
    --cinza-bg: #F5F4F0;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Source Sans 3', sans-serif; background: #ECEAE4; color: var(--texto); }}
  .header {{ background: var(--azul); padding: 0; }}
  .header-stripe {{ height: 6px; background: linear-gradient(to right, #1A1A1A 33.3%, #fff 33.3% 66.6%, var(--vermelho) 66.6%); }}
  .header-inner {{ padding: 24px 40px; display: flex; align-items: center; gap: 18px; }}
  .header-inner img {{ width: 52px; height: auto; filter: drop-shadow(0 1px 3px rgba(0,0,0,0.4)); }}
  .brand-title {{ font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 900; color: #fff; }}
  .brand-title span {{ color: var(--dourado); }}
  .brand-sub {{ font-size: 11px; color: rgba(255,255,255,0.6); letter-spacing: 2px; text-transform: uppercase; margin-top: 3px; }}
  .header-bottom {{ height: 3px; background: var(--dourado); opacity: 0.5; }}
  .content {{ max-width: 900px; margin: 40px auto; padding: 0 24px; }}
  .section-title {{ font-family: 'Playfair Display', serif; font-size: 22px; color: var(--azul); margin-bottom: 24px; padding-bottom: 10px; border-bottom: 2px solid var(--dourado); }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }}
  .edicao-card {{ background: #fff; border-radius: 8px; padding: 24px; text-decoration: none; color: var(--texto); border-top: 4px solid var(--azul); box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: transform 0.15s, box-shadow 0.15s; display: block; }}
  .edicao-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.1); }}
  .edicao-numero {{ font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: var(--dourado); margin-bottom: 8px; }}
  .edicao-nome {{ font-family: 'Playfair Display', serif; font-size: 18px; font-weight: 700; color: var(--azul); margin-bottom: 12px; }}
  .edicao-link {{ font-size: 13px; color: var(--vermelho); font-weight: 600; }}
  .empty {{ text-align: center; color: #888; padding: 60px 0; font-size: 15px; }}
  .footer {{ text-align: center; padding: 40px; font-size: 12px; color: #999; margin-top: 60px; }}
</style>
</head>
<body>
<header class="header">
  <div class="header-stripe"></div>
  <div class="header-inner">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Bras%C3%A3o_do_Maranh%C3%A3o.svg/120px-Bras%C3%A3o_do_Maranh%C3%A3o.svg.png" alt="Brasão MA">
    <div>
      <div class="brand-title">AGE <span>Informa</span></div>
      <div class="brand-sub">Auditoria Geral do Estado do Maranhão</div>
    </div>
  </div>
  <div class="header-bottom"></div>
</header>
<div class="content">
  <h2 class="section-title">Todas as edições</h2>
  {'<div class="grid">' + cards_html + '</div>' if edicoes else '<p class="empty">Nenhuma edição publicada ainda.</p>'}
</div>
<footer class="footer">AGE Informa · GAUD-IV / GMQ · Auditoria Geral do Estado do Maranhão</footer>
</body>
</html>"""

    PORTAL_INDEX.write_text(portal_html, encoding="utf-8")
    print(f"✅ Portal atualizado: {len(edicoes)} edição(ões) listada(s)")

def git_push():
    """Faz commit e push das alterações."""
    cmds = [
        ["git", "add", "age-informa/"],
        ["git", "commit", "-m", f"boletim: edição publicada em {datetime.now().strftime('%d/%m/%Y %H:%M')}"],
        ["git", "push"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Erro no comando {' '.join(cmd)}:")
            print(result.stderr)
            return False
        print(f"✓ {' '.join(cmd)}")
    return True

def main():
    print("\n🚀 Publicando AGE Informa no GitHub Pages...\n")

    edicoes = listar_edicoes()
    if not edicoes:
        print("⚠️  Nenhuma edição encontrada para publicar.")
        return

    print(f"📄 {len(edicoes)} edição(ões) encontrada(s):")
    for e in edicoes:
        print(f"   - {e.name}")

    atualizar_portal(edicoes)

    print("\n📤 Enviando para o GitHub...")
    if git_push():
        print("\n✅ Publicado com sucesso!")
        print("🔗 Acesse: https://feviom.github.io/Claude_Projeto_01/age-informa/")
    else:
        print("\n⚠️  Publicação falhou. Verifique as mensagens acima.")

if __name__ == "__main__":
    main()
