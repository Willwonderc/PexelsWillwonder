// Construit la rubrique depuis ../donnees : dist/ (fichiers à servir sous /statique/rubrique-monde/) et ../demo/ (page de démonstration).
// Usage : npm ci && node construire.mjs [--base /statique/rubrique-monde/]
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';

const ici = path.dirname(fileURLToPath(import.meta.url));
const lire = (f) => fs.readFileSync(path.join(ici, f), 'utf8');
const i = process.argv.indexOf('--base'), BASE = i > 0 ? process.argv[i + 1] : '/statique/rubrique-monde/';
const dist = path.join(ici, 'dist'), demo = path.join(ici, '..', 'demo');
fs.mkdirSync(dist, { recursive: true }); fs.mkdirSync(demo, { recursive: true });

// 1. Données : le registre de la rubrique et les points de terre, en un script qui pose window.MONDE
const d = JSON.parse(lire('../donnees/rubrique-monde.json'));
d.geo = { terres: JSON.parse(lire('../donnees/geo-terres.json')).terres };
fs.writeFileSync(path.join(dist, 'rubrique-monde-donnees.js'), 'window.MONDE=' + JSON.stringify(d).replace(/<\//g, '<\\/') + ';\n');

// 2. Script de la rubrique (three.js et Motion inclus), feuille de style, amorce
await build({ entryPoints: [path.join(ici, 'src/rubrique-monde.js')], bundle: true, minify: true, format: 'iife', target: 'es2020',
  legalComments: 'none', outfile: path.join(dist, 'rubrique-monde.js') });
fs.writeFileSync(path.join(dist, 'rubrique-monde.css'), ['rubrique.css', 'affiche.css', 'p4a.css'].map((f) => lire('styles/' + f)).join('\n'));
fs.copyFileSync(path.join(ici, 'src/amorce.js'), path.join(dist, 'rubrique-monde-amorce.js'));
fs.copyFileSync(path.join(ici, 'styles/bouton.css'), path.join(dist, 'bouton.css'));

// 3. Fragment du gabarit (bouton), avec le détail calculé depuis les données
const p0 = d.photos.find((p) => p.id === '38694055') || d.photos[0];
const detail = `${d.photos.length} photos · ${d.total} parutions · ${d.repertoire.length} médias · ${d.pays.length} pays, et des sites dont le lieu n’est pas établi`;
const fragment = (base) => lire('gabarit/fragment-galeries.html').replaceAll('__BASE__', base).replace('__BANDE__', p0.grande).replace('__DETAIL__', detail);
fs.writeFileSync(path.join(dist, 'fragment-galeries.html'), fragment(BASE));

// 4. Page de démonstration : la page Galeries simulée, qui charge dist/ comme le fera le site
const tuile = (id, nom, n) => { const p = d.photos.find((x) => x.id === id); return p ? `<div class="h-galerie"><span><img src="${p.vignette}" alt="" loading="lazy"></span><b>${nom}</b>${n ? `<small>${n} photos</small>` : ''}</div>` : ''; };
const page = lire('gabarit/demo.html')
  .replace('/*__CSS__*/', lire('gabarit/demo-hote.css') + '\n' + lire('styles/bouton.css'))
  .replace('<!--__ENTREE__-->', fragment('../sources/dist/'))
  .replace('<!--__THEMES__-->', [['38694055', 'Jardins des châteaux de la Loire', 24], ['34354424', 'Parcs et jardins', 42], ['27116682', 'Ciel et astrophotographie', 22], ['13102252', 'Nuages et couchers de soleil', 39]].map((t) => tuile(...t)).join(''))
  .replace('<!--__LIEUX__-->', [['23414382', 'Niort'], ['19047688', 'Poitiers'], ['34500384', 'Cognac'], ['13087478', 'Moyemont']].map((t) => tuile(...t)).join(''))
  .replace('__BANDEAU__', p0.grande);
fs.writeFileSync(path.join(demo, 'index.html'), page);
console.log(`dist/ : ${fs.readdirSync(dist).join(', ')} · démo : ../demo/index.html · ${d.photos.length} photos, ${d.total} parutions, ${d.repertoire.length} médias`);
