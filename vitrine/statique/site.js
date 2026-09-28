/* Site de Karl Forterre : fondu de l'accueil, photos utilisées dans des projets et
   visionneuse plein écran. JavaScript léger, sans bibliothèque. Sans lui, le site
   fonctionne tout autant : chaque vignette mène à la page de sa photo. */
(function () {
  "use strict";

  var calme = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Accueil : fondu lent entre les photos de l'ouverture ---------- */

  var defile = document.querySelector(".defile");
  if (defile && !calme && "content" in document.createElement("template")) {
    var modeles = defile.querySelectorAll("template");
    var diapos = [defile.querySelector(".diapo")];
    var total = modeles.length + 1, actuelle = 0, montree = diapos[0], DUREE = 7000;

    var preparer = function (i) {
      if (!diapos[i]) {
        var contenu = document.importNode(modeles[i - 1].content, true);
        diapos[i] = contenu.firstElementChild;
        defile.appendChild(diapos[i]);
      }
      return diapos[i];
    };

    var avancer = function () {
      if (document.hidden) { setTimeout(avancer, DUREE); return; }
      var i = (actuelle + 1) % total, diapo = preparer(i), img = diapo.querySelector("img"), fait = false;
      var suite = function (reussie) {
        if (fait) return;
        fait = true;
        actuelle = i;
        if (reussie) {
          montree.classList.remove("visible");
          diapo.classList.add("visible");
          montree = diapo;
        }
        if (total > 2) preparer((i + 1) % total);
        setTimeout(avancer, DUREE);
      };
      if (img.complete) { suite(img.naturalWidth > 0); return; }
      img.addEventListener("load", function () { suite(true); });
      img.addEventListener("error", function () { suite(false); });
    };

    if (total > 1) {
      preparer(1);
      setTimeout(avancer, DUREE);
    }
  }

  /* ---------- Galeries : index des photos utilisées dans des projets ----------
     Les noms entrent l'un après l'autre quand l'index arrive à l'écran. Les grandes
     photos du survol se chargent au premier passage de la souris ou du clavier ; sur
     ordinateur, aussi d'avance, une fois la page chargée, pour que le premier survol soit
     immédiat. Chacune ne se montre qu'une fois chargée. */

  var index = document.querySelector(".index-usages");
  if (index && !calme && "IntersectionObserver" in window) {
    index.classList.add("index-anime");
    var arrivee = new IntersectionObserver(function (entrees) {
      if (!entrees[0].isIntersecting) return;
      index.classList.add("vu");
      arrivee.disconnect();
    }, { threshold: 0.12 });
    arrivee.observe(index);
  }
  if (index && "content" in document.createElement("template")) {
    var chargerFonds = function () {
      index.removeEventListener("pointerenter", auPointeur);
      index.removeEventListener("focusin", chargerFonds);
      Array.prototype.forEach.call(index.querySelectorAll(".index-fond"), function (fond) {
        var modele = fond.querySelector("template");
        if (!modele) return;
        var img = document.importNode(modele.content, true).firstElementChild;
        var pret = function () { fond.classList.add("pret"); };
        img.addEventListener("load", pret);
        fond.replaceChild(img, modele);
        if (img.complete && img.naturalWidth) pret();
      });
    };
    var auPointeur = function (ev) {
      if (ev.pointerType !== "touch") chargerFonds();
    };
    index.addEventListener("pointerenter", auPointeur);
    index.addEventListener("focusin", chargerFonds);
    var ordinateur = window.matchMedia && window.matchMedia("(hover: hover) and (min-width: 641px)").matches;
    var economie = navigator.connection && navigator.connection.saveData;
    if (ordinateur && !economie) {
      window.addEventListener("load", function () {
        (window.requestIdleCallback || function (f) { setTimeout(f, 1500); })(chargerFonds);
      });
    }
  }

  /* Une bande par photo : quand plusieurs sites ou campagnes ont utilisé la même photo,
     leurs noms (et le mois du signalement, s'il diffère) y défilent comme au générique.
     Les bandes défilent chacune à son tour ; tout s'arrête quand l'index sort de l'écran
     ou que la page est cachée. Sans script, ou si l'appareil demande moins d'animations,
     les noms restent l'un sous l'autre. */

  var bandes = [];
  if (index && !calme && "IntersectionObserver" in window) {
    Array.prototype.forEach.call(index.querySelectorAll(".index-ligne"), function (ligne) {
      var noms = ligne.querySelectorAll(".index-nom > span");
      var mois = ligne.querySelectorAll(".index-quand > span");
      if (noms.length > 1) bandes.push({ suites: mois.length > 1 ? [noms, mois] : [noms], rang: 0 });
    });
  }
  if (bandes.length) {
    var RELAIS = 6000, PREMIER = 4500, tour = 0, minuterie = null, enVue = false;
    bandes.forEach(function (b) {
      b.montres = b.suites.map(function (suite) {
        suite[0].parentNode.classList.add("index-relais");
        suite[0].classList.add("actif");
        return suite[0];
      });
    });
    /* Relais d'une bande : le nom affiché sort, le suivant entre ; un mois identique au
       précédent reste en place. */
    var relayer = function () {
      var b = bandes[tour++ % bandes.length];
      b.rang = (b.rang + 1) % b.suites[0].length;
      b.suites.forEach(function (suite, k) {
        var avant = b.montres[k], apres = suite[b.rang];
        if (apres.textContent === avant.textContent) return;
        avant.parentNode.classList.add("demarre");
        avant.classList.remove("actif");
        avant.classList.add("sortant");
        apres.classList.remove("sortant");
        apres.classList.add("actif");
        b.montres[k] = apres;
      });
    };
    var planifier = function (delai) {
      minuterie = setTimeout(function () {
        relayer();
        planifier(RELAIS / bandes.length);
      }, delai);
    };
    var regler = function () {
      var marche = enVue && !document.hidden;
      if (marche && minuterie === null) planifier(PREMIER);
      if (!marche && minuterie !== null) {
        clearTimeout(minuterie);
        minuterie = null;
      }
    };
    new IntersectionObserver(function (entrees) {
      enVue = entrees[entrees.length - 1].isIntersecting;
      regler();
    }).observe(index);
    document.addEventListener("visibilitychange", regler);
  }

  /* ---------- Photos utilisées : chaque photo apparaît à son arrivée à l'écran ---------- */

  var salles = document.querySelectorAll(".salle");
  if (salles.length && !calme && "IntersectionObserver" in window) {
    document.documentElement.classList.add("salles-animees");
    var observateur = new IntersectionObserver(function (entrees) {
      entrees.forEach(function (entree) {
        if (!entree.isIntersecting) return;
        entree.target.classList.add("vue");
        observateur.unobserve(entree.target);
      });
    }, { threshold: 0.2 });
    Array.prototype.forEach.call(salles, function (s) { observateur.observe(s); });
  }

  /* ---------- Visionneuse plein écran ---------- */

  var dialogue = document.querySelector("dialog.visionneuse");
  if (!dialogue || typeof dialogue.showModal !== "function" || !window.history.pushState) return;

  var cadre = dialogue.querySelector(".v-cadre"),
      lienImage = dialogue.querySelector(".v-image"),
      apercu = dialogue.querySelector(".v-apercu"),
      grande = dialogue.querySelector(".v-grande"),
      lienTitre = dialogue.querySelector(".v-titre a"),
      boutonPexels = dialogue.querySelector(".v-pexels"),
      texteRang = dialogue.querySelector(".v-rang");
  var LARGEURS = [800, 1200, 1600, 2200, 3000];
  var nomSite = document.querySelector('meta[property="og:site_name"]');
  var suffixe = nomSite ? " — " + nomSite.getAttribute("content") : "";
  var titreOrigine = document.title;
  var liens = [], rang = 0, poussee = false, balayage = false, depart = null;

  function photo(lien) {
    var img = lien.querySelector("img");
    var base = img.getAttribute("src").split("?")[0];
    return {
      page: lien.getAttribute("href"),
      pexels: lien.getAttribute("data-pexels"),
      titre: img.getAttribute("alt"),
      base: base,
      id: (base.match(/photos\/(\d+)/) || ["", ""])[1],
      apercu: img.currentSrc || img.src,
      ratio: img.getAttribute("width") / img.getAttribute("height"),
      couleur: lien.style.backgroundColor
    };
  }

  function sources(base) {
    return LARGEURS.map(function (l) {
      return base + "?auto=compress&cs=tinysrgb&w=" + l + " " + l + "w";
    }).join(", ");
  }

  function largeurAffichee(ratio) {
    var boite = cadre.getBoundingClientRect();
    return Math.ceil(Math.min(boite.width, boite.height * ratio)) || window.innerWidth;
  }

  function precharger(i) {
    var lien = liens[(i + liens.length) % liens.length];
    if (!lien) return;
    var p = photo(lien), img = new Image();
    img.sizes = largeurAffichee(p.ratio) + "px";
    img.srcset = sources(p.base);
  }

  function afficher() {
    var p = photo(liens[rang]);
    lienImage.style.setProperty("--r", p.ratio);
    lienImage.style.backgroundColor = p.couleur;
    lienImage.href = p.pexels;
    lienImage.setAttribute("data-goatcounter-click", "pexels-image-" + p.id);
    boutonPexels.href = p.pexels;
    boutonPexels.setAttribute("data-goatcounter-click", "pexels-" + p.id);
    boutonPexels.setAttribute("data-goatcounter-title", p.titre);
    lienTitre.href = p.page;
    lienTitre.textContent = p.titre;
    texteRang.textContent = (rang + 1) + " / " + liens.length;
    apercu.src = p.apercu;
    grande.classList.remove("prete");
    grande.removeAttribute("srcset");
    grande.removeAttribute("src");
    grande.alt = p.titre;
    grande.sizes = largeurAffichee(p.ratio) + "px";
    grande.srcset = sources(p.base);
    grande.src = p.base + "?auto=compress&cs=tinysrgb&w=1600";
    document.title = p.titre + suffixe;
    if (window.goatcounter && window.goatcounter.count) {
      window.goatcounter.count({ path: p.page, title: p.titre });
    }
    precharger(rang + 1);
    precharger(rang - 1);
  }

  function noter() {
    var etat = { visionneuse: liens[rang].getAttribute("href") };
    if (poussee) {
      history.replaceState(etat, "", etat.visionneuse);
    } else {
      history.pushState(etat, "", etat.visionneuse);
      poussee = true;
    }
  }

  function ouvrir(i) {
    rang = i;
    if (!dialogue.open) {
      dialogue.showModal();
      document.documentElement.classList.add("v-ouverte");
    }
    afficher();
    noter();
  }

  function aller(sens) {
    if (liens.length < 2) return;
    rang = (rang + sens + liens.length) % liens.length;
    afficher();
    noter();
  }

  grande.addEventListener("load", function () { grande.classList.add("prete"); });

  document.addEventListener("click", function (ev) {
    if (ev.defaultPrevented || ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
    var lien = ev.target.closest ? ev.target.closest("a.carreau") : null;
    if (!lien || !lien.getAttribute("data-pexels")) return;
    var grille = lien.closest(".grille");
    liens = Array.prototype.slice.call(grille.querySelectorAll("a.carreau"));
    ev.preventDefault();
    ouvrir(liens.indexOf(lien));
  });

  dialogue.querySelector(".v-precedente").addEventListener("click", function () { aller(-1); });
  dialogue.querySelector(".v-suivante").addEventListener("click", function () { aller(1); });
  dialogue.querySelector(".v-fermer").addEventListener("click", function () { dialogue.close(); });

  dialogue.addEventListener("keydown", function (ev) {
    if (ev.key === "ArrowRight") { ev.preventDefault(); aller(1); }
    else if (ev.key === "ArrowLeft") { ev.preventDefault(); aller(-1); }
  });

  /* Fermeture : bouton, touche Échap, clic à côté de la photo ou retour arrière. */
  dialogue.addEventListener("close", function () {
    document.documentElement.classList.remove("v-ouverte");
    document.title = titreOrigine;
    if (poussee) {
      poussee = false;
      history.back();
    }
    var lien = liens[rang];
    if (lien) {
      lien.focus({ preventScroll: true });
      lien.scrollIntoView({ block: "nearest" });
    }
  });

  cadre.addEventListener("click", function (ev) {
    if (ev.target === cadre) dialogue.close();
  });

  window.addEventListener("popstate", function (ev) {
    var etat = ev.state && ev.state.visionneuse;
    if (dialogue.open && !etat) {
      poussee = false;
      dialogue.close();
    } else if (!dialogue.open && etat) {
      location.reload();
    }
  });

  window.addEventListener("pageshow", function (ev) {
    if (ev.persisted && dialogue.open && !(history.state && history.state.visionneuse)) {
      poussee = false;
      dialogue.close();
    }
  });

  /* Au doigt : glisser vers la gauche ou la droite pour changer de photo. */
  cadre.addEventListener("pointerdown", function (ev) {
    balayage = false;
    depart = ev.pointerType === "mouse" ? null : { x: ev.clientX, y: ev.clientY };
  });
  cadre.addEventListener("pointerup", function (ev) {
    if (!depart) return;
    var dx = ev.clientX - depart.x, dy = ev.clientY - depart.y;
    depart = null;
    if (Math.abs(dx) > 50 && Math.abs(dx) > 1.5 * Math.abs(dy)) {
      balayage = true;
      aller(dx < 0 ? 1 : -1);
    }
  });
  cadre.addEventListener("pointercancel", function () { depart = null; });
  lienImage.addEventListener("click", function (ev) {
    if (balayage) { ev.preventDefault(); balayage = false; }
  });
})();
