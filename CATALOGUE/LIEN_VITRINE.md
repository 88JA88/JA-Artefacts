# Échange avec VITRINE

CATALOGUE est la source unique du titre et de la photo principale des objets.

Après chaque création ou modification d’un objet :

1. enregistrer l’objet dans `donnees.js` et son PDF dans `ANALYSES` ;
2. lancer `generer_echange_vitrine.py` ;
3. publier ensemble `vitrine.json` et le dossier `vignettes`.

Le générateur reprend le numéro et la désignation de `donnees.js`. Il extrait
la plus grande photographie de la première page du PDF et en fait la vignette
de référence. VITRINE lit ensuite ces fichiers automatiquement à partir du
numéro de l’objet.
