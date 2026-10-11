/* ---------- JUEGOS ---------- */
const GD = TOUR.games || {trivia:[],vol:[],year:[],who:[],dares:[],hunt:[],poses:[]};
const ME = (()=>{ let m=store.get('me',null); if(!m||!m.id){ m={id:Math.random().toString(36).slice(2,10),name:''}; store.set('me',m); } return m; })();
const NTFY = 'https://ntfy.sh/';
const NET = {code:store.get('room',null), es:null, seen:new Set(), last:null, ok:false, retry:0, rt:null};
const GS = {players:{}, scores:{}, awarded:new Set(), games:{}, game:null, found:{}, photos:{}, rateAsk:null, lastDare:null};
const GNAME = {trivia:'Trivial segoviano', vol:'¿Verdad o leyenda?', year:'Adivina el año', who:'¿Quién es más probable?'};
const ALPH = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
const canNet = () => IS_WEB && 'EventSource' in window;
const topicOf = c => 'sgvpie26-' + c.toLowerCase();
const nameOf = pid => pid===ME.id ? (ME.name||'Tú') : (GS.players[pid]||'Tu pareja');
const others = () => Object.keys(GS.players).filter(p=>p!==ME.id);

function netOpen(){
  if(!NET.code || !canNet()) return;
  try{ NET.es && NET.es.close(); }catch(e){}
  const es = new EventSource(NTFY + topicOf(NET.code) + '/sse?since=' + (NET.last || 'all'));
  NET.es = es;
  es.onopen = () => { NET.ok = true; NET.retry = 0; paintNet(); };
  es.onmessage = e => {
    let d; try{ d = JSON.parse(e.data); }catch(x){ return; }
    if(d.event && d.event!=='message') return;
    if(NET.seen.has(d.id)) return; NET.seen.add(d.id); NET.last = d.id;
    let m; try{ m = JSON.parse(d.message); }catch(x){ return; }
    if(!m || !m.t) return;
    m._at = (d.time ? d.time*1000 : Date.now());
    onNet(m);
  };
  es.onerror = () => { NET.ok = false; paintNet(); try{ es.close(); }catch(x){} clearTimeout(NET.rt); NET.rt = setTimeout(netOpen, Math.min(15000, 800 * 2 ** NET.retry++)); };
}
async function netSend(m){
  m.from = ME.id; m.name = ME.name || 'Tú'; m.ts = Date.now();
  if(!NET.code || !canNet()){ m._at = Date.now(); onNet(m); return; }
  try{ const r = await fetch(NTFY + topicOf(NET.code), {method:'POST', body: JSON.stringify(m)}); if(!r.ok) throw 0; }
  catch(e){ toast('No se ha podido enviar: sin cobertura. Vuelve a intentarlo'); }
}
function joinRoom(code){
  NET.code = code.toUpperCase().replace(/[^A-Z0-9]/g,'').slice(0,6); store.set('room', NET.code);
  NET.seen = new Set(); NET.last = null; Object.assign(GS, {players:{}, scores:{}, awarded:new Set(), games:{}, game:null, found:{}, photos:{}, rateAsk:null});
  netOpen(); setTimeout(()=>netSend({t:'hello'}), 600); renderGames();
}
function leaveRoom(){ try{ NET.es && NET.es.close(); }catch(e){} NET.code=null; store.set('room',null); NET.ok=false; Object.assign(GS,{players:{},scores:{},awarded:new Set(),games:{},game:null,found:{},photos:{},rateAsk:null}); renderGames(); }
function newCode(){ let c=''; for(let i=0;i<4;i++) c+=ALPH[Math.floor(Math.random()*ALPH.length)]; return c; }
function paintNet(){ const el=$('#netDot'); if(el){ el.className='netdot '+(NET.code?(NET.ok?'on':'off'):''); } }
document.addEventListener('visibilitychange', ()=>{ if(!document.hidden && NET.code && (!NET.es || NET.es.readyState===2)) netOpen(); });

function award(pid, pts, key){ if(GS.awarded.has(key)) return; GS.awarded.add(key); GS.scores[pid]=(GS.scores[pid]||0)+pts; }
function itemsOf(g){ return GD[g]||[]; }
function itemById(g,id){ return itemsOf(g).find(x=>x.id===id); }

