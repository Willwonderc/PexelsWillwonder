// Rubrique « Mes photos utilisées dans le monde », version 4A validée par Karl (28 nov. 2026) : « Une photographie qui voyage ». Le globe de nuit (v3), puis l'affiche claire de chaque photo,
// inspirée de la maquette « Cognac, une photographie qui voyage » : éclat de triangles aux couleurs de la photo.
// three.js : le globe (points de terre, arcs, couronne des sites en ligne, lieux racontés).
// Motion : le mouvement de l'interface (entrées des textes, cascades, panneau de la fiche).
import './dialogue.js';
import * as THREE from 'three';
import { animate, stagger } from 'motion';
import { demarrer, M, css, $, $$, esc, pluriel, calme, tactile, lieuMedia, credit, lienNotice, son } from './coquille.js';
import { eclatSVG, jouerEclat, graineDe } from './eclat.js';
import { couleurs, titreAffiche, compteur, regardsTitre, regardHTML } from './affiche.js';

const D = window.MONDE;
const RAD = Math.PI / 180, ORBITE = 1.36;
const sec = (ms) => ms / 1000;

/* ---------- Géographie ---------- */
function vec(lat, lon, r = 1) {
  const p = lat * RAD, t = lon * RAD;
  return new THREE.Vector3(r * Math.cos(p) * Math.sin(t), r * Math.sin(p), r * Math.cos(p) * Math.cos(t));
}
const FRANCE = vec(46.6, 2.4).normalize();
const NORD = new THREE.Vector3(0, 1, 0).sub(FRANCE.clone().multiplyScalar(FRANCE.y)).normalize();
const EST = new THREE.Vector3().crossVectors(NORD, FRANCE).normalize();
// Couronne des sites en ligne : un petit cercle autour de la France, à l'altitude de l'orbite.
function couronne(psi, r = ORBITE, ouverture = 52) {
  const a = ouverture * RAD;
  return FRANCE.clone().multiplyScalar(Math.cos(a)).add(EST.clone().multiplyScalar(Math.sin(a) * Math.cos(psi * RAD)))
    .add(NORD.clone().multiplyScalar(Math.sin(a) * Math.sin(psi * RAD))).multiplyScalar(r);
}
const PAYS = { 'Dallas, Texas': 'États-Unis', 'Vexin, Oise': 'France', 'Deux-Sèvres': 'France', 'La Rochelle': 'France' };
const pays = (u) => (u.lieu ? (PAYS[u.lieu.nom] || u.lieu.nom) : null);

const usages = [];
D.photos.forEach((p, ip) => p.usages.forEach((u) => usages.push({ u, p, ip })));
const enLigne = usages.filter((x) => !x.u.lieu);
enLigne.forEach((x, i) => { x.sat = couronne(28 + i * (124 / Math.max(1, enLigne.length - 1))); });
usages.forEach((x) => {
  x.a = vec(x.p.origine.lat, x.p.origine.lon);
  x.b = x.sat || vec(x.u.lieu.lat, x.u.lieu.lon);
  if (x.u.raconte && x.u.raconte.lat != null) x.c = vec(x.u.raconte.lat, x.u.raconte.lon);
  x.groupe = pays(x.u) || 'En ligne';
});
const GROUPES = ['France', 'Espagne', 'Lituanie', 'États-Unis', 'Brésil', 'En ligne'];

/* ---------- Scène three.js ---------- */
let renderer, scene3, camera, globe, decor, etiquettes, etat, arcs = [], marques = {}, horloge = new THREE.Timer(), boucle = 0, ok3d = true;
const vise = { lat: 46.6, lon: 2.4, cx: 0, cy: 0, rpx: 200 }, cur = { lat: 20, lon: -40, cx: 0, cy: 0, rpx: 600 };
let glisse = null, respire = 0, ambiance = true, surbrillance = null;

