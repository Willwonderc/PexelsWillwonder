// Coquille commune des deux propositions (version 3) : adresses, ouverture et fermeture de la rubrique,
// retour au bouton, lien direct, clavier, son facultatif, page hôte simulée.
// Adresses : #monde (ouverture), #monde/photo-<id> (fiche). Sans adresse : la page hôte.
// Valeurs de mouvement : référentiel du LAB (REFERENTIEL-MOUVEMENT.md, 28 nov. 2026).

export const M = {
  // Courbes nommées du référentiel, § 3
  sortie: [0.2, 0.8, 0.2, 1],   // entrée d'un élément qui arrive
  aller: [0.4, 0, 0.2, 1],      // déplacement, voiles
  // Durées, § 2 (en millisecondes)
  survol: 240, entree: 400, sortieD: 300, deplacement: 450, voileOuvre: 520, voileFerme: 380, attention: 1350,
  pas: 60, cascadeMax: 600,     // § 5
};
export const css = (c) => `cubic-bezier(${c.join(',')})`;

export const $ = (s, r) => (r || document).querySelector(s);
export const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
export function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
export function pluriel(n, mot, pl) { return n + ' ' + (n > 1 ? (pl || mot + 's') : mot); }
export const calme = window.matchMedia('(prefers-reduced-motion: reduce)');
export const tactile = window.matchMedia('(hover: none)');

export function lieuMedia(u) { return u.lieu ? u.lieu.nom : 'En ligne · lieu non établi'; }
export function credit(p) {
  return 'Photo : Karl Forterre · <a href="' + p.site + '" target="_blank" rel="noopener noreferrer">Voir la photo dans les galeries</a> · <a href="' + p.pexels + '" target="_blank" rel="noopener noreferrer">L’original sur Pexels</a>';
}
export function lienNotice(u) {
  return '<a class="notice-lien" href="' + esc(u.url) + '" target="_blank" rel="noopener noreferrer" title="S’ouvre dans un nouvel onglet">' +
    '<span class="lien-libelle">' + esc(u.lien) + '</span><span class="lien-hote">' + esc(u.hote) + '</span><span class="fleche" aria-hidden="true"></span></a>';
}

/* Son synthétisé : bouton retiré à la demande de Karl (28 novembre 2026), le son reste donc coupé */
let audio = null, sonActif = false;
export function son(type) {
  if (!sonActif) return;
  try {
    audio = audio || new (window.AudioContext || window.webkitAudioContext)();
    const t = audio.currentTime, g = audio.createGain();
    g.connect(audio.destination);
    if (type === 'papier') {
      const n = audio.sampleRate * 0.16, b = audio.createBuffer(1, n, audio.sampleRate), d = b.getChannelData(0);
      for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / n, 2.4);
      const s = audio.createBufferSource(), f = audio.createBiquadFilter();
      f.type = 'bandpass'; f.frequency.value = 1800; f.Q.value = 0.7;
      s.buffer = b; s.connect(f); f.connect(g); g.gain.value = 0.22; s.start(t);
    } else {
      const o = audio.createOscillator();
      o.type = 'sine'; o.frequency.setValueAtTime(type === 'grave' ? 330 : 880, t);
      o.frequency.exponentialRampToValueAtTime(type === 'grave' ? 220 : 1320, t + 0.18);
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.07, t + 0.02); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.5);
      o.connect(g); o.start(t); o.stop(t + 0.55);
    }
  } catch (e) { /* le son n'est qu'un plus */ }
}

/**
 * vue = {
 *   preparer(ctx)                      : construit la scène une fois (appelé à la première ouverture)
 *   afficher(route, ctx, {premier})    : route = {photo: id|null} ; doit poser scene.dataset.vue et le focus
 *   ouverture(ctx) -> {fin: Promise, couper()} : séquence d'ouverture (optionnelle), jouée après le voile
 *   fermer(ctx)                        : la rubrique se ferme (arrêter les boucles)
 *   touche(e, ctx)                     : touches propres (flèches)
 * }
 */