function onNet(m){
  if(m.from) GS.players[m.from] = m.name || GS.players[m.from] || 'Jugador';
  if(m.from && GS.scores[m.from]==null) GS.scores[m.from]=0;
  const gm = m.gid ? GS.games[m.gid] : null;
  switch(m.t){
    case 'start':
      GS.games[m.gid] = {gid:m.gid, g:m.g, items:m.items, host:m.from, i:0, ans:{}, players:new Set([m.from]), revealed:{}, over:false, at:m._at};
      GS.game = GS.games[m.gid];
      if(m.from!==ME.id && Date.now()-m._at < 5*60*1000) netSend({t:'join', gid:m.gid});
      { const g0=GS.games[m.gid]; if(Date.now()-m._at < 10*60*1000) setTimeout(()=>{ if(GS.game===g0 && !g0.over) openGame(); }, 450); }
      break;
    case 'join': if(gm) gm.players.add(m.from); break;
    case 'ans':
      if(!gm) break;
      gm.players.add(m.from);
      gm.ans[m.i] = gm.ans[m.i] || {};
      if(!(m.from in gm.ans[m.i])) gm.ans[m.i][m.from] = {v:m.v, ms:m.ms};
      break;
    case 'next': if(gm && m.i>gm.i){ scoreRound(gm, gm.i); gm.i = m.i; } break;
    case 'end': if(gm && !gm.over){ scoreRound(gm, gm.i); gm.over = true; } break;
    case 'found': if(!GS.found[m.id]){ GS.found[m.id] = m.from; award(m.from, 100, 'hunt:'+m.id); } break;
    case 'dare': award(m.target, m.pts||50, 'dare:'+m.id+':'+m.target); break;
    case 'photo': GS.photos[m.pid] = {from:m.from, title:m.title, rated:false}; if(m.from!==ME.id) GS.rateAsk = m.pid; break;
    case 'rate': if(GS.photos[m.pid]) GS.photos[m.pid].rated = true; award(m.target, (m.stars||0)*20, 'rate:'+m.pid); if(GS.rateAsk===m.pid) GS.rateAsk=null; break;
  }
  { const gmEl=$('#gm'); if(GS.game && gmEl && gmEl.dataset.kind==='game') paintGame(); }
  if(tab==='games') softRenderGames();
}

/* reglas de puntuación por ronda: deterministas a partir de los mensajes */
function scoreRound(gm, i){
  const key='round:'+gm.gid+':'+i; if(gm.revealed[i]) return; gm.revealed[i]=true;
  const it = itemById(gm.g, gm.items[i]); const ans = gm.ans[i]||{}; if(!it) return;
  const ids = Object.keys(ans);
  if(gm.g==='trivia' || gm.g==='vol'){
    const ok = gm.g==='trivia' ? it.a : (it.truth?1:0);
    ids.forEach(p=>{ const a=ans[p]; if(a.v===ok) award(p, 100 + Math.round(50*Math.max(0,1-(a.ms||20000)/20000)), key+':'+p); });
  } else if(gm.g==='year'){
    const ds = ids.filter(p=>ans[p].v!=null).map(p=>({p, d:Math.abs(ans[p].v-it.y)}));
    if(ds.length){ const best=Math.min(...ds.map(x=>x.d)); ds.forEach(x=>{ if(x.d===best) award(x.p, x.d===0?150:100, key+':'+x.p); else if(x.d<=10) award(x.p, 30, key+':'+x.p); }); }
  } else if(gm.g==='who'){
    const vs = ids.map(p=>ans[p].v).filter(Boolean);
    if(vs.length>=2 && vs.every(v=>v===vs[0])) ids.forEach(p=>award(p, 50, key+':'+p));
  }
}

