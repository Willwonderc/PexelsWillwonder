// Pièces de l'affiche communes aux deux versions : titre « <lieu>, une photographie qui voyage », regards, couleurs.
import { esc, lieuMedia, lienNotice } from './coquille.js';

const NOMBRES = ['zéro', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept', 'huit', 'neuf', 'dix'];
export const nombre = (n) => NOMBRES[n] || String(n);
export const deux = (n) => String(n).padStart(2, '0');

// Variables de couleur d'une photo : --p0..--p3 (couleurs), --s0..--s3 (texte lisible posé dessus)
export function couleurs(p) {
  return p.palette.map((x, i) => '--p' + i + ':' + x.c + ';--s' + i + ':' + x.sur).join(';');
}
export function titreAffiche(p, balise = 'h1') {
  const t = p.titre, init = t.charAt(0), reste = t.slice(1);
  const texte = t + ', une photographie qui voyage';
  return '<' + balise + ' class="titre-affiche" tabindex="-1" aria-label="' + esc(texte) + '"><span aria-hidden="true">' +
    '<span class="initiale">' + esc(init) + '</span><span class="reste">' + esc(reste) + ',</span>' +
    '<span class="sous">une photographie<br>qui voyage</span></span></' + balise + '>';
}
export function compteur(p) {
  const n = p.usages.length;
  return '<p class="compteur"><b>' + deux(n) + '</b><span>' + (n > 1 ? 'publications' : 'publication') + '</span><small>une photographie</small></p>';
}
export function regardsTitre(p) {
  const n = p.usages.length;
  return 'Une image, ' + nombre(n) + ' regard' + (n > 1 ? 's' : '');
}
export function regardHTML(u, k, signe) {
  const c = 'var(--p' + (k % 4) + ')', s = 'var(--s' + (k % 4) + ')';
  return '<article class="notice regard" id="' + u.id + '" data-usage="' + u.id + '" style="--c:' + c + ';--s:' + s + '">' +
    '<p class="regard-tete"><span class="regard-num">' + deux(k + 1) + '</span> / ' + esc(u.support) + '</p>' +
    '<h3 class="notice-nom">' + esc(u.nom) + '</h3>' +
    '<p class="notice-lieu">' + signe(u.lieu ? 'plein' : 'couronne') + esc(lieuMedia(u)) + '</p>' +
    '<p class="notice-texte">' + esc(u.texte) + '</p>' +
    (u.titre ? '<p class="notice-titre"><span lang="' + u.langue + '">« ' + esc(u.titre) + ' »</span>' + (u.date ? ' <span class="date">· ' + esc(u.date) + '</span>' : '') + '</p>' : '') +
    (u.raconte ? '<p class="notice-raconte">' + signe('carre') + 'Raconte : ' + esc(u.raconte.nom) + '</p>' : '') +
    lienNotice(u) + '</article>';
}