export function demarrer(vue) {
  const D = window.MONDE;
  const monde = $('#monde'), scene = $('#scene'), entree = $('#entree'), fermer = $('#fermer'),
    fermerTexte = $('#fermer-texte'), voile = $('#voile'), bande = $('.entree-bande'), passer = $('#passer'), annonce = $('#annonce');
  const parId = {}; D.photos.forEach((p) => { parId[p.id] = p; });
  const RUBRIQUE = 'Mes photos utilisées dans le monde', titreHote = document.title;
  // Tout le reste de la page devient inerte pendant que la rubrique est ouverte (dialogue modal).
  const reste = (oui) => { Array.from(document.body.children).forEach((el) => { if (el === monde || el === voile || el.tagName === 'SCRIPT') return;
    if (oui) { el.inert = true; el.setAttribute('aria-hidden', 'true'); } else { el.inert = false; el.removeAttribute('aria-hidden'); } }); };
  let direct = false, anim = null, prepare = false, sequence = null, premier = true;
  const ctx = { D, parId, scene, monde, voile, M, son, annoncer: (t) => { annonce.textContent = t; }, enOuverture: () => !!sequence, rubrique: RUBRIQUE };


  const rognure = (b) => 'inset(' + b.top + 'px ' + (innerWidth - b.right) + 'px ' + (innerHeight - b.bottom) + 'px ' + b.left + 'px)';
  const lire = () => { const m = location.hash.match(/^#monde(?:\/photo-(\d+))?$/); return m ? { photo: m[1] || null } : null; };

  function montrer() {
    monde.hidden = false;
    reste(true);
    document.documentElement.classList.add('verrou');
    fermerTexte.textContent = direct ? 'Fermer, vers les galeries' : 'Fermer';
    if (!prepare) { vue.preparer(ctx); prepare = true; }
    requestAnimationFrame(() => monde.classList.add('visible'));
  }
  function finSequence() {
    if (!sequence) return;
    const s = sequence; sequence = null; passer.hidden = true; monde.classList.remove('en-ouverture', 'instant');
    s.couper && s.couper();
  }
  function clore() {
    finSequence();
    vue.fermer && vue.fermer(ctx);
    monde.classList.remove('visible'); monde.hidden = true;
    reste(false);
    document.documentElement.classList.remove('verrou');
    document.title = titreHote;
    premier = true;
    if (direct) { direct = false; entree.scrollIntoView({ block: 'center' }); entree.focus({ preventScroll: true }); voile.hidden = true; return; }
    entree.focus({ preventScroll: true });
    if (calme.matches || !voile.animate) { voile.hidden = true; return; }
    // Fermeture : le voile de photographie revient dans la bande du bouton (380 ms, courbe « aller »)
    voile.hidden = false; voile.style.clipPath = ''; voile.style.opacity = '';
    const a = anim = voile.animate([{ clipPath: 'inset(0px 0px 0px 0px)', opacity: 1 }, { clipPath: rognure(bande.getBoundingClientRect()), opacity: 1 }],
      { duration: M.voileFerme, easing: css(M.aller) });
    a.onfinish = a.oncancel = () => { if (anim === a) anim = null; voile.hidden = true; };
  }
  function rendre() {
    const r = lire();
    if (!r) { if (!monde.hidden) clore(); return; }
    const ouvrir = monde.hidden;
    if (ouvrir) montrer();
    if (r.photo && !parId[r.photo]) r.photo = null;
    document.title = (r.photo ? parId[r.photo].libelle + ' — ' : '') + RUBRIQUE + ' — Karl Forterre';
    const p1 = premier; premier = false;
    vue.afficher(r, ctx, { premier: p1 });
    if (ouvrir && !r.photo && !direct && !calme.matches && vue.ouverture) {
      monde.classList.add('instant');
      sequence = vue.ouverture(ctx);
      if (!sequence) monde.classList.remove('instant');
      if (sequence) {
        monde.classList.add('en-ouverture'); passer.hidden = false;
        sequence.fin.then(() => { if (sequence) { sequence = null; passer.hidden = true; monde.classList.remove('en-ouverture', 'instant'); } });
      }
    } else voile.hidden = true;
  }
  function quitter() {
    if (anim) anim.cancel();
    if (lire()) history.pushState(null, '', location.pathname + location.search);
    rendre();
  }
  ctx.aller = (hash) => { if (location.hash !== hash) location.hash = hash; else rendre(); };

  entree.addEventListener('click', () => {
    direct = false;
    if (anim) anim.cancel();
    if (calme.matches || !voile.animate) { location.hash = 'monde'; return; }
    // La bande de photographie du bouton s'agrandit jusqu'à couvrir l'écran (520 ms, « aller ») ; la scène prend le relais.
    voile.hidden = false; voile.style.clipPath = 'inset(0px 0px 0px 0px)'; voile.style.opacity = '';
    const a = anim = voile.animate([{ clipPath: rognure(bande.getBoundingClientRect()) }, { clipPath: 'inset(0px 0px 0px 0px)' }],
      { duration: M.voileOuvre, easing: css(M.aller) });
    a.onfinish = () => { if (anim === a) { anim = null; location.hash = 'monde'; } };
    a.oncancel = () => { if (anim === a) anim = null; voile.hidden = true; };
  });
  fermer.addEventListener('click', quitter);
  voile.addEventListener('click', () => { if (anim) quitter(); });
  passer.addEventListener('click', () => { finSequence(); scene.querySelector('h1') && scene.querySelector('h1').focus({ preventScroll: true }); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && (anim || !monde.hidden)) { e.preventDefault(); quitter(); return; }
    if (monde.hidden || e.metaKey || e.ctrlKey || e.altKey) return;
    if (sequence && e.key !== 'Tab' && e.key !== 'Shift') { finSequence(); }
    vue.touche && vue.touche(e, ctx);
  });
  monde.addEventListener('pointerdown', (e) => { if (sequence && !e.target.closest('.barre')) finSequence(); });

  addEventListener('hashchange', rendre);
  if (lire()) direct = true;
  rendre();
  return ctx;
}