/* ---------- partida en curso (modal) ---------- */
let QT = {i:-1, gid:null, shownAt:0, timer:null, revealTimer:null};
const LIMIT = {trivia:20, vol:12, year:25, who:15};
function startGame(g, n){
  const pool = itemsOf(g).slice();
  // prioriza preguntas de paradas ya hechas o la actual
  const seen = new Set(S.filter((s,i)=>done.has(s.id)||i<=cur).map(s=>s.id).concat(['general']));
  pool.sort((a,b)=> (seen.has(b.stop)?1:0)-(seen.has(a.stop)?1:0) || Math.random()-.5);
  const items = pool.slice(0, n).sort(()=>Math.random()-.5).map(x=>x.id);
  if(!items.length){ toast('No hay preguntas cargadas para este juego'); return; }
  netSend({t:'start', g, gid:Math.random().toString(36).slice(2,9), items});
}
function openGame(){
  const ex=$('#gm'); if(ex){ if(ex.dataset.kind==='game') paintGame(); else toast((GS.game?GNAME[GS.game.g]:'Partida')+' empezada: cierra esto para jugar'); return; }
  const d=document.createElement('div'); d.id='gm'; d.className='modal'; d.dataset.kind='game'; d.setAttribute('role','dialog');
  document.body.appendChild(d); paintGame();
}
function closeModal(){ const d=$('#gm'); const wasCam=d&&d.classList.contains('cam'); if(d) d.remove(); if(wasCam===false && GS.game && !GS.game.over && false){} clearInterval(QT.timer); clearTimeout(QT.revealTimer); QT={i:-1,gid:null,shownAt:0,timer:null,revealTimer:null}; stopCam(); if(tab==='games') renderGames(); }
function participants(gm){ const s=new Set(gm.players); s.add(ME.id); return [...s]; }
function paintGame(){
  const d=$('#gm'); const gm=GS.game; if(!d||!gm) return;
  if(gm.over) return paintFinal(gm);
  const i=gm.i, it=itemById(gm.g, gm.items[i]); if(!it){ return; }
  if(QT.gid!==gm.gid || QT.i!==i){ QT.gid=gm.gid; QT.i=i; QT.shownAt=Date.now(); QT.revealAt=0; QT.nudged=false; clearInterval(QT.timer); clearTimeout(QT.revealTimer); QT.timer=setInterval(()=>{ paintTimer(); },250); }
  const ans=gm.ans[i]||{}, mine=ans[ME.id], ppl=participants(gm);
  const lim=LIMIT[gm.g]*1000, el=Date.now()-QT.shownAt;
  const everyone = ppl.every(p=>p in ans);
  const reveal = everyone || el>lim+600;
  if(reveal && !QT.revealAt) QT.revealAt = Date.now();
  let body='';
  const q = gm.g==='trivia'? it.q : gm.g==='vol'? it.s : it.q;
  body += `<div class="gm-top"><button class="gm-x" id="gmClose" aria-label="Cerrar">${ICON.x}</button><span class="gm-k">${esc(GNAME[gm.g])} · ${i+1}/${gm.items.length}</span><span class="gm-sc">${ppl.map(p=>`<b class="${p===ME.id?'mine':''}">${esc(nameOf(p).slice(0,10))} ${GS.scores[p]||0}</b>`).join('')}</span></div>`;
  body += `<div class="gm-bar"><i id="gmBar" style="width:${Math.max(0,100-el/lim*100)}%"></i></div>`;
  body += `<h3 class="gm-q">${esc(q)}</h3>`;
  if(gm.g==='trivia'){
    body += `<div class="gm-opts">${it.opts.map((o,k)=>{ const c = reveal ? (k===it.a?' right':(mine&&mine.v===k?' wrong':'')) : (mine&&mine.v===k?' picked':''); const who = reveal? ppl.filter(p=>ans[p]&&ans[p].v===k).map(p=>`<em>${esc(nameOf(p).slice(0,8))}</em>`).join('') : ''; return `<button class="gm-o${c}" data-v="${k}" ${mine||reveal?'disabled':''}><span>${'ABCD'[k]}</span><b class="gm-t">${esc(o)}</b>${who}</button>`; }).join('')}</div>`;
  } else if(gm.g==='vol'){
    const ok = it.truth?1:0;
    body += `<div class="gm-opts two">${['Leyenda','Verdad'].map((o,k)=>{ const c = reveal ? (k===ok?' right':(mine&&mine.v===k?' wrong':'')) : (mine&&mine.v===k?' picked':''); const who = reveal? ppl.filter(p=>ans[p]&&ans[p].v===k).map(p=>`<em>${esc(nameOf(p).slice(0,8))}</em>`).join('') : ''; return `<button class="gm-o big${c}" data-v="${k}" ${mine||reveal?'disabled':''}>${o}${who}</button>`; }).join('')}</div>`;
  } else if(gm.g==='year'){
    const mid = Math.round((it.min+it.max)/2);
    if(!mine && !reveal) body += `<div class="gm-year"><output id="yrOut">${mid}</output><input type="range" id="yr" min="${it.min}" max="${it.max}" value="${mid}" step="1" aria-label="Año"><div class="gm-yr-l"><span>${it.min}</span><span>${it.max}</span></div><button class="btn primary arrived" id="yrGo">Fijar año</button></div>`;
    else body += `<div class="gm-year res">${reveal?`<div class="gm-y-ok">${it.y}</div>`:''}${ppl.map(p=>ans[p]?`<div class="gm-y-row"><b>${esc(nameOf(p))}</b><span>${ans[p].v??'—'}${reveal&&ans[p].v!=null?` · ${Math.abs(ans[p].v-it.y)} años de diferencia`:''}</span></div>`:`<div class="gm-y-row"><b>${esc(nameOf(p))}</b><span>pensando…</span></div>`).join('')}</div>`;
  } else if(gm.g==='who'){
    body += `<div class="gm-opts two">${ppl.map(p=>{ const c = reveal ? '' : (mine&&mine.v===p?' picked':''); const votes = reveal? ppl.filter(x=>ans[x]&&ans[x].v===p).map(x=>`<em>${esc(nameOf(x).slice(0,8))}</em>`).join('') : ''; return `<button class="gm-o big${c}" data-v="${p}" ${mine||reveal?'disabled':''}>${esc(p===ME.id?'Yo':nameOf(p))}${votes}</button>`; }).join('')}</div>`;
    if(ppl.length<2) body += `<p class="gm-note">Este juego necesita a tu pareja en la sala.</p>`;
  }
  if(reveal){
    const why = it.why ? `<p class="gm-why">${esc(it.why)}</p>` : '';
    let verdict='';
    if(gm.g==='who'){ const vs=ppl.map(p=>ans[p]&&ans[p].v).filter(Boolean); verdict = vs.length>=2 ? (vs.every(v=>v===vs[0]) ? `<p class="gm-hit">¡Coincidís! +50 cada uno</p>` : `<p class="gm-miss">No coincidís… a debatirlo</p>`) : ''; }
    body += verdict + why;
    const last = i>=gm.items.length-1;
    const host = gm.host===ME.id || (QT.revealAt && Date.now()-QT.revealAt>8000);
    body += host ? `<button class="btn primary arrived" id="gmNext">${last?'Ver resultado':'Siguiente'}</button>` : `<p class="gm-note">Esperando a ${esc(nameOf(gm.host))}…</p>`;
  } else if(mine){
    body += `<p class="gm-note">${ppl.length>1?'Esperando a tu pareja…':'Respuesta guardada'}</p>`;
  }
  d.innerHTML = `<div class="gm-in">${body}</div>`;
  $('#gmClose').onclick = closeModal;
  d.querySelectorAll('.gm-o[data-v]').forEach(b=>b.onclick=()=>{ const v = gm.g==='who' ? b.dataset.v : +b.dataset.v; b.classList.add('picked'); netSend({t:'ans', gid:gm.gid, i, v, ms:Date.now()-QT.shownAt}); try{navigator.vibrate&&navigator.vibrate(15)}catch(e){} });
  const yr=$('#yr'); if(yr){ yr.oninput=()=>$('#yrOut').textContent=yr.value; $('#yrGo').onclick=()=>netSend({t:'ans', gid:gm.gid, i, v:+yr.value, ms:Date.now()-QT.shownAt}); }
  const nx=$('#gmNext'); if(nx) nx.onclick=()=>{ nx.disabled=true; netSend(i>=gm.items.length-1 ? {t:'end', gid:gm.gid} : {t:'next', gid:gm.gid, i:i+1}); };
}
function paintTimer(){
  const gm=GS.game; if(!gm||gm.over) return; const lim=LIMIT[gm.g]*1000, el=Date.now()-QT.shownAt;
  const b=$('#gmBar'); if(b) b.style.width=Math.max(0,100-el/lim*100)+'%';
  const ans=gm.ans[gm.i]||{};
  if(el>lim+600 && !QT.revealAt){ if(!(ME.id in ans) && (gm.g==='year')){ const yr=$('#yr'); if(yr) netSend({t:'ans',gid:gm.gid,i:gm.i,v:+yr.value,ms:lim}); } paintGame(); }
  if(QT.revealAt && !QT.nudged && Date.now()-QT.revealAt>8000 && gm.host!==ME.id){ QT.nudged=true; paintGame(); }
}
function paintFinal(gm){
  clearInterval(QT.timer);
  const ppl=participants(gm); const pts=p=>{ let s=0; GS.awarded.forEach(k=>{}); return GS.scores[p]||0; };
  const sorted=ppl.slice().sort((a,b)=>pts(b)-pts(a));
  const tie = sorted.length>1 && pts(sorted[0])===pts(sorted[1]);
  const d=$('#gm');
  d.innerHTML = `<div class="gm-in final"><div class="gm-top"><button class="gm-x" id="gmClose" aria-label="Cerrar">${ICON.x}</button><span class="gm-k">${esc(GNAME[gm.g])}</span></div>
    <div class="gm-crown">${ICON.crown}</div>
    <h3 class="gm-q">${sorted.length<2? '¡Partida terminada!' : tie? '¡Empate! Segovia os une' : esc(nameOf(sorted[0]))+' gana el duelo'}</h3>
    <div class="gm-board">${sorted.map((p,k)=>`<div class="${k===0&&!tie?'win':''}"><b>${esc(nameOf(p))}</b><span>${pts(p)} pts</span></div>`).join('')}</div>
    <p class="gm-note">Los puntos se suman al marcador del día.</p>
    <div class="row" style="justify-content:center"><button class="btn primary" id="gmAgain">Otra partida</button><button class="btn" id="gmDone">Volver</button></div></div>`;
  $('#gmClose').onclick=closeModal; $('#gmDone').onclick=closeModal; $('#gmAgain').onclick=()=>{ closeModal(); startGame(gm.g, gm.items.length); };
  if(!gm.cele){ gm.cele=true; burst(); }
}

