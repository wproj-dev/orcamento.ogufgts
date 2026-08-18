import json

# --- CONFIGURAÇÃO ---
ARQUIVO_JSON = "fgts -reunião.json"
ARQUIVO_HTML_ORIGEM = "index.html"
ARQUIVO_HTML_DESTINO = "index_novo.html"

CAMPOS_DETALHES = [
    "A CONTRATAR AVANÇAR", 
    "A CONTRATAR GM PÚBLICO", 
    "A CONTRATAR GM PRIVADO", 
    "A CONTRATAR REFROTA PRIVADO", 
    "CONTRATADO AVANÇAR", 
    "CONTRATADO GM PÚBLICO", 
    "CONTRATADO REFROTA PRIVADO", 
    "CONTRATADO REFROTA PÚBLICO", 
    "SELEÇÃO A PUBLICAR AVANÇAR", 
    "SELEÇÃO A PUBLICAR GM PRIVADO", 
    "SELEÇÃO A PUBLICAR REFROTA PRIVADO"
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
        if valor is not None:
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

# 2. Bloco HTML unificado do FGTS (Novo Slide-Card Completo)
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
    <div class="slide-card" style="margin-top: 40px;">
        
        <!-- Cabeçalho Principal Centralizado -->
        <header class="dashboard-header">
            <h1>Fundo de Garantia do Tempo de Serviço</h1>
            <h3>Financiamento</h3>
        </header>

        <section class="dashboard-section">
"""

def gerar_secao_regiao(titulo, row):
    pac_publico = row.get("A CONTRATAR GM PÚBLICO")
    
    pac_privado = safe_sum(row, [
        "A CONTRATAR GM PRIVADO", 
        "A CONTRATAR REFROTA PRIVADO", 
        "SELEÇÃO A PUBLICAR GM PRIVADO", 
        "SELEÇÃO A PUBLICAR REFROTA PRIVADO"
    ])
    
    nao_pac = safe_sum(row, [
        "A CONTRATAR AVANÇAR", 
        "SELEÇÃO A PUBLICAR AVANÇAR"
    ])

    html = f"""
            <div style="margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid #e2e8f0;">
                <h3 class="actions-title" style="font-size: 1.1rem; margin-bottom: 12px; color: #1e293b;">{titulo}</h3>
                
                <div class="cards-row" style="grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 12px;">
                    <!-- Coluna Principal (Limite, Executado, Saldo) -->
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
    for chave_obs in ["A CONTRATAR GM PÚBLICO", "A CONTRATAR GM PRIVADO", "SELEÇÃO A PUBLICAR AVANÇAR", "SELEÇÃO A PUBLICAR GM PRIVADO"]:
        val_obs = obs.get(chave_obs)
        if val_obs:
            textos_obs.append(val_obs)
            
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

# 3. Inserção ultra segura: insere logo antes do encerramento da div presentation-wrapper
try:
    with open(ARQUIVO_HTML_ORIGEM, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # O alvo exato onde termina o primeiro card e o wrapper geral
    alvo = '  </div> \n  </div>'
    if alvo not in conteudo:
        alvo = '</div> \n  </div>'
    if alvo not in conteudo:
        alvo = '</div> \n  </div>'

    # Se achar o fechamento correto, injetamos logo ali em cima
    if '</div> \n  </div>' in conteudo or '</div> \n  </div>' in conteudo:
        # Vamos procurar pelo fechamento do container principal antes do script.js
        partes = conteudo.rsplit('</div>', 2)
        if len(partes) >= 2:
            # Reconstrói inserindo o novo bloco do FGTS bem no final do presentation-wrapper
            novo_conteudo = partes[0] + '</div>' + html_snippet + '\n  </div>\n</div>' + partes[2] if len(partes) > 2 else partes[0] + '</div>' + html_snippet + '\n  </div>\n</div>'
            
            # Garantimos que o script.js continue preservado no final
            if '<script src="script.js"></script>' not in novo_conteudo:
                novo_conteudo = conteudo.replace('<script src="script.js"></script>', html_snippet + '\n  </div>\n</div>\n\n  <script src="script.js"></script>')

            with open(ARQUIVO_HTML_DESTINO, "w", encoding="utf-8") as f:
                f.write(novo_conteudo)
            print(f"✅ Sucesso absoluto! O arquivo '{ARQUIVO_HTML_DESTINO}' foi gerado abaixo de tudo.")
        else:
            raise Exception("Estrutura não encontrada")
    else:
        # Método alternativo limpo baseado na tag do script
        script_tag = '<script src="script.js"></script>'
        if script_tag in conteudo:
            # Corta antes dos 2 últimos </div> que fecham o slide-card principal e o presentation-wrapper
            pos = conteudo.rfind('</div> \n  </div>')
            if pos == -1:
                pos = conteudo.rfind('</div>')
            
            novo_conteudo = conteudo[:pos] + html_snippet + "\n    </div>\n  </div>\n\n  " + script_tag
            with open(ARQUIVO_HTML_DESTINO, "w", encoding="utf-8") as f:
                f.write(novo_conteudo)
            print(f"✅ Sucesso alternativo aplicado em '{ARQUIVO_HTML_DESTINO}'!")
        else:
            print("❌ Erro: Estrutura do HTML não identificada.")

except Exception as e:
    print(f"❌ Erro ao processar: {e}")