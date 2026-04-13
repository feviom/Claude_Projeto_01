# Claude Projeto 01 — AGE Informa

Repositório do sistema de geração e publicação do **AGE Informa**,
informativo semanal da Auditoria-Geral do Estado do Maranhão (AGE/MA).

## Estrutura

- `age-informa/` — portal e edições publicadas
- `agent/` — scripts Python do agente
- `skills/` — skill do agente (system prompt)
- `templates/` — template HTML do boletim

## Como gerar o boletim

### 1. Configurar a API

```bash
export ANTHROPIC_API_KEY="sua-chave-aqui"
```

### 2. Instalar dependências

```bash
pip install -r agent/requirements.txt
```

### 3. Gerar o boletim da semana

```bash
python agent/gerar_boletim.py --semana "14 a 18 de abril de 2026"
```

### 4. Revisar o boletim gerado

Abrir o arquivo em `age-informa/edicoes/age-informa-01-2026.html` no navegador.
Editar diretamente o HTML se necessário.

### 5. Publicar no GitHub Pages

```bash
python agent/publicar.py
```

O portal fica disponível em:
https://feviom.github.io/Claude_Projeto_01/age-informa/

## Fluxo semanal (Modelo 1 — Assistido)

```
Toda segunda-feira:

1. Abrir terminal na pasta do projeto
2. Executar: python agent/gerar_boletim.py --semana "DD a DD de mês de AAAA"
3. Abrir o HTML gerado no navegador e revisar
4. Ajustar se necessário (editar diretamente o HTML)
5. Executar: python agent/publicar.py
6. Copiar o texto de age-informa-NN-AAAA-whatsapp.txt e enviar ao grupo
```

## Variáveis de ambiente necessárias

| Variável | Como obter |
|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys |
