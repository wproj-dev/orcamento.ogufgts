// Conversor e Formatador de Valores
function formatarMoeda(valor) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor || 0);
}

function parseValor(valor) {
  if (typeof valor === 'number') return valor;
  if (!valor) return 0;
  const limpo = valor.toString()
    .replace(/R\$\s?/g, '')
    .replace(/\./g, '')
    .replace(',', '.')
    .trim();
  return parseFloat(limpo) || 0;
}

// Leitor Genérico de Arquivos JSON Locais
async function carregarJSON(caminho) {
  try {
    const resposta = await fetch(caminho);
    if (!resposta.ok) throw new Error(`Status ${resposta.status}`);
    return await resposta.json();
  } catch (e) {
    console.warn(`[Aviso] Não foi possível carregar '${caminho}':`, e.message);
    return null;
  }
}

// Controlador Principal do Dashboard
async function carregarDashboard() {
  const [
    execucao2319,
    execucaoFinanceira
  ] = await Promise.all([
    carregarJSON('EXECUÇÃO 2319 2026.json'),
    carregarJSON('Execução Financeira 2026.json')
  ]);

  if (execucao2319 && Array.isArray(execucao2319)) {
    processarExecucaoOrcametaria(execucao2319);
  }

  if (execucaoFinanceira && Array.isArray(execucaoFinanceira)) {
    processarExecucaoFinanceira(execucaoFinanceira);
  }
}

