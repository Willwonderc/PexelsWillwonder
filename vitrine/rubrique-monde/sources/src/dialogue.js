// Injecte le voile et le dialogue de la rubrique à la fin de <body>, s'ils n'y sont pas déjà.
// Ce module est importé en premier : il s'exécute avant la coquille.
if (!document.getElementById('monde')) {
  document.body.insertAdjacentHTML('beforeend',
    '<div id="voile" hidden aria-hidden="true"></div>' +
    '<div id="monde" role="dialog" aria-modal="true" aria-label="Mes photos utilisées dans le monde" hidden>' +
    '<div id="decor" aria-hidden="true"></div>' +
    '<div class="barre"><a class="barre-titre" href="#monde">Mes photos utilisées dans le monde</a><div class="barre-actions">' +
    '<button type="button" id="passer" class="pilule pilule--douce" hidden>Passer l’ouverture</button>' +
    '<button type="button" id="son" class="pilule pilule--douce" aria-pressed="false"><span class="son-icone" aria-hidden="true"></span><span class="son-texte">Son coupé</span></button>' +
    '<button type="button" id="fermer" class="pilule fermer"><span id="fermer-texte">Fermer</span><span class="croix" aria-hidden="true"></span></button>' +
    '</div></div><main id="scene"></main><p id="annonce" class="vh" aria-live="polite"></p></div>');
}
// La bande de photographie du bouton sert aussi au voile d'ouverture : on reporte sa variable sur la racine.
{
  const b = document.getElementById('entree');
  const bande = b && getComputedStyle(b).getPropertyValue('--bande').trim();
  if (bande) document.documentElement.style.setProperty('--bande', bande);
}