function texturePoint(type) {
  const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
  g.translate(32, 32);
  if (type === 'plein') { g.fillStyle = '#fff'; g.beginPath(); g.arc(0, 0, 20, 0, 7); g.fill(); }
  if (type === 'anneau') { g.strokeStyle = '#fff'; g.lineWidth = 7; g.beginPath(); g.arc(0, 0, 22, 0, 7); g.stroke(); }
  if (type === 'carre') { g.fillStyle = '#fff'; g.fillRect(-16, -16, 32, 32); }
  if (type === 'onde') { g.strokeStyle = '#fff'; g.lineWidth = 3; g.beginPath(); g.arc(0, 0, 28, 0, 7); g.stroke(); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

function arcCourbe(a, b, haut) {
  const da = a.clone().normalize(), db = b.clone().normalize(), ra = a.length(), rb = b.length();
  const angle = da.angleTo(db), pts = [];
  const bosse = haut != null ? haut : 0.04 + 0.32 * angle / Math.PI;
  for (let i = 0; i <= 48; i++) {
    const t = i / 48, s = Math.sin(angle) || 1;
    const d = angle < 1e-4 ? da.clone() : da.clone().multiplyScalar(Math.sin((1 - t) * angle) / s).add(db.clone().multiplyScalar(Math.sin(t * angle) / s));
    pts.push(d.normalize().multiplyScalar(ra + (rb - ra) * t + bosse * Math.sin(Math.PI * t) + 0.004));
  }
  return new THREE.CatmullRomCurve3(pts);
}

function construire3D() {
  decor = $('#decor');
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  } catch (e) { ok3d = false; decor.classList.add('sans-3d'); return; }
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  decor.appendChild(renderer.domElement);
  etiquettes = document.createElement('div'); etiquettes.className = 'etiquettes'; decor.appendChild(etiquettes);
  scene3 = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100);
  globe = new THREE.Group(); scene3.add(globe);

  // Corps du globe : il cache ce qui est derrière ; un liseré de lumière en dessine le bord.
  globe.add(new THREE.Mesh(new THREE.SphereGeometry(0.992, 64, 48), new THREE.MeshBasicMaterial({ color: 0x0d0d0e })));
  const bord = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, side: THREE.BackSide, blending: THREE.AdditiveBlending,
    vertexShader: 'varying vec3 n; void main(){ n = normalize(normalMatrix*normal); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: 'varying vec3 n; void main(){ float f = pow(clamp(1.0 + n.z, 0., 1.), 9.0); gl_FragColor = vec4(vec3(1.), f*0.45); }',
  });
  scene3.add(new THREE.Mesh(new THREE.SphereGeometry(1.025, 64, 48), bord));

  // Terres : un semis de points, plus pâles vers le bord.
  const T = D.geo.terres, pos = new Float32Array(T.length / 2 * 3);
  for (let i = 0; i < T.length; i += 2) { const v = vec(T[i], T[i + 1], 1.0); pos.set([v.x, v.y, v.z], i / 2 * 3); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  etat = { echelle: { value: 300 } };
  const terre = new THREE.Points(g, new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, uniforms: { echelle: etat.echelle },
    vertexShader: 'uniform float echelle; varying float a; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.); vec3 n = normalize(normalMatrix*position); a = smoothstep(0.0, 0.55, n.z); gl_PointSize = max(1.5, echelle*0.02/(-mv.z)); gl_Position = projectionMatrix*mv; }',
    fragmentShader: 'varying float a; void main(){ vec2 c = gl_PointCoord-.5; if(dot(c,c)>.25) discard; gl_FragColor = vec4(vec3(.86), .10 + .62*a); }',
  }));
  globe.add(terre);

  // Couronne des sites en ligne : un cercle pointillé
  const cpts = []; for (let k = 0; k <= 180; k++) cpts.push(couronne(k * 2));
  const cg = new THREE.BufferGeometry().setFromPoints(cpts);
  const cl = new THREE.Line(cg, new THREE.LineDashedMaterial({ color: 0xffffff, transparent: true, opacity: 0.32, dashSize: 0.018, gapSize: 0.022 }));
  cl.computeLineDistances(); globe.add(cl);

  const tex = { plein: texturePoint('plein'), anneau: texturePoint('anneau'), carre: texturePoint('carre'), onde: texturePoint('onde') };
  const sprite = (t, taille, op = 1) => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex[t], transparent: true, opacity: op, depthTest: true, depthWrite: false })); s.scale.setScalar(taille); return s; };
  const marque = (cle, v, type, taille) => {
    if (marques[cle]) return marques[cle];
    const m = { v: v.clone(), s: sprite(type, taille, 0.35), onde: sprite('onde', taille * 2.4, 0), allume: 0, t0: -9 };
    m.s.position.copy(v); m.onde.position.copy(v); globe.add(m.s); globe.add(m.onde); marques[cle] = m; return m;
  };
  usages.forEach((x) => {
    x.mo = marque('o:' + x.p.origine.nom, x.a, 'anneau', 0.042);
    x.mb = marque(x.sat ? 'sat:' + x.u.id : 'm:' + x.u.lieu.nom, x.b, 'plein', 0.03);
    if (x.c) x.mc = marque('r:' + x.u.raconte.nom, x.c, 'carre', 0.028);
    const geo = new THREE.TubeGeometry(arcCourbe(x.a, x.b), 64, 0.0036, 6, false);
    const mat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.85, depthWrite: false });
    const mesh = new THREE.Mesh(geo, mat); globe.add(mesh);
    const total = geo.index.count; geo.setDrawRange(0, 0);
    const arc = { x, mesh, geo, total, prog: 0, cible: 0, op: 0.85 };
    if (x.c) {
      const lg = new THREE.BufferGeometry().setFromPoints(arcCourbe(x.b, x.c, 0.12).getPoints(80));
      arc.raconte = new THREE.Line(lg, new THREE.LineDashedMaterial({ color: 0xffffff, transparent: true, opacity: 0, dashSize: 0.02, gapSize: 0.016 }));
      arc.raconte.computeLineDistances(); globe.add(arc.raconte);
    }
    x.arc = arc; arcs.push(arc);
  });

  new ResizeObserver(cadrer).observe(decor);
  // Glisser pour tourner le globe (souris, doigt) ; la molette reste au défilement.
  renderer.domElement.addEventListener('pointerdown', (e) => {
    glisse = { x: e.clientX, y: e.clientY, lat: vise.lat, lon: vise.lon, id: e.pointerId }; ambiance = false;
    renderer.domElement.setPointerCapture(e.pointerId);
  });
  renderer.domElement.addEventListener('pointermove', (e) => {
    if (!glisse) return;
    const k = 90 / Math.max(120, vise.rpx * 1.6);
    vise.lon = glisse.lon - (e.clientX - glisse.x) * k; vise.lat = Math.max(-60, Math.min(75, glisse.lat + (e.clientY - glisse.y) * k));
  });
  const lacher = () => { glisse = null; };
  renderer.domElement.addEventListener('pointerup', lacher); renderer.domElement.addEventListener('pointercancel', lacher);
}