/* ---------- reto foto histórica ---------- */
let CAM={stream:null, facing:'environment', pose:null};
function stopCam(){ try{ CAM.stream && CAM.stream.getTracks().forEach(t=>t.stop()); }catch(e){} CAM.stream=null; }
async function openPose(p){
  CAM.pose=p; CAM.facing = p.camera==='front' ? 'user' : 'environment';
  const d=document.createElement('div'); d.id='gm'; d.className='modal cam'; document.body.appendChild(d);
  d.innerHTML = `<div class="cam-wrap"><video id="camV" playsinline muted autoplay></video><img id="camG" src="${esc(poseSrc(p))}" alt=""><div class="cam-top"><button class="gm-x" id="gmClose" aria-label="Cerrar">${ICON.x}</button><span>${esc(p.title)}</span></div>
    <div class="cam-how">${esc(p.how)}</div>
    <div class="cam-ctl"><label class="cam-op">Fantasma <input type="range" id="camO" min="0" max="90" value="45"></label>
    <div class="cam-btns"><button class="fab" id="camFlip" aria-label="Cambiar cámara">${ICON.flip}</button><button class="shutter" id="camShot" aria-label="Hacer foto"></button><label class="fab" aria-label="Elegir foto">${ICON.img}<input type="file" accept="image/*" id="camFile" hidden></label></div></div></div>`;
  $('#gmClose').onclick=closeModal;
  const g=$('#camG'); $('#camO').oninput=e=>g.style.opacity=e.target.value/100; g.style.opacity=.45;
  $('#camFlip').onclick=()=>{ CAM.facing = CAM.facing==='user'?'environment':'user'; startCam(); };
  $('#camShot').onclick=()=>{ const v=$('#camV'); if(!CAM.stream||!v.videoWidth){ $('#camFile').click(); return; } compose(v, v.videoWidth, v.videoHeight, CAM.facing==='user'); };
  $('#camFile').onchange=e=>{ const f=e.target.files[0]; if(!f) return; const im=new Image(); im.onload=()=>compose(im, im.naturalWidth, im.naturalHeight, false); im.src=URL.createObjectURL(f); };
  startCam();
}
const poseSrc = p => { const all=[]; S.forEach(s=>{ (s.images||[]).forEach(im=>all.push(im.src)); if(s.ba){ all.push(s.ba.before, s.ba.after); } }); return all.find(u=>u.split('?')[0]===p.img) || p.img; };
async function startCam(){
  stopCam(); const v=$('#camV'); if(!v) return;
  if(!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia){ camFallback(); return; }
  try{ CAM.stream = await navigator.mediaDevices.getUserMedia({video:{facingMode:CAM.facing, width:{ideal:1280}, height:{ideal:1280}}, audio:false}); v.srcObject=CAM.stream; v.classList.toggle('mirror', CAM.facing==='user'); await v.play().catch(()=>{}); }
  catch(e){ camFallback(); }
}
function camFallback(){ const h=$('.cam-how'); if(h) h.textContent='Sin acceso a la cámara aquí: toca el botón de la foto y hazla con la cámara del móvil. '+(CAM.pose?CAM.pose.how:''); }
function compose(src, w, h, mirror){
  const g=$('#camG'); const W=1080, half=Math.round(W*0.75), H=half*2+120;
  const c=document.createElement('canvas'); c.width=W; c.height=H; const x=c.getContext('2d');
  x.fillStyle='#111'; x.fillRect(0,0,W,H);
  const draw=(img,iw,ih,y0,flip)=>{ const r=Math.max(W/iw, half/ih), dw=iw*r, dh=ih*r; x.save(); x.beginPath(); x.rect(0,y0,W,half); x.clip(); if(flip){ x.translate(W,0); x.scale(-1,1); } x.drawImage(img,(W-dw)/2,y0+(half-dh)/2,dw,dh); x.restore(); };
  try{ draw(g, g.naturalWidth, g.naturalHeight, 0, false); }catch(e){}
  draw(src, w, h, half, mirror);
  x.fillStyle='#fff'; x.font='700 40px system-ui, sans-serif'; x.textBaseline='middle';
  x.fillText(CAM.pose.title, 40, half*2+44); x.globalAlpha=.7; x.font='500 28px system-ui, sans-serif'; x.fillText('Segovia a pie · 11·10·2026', 40, half*2+90); x.globalAlpha=1;
  x.fillStyle='rgba(0,0,0,.55)'; [['ANTES',0],['VOSOTROS',half]].forEach(([t,y])=>{ x.fillRect(24,y+24,t.length*24+40,52); }); x.fillStyle='#fff'; x.font='800 30px system-ui, sans-serif'; [['ANTES',0],['VOSOTROS',half]].forEach(([t,y])=>x.fillText(t,44,y+51));
  c.toBlob(b=>showShot(b), 'image/jpeg', .85);
}
function showShot(blob){
  stopCam(); const url=URL.createObjectURL(blob); const d=$('#gm'); const pid=CAM.pose.id+'-'+Math.random().toString(36).slice(2,6);
  savePhoto(blob, CAM.pose.title);
  d.className='modal'; d.innerHTML=`<div class="gm-in"><div class="gm-top"><button class="gm-x" id="gmClose" aria-label="Cerrar">${ICON.x}</button><span class="gm-k">Reto foto</span></div>
    <img class="shot" src="${url}" alt="Vuestra recreación junto a la imagen histórica">
    <div class="row" style="justify-content:center">${navigator.canShare?`<button class="btn primary" id="shShare">Compartir</button>`:''}<button class="btn ${navigator.canShare?'':'primary'}" id="shAsk">${others().length?'Pedir nota a '+esc(nameOf(others()[0])):'Guardada'}</button><button class="btn ghost" id="shAgain">Repetir</button></div>
    <p class="gm-note">Mantén pulsada la imagen para guardarla en tu carrete.</p></div>`;
  $('#gmClose').onclick=closeModal; $('#shAgain').onclick=()=>{ const p=CAM.pose; closeModal(); openPose(p); };
  const sh=$('#shShare'); if(sh) sh.onclick=async()=>{ try{ const f=new File([blob],'segovia-reto.jpg',{type:'image/jpeg'}); if(navigator.canShare({files:[f]})) await navigator.share({files:[f], title:'Segovia a pie', text:CAM.pose.title}); }catch(e){} };
  $('#shAsk').onclick=()=>{ if(others().length){ netSend({t:'photo', pid, title:CAM.pose.title}); toast('Enviado: tu pareja puntuará la foto'); $('#shAsk').disabled=true; } };
}
function savePhoto(blob, title){
  try{ const r=new FileReader(); r.onload=()=>{ const im=new Image(); im.onload=()=>{ const c=document.createElement('canvas'); const s=360/im.width; c.width=360; c.height=Math.round(im.height*s); c.getContext('2d').drawImage(im,0,0,c.width,c.height); const list=store.get('shots',[]); list.unshift({t:title, d:c.toDataURL('image/jpeg',.7)}); store.set('shots', list.slice(0,8)); }; im.src=r.result; }; r.readAsDataURL(blob); }catch(e){}
}

