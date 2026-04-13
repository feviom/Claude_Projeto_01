#!/usr/bin/env python3
"""
AGE Informa — Agente de geração do boletim semanal
Uso: python agent/gerar_boletim.py --semana "07 a 11 de abril de 2026"
"""

import anthropic
import argparse
import json
import os
import re
from pathlib import Path
from datetime import datetime

# ── Configuração ──────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent
SKILLS_DIR = BASE_DIR / "skills"
TEMPLATES_DIR = BASE_DIR / "templates"
EDICOES_DIR = BASE_DIR / "age-informa" / "edicoes"
CONFIG_FILE = BASE_DIR / "agent" / "config.json"

def carregar_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def salvar_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def carregar_skill():
    skill_path = SKILLS_DIR / "boletim-age-informa.md"
    return skill_path.read_text(encoding="utf-8")

def carregar_template():
    template_path = TEMPLATES_DIR / "boletim-template.html"
    return template_path.read_text(encoding="utf-8")

# ── Agente ────────────────────────────────────────────────────────────────────

def gerar_boletim(semana: str, edicao: int, ano: int) -> dict:
    """Chama a API da Anthropic para gerar o boletim."""

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    skill = carregar_skill()

    prompt = f"""Gere a edição Nº {edicao:02d}/{ano} do AGE Informa.

Período de referência: semana de {semana}.

Siga rigorosamente o processo definido na skill:
1. Use a ferramenta de busca web para varrer cada uma das 15 fontes
2. Aplique os critérios de relevância A–E
3. Selecione o Destaque da Semana e distribua os demais itens
4. Redija todo o conteúdo seguindo as regras editoriais
5. Retorne APENAS um JSON com a seguinte estrutura, sem nenhum texto fora do JSON:

{{
  "destaque": {{
    "tag": "categoria da notícia",
    "titulo": "título do destaque",
    "texto": "parágrafo de contextualização (5–8 linhas)",
    "fonte": "nome da fonte",
    "url": "https://..."
  }},
  "normas": [
    {{"fonte": "...", "titulo": "...", "resumo": "...", "url": "..."}}
  ],
  "tribunais": [
    {{"fonte": "TCE-MA ou TCU", "titulo": "...", "resumo": "...", "url": "..."}}
  ],
  "boas_praticas": [
    {{"fonte": "...", "titulo": "...", "resumo": "...", "url": "..."}}
  ],
  "capacitacao": [
    {{"fonte": "...", "nome": "...", "carga": "...", "data": "...", "url": "..."}}
  ],
  "controle_interno": [
    {{"fonte": "...", "titulo": "...", "resumo": "...", "url": "..."}}
  ],
  "internacional": [
    {{"fonte": "...", "titulo": "...", "resumo": "...", "url": "..."}}
  ],
  "whatsapp": "texto completo formatado para WhatsApp"
}}

As seções "controle_interno" e "internacional" podem ser arrays vazios [] se não houver conteúdo relevante.
"""

    print(f"🔍 Coletando notícias das fontes monitoradas...")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=skill,
        messages=[{"role": "user", "content": prompt}],
        tools=[{"type": "web_search_20250305", "name": "web_search"}]
    )

    # Extrai o texto da resposta (pode ter blocos de tool_use intermediários)
    texto_resposta = ""
    for bloco in response.content:
        if bloco.type == "text":
            texto_resposta += bloco.text

    # Parse do JSON
    try:
        # Remove possíveis marcadores de código markdown
        texto_limpo = re.sub(r"```json|```", "", texto_resposta).strip()
        conteudo = json.loads(texto_limpo)
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao interpretar resposta do agente: {e}")
        print(f"Resposta recebida:\n{texto_resposta[:500]}")
        raise

    return conteudo

# ── Montagem do HTML ──────────────────────────────────────────────────────────

