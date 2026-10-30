// Legge opere e testi da opere.json e li dispone nella griglia.
// Per aggiungere un'opera non serve toccare questo file: vedi LEGGIMI.md.
(async function () {
  const $ = id => document.getElementById(id);
  const griglia = $('griglia'), filtri = $('filtri'), scheda = $('scheda');
  $('anno').textContent = new Date().getFullYear();
  logo();

  let dati;
  try {
    const r = await fetch('opere.json', { cache: 'no-cache' });
    dati = await r.json();
  } catch (e) {
    griglia.innerHTML = '<p class="msg wrap">Non è stato possibile caricare le opere. Controlla che il file opere.json sia scritto correttamente (virgole e virgolette).</p>';
    return;
  }

  // Contatti, biografia, ritratto
  const email = (dati.email_contatto || '').trim();
  if (email) {
    const a = $('contatto-email').querySelector('a');
    a.href = 'mailto:' + email;
    a.querySelector('.v').textContent = email;
    $('contatto-email').hidden = false;
  }
  $('bio-testo').replaceChildren(...paragrafi(dati.biografia));
  if (dati.ritratto) {
    const img = new Image();
    img.src = dati.ritratto;
    img.alt = 'Ritratto di Sara Citarella';
    img.onerror = () => img.remove();
    $('ritratto').prepend(img);
  }

  const opere = (dati.opere || [])
    .filter(o => o && o.titolo && o.pubblicata !== false)
    .map((o, i) => ({ ...o, id: 'opera-' + slug(o.titolo), ordine: i }))
    .sort((a, b) => (Number(b.anno) || 0) - (Number(a.anno) || 0) || a.ordine - b.ordine);
  // Numero di catalogo: la più vecchia è la 01
  opere.forEach((o, i) => { o.num = String(opere.length - i).padStart(2, '0'); });

  // Filtri: tutte, ogni anno presente, disponibili
  const anni = [...new Set(opere.map(o => o.anno).filter(Boolean))].sort((a, b) => b - a);
  const scelte = [['tutte', 'Tutte'], ...anni.map(a => [String(a), String(a)]), ['disponibili', 'Disponibili']];
  let filtro = 'tutte';
  for (const [val, label] of scelte) {
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = label;
    b.setAttribute('aria-pressed', val === filtro);
    b.addEventListener('click', () => {
      filtro = val;
      filtri.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x === b));
      disegna();
    });
    filtri.append(b);
  }

  let visibili = [];
  function disegna() {
    visibili = opere.filter(o =>
      filtro === 'tutte' ? true :
      filtro === 'disponibili' ? o.disponibile !== false :
      String(o.anno) === filtro);
    griglia.replaceChildren(...visibili.map(cella));
    if (!visibili.length) griglia.innerHTML = '<p class="msg wrap">Nessuna opera in questa selezione.</p>';
  }

  function cella(o) {
    const w = Number(o.larghezza) || 50, h = Number(o.altezza) || 50;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'tile';
    btn.id = o.id;
    btn.setAttribute('aria-label', o.titolo + ', apri la scheda');

    const fig = document.createElement('span');
    fig.className = 'tile-img';
    if (o.immagine) {
      const img = new Image();
      img.alt = o.titolo;
      img.loading = 'lazy';
      img.onerror = () => { img.remove(); fig.append(vuoto(w, h)); };
      img.src = o.immagine;
      fig.append(img);
    } else {
      fig.append(vuoto(w, h));
    }

    const cap = document.createElement('span');
    cap.className = 'tile-cap';
    cap.innerHTML = '<span class="tile-n"></span><span class="tile-t"></span><span class="tile-m"></span>';
    cap.querySelector('.tile-n').textContent = o.num;
    cap.querySelector('.tile-t').textContent = o.titolo;
    const m = cap.querySelector('.tile-m');
    m.textContent = [o.anno, misure(o, false)].filter(Boolean).join(' · ');
    if (o.disponibile === false) {
      const s = document.createElement('span');
      s.className = 'sold';
      s.textContent = ' · Non disponibile';
      m.append(s);
    }

    btn.append(fig, cap);
    btn.addEventListener('click', () => apri(o));
    return btn;
  }

  // Segnaposto nelle proporzioni reali dell'opera
  function vuoto(w, h) {
    const v = document.createElement('span');
    v.className = 'vuoto';
    v.style.setProperty('--w', w);
    v.style.setProperty('--lato', Math.max(w, h));
    v.style.setProperty('--ar', w + ' / ' + h);
    v.textContent = 'Foto in arrivo';
    return v;
  }

  function misure(o, conProfondita) {
    if (!o.larghezza || !o.altezza) return '';
    let s = o.larghezza + '×' + o.altezza;
    if (conProfondita && o.profondita) s += '×' + o.profondita;
    return s + ' cm';
  }

  function paragrafi(testo) {
    return String(testo || '').split('\n').filter(s => s.trim()).map(t => {
      const p = document.createElement('p'); p.textContent = t; return p;
    });
  }

  // Scheda dell'opera
  let corrente = null;
  function apri(o) {
    corrente = o;
    const fig = $('scheda-img');
    fig.className = 'sheet-img';
    fig.replaceChildren();
    if (o.immagine) {
      const img = new Image();
      img.alt = o.titolo;
      img.onerror = () => { img.remove(); fig.classList.add('missing'); fig.textContent = 'Foto in arrivo'; };
      img.src = o.immagine;
      fig.append(img);
    } else {
      fig.classList.add('missing');
      fig.textContent = 'Foto in arrivo';
    }

    $('scheda-num').textContent = 'N. ' + o.num + (o.anno ? ' · ' + o.anno : '');
    $('scheda-titolo').textContent = o.titolo;

    const righe = [
      ['Tecnica', o.tecnica],
      ['Supporto', o.supporto],
      ['Misure', misure(o, true)],
      ['Stato', o.disponibile === false ? 'Non disponibile' : 'Disponibile'],
      ['Prezzo', o.disponibile !== false && o.prezzo ? '€ ' + Number(o.prezzo).toLocaleString('it-IT') : '']
    ].filter(r => r[1]);
    const dl = $('scheda-dati');
    dl.replaceChildren();
    for (const [k, v] of righe) {
      const dt = document.createElement('dt'); dt.textContent = k;
      const dd = document.createElement('dd'); dd.textContent = v;
      dl.append(dt, dd);
    }
    $('scheda-desc').replaceChildren(...paragrafi(o.descrizione));

    const cta = $('scheda-cta');
    if (email) {
      cta.href = 'mailto:' + email + '?subject=' + encodeURIComponent('Informazioni su «' + o.titolo + '»');
      cta.removeAttribute('target');
    } else {
      cta.href = 'https://www.instagram.com/saracitarella.art';
      cta.target = '_blank';
    }

    if (!scheda.open) scheda.showModal();
    scheda.scrollTop = 0;
    if (location.hash !== '#' + o.id) history.replaceState(null, '', '#' + o.id);
  }

  function sposta(d) {
    if (!corrente || !visibili.length) return;
    const i = visibili.indexOf(corrente);
    apri(visibili[(i + d + visibili.length) % visibili.length]);
  }
  $('prec').addEventListener('click', () => sposta(-1));
  $('succ').addEventListener('click', () => sposta(1));
  $('chiudi').addEventListener('click', () => scheda.close());
  scheda.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft') sposta(-1);
    if (e.key === 'ArrowRight') sposta(1);
  });
  scheda.addEventListener('close', () => {
    if (location.hash.startsWith('#opera-')) history.replaceState(null, '', location.pathname + location.search);
    corrente = null;
  });

  // Tele generate come i suoi quadri: campiture stese a spatola,
  // con i bordi sfrangiati e raschiature verticali che lasciano vedere il fondo
  function tela(w, h, campiture, fondo, seme) {
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    const g = c.getContext('2d');
    const caso = () => (seme = (seme * 16807) % 2147483647) / 2147483647;
    g.fillStyle = fondo;
    g.fillRect(0, 0, w, h);
    for (const [colore, x0, y0, x1, y1] of campiture) {
      const bx = x0 * w, by = y0 * h, bw = (x1 - x0) * w, bh = (y1 - y0) * h;
      g.fillStyle = colore;
      for (let x = bx; x < bx + bw; ) {
        const s = 2 + caso() * 7;
        // la spatola parte e si ferma in punti diversi: bordi alto e basso irregolari
        const a = by + (caso() < 0.3 ? caso() * bh * 0.18 : caso() * 4);
        const z = by + bh - (caso() < 0.35 ? caso() * bh * 0.3 : caso() * 4);
        g.globalAlpha = caso() < 0.12 ? 0.55 : 1;
        g.fillRect(x, a, Math.min(s, bx + bw - x), z - a);
        x += s;
      }
    }
    // raschiature del fondo dentro le campiture
    g.fillStyle = fondo;
    for (let i = 0; i < w / 6; i++) {
      g.globalAlpha = 0.6 + caso() * 0.4;
      const y = caso() * h;
      g.fillRect(caso() * w, y, 1 + caso() * 3, h * (0.08 + caso() * 0.5));
    }
    g.globalAlpha = 1;
    return `url(${c.toDataURL('image/jpeg', 0.88)})`;
  }
  function logo() {
    const hero = document.querySelector('.hero');
    // campiture di colori primari, come le sue tele giallo / rosso / blu
    hero.style.setProperty('--tela-colori', tela(400, 400, [
      ['#ffd60a', 0.0, 0.0, 0.48, 0.5], ['#ff1f3d', 0.0, 0.53, 0.48, 1.0],
      ['#f7f6f2', 0.51, 0.0, 1.0, 0.5], ['#1f3bff', 0.51, 0.53, 1.0, 1.0]
    ], '#111111', 5));
  }

  function slug(t) {
    return String(t).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
  }

  disegna();

  // Link diretto a un'opera: sito/#opera-comfort-zone
  const dalLink = opere.find(o => '#' + o.id === location.hash);
  if (dalLink) apri(dalLink);
})();