/* ---------- retos de pareja y caza ---------- */
function drawDare(){
  const here = S[cur]?.id; const pool = GD.dares.filter(d=>d.stop===here); const all = pool.length? pool : GD.dares;
  const fresh = all.filter(d=>!GS.awarded.has('dare:'+d.id+':'+ME.id) && d.id!==GS.lastDare);
  const d = (fresh.length?fresh:all)[Math.floor(Math.random()*(fresh.length?fresh:all).length)];
  if(!d) return; GS.lastDare=d.id;
  const m=document.createElement('div'); m.id='gm'; m.className='modal'; document.body.appendChild(m);
  const ppl=[ME.id].concat(others());
  m.innerHTML=`<div class="gm-in"><div class="gm-top"><button class="gm-x" id="gmClose" aria-label="Cerrar">${ICON.x}</button><span class="gm-k">Reto de pareja · ${d.pts} pts</span></div>
    <div class="dare">${esc(d.d)}</div>
    <p class="gm-note">¿Quién lo ha cumplido?</p>
    <div class="gm-opts two">${ppl.map(p=>`<button class="gm-o big" data-p="${p}">${esc(p===ME.id?'Yo':nameOf(p))}</button>`).join('')}</div>
    <button class="btn ghost arrived" id="dareNext">Otro reto</button></div>`;
  $('#gmClose').onclick=closeModal; $('#dareNext').onclick=()=>{ closeModal(); drawDare(); };
  m.querySelectorAll('[data-p]').forEach(b=>b.onclick=()=>{ netSend({t:'dare', id:d.id, target:b.dataset.p, pts:d.pts}); burst(); closeModal(); toast('+'+d.pts+' para '+(b.dataset.p===ME.id?'ti':nameOf(b.dataset.p))); });
}
function huntFor(stopId){ return GD.hunt.filter(h=>h.stop===stopId); }
function huntHTML(s){
  const hs=huntFor(s.id); if(!hs.length) return '';
  return `<div class="hunt"><b>Caza del detalle</b>${hs.map(h=>{ const f=GS.found[h.id]; return `<div class="hunt-i"><div><span>${esc(h.find)}</span><small>${esc(h.hint||'')}</small></div>${f?`<em>${esc(f===ME.id?'¡Tuyo!':nameOf(f))} +100</em>`:`<button class="btn sm primary" data-hunt="${h.id}">¡Lo veo!</button>`}</div>`; }).join('')}</div>`;
}
document.addEventListener('click', e=>{ const b=e.target.closest('[data-hunt]'); if(!b) return; b.disabled=true; netSend({t:'found', id:b.dataset.hunt}); burst(); setTimeout(()=>{ if(tab==='stop') render(); },700); });

