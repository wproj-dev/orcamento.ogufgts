import json
import re

# --- CONFIGURAÇÃO ---
ARQUIVO_JSON = "fgts -reunião.json"
ARQUIVO_HTML_ORIGEM = "index.html"
ARQUIVO_HTML_DESTINO = "index.html"

# LISTA ATUALIZADA COM AS NOVAS COLUNAS DO EXCEL
CAMPOS_DETALHES = [
    "A CONTRATAR AVANÇAR", 
    "A CONTRATAR GM PRIVADO", 
    "A CONTRATAR GM PÚBLICO", 
    "A CONTRATAR REFROTA PRIVADO", 
    "A CONTRATAR REFROTA PÚBLICO", 
    "SELEÇÃO A PUBLICAR AVAÇAR", 
    "SELEÇÃO A PUBLICAR AVANÇAR",
    "SELEÇÃO A PUBLICAR REFROTA PRIVADO", 
    "CONTRATADO AVANÇAR", 
    "CONTRATADO REFROTA PRIVADO", 
    "CONTRATADO REFROTA PÚBLICO", 
    "CONTRATADO GM PÚBLICO"
]

def fmt(val):
    if val is None or val == "": return "-"
    if isinstance(val, (int, float)):
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(val)

def safe_sum(row, chaves):
    total = 0.0
    tem_valor = False
    for c in chaves:
        v = row.get(c)
        if isinstance(v, (int, float)):
            total += v
            tem_valor = True
    return total if tem_valor else None

def gerar_submenu(row):
    html = '<details class="submenu"><summary>Ver detalhes</summary><ul>'
    for campo in CAMPOS_DETALHES:
        valor = row.get(campo)
        if valor is not None and valor != "": # Evita mostrar campos vazios caso use AVAÇAR ou AVANÇAR
            html += f'<li><span class="sub-label">{campo}:</span> <span class="sub-value">{fmt(valor)}</span></li>'
    html += '</ul></details>'
    return html

# 1. Carrega os dados do JSON
try:
    with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"❌ Erro: O arquivo '{ARQUIVO_JSON}' não foi encontrado.")
    exit()

# 2. Bloco HTML unificado do FGTS
html_snippet = """
    <!-- ESTILOS EXCLUSIVOS DO FGTS -->
    <style>
        .submenu { background: #ffffff; padding: 10px 14px; border-radius: 8px; border: 1px solid #e2e8f0; cursor: pointer; font-size: 0.85rem; margin-top: 10px; }
        .submenu summary { font-weight: 600; color: #475569; outline: none; }
        .submenu ul { list-style: none; padding: 8px 0 0 0; margin: 0; }
        .submenu li { padding: 5px 0; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; color: #475569; }
        .sub-label { font-weight: 500; }
        .sub-value { font-weight: 600; color: #1e293b; }
    </style>

    <!-- NOVO SLIDE-CARD UNIFICADO PARA O FGTS (Abaixo de tudo) -->
    <div class="slide-card" style="margin-top: 40px;" id="bloco-fgts-dinamico">
        
        <!-- Cabeçalho Principal Centralizado -->
        <header class="dashboard-header">
            <h1>Fundo de Garantia do Tempo de Serviço</h1>
            <h3>Financiamento</h3>
        </header>

        <section class="dashboard-section">
"""

