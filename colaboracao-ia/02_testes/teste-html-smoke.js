#!/usr/bin/env node
// Teste de fumaça (smoke test) para materiais HTML de "O Japonês por Trás das Palavras".
// Somente leitura: abre o arquivo no Chromium e nunca o altera.
// O que é e o que não é coberto: ver 02_testes/COBERTURA.md.
//
// Uso:
//   node teste-html-smoke.js <arquivo.html> [--saida <pasta>]
//
// Cada execução grava em uma pasta NOVA:
//   <saida>/<AAAAMMDD-HHMMSS>_<nome-do-arquivo>/relatorio.json + capturas
// (padrão de <saida>: 02_testes/resultados). Uma pasta existente nunca é sobrescrita.
// Código de saída: 0 sem falhas; 1 com falhas (erro de script ou arquivo local ausente);
// 2 erro de uso.

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const { pathToFileURL } = require('url');
const { execFileSync } = require('child_process');

const VERSAO_SCRIPT = '2';
const VIEWPORTS = [
  { nome: 'desktop', width: 1280, height: 900 },
  { nome: 'celular', width: 390, height: 844 },
];
// Botões com estes termos não são clicados (podem apagar progresso ou dados).
const DESTRUTIVO = /reset|apagar|limpar|excluir|remover|danger|delete|clear/i;

function args() {
  const a = process.argv.slice(2);
  const alvo = a.find((x, i) => !x.startsWith('--') && a[i - 1] !== '--saida');
  const iSaida = a.indexOf('--saida');
  const saida = iSaida >= 0 ? a[iSaida + 1] : path.join(__dirname, 'resultados');
  if (!alvo) {
    console.error('Uso: node teste-html-smoke.js <arquivo.html> [--saida <pasta>]');
    process.exit(2);
  }
  return { alvo: path.resolve(alvo), saida: path.resolve(saida) };
}

function pastaNova(base, alvo) {
  const d = new Date();
  const p2 = (n) => String(n).padStart(2, '0');
  const carimbo = `${d.getFullYear()}${p2(d.getMonth() + 1)}${p2(d.getDate())}-${p2(d.getHours())}${p2(d.getMinutes())}${p2(d.getSeconds())}`;
  const slug = path.basename(alvo).normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/[^A-Za-z0-9._-]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60) || 'arquivo';
  let pasta = path.join(base, `${carimbo}_${slug}`);
  for (let n = 2; fs.existsSync(pasta); n++) pasta = path.join(base, `${carimbo}_${slug}_${n}`);
  fs.mkdirSync(pasta, { recursive: true });
  return pasta;
}

