/* Site de Karl Forterre : fondu de l'accueil et visionneuse plein écran.
   JavaScript léger, sans bibliothèque. Sans lui, le site fonctionne tout autant :
   chaque vignette mène à la page de sa photo. */
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