def montar_html(conteudo: dict, semana: str, edicao: int, ano: int) -> str:
    """Monta o HTML final do boletim a partir do conteúdo gerado."""

    template = carregar_template()

    # Seção: normas
    normas_html = ""
    for item in conteudo.get("normas", []):
        normas_html += f"""
        <div class="news-item">
          <div class="news-accent azul-ac"></div>
          <div class="news-content">
            <div class="news-fonte">{item['fonte']}</div>
            <div class="news-titulo">{item['titulo']}</div>
            <div class="news-resumo">{item['resumo']}</div>
            <a href="{item['url']}" class="news-link" target="_blank">Acessar →</a>
          </div>
        </div>"""

    # Seção: tribunais
    tribunais_html = '<div class="grid-2">'
    cores = {"TCE-MA": "", "TCU": "vermelho-top"}
    for item in conteudo.get("tribunais", []):
        cor = cores.get(item["fonte"], "")
        tribunais_html += f"""
        <div class="card {cor}">
          <div class="card-fonte">{item['fonte']}</div>
          <div class="card-titulo">{item['titulo']}</div>
          <div class="card-texto">{item['resumo']}</div>
          {f'<a href="{item["url"]}" class="news-link" target="_blank">Ler →</a>' if item.get('url') else ''}
        </div>"""
    tribunais_html += "</div>"

    # Seção: boas práticas
    boas_praticas_html = ""
    acentos = ["dourado-ac", "azul-ac", "verde-ac"]
    for i, item in enumerate(conteudo.get("boas_praticas", [])):
        ac = acentos[i % len(acentos)]
        boas_praticas_html += f"""
        <div class="news-item">
          <div class="news-accent {ac}"></div>
          <div class="news-content">
            <div class="news-fonte">{item['fonte']}</div>
            <div class="news-titulo">{item['titulo']}</div>
            <div class="news-resumo">{item['resumo']}</div>
            <a href="{item['url']}" class="news-link" target="_blank">Acessar →</a>
          </div>
        </div>"""

    # Seção: capacitação
    capacitacao_html = '<div class="capacitacao-grid">'
    for item in conteudo.get("capacitacao", []):
        capacitacao_html += f"""
        <div class="curso-item">
          <div class="curso-info">
            <div class="curso-fonte">{item['fonte']}</div>
            <div class="curso-nome">{item['nome']}</div>
            <div class="curso-meta">{item['carga']} · {item['data']}</div>
          </div>
        </div>"""
    capacitacao_html += "</div>"

    # Seções condicionais
    controle_interno_html = ""
    if conteudo.get("controle_interno"):
        itens_ci = ""
        for item in conteudo["controle_interno"]:
            itens_ci += f"""
            <div class="news-item">
              <div class="news-accent azul-ac"></div>
              <div class="news-content">
                <div class="news-fonte">{item['fonte']}</div>
                <div class="news-titulo">{item['titulo']}</div>
                <div class="news-resumo">{item['resumo']}</div>
                <a href="{item['url']}" class="news-link" target="_blank">Acessar →</a>
              </div>
            </div>"""
        controle_interno_html = f"""
        <section class="section">
          <div class="section-header">
            <div class="section-icon azul"><svg viewBox="0 0 24 24"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg></div>
            <div class="section-name">Controle Interno em Foco</div>
          </div>
          {itens_ci}
        </section>"""

    internacional_html = ""
    if conteudo.get("internacional"):
        itens_int = ""
        for item in conteudo["internacional"]:
            itens_int += f"""
            <div class="news-item">
              <div class="news-accent azul-ac"></div>
              <div class="news-content">
                <div class="news-fonte">{item['fonte']}</div>
                <div class="news-titulo">{item['titulo']}</div>
                <div class="news-resumo">{item['resumo']}</div>
                <a href="{item['url']}" class="news-link" target="_blank">Acessar →</a>
              </div>
            </div>"""
        internacional_html = f"""
        <section class="section">
          <div class="section-header">
            <div class="section-icon azul"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg></div>
            <div class="section-name">Internacional</div>
          </div>
          {itens_int}
        </section>"""

    # Substituições no template
    d = conteudo["destaque"]
    html = template
    html = html.replace("{{EDICAO}}", f"{edicao:02d}")
    html = html.replace("{{ANO}}", str(ano))
    html = html.replace("{{SEMANA}}", semana)
    html = html.replace("{{DESTAQUE_TAG}}", d["tag"])
    html = html.replace("{{DESTAQUE_TITULO}}", d["titulo"])
    html = html.replace("{{DESTAQUE_TEXTO}}", d["texto"])
    html = html.replace("{{NORMAS}}", normas_html)
    html = html.replace("{{TRIBUNAIS}}", tribunais_html)
    html = html.replace("{{BOAS_PRATICAS}}", boas_praticas_html)
    html = html.replace("{{CAPACITACAO}}", capacitacao_html)
    html = html.replace("{{CONTROLE_INTERNO}}", controle_interno_html)
    html = html.replace("{{INTERNACIONAL}}", internacional_html)

    return html

