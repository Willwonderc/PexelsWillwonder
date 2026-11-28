/* Amorce de la rubrique « Mes photos utilisées dans le monde » (à charger avec la page /galeries/, en defer).
   Rien de lourd n'est chargé avec la page : au survol ou au focus du bouton, on précharge ; au premier clic, on charge
   la feuille de style, les données et le script, puis on rejoue le clic. Un lien direct #monde… charge tout de suite.
   Échap pendant le chargement annule l'ouverture. Base des fichiers : attribut data-base du <script>. */
(function () {
  'use strict';
  var moi = document.currentScript, base = (moi && moi.dataset.base) || '/statique/rubrique-monde/';
  var etat = 0, annule = false, suites = [];
  function fichier(nom, type, fin) {
    var el = document.createElement(type === 'css' ? 'link' : 'script');
    if (type === 'css') { el.rel = 'stylesheet'; el.href = base + nom; } else { el.src = base + nom; }
    el.onload = fin; el.onerror = function () { etat = 0; var b = document.getElementById('entree'); if (b) b.removeAttribute('aria-busy'); };
    document.head.appendChild(el);
  }
  function charger(fin) {
    if (etat === 2) { if (fin) fin(); return; }
    if (fin) suites.push(fin);
    if (etat === 1) return;
    etat = 1;
    fichier('rubrique-monde.css', 'css', function () {
      fichier('rubrique-monde-donnees.js', 'js', function () {
        fichier('rubrique-monde.js', 'js', function () { etat = 2; var s = suites; suites = []; s.forEach(function (f) { f(); }); });
      });
    });
  }
  var bouton = document.getElementById('entree');
  if (!bouton) return;
  bouton.addEventListener('click', function (e) {
    if (etat === 2) return;
    e.preventDefault(); e.stopImmediatePropagation(); annule = false;
    bouton.setAttribute('aria-busy', 'true');
    charger(function () { bouton.removeAttribute('aria-busy'); if (!annule) bouton.click(); });
  }, true);
  ['pointerenter', 'focus', 'touchstart'].forEach(function (t) { bouton.addEventListener(t, function () { charger(); }, { passive: true, once: true }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && etat === 1) annule = true; });
  if (/^#monde(\/|$)/.test(location.hash)) charger();
})();
