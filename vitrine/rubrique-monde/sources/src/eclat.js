// L'éclat : un langage de formes propre à la rubrique (triangles d'une trame régulière), inventé pour elle.
// Ses couleurs sont la palette tirée de chaque photo. Une graine par photo : chaque éclat est unique et stable.
import { animate, stagger } from 'motion';
import { M, calme } from './coquille.js';

function alea(graine) { let s = graine >>> 0 || 1; return () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return ((s >>> 0) % 100000) / 100000; }; }
export function graineDe(id) { let h = 2166136261; for (const c of String(id)) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h; }

// Trame de triangles équilatéraux ; un cœur dense (où se pose le titre), une traîne qui s'éparpille vers la droite.
export function eclatSVG(palette, graine, o = {}) {
  const W = o.largeur || 1000, H = o.hauteur || 460, cote = o.cote || 54, r = alea(graine);
  const h = cote * Math.sqrt(3) / 2, tris = [];
  const cx = W * (o.cx || 0.36), cy = H * 0.5, rx = W * (o.rx || 0.36), ry = H * 0.46;
  for (let j = -1; j < H / h + 1; j++) {
    for (let i = -2; i < W / (cote / 2) + 2; i++) {
      const x0 = i * cote / 2 + (j % 2 ? cote / 2 : 0), y0 = j * h, haut = (i + j) % 2 === 0;
      const p = haut ? [[x0, y0 + h], [x0 + cote / 2, y0], [x0 + cote, y0 + h]] : [[x0, y0], [x0 + cote, y0], [x0 + cote / 2, y0 + h]];
      const gx = (p[0][0] + p[1][0] + p[2][0]) / 3, gy = (p[0][1] + p[1][1] + p[2][1]) / 3;
      const d = Math.hypot((gx - cx) / rx, (gy - cy) / ry) + (r() - 0.5) * 0.22;
      let garde = d < 1, echelle = 1;
      if (!garde && gx > cx && d < 2.4) { garde = r() < Math.pow(1 - (d - 1) / 1.4, 1.6) * 0.75; echelle = 0.45 + 0.5 * (1 - (d - 1) / 1.4) * r() + 0.1; }
      if (!garde && gx < cx && d < 1.25) garde = r() < 0.35;
      if (garde && o.reserve && gx > W * o.reserve[0] && gy > H * o.reserve[1] && gy < H * o.reserve[2]) garde = false;
      if (!garde) continue;
      const k = r();
      let ci = d < 0.78 ? (k < 0.74 ? 0 : k < 0.84 ? 2 : k < 0.93 ? 1 : 3) : (k < 0.36 ? 0 : k < 0.58 ? 1 : k < 0.8 ? 2 : 3);
      const op = d < 0.78 ? 0.86 + 0.14 * r() : 0.55 + 0.45 * r();
      const pts = echelle === 1 ? p : p.map(([x, y]) => [gx + (x - gx) * echelle, gy + (y - gy) * echelle]);
      tris.push({ pts, c: palette[ci % palette.length].c, op, gx, gy, d });
    }
  }
  const poly = tris.map((t) => '<polygon class="tri" points="' + t.pts.map((q) => q[0].toFixed(1) + ',' + q[1].toFixed(1)).join(' ') + '" fill="' + t.c + '" fill-opacity="' + t.op.toFixed(2) + '" data-x="' + (t.gx / W).toFixed(3) + '"/>').join('');
  return '<svg class="eclat" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="xMinYMid meet" aria-hidden="true" focusable="false">' + poly + '</svg>';
}

// Entrée de l'éclat : les triangles arrivent du côté du globe, par six groupes selon leur abscisse
// (pas de 80 ms, 520 ms chacun, courbe « sortie » ; référentiel § 2 et § 5).
export function jouerEclat(racine, depuis = 'gauche') {
  const tris = Array.from(racine.querySelectorAll('.tri'));
  if (calme.matches || !tris.length) return;
  const groupes = [[], [], [], [], [], []];
  tris.forEach((t) => { const x = parseFloat(t.dataset.x); groupes[Math.min(5, Math.max(0, Math.floor((depuis === 'gauche' ? x : 1 - x) * 6)))].push(t); });
  groupes.forEach((g, i) => {
    if (!g.length) return;
    animate(g, { opacity: [0, 1], transform: [depuis === 'gauche' ? 'translateX(-180px) scale(.3)' : 'translateX(180px) scale(.3)', 'translateX(0) scale(1)'] },
      { duration: 0.52, ease: M.sortie, delay: i * 0.08 });
  });
}