/* Cadrage : où se tient le globe selon la vue et l'écran */
let vueCourante = 'index';
function cadrer() {
  if (!ok3d) return;
  const W = decor.clientWidth, H = decor.clientHeight;
  renderer.setSize(W, H, false); camera.aspect = W / H;
  const large = innerWidth >= 900, barre = $('.barre').offsetHeight;
  if (!large) { vise.cx = W / 2; vise.cy = H / 2 + 6; vise.rpx = Math.min(W, H) * 0.3; }
  else if (vueCourante === 'fiche') { const pan = $('.panneau') ? $('.panneau').offsetWidth + 48 : W * 0.42; vise.cx = (W - pan) / 2 + 12; vise.cy = barre + (H - barre) / 2; vise.rpx = Math.min(W - pan, H - barre) * 0.33; }
  else { const col = $('.colonne') ? $('.colonne').getBoundingClientRect().right : W * 0.42; vise.cx = col + (W - col) / 2; vise.cy = barre + (H - barre) / 2; vise.rpx = Math.min(W - col, H - barre) * 0.33; }
  if (vueCourante === 'fiche') vise.rpx *= zoom;
  // la caméra reste hors du globe
  vise.rpx = Math.min(vise.rpx, 0.7 * (H / 2) / Math.tan(camera.fov * RAD / 2));
  etat.echelle.value = H;
  // Zone permise aux étiquettes : jamais sous la colonne de texte, jamais hors de l'écran.
  if (!large) zone = { x0: 6, x1: W - 6, y0: 6, y1: H - 6 };
  else if (vueCourante === 'fiche') zone = { x0: 8, x1: ($('.panneau') ? $('.panneau').getBoundingClientRect().left : W * 0.58) - 18, y0: barre + 8, y1: H - 8 };
  else zone = { x0: ($('.colonne') ? $('.colonne').getBoundingClientRect().right : W * 0.42) + 18, x1: W - 8, y0: barre + 8, y1: H - 8 };
}
let zone = { x0: 0, x1: 99999, y0: 0, y1: 99999 };
function orienter(points) {
  // Le globe se tourne vers le lieu de prise de vue (premier point) et s'en approche (× 2 à × 3,2) :
  // on voit clairement où l'on est ; les lieux proches restent dans le cadre, les lointains en sortent.
  const s = points[0].clone().normalize();
  vise.lat = Math.asin(s.y) / RAD; vise.lon = Math.atan2(s.x, s.z) / RAD;
  const sol = points.filter((v) => v.length() < 1.1);
  const ecart = Math.max(0.05, ...sol.map((v) => (v.clone().normalize().angleTo(s) < 0.6 ? Math.sin(v.clone().normalize().angleTo(s)) : 0)));
  zoom = Math.max(2, Math.min(3.2, 0.8 / ecart)); cadrer();
}
let zoom = 1;