// Lógica de Processamento da Execução Orçamentária
function processarExecucaoOrcametaria(dados) {
  let limiteTotal = 0;
  let empenhadoTotal = 0;
  let bloqueadoTotal = 0;
  let saldoTotal = 0;
  
  const mapaAcoes = {};
  
  let eofDiscricionario = 0; 
  let eofPac = 0;             
  let eofEmendas = 0;        

  // Ignora as primeiras 7 linhas de metadados do arquivo
  const dadosValidos = dados.slice(7);

  dadosValidos.forEach(linha => {
    const nomeAcaoBruto = String(linha["EXECUÇÃO 2319 2026"] || "").trim();
    const upper = nomeAcaoBruto.toUpperCase();

    if (
      !nomeAcaoBruto || 
      upper.includes("FILTRO DO RELATÓRIO") ||
      upper.includes("FILTRO DE EXIBIÇÃO") ||
      upper.includes("{ITEM INFORMAÇÃO}") ||
      upper.includes("PÁGINAS:") ||
      upper.includes("MÊS LANÇAMENTO:") ||
      (upper.includes("AÇÃO GOVERNO") && upper.length < 20) ||
      upper.includes("TOTAL GERAL") ||
      upper.includes("TOTAL DO PROGRAMA") ||
      nomeAcaoBruto.includes("{Saldo") ||
      nomeAcaoBruto.includes("Métrica:")
    ) {
      return;
    }

    const eofRaw = String(linha["Unnamed: 1"] || "").trim();
    const matchEof = eofRaw.match(/(\d+)/);
    const eofVal = matchEof ? parseInt(matchEof[1], 10) : 0;

    const dotacao = parseValor(linha["Unnamed: 2"]);
    const saldo = parseValor(linha["Unnamed: 3"]);
    const bloqueado = parseValor(linha["Unnamed: 4"]);
    const empenhado = parseValor(linha["Unnamed: 5"]);

    limiteTotal += dotacao;
    saldoTotal += saldo;
    bloqueadoTotal += bloqueado;
    empenhadoTotal += empenhado;

    if (eofVal === 2) {
      eofDiscricionario += empenhado;
    } else if (eofVal === 3) {
      eofPac += empenhado;
    } else if ([6, 7, 8, 9].includes(eofVal)) {
      eofEmendas += empenhado;
    }

    let chaveAcao = nomeAcaoBruto;
    const matchCodigo = nomeAcaoBruto.match(/^([0-9A-Z]{4})/);
    if (matchCodigo) {
      chaveAcao = matchCodigo[1];
    }

    if (mapaAcoes[chaveAcao]) {
      mapaAcoes[chaveAcao].dotacao += dotacao;
      mapaAcoes[chaveAcao].saldo += saldo;
      mapaAcoes[chaveAcao].bloqueado += bloqueado;
      mapaAcoes[chaveAcao].empenhado += empenhado;
    } else {
      mapaAcoes[chaveAcao] = {
        nome: nomeAcaoBruto,
        dotacao: dotacao,
        saldo: saldo,
        bloqueado: bloqueado,
        empenhado: empenhado
      };
    }
  });

  if (limiteTotal > 0) {
    document.getElementById('limite-total').textContent = formatarMoeda(limiteTotal);
    document.getElementById('val-saldo').textContent = formatarMoeda(saldoTotal);
    document.getElementById('val-empenhado').textContent = formatarMoeda(empenhadoTotal);
    document.getElementById('val-bloqueado').textContent = formatarMoeda(bloqueadoTotal);

    document.getElementById('pct-saldo').textContent = `${((saldoTotal / limiteTotal) * 100).toFixed(2)}%`;
    document.getElementById('pct-empenhado').textContent = `${((empenhadoTotal / limiteTotal) * 100).toFixed(2)}%`;
    document.getElementById('pct-bloqueado').textContent = `${((bloqueadoTotal / limiteTotal) * 100).toFixed(2)}%`;
  }

  // Renderização em Tabela Detalhada das Ações Orçamentárias
  const dropdownContent = document.querySelector('.actions-dropdown-content');
  if (dropdownContent) {
    const acoesArray = Object.values(mapaAcoes);
    
    let htmlTabela = `
      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem; text-align: left;">
          <thead>
            <tr style="border-bottom: 2px solid #e2e8f0; color: #475569;">
              <th style="padding: 10px;">Ação</th>
              <th style="padding: 10px; text-align: right;">Dotação</th>
              <th style="padding: 10px; text-align: right;">Crédito Disp.</th>
              <th style="padding: 10px; text-align: right;">Empenhado</th>
              <th style="padding: 10px; text-align: right;">Bloqueado</th>
            </tr>
          </thead>
          <tbody>
    `;

    if (acoesArray.length > 0) {
      acoesArray.forEach((acao, index) => {
        const bgRow = index % 2 === 0 ? '#ffffff' : '#f8fafc';
        htmlTabela += `
          <tr style="background-color: ${bgRow}; border-bottom: 1px solid #edf2f7;">
            <td style="padding: 10px; font-weight: 700; color: #0f172a;">${acao.nome}</td>
            <td style="padding: 10px; text-align: right;">${formatarMoeda(acao.dotacao)}</td>
            <td style="padding: 10px; text-align: right;">${formatarMoeda(acao.saldo)}</td>
            <td style="padding: 10px; text-align: right;">${formatarMoeda(acao.empenhado)}</td>
            <td style="padding: 10px; text-align: right;">${formatarMoeda(acao.bloqueado)}</td>
          </tr>
        `;
      });
    } else {
      htmlTabela += `<tr><td colspan="5" style="padding: 15px; text-align: center; color: #64748b;">Nenhuma ação encontrada</td></tr>`;
    }

    htmlTabela += `
          </tbody>
        </table>
      </div>
    `;

    dropdownContent.innerHTML = htmlTabela;
  }

  document.getElementById('eof-discricionario').textContent = formatarMoeda(eofDiscricionario);
  document.getElementById('eof-pac').textContent = formatarMoeda(eofPac);
  document.getElementById('eof-emendas').textContent = formatarMoeda(eofEmendas);
}