def gerar_secao_regiao(titulo, row):
    # CÁLCULOS ATUALIZADOS COM AS NOVAS COLUNAS
    pac_publico = safe_sum(row, [
        "A CONTRATAR GM PÚBLICO",
        "A CONTRATAR REFROTA PÚBLICO" # Novo campo adicionado aqui
    ])
    
    pac_privado = safe_sum(row, [
        "A CONTRATAR GM PRIVADO", 
        "A CONTRATAR REFROTA PRIVADO", 
        "SELEÇÃO A PUBLICAR REFROTA PRIVADO"
    ])
    
    nao_pac = safe_sum(row, [
        "A CONTRATAR AVANÇAR", 
        "SELEÇÃO A PUBLICAR AVAÇAR", # Com erro de digitação do Excel
        "SELEÇÃO A PUBLICAR AVANÇAR" # Escrito corretamente (segurança)
    ])

    html = f"""
            <div style="margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid #e2e8f0;">
                <h3 class="actions-title" style="font-size: 1.1rem; margin-bottom: 12px; color: #1e293b;">{titulo}</h3>
                
                <div class="cards-row" style="grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 12px;">
                    <!-- Coluna Principal -->
                    <div class="info-card" style="background: #f8fafc; text-align: left;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr><td style="padding: 6px 0; border-bottom: 1px solid #e2e8f0; color: #64748b; font-weight: 500;">Limite</td><td style="padding: 6px 0; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: 600; color: #0f172a;">{fmt(row.get('LIMITE'))}</td></tr>
                            <tr><td style="padding: 6px 0; border-bottom: 1px solid #e2e8f0; color: #64748b; font-weight: 500;">Valor Executado</td><td style="padding: 6px 0; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: 600; color: #0f172a;">{fmt(row.get('VALOR EXECUTADO'))}</td></tr>
                            <tr><td style="padding: 6px 0; border-bottom: none; color: #64748b; font-weight: 500;">Saldo</td><td style="padding: 6px 0; border-bottom: none; text-align: right; font-weight: 600; color: #0f172a;">{fmt(row.get('SALDO'))}</td></tr>
                        </table>
                    </div>
                    
                    <!-- Coluna Previsto -->
                    <div class="info-card" style="background: #f8fafc; text-align: left;">
                        <h4 style="margin-top: 0; color: #ea580c; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px;">Previsto</h4>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr><td style="padding: 6px 0; border-bottom: 1px solid #e2e8f0; color: #64748b; font-weight: 500;">PAC Público</td><td style="padding: 6px 0; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: 600; color: #0f172a;">{fmt(pac_publico)}</td></tr>
                            <tr><td style="padding: 6px 0; border-bottom: 1px solid #e2e8f0; color: #64748b; font-weight: 500;">PAC Privado</td><td style="padding: 6px 0; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: 600; color: #0f172a;">{fmt(pac_privado)}</td></tr>
                            <tr><td style="padding: 6px 0; border-bottom: none; color: #64748b; font-weight: 500;">Não PAC</td><td style="padding: 6px 0; border-bottom: none; text-align: right; font-weight: 600; color: #0f172a;">{fmt(nao_pac)}</td></tr>
                        </table>
                    </div>
                </div>

                {gerar_submenu(row)}
            </div>
    """
    return html

# Bloco Brasil
brasil = next((item for item in data if item.get("REGIÃO") == "Brasil"), None)
if brasil:
    html_snippet += gerar_secao_regiao("Brasil", brasil)

# Blocos Regionais
for row in data:
    regiao = row.get("REGIÃO")
    if regiao and regiao not in ["Brasil", "Observações:"]:
        html_snippet += gerar_secao_regiao(regiao, row)

# Observações
obs = next((item for item in data if item.get("REGIÃO") == "Observações:"), None)
if obs:
    textos_obs = []
    # Usando as colunas atuais que podem conter observações
    for chave_obs in ["A CONTRATAR GM PÚBLICO", "A CONTRATAR GM PRIVADO", "A CONTRATAR REFROTA PRIVADO", "SELEÇÃO A PUBLICAR AVAÇAR"]:
        val_obs = obs.get(chave_obs)
        if val_obs:
            textos_obs.append(val_obs)
            
    if textos_obs:
        html_snippet += f"""
                <div>
                    <h3 class="actions-title" style="font-size: 1.1rem; margin-bottom: 12px; color: #1e293b;">Observações</h3>
                    <p style="font-size: 0.9rem; color: #475569; white-space: pre-line; line-height: 1.6; margin: 0;">{"<br><br>".join(textos_obs)}</p>
                </div>
        """

html_snippet += """
        </section>
        
        <footer class="slide-footer">
            <span>2026</span>
        </footer>
    </div>
"""

# 3. Leitura e injeção limpa no HTML usando Marcadores à Prova de Falhas
try:
    with open(ARQUIVO_HTML_ORIGEM, "r", encoding="utf-8") as f:
        conteudo = f.read()

    marcador_inicio = "<!-- INICIO_FGTS -->"
    marcador_fim = "<!-- FIM_FGTS -->"

    if marcador_inicio in conteudo and marcador_fim in conteudo:
        padrao = re.compile(f"{marcador_inicio}.*?{marcador_fim}", re.DOTALL)
        novo_conteudo = re.sub(padrao, f"{marcador_inicio}\n{html_snippet}\n{marcador_fim}", conteudo)
        
        with open(ARQUIVO_HTML_DESTINO, "w", encoding="utf-8") as f:
            f.write(novo_conteudo)
        print(f"✅ Sucesso! O arquivo '{ARQUIVO_HTML_DESTINO}' foi atualizado com a nova estrutura de colunas do Excel.")
    else:
        print("❌ Erro: Os marcadores não foram encontrados no index.html.")
        print("Abra o index.html e cole <!-- INICIO_FGTS --> e <!-- FIM_FGTS --> no final do arquivo, logo antes da tag <script>.")

except Exception as e:
    print(f"❌ Erro ao processar: {e}")