/* Boucle : le temps fait avancer le mouvement, jamais le nombre d'images (référentiel, § 1 et § 8) */
const amortir = (a, b, dt, tau) => a + (b - a) * (1 - Math.exp(-dt / tau));
function tour() {
  boucle = requestAnimationFrame(tour);
  horloge.update(); const dt = Math.min(0.1, horloge.getDelta()), t = horloge.getElapsed(), tau = calme.matches ? 0.0001 : 0.48;
  if (ambiance && !calme.matches && vueCourante === 'index') respire += dt;
  const lonAmb = vueCourante === 'index' && ambiance && !calme.matches ? Math.sin(respire * 2 * Math.PI / 24) * 14 : 0;
  // court chemin en longitude
  let dl = ((vise.lon + lonAmb - cur.lon) % 360 + 540) % 360 - 180;
  cur.lon += dl * (1 - Math.exp(-dt / (glisse ? 0.08 : tau)));
  cur.lat = amortir(cur.lat, vise.lat, dt, glisse ? 0.08 : tau);
  cur.cx = amortir(cur.cx, vise.cx, dt, tau); cur.cy = amortir(cur.cy, vise.cy, dt, tau); cur.rpx = amortir(cur.rpx, vise.rpx, dt, tau);
  globe.rotation.set(cur.lat * RAD, -cur.lon * RAD, 0, 'XYZ');
  const W = decor.clientWidth, H = decor.clientHeight, f = (H / 2) / Math.tan(camera.fov * RAD / 2);
  camera.position.set(0, 0, f / cur.rpx); camera.lookAt(0, 0, 0);
  camera.setViewOffset(W, H, W / 2 - cur.cx, H / 2 - cur.cy, W, H); camera.updateProjectionMatrix();
  arcs.forEach((a) => {
    a.prog = calme.matches ? a.cible : Math.min(a.cible, a.prog + dt / sec(M.deplacement + 350)) ; if (a.cible < a.prog) a.prog = a.cible;
    const e = 1 - Math.pow(1 - a.prog, 3);
    a.geo.setDrawRange(0, Math.floor(a.total * e / 6) * 6);
    const visee = surbrillance ? (surbrillance(a.x) ? 1 : 0.1) : 0.78;
    a.mesh.material.opacity = amortir(a.mesh.material.opacity, visee, dt, 0.18);
    if (a.raconte) a.raconte.material.opacity = amortir(a.raconte.material.opacity, a.prog >= 1 ? visee * 0.8 : 0, dt, 0.18);
    if (a.prog >= 1 && !a.arrive) { a.arrive = true; [a.x.mb, a.x.mc].forEach((m) => { if (m) { m.allume = 1; m.t0 = t; } }); }
    if (a.prog < 1) a.arrive = false;
  });
  Object.values(marques).forEach((m) => {
    const vis = m.allume ? 1 : 0.35;
    m.s.material.opacity = amortir(m.s.material.opacity, vis, dt, 0.2);
    const k = (t - m.t0) / sec(M.attention);
    m.onde.material.opacity = !calme.matches && k >= 0 && k < 1 ? 0.7 * (1 - k) * (1 - k) : 0;
    m.onde.scale.setScalar(m.s.scale.x * (1 + k * 2.6));
  });
  renderer.render(scene3, camera);
  placerEtiquettes(W, H);
}

/* Étiquettes HTML posées sur le globe (noms lisibles, police du site) */
let lots = [];
function poserEtiquettes(liste) {
  etiquettes.innerHTML = liste.map((l, i) => '<div class="etq etq--' + l.type + '" data-i="' + i + '"' + (l.couleur ? ' style="--c:' + l.couleur + '"' : '') + '><b>' + esc(l.nom) + '</b>' + (l.sous ? '<span>' + esc(l.sous) + '</span>' : '') + '</div>').join('');
  lots = liste.map((l, i) => ({ ...l, el: etiquettes.children[i] }));
}
const vtmp = new THREE.Vector3();
function placerEtiquettes(W, H) {
  // Téléphone, fiche : les étiquettes sont cachées (le trajet se lit sous le globe) ; rien à placer.
  if (!etiquettes.offsetWidth) { lots.forEach((l) => { l.el.style.opacity = 0; }); return; }
  const places = [];
  lots.forEach((l) => {
    vtmp.copy(l.v).applyEuler(globe.rotation);
    const derriere = vtmp.z < 0 && Math.hypot(vtmp.x, vtmp.y) < 1.02, face = l.v.length() > 1.1 ? !derriere : vtmp.z > 0.3;
    vtmp.project(camera);
    let x = (vtmp.x + 1) / 2 * W, y = (1 - vtmp.y) / 2 * H;
    if (!face || l.montre === false) { l.el.style.opacity = 0; return; }
    const w = l.el.offsetWidth, h = l.el.offsetHeight;
    // Deux places possibles (à droite du point, puis à gauche), poussées vers le bas en cas de chevauchement ;
    // on garde la première qui tient dans la zone, sinon on borne la position.
    const Z = zone, libre = (ax, ay) => !places.some((q) => ax < q.x + q.w + 6 && ax + w + 6 > q.x && ay < q.y + q.h + 2 && ay + h + 2 > q.y);
    let px = null, py = null;
    for (const cx of [x + 12, x - w - 12]) {
      const bx = Math.max(Z.x0, Math.min(Z.x1 - w, cx));
      let by = Math.max(Z.y0, Math.min(Z.y1 - h, y - h / 2));
      for (let n = 0; n < 14 && !libre(bx, by); n++) { const c = places.find((q) => bx < q.x + q.w + 6 && bx + w + 6 > q.x && by < q.y + q.h + 2 && by + h + 2 > q.y); by = c.y + c.h + 3; }
      if (by + h <= Z.y1 && libre(bx, by)) { px = bx; py = by; break; }
    }
    if (px === null) {
      // Plus de place sous le point : on remonte au-dessus des étiquettes déjà posées.
      const bx = Math.max(Z.x0, Math.min(Z.x1 - w, x + 12)); let by = Math.max(Z.y0, Math.min(Z.y1 - h, y - h / 2));
      for (let n = 0; n < 14 && !libre(bx, by); n++) { const c = places.find((q) => bx < q.x + q.w + 6 && bx + w + 6 > q.x && by < q.y + q.h + 2 && by + h + 2 > q.y); by = c.y - h - 3; }
      px = bx; py = Math.max(Z.y0, by);
    }
    const tient = px >= Z.x0 - 0.5 && px + w <= Z.x1 + 0.5 && py >= Z.y0 - 0.5 && py + h <= Z.y1 + 0.5 && libre(px, py);
    l.el.style.transform = 'translate(' + Math.round(px) + 'px,' + Math.round(py) + 'px)';
    l.el.style.opacity = tient ? (l.attenue ? 0.38 : 1) : 0;
    if (tient) places.push({ x: px, y: py, w, h });
  });
}