// Lógica de Execução Financeira
function processarExecucaoFinanceira(dados) {
  let totalAcumulado = 0;
  
  let discricionarioTotal = 0;
  let discricionarioRap = 0;
  let discricionarioEx = 0;
  
  let emendasTotal = 0;
  let emendasRap = 0;
  let emendasEx = 0;

  let pacTotal = 0;
  let pacRap = 0;
  let pacEx = 0;

  const whitelistAcoes = ['00T1', '00T3', '10SS', '15UE', '1D73', '2D49', '00T0', '00SZ'];

  const dadosValidos = dados.slice(7);

  dadosValidos.forEach(linha => {
    const valoresArr = Object.values(linha);
    const acaoGov = String(linha["Execução Financeira 2026"] || valoresArr[0] || "").trim();
    const descAcao = String(linha["Unnamed: 1"] || "").trim();
    const textoLinhaCompleto = valoresArr.join(" ").toUpperCase();
    
    const upperAcao = acaoGov.toUpperCase();
    const upperDesc = descAcao.toUpperCase();

    if (
      !acaoGov || 
      upperAcao.includes("FILTRO") ||
      upperAcao.includes("TOTAL") ||
      upperAcao.includes("SOMA") ||
      upperAcao.includes("SUBTOTAL") ||
      upperAcao.includes("AÇÃO GOVERNO") ||
      upperDesc.includes("TOTAL") ||
      upperDesc.includes("SOMA") ||
      upperDesc.includes("SUBTOTAL")
    ) {
      return;
    }

    const contemAcaoPermitida = whitelistAcoes.some(codigo => textoLinhaCompleto.includes(codigo));
    if (!contemAcaoPermitida) {
      return;
    }

    const resultadoEofRaw = String(linha["Unnamed: 4"] || "").trim();
    if (!resultadoEofRaw) return;

    const matchEof = resultadoEofRaw.match(/(\d+)/);
    const eofVal = matchEof ? parseInt(matchEof[1], 10) : 0;

    if (![2, 3, 6, 7, 8, 9].includes(eofVal)) {
      return;
    }

    const valExercicio = parseValor(linha["Unnamed: 7"]); 
    const valRap = parseValor(linha["Unnamed: 8"]);      
    const valTotal = parseValor(linha["Unnamed: 9"]);      

    const somaLinha = valTotal > 0 ? valTotal : (valExercicio + valRap);

    if (somaLinha > 0) {
      if (eofVal === 2) {
        discricionarioTotal += somaLinha;
        discricionarioRap += valRap;
        discricionarioEx += valExercicio;
        totalAcumulado += somaLinha; // Corrigido de somaLinhead para somaLinha
      } else if (eofVal === 3) {
        pacTotal += somaLinha;
        pacRap += valRap;
        pacEx += valExercicio;
        totalAcumulado += somaLinha;
      } else if ([6, 7, 8, 9].includes(eofVal)) {
        emendasTotal += somaLinha;
        emendasRap += valRap;
        emendasEx += valExercicio;
        totalAcumulado += somaLinha;
      }
    }
  });

  document.getElementById('pag-acumulado').textContent = formatarMoeda(totalAcumulado);
  
  document.getElementById('pag-discricionario').textContent = formatarMoeda(discricionarioTotal);
  document.getElementById('discricionario-rap').textContent = formatarMoeda(discricionarioRap);
  document.getElementById('discricionario-ex').textContent = formatarMoeda(discricionarioEx);
  
  document.getElementById('pag-emendas').textContent = formatarMoeda(emendasTotal);
  document.getElementById('emendas-rap').textContent = formatarMoeda(emendasRap);
  document.getElementById('emendas-ex').textContent = formatarMoeda(emendasEx);

  document.getElementById('pag-pac').textContent = formatarMoeda(pacTotal);
  document.getElementById('pac-rap').textContent = formatarMoeda(pacRap);
  document.getElementById('pac-ex').textContent = formatarMoeda(pacEx);
}

document.addEventListener('DOMContentLoaded', carregarDashboard);