function commitGit(arquivo) {
  // SHA completo do commit e do blob do arquivo, se ele estiver num repositório git.
  try {
    const dir = path.dirname(arquivo);
    const commit = execFileSync('git', ['-C', dir, 'rev-parse', 'HEAD'], { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim();
    let blob = null;
    try { blob = execFileSync('git', ['-C', dir, 'rev-parse', `HEAD:./${path.basename(arquivo)}`], { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim(); } catch { /* arquivo fora do commit */ }
    const sujo = execFileSync('git', ['-C', dir, 'status', '--porcelain', '--', path.basename(arquivo)], { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim() !== '';
    return { commit, blob_no_commit: blob, alterado_desde_o_commit: sujo };
  } catch { return null; }
}

// Instalado em cada página antes de qualquer script dela: conta mutações do DOM,
// chamadas de play() em áudio/vídeo e escritas no armazenamento local.
function instrumentar() {
  window.__qa = { mutacoes: 0, plays: 0, armazenamento: 0, dialogos: 0 };
  new MutationObserver((ms) => { window.__qa.mutacoes += ms.length; })
    .observe(document, { subtree: true, childList: true, attributes: true, characterData: true });
  const play = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function () { window.__qa.plays++; return play.apply(this, arguments); };
  try {
    const set = Storage.prototype.setItem;
    Storage.prototype.setItem = function () { window.__qa.armazenamento++; return set.apply(this, arguments); };
  } catch { /* armazenamento indisponível */ }
}

(async () => {
  const { alvo, saida } = args();
  if (!fs.existsSync(alvo)) { console.error(`Arquivo não encontrado: ${alvo}`); process.exit(2); }
  const url = pathToFileURL(alvo).href; // trata espaços, acentos e caminhos do Windows
  const pasta = pastaNova(saida, alvo);
  const R = {
    script: { nome: path.basename(__filename), versao: VERSAO_SCRIPT },
    executado_em: new Date().toISOString(),
    ambiente: { node: process.version, playwright: require('playwright/package.json').version, navegador: 'chromium' },
    alvo: { caminho: alvo, url, sha256: crypto.createHash('sha256').update(fs.readFileSync(alvo)).digest('hex'), git: commitGit(alvo) },
    falhas: [], avisos: [], viewports: {},
  };

  const browser = await chromium.launch();
  for (const vp of VIEWPORTS) {
    const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
    await ctx.addInitScript(instrumentar);
    const pg = await ctx.newPage();
    const V = { erros_script: [], erros_console: [], recursos_locais_ausentes: [], recursos_externos_falhos: [] };
    pg.on('pageerror', (e) => V.erros_script.push(e.message));
    pg.on('console', (m) => { if (m.type() === 'error') V.erros_console.push(m.text()); });
    pg.on('requestfailed', (q) => {
      const u = q.url(); const item = `${u} (${q.failure()?.errorText})`;
      (u.startsWith('file:') ? V.recursos_locais_ausentes : V.recursos_externos_falhos).push(item);
    });
    pg.on('dialog', async (d) => { V.dialogos = (V.dialogos || 0) + 1; await d.dismiss(); });

    await pg.goto(url, { waitUntil: 'load' });
    await pg.waitForTimeout(300);

    V.rolagem_horizontal_px = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);

    if (vp.nome === 'desktop') {
      Object.assign(V, await pg.evaluate(() => {
        const cjk = /[぀-ヿ㐀-鿿]/;
        const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let japones = 0, semLangJa = 0;
        for (let n = tw.nextNode(); n; n = tw.nextNode()) {
          if (!cjk.test(n.nodeValue)) continue;
          japones++;
          const el = n.parentElement && n.parentElement.closest('[lang]');
          if (!el || !el.getAttribute('lang').toLowerCase().startsWith('ja')) semLangJa++;
        }
        const ids = new Set([...document.querySelectorAll('[id]')].map((e) => e.id));
        return {
          lang_documento: document.documentElement.getAttribute('lang'),
          titulo: document.title,
          trechos_japones: japones,
          trechos_japones_sem_lang_ja: semLangJa,
          botoes_total: document.querySelectorAll('button').length,
          botoes_sem_nome: [...document.querySelectorAll('button')].filter((b) => !((b.innerText || '').trim() || b.getAttribute('aria-label') || b.getAttribute('aria-labelledby') || b.title)).length,
          imagens_sem_alt: document.querySelectorAll('img:not([alt])').length,
          campos_sem_rotulo: [...document.querySelectorAll('input:not([type=hidden]),select,textarea')].filter((i) => !(i.labels?.length || i.getAttribute('aria-label') || i.getAttribute('aria-labelledby'))).length,
          h1: document.querySelectorAll('h1').length,
          links_internos_quebrados: [...document.querySelectorAll('a[href^="#"]')].map((a) => a.getAttribute('href')).filter((h) => h.length > 1 && !ids.has(decodeURIComponent(h.slice(1)))),
        };
      }));

      // Interação: um clique por botão visível e habilitado, na ordem do documento, sem recarregar
      // a página (o estado se acumula). A reação é medida por sinais, não pela aparência.
      const botoes = pg.locator('button');
      const total = await botoes.count();
      const cliques = [];
      for (let i = 0; i < total; i++) {
        const b = botoes.nth(i);
        const info = await b.evaluate((x) => ({
          rotulo: ((x.innerText || x.getAttribute('aria-label') || x.title || x.id || '').trim()).slice(0, 50),
          marcadores: `${x.id} ${x.className} ${x.innerText}`,
          visivel: !!(x.offsetWidth || x.offsetHeight || x.getClientRects().length),
          desabilitado: x.disabled || x.getAttribute('aria-disabled') === 'true',
        })).catch(() => null);
        if (!info) { cliques.push({ indice: i, resultado: 'removido_do_dom' }); continue; }
        const base = { indice: i, rotulo: info.rotulo };
        if (DESTRUTIVO.test(info.marcadores)) { cliques.push({ ...base, resultado: 'nao_testado_destrutivo' }); continue; }
        if (!info.visivel) { cliques.push({ ...base, resultado: 'nao_testado_oculto' }); continue; }
        if (info.desabilitado) { cliques.push({ ...base, resultado: 'nao_testado_desabilitado' }); continue; }
        const antes = await pg.evaluate(() => ({ ...window.__qa, url: location.href }));
        try { await b.click({ timeout: 2000 }); } catch (e) { cliques.push({ ...base, resultado: 'clique_falhou', detalhe: e.message.split('\n')[0] }); continue; }
        await pg.waitForTimeout(250);
        const depois = await pg.evaluate(() => ({ ...window.__qa, url: location.href }));
        const sinais = [];
        if (depois.mutacoes > antes.mutacoes) sinais.push('dom');
        if (depois.plays > antes.plays) sinais.push('audio_play');
        if (depois.armazenamento > antes.armazenamento) sinais.push('armazenamento');
        if (depois.url !== antes.url) sinais.push('navegacao');
        cliques.push({ ...base, resultado: sinais.length ? 'reagiu' : 'sem_reacao_detectada', sinais });
      }
      const conta = (r) => cliques.filter((c) => c.resultado === r).length;
      V.cliques = {
        resumo: {
          botoes: total, clicados: cliques.filter((c) => c.resultado === 'reagiu' || c.resultado === 'sem_reacao_detectada').length,
          reagiram: conta('reagiu'), sem_reacao_detectada: conta('sem_reacao_detectada'),
          nao_testados_ocultos: conta('nao_testado_oculto'), nao_testados_desabilitados: conta('nao_testado_desabilitado'),
          nao_testados_destrutivos: conta('nao_testado_destrutivo'), cliques_falhos: conta('clique_falhou'),
        },
        detalhe: cliques,
      };
    }

    await pg.screenshot({ path: path.join(pasta, `captura-${vp.nome}.png`), fullPage: false });
    R.viewports[vp.nome] = V;
    await ctx.close();
  }
  await browser.close();

  for (const [nome, V] of Object.entries(R.viewports)) {
    if (V.erros_script.length) R.falhas.push(`[${nome}] ${V.erros_script.length} erro(s) de script`);
    if (V.recursos_locais_ausentes.length) R.falhas.push(`[${nome}] ${V.recursos_locais_ausentes.length} arquivo(s) local(is) ausente(s)`);
    if (V.rolagem_horizontal_px > 0) R.avisos.push(`[${nome}] rolagem horizontal de ${V.rolagem_horizontal_px}px`);
    if (V.recursos_externos_falhos.length) R.avisos.push(`[${nome}] ${V.recursos_externos_falhos.length} recurso(s) externo(s) não carregaram (pode ser bloqueio de rede do ambiente)`);
  }
  const d = R.viewports.desktop;
  if (d.trechos_japones_sem_lang_ja) R.avisos.push(`${d.trechos_japones_sem_lang_ja} de ${d.trechos_japones} trecho(s) em japonês sem lang="ja"`);
  if (d.botoes_sem_nome || d.imagens_sem_alt || d.campos_sem_rotulo) R.avisos.push('elementos sem nome acessível (ver viewports.desktop)');
  if (d.links_internos_quebrados.length) R.falhas.push(`${d.links_internos_quebrados.length} link(s) interno(s) quebrado(s)`);
  if (d.cliques.resumo.cliques_falhos) R.avisos.push(`${d.cliques.resumo.cliques_falhos} clique(s) falharam`);

  fs.writeFileSync(path.join(pasta, 'relatorio.json'), JSON.stringify(R, null, 2));
  console.log(`Relatório: ${path.join(pasta, 'relatorio.json')}`);
  console.log(`Falhas: ${R.falhas.length ? R.falhas.join('; ') : 'nenhuma'}`);
  console.log(`Avisos: ${R.avisos.length ? R.avisos.join('; ') : 'nenhum'}`);
  console.log(`Cliques: ${JSON.stringify(d.cliques.resumo)}`);
  process.exit(R.falhas.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