/* ---------- Interface ---------- */
const parId = {}; D.photos.forEach((p) => { parId[p.id] = p; });
const nbPays = D.pays.length;
let repere = null, posIndex = 0, posPour = null;

function signe(t) { return '<i class="sg sg--' + t + '" aria-hidden="true"></i>'; }
function destinations(p) {
  const l = []; p.usages.forEach((u) => { const n = pays(u) || 'en ligne'; if (!l.includes(n)) l.push(n); }); return l.join(', ');
}
function indexHTML() {
  return '<div class="colonne"><header class="tete">' +
    '<h1 tabindex="-1"><span class="ligne">Mes photos</span> <span class="ligne">utilisées</span> <span class="ligne">dans le monde</span></h1>' +
    '<p class="chapo">' + D.photos.length + ' photographies publiées sur Pexels ont été reprises ' + D.total + ' fois, par ' + D.repertoire.length + ' médias, guides et entreprises. Chaque arc part du lieu de la prise de vue et va jusqu’au média qui a choisi l’image.</p>' +
    '<ul class="legende" aria-label="Les signes du globe">' +
    '<li>' + signe('anneau') + 'Lieu de la prise de vue</li><li>' + signe('plein') + 'Média, dans son pays (' + nbPays + ' pays)</li>' +
    '<li>' + signe('couronne') + 'Couronne : site en ligne dont le lieu n’est pas établi (' + D.en_ligne + ')</li><li>' + signe('carre') + 'Lieu dont parle l’article, s’il est ailleurs</li></ul>' +
    '<p class="source">Retrouvées par recherche d’images · parutions vérifiées au ' + esc(D.date) + '. Faites tourner le globe du doigt ou de la souris.</p></header>' +
    '<h2 class="liste-titre">Les ' + D.photos.length + ' photos</h2><ol class="liste">' + D.photos.map((p) =>
      '<li><a class="vue" href="#monde/photo-' + p.id + '" data-cle="' + p.id + '"><img src="' + p.vignette + '" alt="" loading="lazy">' +
      '<span class="vue-texte"><span class="vue-nom">' + esc(p.libelle) + '</span><span class="vue-trajet">' + esc(p.origine.inconnu ? 'Lieu de prise non indiqué' : p.origine.nom) + ' → ' + esc(destinations(p)) + '</span></span>' +
      '<span class="vue-compte" aria-label="' + pluriel(p.usages.length, 'parution') + '">' + p.usages.map((u, k) => '<i style="background:' + p.palette[k % 4].c + '"></i>').join('') + '</span></a></li>').join('') + '</ol></div>';
}
function phraseTrajet(p) {
  const n = p.usages.length, lieux = destinations(p).replace('en ligne', 'un site dont le lieu n’est pas établi');
  return (p.origine.inconnu ? 'Le lieu de la prise de vue n’est pas indiqué.' : 'Prise de vue : ' + esc(p.origine.nom) + '.') + ' ' +
    (n > 1 ? 'Reprise ' + n + ' fois' : 'Reprise une fois') + ' : ' + esc(lieux) + '.';
}
function noticeHTML(u) {
  return '<article class="notice" id="' + u.id + '" data-usage="' + u.id + '">' +
    '<p class="notice-lieu">' + signe(u.lieu ? 'plein' : 'couronne') + esc(lieuMedia(u)) + '</p>' +
    '<h2 class="notice-nom">' + esc(u.nom) + '</h2><p class="notice-support">' + esc(u.support) + '</p>' +
    '<p class="notice-texte">' + esc(u.texte) + '</p>' +
    (u.titre ? '<p class="notice-titre"><span lang="' + u.langue + '">« ' + esc(u.titre) + ' »</span>' + (u.date ? ' <span class="date">· ' + esc(u.date) + '</span>' : '') + '</p>' : '') +
    (u.raconte ? '<p class="notice-raconte">' + signe('carre') + 'Raconte : ' + esc(u.raconte.nom) + '</p>' : '') +
    lienNotice(u) + '</article>';
}
function ficheHTML(p) {
  const n = D.photos.length, i = D.photos.indexOf(p), prec = D.photos[(i - 1 + n) % n], suiv = D.photos[(i + 1) % n];
  return '<article class="panneau affiche" data-cle="' + p.id + '" style="' + couleurs(p) + '">' +
    '<nav class="retour" aria-label="Rubrique"><a href="#monde" class="pilule pilule--douce">← Toutes les photos</a><span class="pas"><a class="pas-lien" href="#monde/photo-' + prec.id + '" aria-label="Photo précédente : ' + esc(prec.libelle) + '">←</a><span>Photo ' + (i + 1) + ' sur ' + n + '</span><a class="pas-lien" href="#monde/photo-' + suiv.id + '" aria-label="Photo suivante : ' + esc(suiv.libelle) + '">→</a></span></nav>' +
    '<header class="affiche-tete">' + eclatSVG(p.palette, graineDe(p.id), { reserve: [0.8, 0.22, 0.8] }) + titreAffiche(p) + compteur(p) + '</header>' +
    '<div class="affiche-corps"><figure class="photo"><img src="' + p.grande + '" alt="' + esc(p.libelle) + '" style="aspect-ratio:' + p.ratio + '">' +
    '<figcaption><span class="photo-nom">' + esc(p.libelle) + '</span><span class="credit">' + credit(p) + '</span><span class="trajet">' + phraseTrajet(p) + '</span></figcaption></figure>' +
    '<section class="regards" aria-label="' + regardsTitre(p) + '"><h2 class="regards-titre">' + regardsTitre(p) + '<small>Retrouvées par recherche d’images</small></h2>' +
    p.usages.map((u, k) => regardHTML(u, k, signe)).join('') + '</section></div>' +
    '<nav class="suite" aria-label="Autres photos"><a rel="prev" href="#monde/photo-' + prec.id + '"><small>← Photo précédente</small>' + esc(prec.libelle) + '</a>' +
    '<a rel="next" href="#monde/photo-' + suiv.id + '"><small>Photo suivante →</small>' + esc(suiv.libelle) + '</a></nav></article>';
}

