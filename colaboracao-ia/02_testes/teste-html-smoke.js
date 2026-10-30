// Smoke test genérico para materiais HTML do projeto (somente leitura: não altera o arquivo testado)
const {chromium}=require('playwright'); const path=require('path'); const fs=require('fs');
const target=process.argv[2]; const url='file://'+path.resolve(target);
(async()=>{
 const b=await chromium.launch(); const R={target, errors:[], failedRequests:[], checks:{}};
 for (const vp of [{name:'desktop',width:1280,height:900},{name:'celular',width:390,height:844}]){
  const ctx=await b.newContext({viewport:{width:vp.width,height:vp.height}}); const pg=await ctx.newPage();
  pg.on('pageerror',e=>R.errors.push(`[${vp.name}] pageerror: ${e.message}`));
  pg.on('console',m=>{if(m.type()==='error')R.errors.push(`[${vp.name}] console: ${m.text()}`)});
  pg.on('requestfailed',q=>R.failedRequests.push(`[${vp.name}] ${q.url().split('/').slice(-2).join('/')}: ${q.failure()?.errorText}`));
  await pg.goto(url); await pg.waitForLoadState('load');
  const c={};
  c.overflowX=await pg.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
  if(vp.name==='desktop'){
   Object.assign(c, await pg.evaluate(()=>({
    lang:document.documentElement.lang||null,
    title:document.title,
    buttons:document.querySelectorAll('button').length,
    buttonsSemNome:[...document.querySelectorAll('button')].filter(x=>!(x.innerText.trim()||x.getAttribute('aria-label'))).length,
    imgsSemAlt:[...document.querySelectorAll('img')].filter(i=>!i.hasAttribute('alt')).length,
    inputsSemRotulo:[...document.querySelectorAll('input,select,textarea')].filter(i=>i.type!=='hidden'&&!(i.labels?.length||i.getAttribute('aria-label')||i.getAttribute('aria-labelledby'))).length,
    h1:document.querySelectorAll('h1').length,
    linksQuebradosInternos:[...document.querySelectorAll('a[href^="#"]')].filter(a=>a.getAttribute('href').length>1&&!document.querySelector(a.getAttribute('href'))).map(a=>a.getAttribute('href')),
    audios:[...document.querySelectorAll('audio,source,[data-src]')].map(a=>a.getAttribute('src')||a.getAttribute('data-src')).filter(Boolean),
    textoJapones:/[぀-ヿ一-龯]/.test(document.body.innerText),
   })));
   // interação: clica cada botão visível (exceto destrutivos) e mede se o DOM reage
   const btns=await pg.$$('button'); let reagiram=0, semReacao=[], pulados=[];
   for(const bt of btns){
     const info=await bt.evaluate(x=>({t:(x.innerText||x.getAttribute('aria-label')||x.id).trim().slice(0,40),danger:/reset|apagar|limpar|danger/i.test(x.id+' '+x.className+' '+x.innerText),vis:!!(x.offsetParent)}));
     if(info.danger||!info.vis){pulados.push(info.t);continue;}
     const before=await pg.evaluate(()=>document.body.innerHTML.length+'|'+document.querySelectorAll('[aria-pressed="true"],.on,.active,.correct,.wrong,.show,[open]').length);
     try{await bt.click({timeout:1500});}catch(e){semReacao.push(info.t+' (não clicável)');continue;}
     await pg.waitForTimeout(150);
     const after=await pg.evaluate(()=>document.body.innerHTML.length+'|'+document.querySelectorAll('[aria-pressed="true"],.on,.active,.correct,.wrong,.show,[open]').length);
     if(before!==after)reagiram++; else semReacao.push(info.t);
   }
   c.cliques={testados:btns.length-pulados.length,reagiram,semReacaoVisivel:semReacao,pulados};
   // exercícios: marca opções de rádio/checkbox e verifica feedback
   const opts=await pg.$$('input[type=radio],input[type=checkbox]'); c.opcoesExercicio=opts.length;
  }
  await pg.screenshot({path:`shot-${vp.name}.png`,fullPage:false});
  R.checks[vp.name]=c; await ctx.close();
 }
 await b.close(); fs.writeFileSync('report.json',JSON.stringify(R,null,1)); console.log(JSON.stringify(R,null,1));
})();
