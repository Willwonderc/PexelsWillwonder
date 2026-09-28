/* Tableau de bord : survol des graphiques et liste des photos (recherche, filtres, tri).
   JavaScript léger, sans bibliothèque. Sans lui, la page montre tout : chaque graphique a
   son tableau de chiffres, et la liste des photos est triée par vues. */
(function () {
  "use strict";

  /* ---------- Graphiques : la mesure la plus proche du pointeur, ou au clavier ---------- */

  document.querySelectorAll(".tb-graphe[data-points]").forEach(function (figure) {
    var points = JSON.parse(figure.getAttribute("data-points"));
    var svg = figure.querySelector("svg");
    var bulle = figure.querySelector(".tb-bulle");
    var reticule = figure.querySelector(".tb-reticule");
    var colonnes = figure.querySelectorAll(".tb-colonne");
    var largeur = svg.viewBox.baseVal.width;
    var courant = -1;

    var montrer = function (i) {
      var p = points[i], boite = svg.getBoundingClientRect(), cadre = figure.getBoundingClientRect();
      var echelle = boite.width / largeur;
      courant = i;
      bulle.querySelector("strong").textContent = p[3];
      bulle.querySelector("span").textContent = p[2];
      bulle.hidden = false;
      var demi = bulle.offsetWidth / 2;
      var x = Math.max(demi, Math.min(cadre.width - demi, boite.left - cadre.left + p[0] * echelle));
      bulle.style.left = x + "px";
      bulle.style.top = (boite.top - cadre.top + p[1] * echelle) + "px";
      if (reticule) {
        reticule.setAttribute("x1", p[0]);
        reticule.setAttribute("x2", p[0]);
        figure.classList.add("survol");
      }
      colonnes.forEach(function (colonne, j) { colonne.classList.toggle("actif", j === i); });
    };

    var cacher = function () {
      courant = -1;
      bulle.hidden = true;
      figure.classList.remove("survol");
      colonnes.forEach(function (colonne) { colonne.classList.remove("actif"); });
    };

    var proche = function (x) {
      var meilleur = 0;
      points.forEach(function (p, i) {
        if (Math.abs(p[0] - x) < Math.abs(points[meilleur][0] - x)) meilleur = i;
      });
      return meilleur;
    };

    svg.addEventListener("pointermove", function (ev) {
      var boite = svg.getBoundingClientRect();
      montrer(proche((ev.clientX - boite.left) * largeur / boite.width));
    });
    svg.addEventListener("pointerleave", cacher);
    figure.addEventListener("focus", function () { montrer(points.length - 1); });
    figure.addEventListener("blur", cacher);
    figure.addEventListener("keydown", function (ev) {
      if (ev.key === "ArrowLeft" || ev.key === "ArrowRight") {
        ev.preventDefault();
        var i = courant < 0 ? points.length - 1 : courant + (ev.key === "ArrowRight" ? 1 : -1);
        montrer(Math.max(0, Math.min(points.length - 1, i)));
      } else if (ev.key === "Escape") {
        cacher();
      }
    });
  });

  /* ---------- Toutes les photos : recherche, filtres et tri, comme dans Telepex ---------- */

  var formulaire = document.querySelector(".tb-filtres");
  var corps = document.querySelector(".tb-photos tbody");
  if (!formulaire || !corps) return;

  var lignes = Array.prototype.slice.call(corps.rows);
  var champs = formulaire.elements;
  var plier = function (texte) {
    return texte.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  };
  var nombre = function (ligne, attribut) { return Number(ligne.getAttribute(attribut)); };

  var appliquer = function () {
    var mots = plier(champs.texte.value).split(/\s+/).filter(Boolean);
    var filtre = champs.filtre.value;
    var tri = champs.tri.value;
    // « -d » : dates d'import croissantes ; les autres tris vont du plus grand au plus petit.
    var sens = tri.charAt(0) === "-" ? 1 : -1;
    var attribut = "data-" + tri.replace("-", "");
    var triees = lignes.slice().sort(function (a, b) {
      return sens * (nombre(a, attribut) - nombre(b, attribut)) || nombre(b, "data-v") - nombre(a, "data-v");
    });
    var visibles = 0;
    var suite = document.createDocumentFragment();
    triees.forEach(function (ligne) {
      var texte = ligne.getAttribute("data-s");
      var montree = (!filtre || ligne.classList.contains(filtre)) &&
        mots.every(function (mot) { return texte.indexOf(mot) >= 0; });
      ligne.hidden = !montree;
      if (montree) visibles++;
      suite.appendChild(ligne);
    });
    corps.appendChild(suite);
    champs.namedItem("compte").value = visibles.toLocaleString("fr-FR") + (visibles > 1 ? " photos" : " photo");
  };

  var attente;
  formulaire.addEventListener("input", function () {
    clearTimeout(attente);
    attente = setTimeout(appliquer, 120);
  });
  formulaire.addEventListener("submit", function (ev) { ev.preventDefault(); });
  formulaire.hidden = false;
})();