const etroit = matchMedia('(max-width:899px)');
function etiquettesIndex() {
  const l = [];
  const parGroupe = {};
  usages.forEach((x) => { (parGroupe[x.groupe] = parGroupe[x.groupe] || []).push(x); });
  const pos = { France: vec(46.6, 2.4), Espagne: vec(40.2, -3.7), Lituanie: vec(55.2, 23.9), 'États-Unis': vec(32.78, -96.8), 'Brésil': vec(-14.2, -51.9) };
  Object.keys(pos).forEach((g) => { if (parGroupe[g]) l.push({ type: 'pays', nom: g, sous: pluriel(parGroupe[g].length, 'parution'), v: pos[g] }); });
  if (parGroupe['En ligne']) l.push({ type: 'couronne', nom: 'En ligne', sous: pluriel(parGroupe['En ligne'].length, 'parution') + ', lieu non établi', v: couronne(90, ORBITE + 0.02) });
  usages.filter((x) => x.c).forEach((x) => l.push({ type: 'raconte', nom: x.u.raconte.nom, sous: 'raconté par ' + x.u.nom, v: x.c }));
  return l;
}
function etiquettesFiche(p) {
  const l = [{ type: 'origine', nom: p.origine.inconnu ? 'Prise en France' : p.origine.nom, sous: p.origine.inconnu ? 'lieu non indiqué' : 'prise de vue', v: vec(p.origine.lat, p.origine.lon) }];
  if (etroit.matches) {
    // Téléphone : le globe dit où l'on est (lieu de prise, puis pays d'arrivée, une fois chacun) ; les médias se lisent dans la fiche.
    const vus = [];
    usages.filter((x) => x.p === p).forEach((x) => {
      const nom = x.sat ? 'En ligne' : (pays(x.u) || x.u.lieu.nom);
      if (vus.includes(nom)) return; vus.push(nom);
      l.push({ type: x.sat ? 'couronne' : 'pays', nom, sous: '', v: x.b, couleur: p.palette[p.usages.indexOf(x.u) % 4].c });
    });
    return l;
  }
  usages.filter((x) => x.p === p).forEach((x) => {
    l.push({ type: x.sat ? 'couronne' : 'media', nom: x.u.nom, sous: x.sat ? 'en ligne · lieu non établi' : x.u.lieu.nom, v: x.b, usage: x.u.id, couleur: p.palette[p.usages.indexOf(x.u) % 4].c });
    if (x.c) l.push({ type: 'raconte', nom: x.u.raconte.nom, sous: 'lieu raconté', v: x.c, usage: x.u.id });
  });
  return l;
}