/* ---------- pestaña Juegos ---------- */
function softRenderGames(){ if(tab!=='games') return; const b=$('#body'), y=b.scrollTop; const a=document.activeElement; if(a && a.tagName==='INPUT') return; b.innerHTML=gamesHTML(); wireGames(); b.scrollTop=y; }
function renderGames(){ if(tab!=='games') return; $('#body').innerHTML=gamesHTML(); wireGames(); }
function gamesHTML(){
  const ppl = [ME.id].concat(others());
  let h='';
  if(!ME.name){
    return h+`<div class="g-hero"><h2>Juegos para dos</h2><p class="hook">Trivial, verdad o leyenda, adivinar años, retos y fotos recreando la Segovia de antes. Cada uno desde su móvil.</p>
      <label class="g-lab" for="gName">¿Cómo te llamas?</label><input class="g-in" id="gName" maxlength="14" autocomplete="given-name" placeholder="Tu nombre"><button class="btn primary arrived" id="gNameGo">Empezar</button></div>`;
  }
  h += `<div class="g-score">${ppl.map(p=>`<div class="${p===ME.id?'mine':''}"><small>${esc(p===ME.id?(ME.name||'Tú'):nameOf(p))}</small><b>${GS.scores[p]||0}</b></div>`).join(ppl.length<2?'':'<span>vs</span>')}${ppl.length<2?`<div class="ghost"><small>Tu pareja</small><b>—</b></div>`:''}</div>`;
  if(canNet()){
    if(!NET.code) h += `<div class="g-room"><div><b>Jugad en pareja</b><small>Crea una sala y pásale el código a tu pareja. Cada uno juega desde su móvil.</small></div><div class="row" style="margin:10px 0 0"><button class="btn primary" id="gCreate">Crear sala</button><input class="g-in code" id="gCode" maxlength="6" placeholder="Código" autocapitalize="characters"><button class="btn" id="gJoin">Unirme</button></div></div>`;
    else h += `<div class="g-room on"><div><b><span id="netDot" class="netdot ${NET.ok?'on':'off'}"></span>Sala ${esc(NET.code)}</b><small>${others().length?'Conectados: '+ppl.map(p=>esc(nameOf(p))).join(' y '):'Esperando a tu pareja: que abra Juegos y ponga este código'}</small></div><div class="row" style="margin:10px 0 0"><button class="btn sm" id="gShareCode">Compartir código</button><button class="btn sm ghost" id="gLeave">Salir</button></div></div>`;
  } else h += `<div class="g-room"><b>Modo en pareja</b><small>Para jugar cada uno desde su móvil, abrid la versión web. Aquí podéis jugar con un solo móvil.</small>${WEB_URL?`<a class="btn sm primary" style="margin-top:10px" href="${WEB_URL}" target="_blank" rel="noopener">Abrir versión web</a>`:''}</div>`;
  if(GS.rateAsk && GS.photos[GS.rateAsk] && !GS.photos[GS.rateAsk].rated){ const ph=GS.photos[GS.rateAsk]; h += `<div class="g-rate"><b>${esc(nameOf(ph.from))} ha recreado «${esc(ph.title)}»</b><small>Mirad su móvil y puntuad el parecido</small><div class="stars">${[1,2,3,4,5].map(n=>`<button data-star="${n}" aria-label="${n} estrellas">${ICON.star}</button>`).join('')}</div></div>`; }
  const cards = [
    ['trivia','Trivial segoviano','10 preguntas, primero de lo que ya habéis visto. Gana quien acierta y más rápido.',10],
    ['vol','¿Verdad o leyenda?','8 frases en 12 segundos cada una. ¿Historia o cuento?',8],
    ['year','Adivina el año','Arrastra hasta el año. Quien más se acerque, gana.',6],
    ['who','¿Quién es más probable?','Preguntas de pareja con guiño histórico. Si coincidís, puntos para los dos.',6],
  ];
  h += `<h3>Duelos</h3><div class="g-list">${cards.map(([g,t,d,n])=>`<button class="g-card" data-game="${g}" data-n="${n}"><span class="g-ic">${ICON['g_'+g]||ICON.star}</span><span class="g-tx"><b>${t}</b><small>${d}</small></span><span class="g-n">${Math.min(n,itemsOf(g).length)}</span></button>`).join('')}</div>`;
  h += `<h3>Retos en la calle</h3><div class="g-list"><button class="g-card" id="gDare"><span class="g-ic">${ICON.g_dare}</span><span class="g-tx"><b>Reto de pareja</b><small>Una carta con un reto para la parada en la que estáis.</small></span></button></div>`;
  h += `<h3>Recread la foto histórica</h3><p class="cap" style="margin-top:-4px">Con la imagen antigua superpuesta en la cámara. Encuadrad igual, o imitad la pose.</p><div class="g-poses">${GD.poses.map(p=>`<button class="g-pose" data-pose="${p.id}"><img src="${esc(poseSrc(p))}" alt="" loading="lazy"><span>${esc(p.title)}</span></button>`).join('')}</div>`;
  const shots=store.get('shots',[]); if(shots.length) h += `<h3>Vuestras recreaciones</h3><div class="g-shots">${shots.map(s=>`<figure><img src="${s.d}" alt="${esc(s.t)}"><figcaption>${esc(s.t)}</figcaption></figure>`).join('')}</div>`;
  const hunted=GD.hunt.filter(x=>GS.found[x.id]).length; h += `<h3>Caza del detalle</h3><p class="cap" style="margin-top:-4px">${hunted}/${GD.hunt.length} encontrados. En cada parada, el primero que lo vea y pulse «¡Lo veo!» se lleva 100 puntos.</p>`;
  if(NET.code || ME.name) h += `<button class="btn ghost offl" id="gRename">Cambiar nombre (${esc(ME.name)})</button>`;
  return h;
}
function wireGames(){
  const go=$('#gNameGo'); if(go) go.onclick=()=>{ const v=$('#gName').value.trim(); if(!v) return $('#gName').focus(); ME.name=v.slice(0,14); store.set('me',ME); GS.players[ME.id]=ME.name; const hc=(location.hash.match(/^#sala([A-Z0-9]{4,6})$/i)||[])[1]; if(hc && !NET.code) joinRoom(hc); else renderGames(); };
  const cr=$('#gCreate'); if(cr) cr.onclick=()=>joinRoom(newCode());
  const jn=$('#gJoin'); if(jn) jn.onclick=()=>{ const v=$('#gCode').value.trim(); if(v.length<4) return toast('El código tiene 4 letras'); joinRoom(v); };
  const lv=$('#gLeave'); if(lv) lv.onclick=leaveRoom;
  const sc=$('#gShareCode'); if(sc) sc.onclick=async()=>{ const url=location.href.split('#')[0]+'#sala'+NET.code; const text='Únete a mi sala en Segovia a pie: código '+NET.code; try{ if(navigator.share){ await navigator.share({title:'Segovia a pie', text, url}); return; } }catch(e){} try{ await navigator.clipboard.writeText(text+' '+url); toast('Copiado: '+NET.code); }catch(e){ toast('Código: '+NET.code); } };
  document.querySelectorAll('[data-game]').forEach(b=>b.onclick=()=>startGame(b.dataset.game, +b.dataset.n));
  const dr=$('#gDare'); if(dr) dr.onclick=drawDare;
  document.querySelectorAll('[data-pose]').forEach(b=>b.onclick=()=>openPose(GD.poses.find(p=>p.id===b.dataset.pose)));
  document.querySelectorAll('[data-star]').forEach(b=>b.onclick=()=>{ const pid=GS.rateAsk, ph=GS.photos[pid]; if(!ph) return; netSend({t:'rate', pid, target:ph.from, stars:+b.dataset.star}); toast('Nota enviada'); });
  const rn=$('#gRename'); if(rn) rn.onclick=()=>{ ME.name=''; store.set('me',ME); renderGames(); };
}
if(NET.code && canNet()) netOpen();