# ── Execução principal ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Gera o boletim AGE Informa")
    parser.add_argument("--semana", required=True,
                        help='Período de referência, ex: "07 a 11 de abril de 2026"')
    parser.add_argument("--dry-run", action="store_true",
                        help="Gera sem salvar arquivo (apenas visualiza no terminal)")
    args = parser.parse_args()

    # Carrega configuração e define número da edição
    config = carregar_config()
    edicao = config["proxima_edicao"]
    ano = config["ano"]

    print(f"\n📋 AGE Informa — Edição Nº {edicao:02d}/{ano}")
    print(f"📅 Semana de referência: {args.semana}")
    print(f"🤖 Gerando com Claude Sonnet...\n")

    # Gera conteúdo via agente
    conteudo = gerar_boletim(args.semana, edicao, ano)

    print("✅ Conteúdo gerado com sucesso!")
    print(f"\n{'─'*60}")
    print("SEÇÕES INCLUÍDAS:")
    print(f"  ✓ Destaque: {conteudo['destaque']['titulo'][:60]}...")
    print(f"  ✓ Normas e Legislação: {len(conteudo.get('normas', []))} item(ns)")
    print(f"  ✓ Tribunais de Contas: {len(conteudo.get('tribunais', []))} item(ns)")
    print(f"  ✓ Boas Práticas: {len(conteudo.get('boas_praticas', []))} item(ns)")
    print(f"  ✓ Capacitação: {len(conteudo.get('capacitacao', []))} item(ns)")
    if conteudo.get("controle_interno"):
        print(f"  ✓ Controle Interno em Foco: {len(conteudo['controle_interno'])} item(ns)")
    if conteudo.get("internacional"):
        print(f"  ✓ Internacional: {len(conteudo['internacional'])} item(ns)")
    print(f"{'─'*60}\n")

    # Monta HTML
    html = montar_html(conteudo, args.semana, edicao, ano)

    if args.dry_run:
        print("⚠️  Modo dry-run — arquivo não salvo.")
        print("\nVERSÃO WHATSAPP:")
        print(conteudo.get("whatsapp", ""))
        return

    # Salva HTML
    EDICOES_DIR.mkdir(parents=True, exist_ok=True)
    nome_arquivo = f"age-informa-{edicao:02d}-{ano}.html"
    caminho = EDICOES_DIR / nome_arquivo
    caminho.write_text(html, encoding="utf-8")
    print(f"💾 Boletim salvo: {caminho}")

    # Salva versão WhatsApp
    wpp_path = EDICOES_DIR / f"age-informa-{edicao:02d}-{ano}-whatsapp.txt"
    wpp_path.write_text(conteudo.get("whatsapp", ""), encoding="utf-8")
    print(f"📱 Versão WhatsApp salva: {wpp_path}")

    # Atualiza config para próxima edição
    config["proxima_edicao"] = edicao + 1
    salvar_config(config)

    print(f"\n✅ Pronto! Edição Nº {edicao:02d}/{ano} gerada com sucesso.")
    print(f"🔗 Após publicar, acesse:")
    print(f"   https://feviom.github.io/Claude_Projeto_01/age-informa/edicoes/{nome_arquivo}")
    print(f"\n▶  Para publicar, execute:")
    print(f"   python agent/publicar.py")

if __name__ == "__main__":
    main()