function montrerArcs(filtre, cascade) {
  // Cascade par groupe de destination (6 groupes au plus) : pas de 80 ms, total ≤ 600 ms (référentiel, § 5).
  arcs.forEach((a) => {
    const on = filtre(a.x);
    if (!on) { a.cible = 0; a.prog = 0; return; }
    if (!cascade || calme.matches) { a.cible = 1; if (calme.matches) a.prog = 1; return; }
    a.cible = 0; a.prog = 0;
    const g = GROUPES.indexOf(a.x.groupe);
    setTimeout(() => { a.cible = 1; }, cascade.delai + Math.max(0, g) * 80);
  });
}

let ctxG, sequenceEnCours = null;
const vue = {
  preparer(ctx) { ctxG = ctx; construire3D(); if (ok3d && !boucle) { horloge.update(); tour(); } },
  afficher(r, ctx, o) {
    const scene = ctx.scene, monde = ctx.monde, p = r.photo && parId[r.photo];
    if (!boucle && ok3d) { horloge.update(); tour(); }
    surbrillance = null;
    if (p) {
      if (scene.dataset.vue === 'index') posIndex = monde.scrollTop;
      vueCourante = 'fiche'; scene.dataset.vue = 'fiche'; scene.innerHTML = ficheHTML(p); repere = p.id;
      monde.scrollTop = 0; $('h1', scene).focus({ preventScroll: true });
      if (ok3d) {
        cadrer(); ambiance = false;
        orienter([p.usages.length ? vec(p.origine.lat, p.origine.lon) : FRANCE].concat(usages.filter((x) => x.p === p).map((x) => x.c || x.b)));
        poserEtiquettes(etiquettesFiche(p));
        arcs.forEach((a) => { a.mesh.material.color.set(a.x.p === p ? p.palette[p.usages.indexOf(a.x.u) % 4].c : '#ffffff'); });
        montrerArcs((x) => x.p === p, { delai: o.premier ? 120 : 200 });
        if (o.premier) { cur.cx = vise.cx; cur.cy = vise.cy; cur.rpx = vise.rpx * 1.4; }
      }
      if (!calme.matches) {
        // L'affiche glisse depuis la droite (450 ms, « aller ») ; l'éclat arrive du côté du globe ; puis le titre.
        animate($('.panneau', scene), { transform: ['translateX(64px)', 'translateX(0)'], opacity: [0, 1] }, { duration: sec(M.deplacement), ease: M.aller });
        jouerEclat($('.affiche-tete', scene), 'gauche');
        animate($$('.titre-affiche .initiale, .titre-affiche .reste, .titre-affiche .sous, .compteur', scene), { opacity: [0, 1], transform: ['translateY(24px)', 'translateY(0)'] }, { duration: sec(M.entree), ease: M.sortie, delay: stagger(sec(M.pas), { startDelay: 0.32 }) });
      }
      ctx.annoncer(p.libelle + ', ' + pluriel(p.usages.length, 'parution'));
      son('grave');
      return;
    }
    zoom = 1;
    vueCourante = 'index'; scene.dataset.vue = 'index'; scene.innerHTML = indexHTML();
    if (ok3d) {
      cadrer(); ambiance = true; vise.lat = 38; vise.lon = 2.4;
      poserEtiquettes(etiquettesIndex());
      arcs.forEach((a) => { a.mesh.material.color.set('#ffffff'); });
      montrerArcs(() => true, o.premier ? null : { delai: 0 });
      if (o.premier) { cur.cx = vise.cx; cur.cy = vise.cy; cur.rpx = vise.rpx; cur.lat = vise.lat; cur.lon = vise.lon; }
    }
    const cible = repere && scene.querySelector('[data-cle="' + repere + '"]');
    if (cible) { if (posPour === repere) monde.scrollTop = posIndex; else cible.scrollIntoView({ block: 'center' }); cible.focus({ preventScroll: true }); }
    else { monde.scrollTop = 0; $('h1', scene).focus({ preventScroll: true }); }
  },
  ouverture(ctx) {
    // Ouverture : la photographie du bouton se referme en un point sur Villandry, là où elle a été prise ;
    // de là partent les arcs vers les médias. Le globe arrive de près, en 0,5 s d'amortissement (τ du référentiel).
    if (!ok3d) return null;
    const scene = ctx.scene;
    let voile = $('#iris');
    if (!voile) { voile = document.createElement('div'); voile.id = 'iris'; voile.setAttribute('aria-hidden', 'true'); ctx.monde.insertBefore(voile, $('.barre')); }
    voile.hidden = false; ctx.voile.hidden = true;
    const villandry = vec(47.34, 0.514), W = () => decor.clientWidth, H = () => decor.clientHeight;
    cur.rpx = vise.rpx * 3.4; cur.lat = 47; cur.lon = -24; cur.cx = vise.cx; cur.cy = vise.cy;
    arcs.forEach((a) => { a.cible = 0; a.prog = 0; });
    Object.values(marques).forEach((m) => { m.allume = 0; });
    const textes = $$('.tete .ligne, .tete .chapo, .tete .legende, .tete .source, .liste-titre, .liste', scene);
    textes.forEach((e) => { e.style.opacity = '0'; });
    let t0 = performance.now(), fini = false, raf = 0, resoudre;
    const DUREE = 800;
    const pas = () => {
      const k = Math.min(1, (performance.now() - t0) / DUREE), e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2; // proche de « aller »
      const v = villandry.clone().applyEuler(globe.rotation).project(camera);
      const x = (v.x + 1) / 2 * W(), y = (1 - v.y) / 2 * H(), rmax = Math.hypot(innerWidth, innerHeight);
      voile.style.clipPath = 'circle(' + (rmax * (1 - e) + 5 * e).toFixed(1) + 'px at ' + x.toFixed(1) + 'px ' + y.toFixed(1) + 'px)';
      if (k < 1) raf = requestAnimationFrame(pas);
      else { voile.hidden = true; voile.style.clipPath = ''; son('ping'); }
    };
    raf = requestAnimationFrame(pas);
    const minuteurs = [
      setTimeout(() => montrerArcs(() => true, { delai: 0 }), 620),
      setTimeout(() => {
        animate(textes, { opacity: [0, 1], transform: ['translateY(24px)', 'translateY(0)'] }, { duration: sec(M.entree), ease: M.sortie, delay: stagger(sec(M.pas)) });
      }, 900),
      setTimeout(() => { fini = true; resoudre(); }, 2200),
    ];
    return {
      fin: new Promise((r) => { resoudre = r; }),
      couper() {
        if (fini) return; fini = true; cancelAnimationFrame(raf); minuteurs.forEach(clearTimeout);
        voile.hidden = true; voile.style.clipPath = '';
        textes.forEach((e) => { e.getAnimations().forEach((a) => a.cancel()); e.style.opacity = ''; e.style.transform = ''; });
        arcs.forEach((a) => { a.cible = 1; a.prog = 1; });
        cur.rpx = vise.rpx; cur.lat = vise.lat; cur.lon = vise.lon; resoudre();
      },
    };
  },
  fermer() { cancelAnimationFrame(boucle); boucle = 0; repere = null; posPour = null; posIndex = 0; },
  touche(e, ctx) {
    if (ctx.scene.dataset.vue !== 'fiche') return;
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      const a = ctx.scene.querySelector(e.key === 'ArrowLeft' ? 'a[rel=prev]' : 'a[rel=next]');
      if (a) { e.preventDefault(); location.hash = a.getAttribute('href'); }
    }
  },
};

const ctx = demarrer(vue);

// Survol ou focus : l'index allume les arcs de la photo ; la fiche, l'arc de la parution.
const scene = $('#scene');
function eclairer(e) {
  const v = e.target.closest && e.target.closest('.vue[data-cle], .notice[data-usage]');
  if (!v) { if (e.type === 'mouseout' || e.type === 'focusout') { surbrillance = null; lots.forEach((l) => { l.attenue = false; }); } return; }
  if (v.dataset.cle && scene.dataset.vue === 'index') {
    const p = parId[v.dataset.cle];
    if (e.type === 'mouseover' || e.type === 'focusin') { surbrillance = (x) => x.p === p; }
  }
  if (v.dataset.usage) {
    const id = v.dataset.usage;
    if (e.type === 'mouseover' || e.type === 'focusin') { surbrillance = (x) => x.u.id === id; lots.forEach((l) => { l.attenue = l.usage && l.usage !== id; }); }
  }
}
['mouseover', 'focusin', 'mouseout', 'focusout'].forEach((t) => scene.addEventListener(t, eclairer));
scene.addEventListener('click', (e) => {
  const l = e.target.closest('a.vue[data-cle]');
  if (l && scene.dataset.vue === 'index') { posIndex = ctx.monde.scrollTop; posPour = l.dataset.cle; }
});
