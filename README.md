# Smart Internship Match

Projet de recherche de stage suivant `TP_1_STUDENT_MANUAL_smart_internship_match.md`.

## Consulter le dashboard

```powershell
python -m http.server 8000 --directory docs
```

Ouvrir <http://localhost:8000/dashboard.html>. Sur GitHub Pages, ajouter
`/dashboard.html` à l'adresse du site ou suivre le lien de la page d'accueil.
`docs/index.html` conserve la vérification JSON demandée à l'étape 15.

Le jeu public vient de `docs/data/matches.json`. Il ne contient actuellement aucune
offre publiable. Pour explorer les offres privées, utiliser
« Explorer mes offres locales » et sélectionner
`data/offers/matches_all_local.json`. L'import est lu dans le navigateur, sans
envoi au serveur. Ne pas copier ce fichier dans `docs/`.

### Remplacement de l'API par le CSV du TD3

L'API France Travail ne fonctionne pas dans cette réalisation (constat signalé
par le candidat). Le fichier fourni `jobs_sample(1).csv` sert de remplacement
technique. Il contient 531 annonces : 431 Indeed et 100 LinkedIn, y compris des
emplois hors stage. Ce ne sont pas des données France Travail ni une preuve que
l'acquisition API fonctionne. Les 19 offres déjà extraites restent conservées à côté.

```powershell
python scripts/import_td3.py --input "jobs_sample(1).csv"
python scripts/match_offers.py
```

L'import crée `data/offers/td3_offers.json`, met à jour les fichiers fusionné et
structuré sans supprimer les autres sources, puis le matching produit le fichier
local à réimporter dans le dashboard. Un nouvel import remplace la source TD3
sans la dupliquer. Le fichier brut et ses sorties restent ignorés par Git.

Ollama n'étant pas joignable lors de cette intégration, les compétences TD3 sont
des mentions détectées dans les descriptions par un vocabulaire fixe documenté
dans `scripts/import_td3.py`. Missions, expérience et rémunération restent vides.
Il ne s'agit pas d'une extraction IA, et une technologie citée n'est pas forcément
exigée du candidat. La provenance et la méthode sont affichées dans le dashboard.
Ces annonces restent non publiables comme les autres annonces JobSpy.

Les filtres affectent la liste d'offres ; les graphiques résument le jeu actif complet.
Le taux d'erreur IA est indiqué comme non mesuré, car il nécessite un audit humain.

## Pipeline des étapes précédentes

```powershell
python -m pip install -r requirements.txt
python scripts/fetch_offers.py
python scripts/merge_offer_sources.py
python scripts/extract_offers.py
python scripts/match_offers.py
python scripts/draft_cv.py
```

La collecte exige `FRANCETRAVAIL_CLIENT_ID` et `FRANCETRAVAIL_CLIENT_SECRET` dans
l'environnement, ou les Secrets du workflow fourni. Ne jamais les écrire dans le
dépôt. L'extraction et la rédaction exigent Ollama et `qwen3:8b` en local.
Sans fichier France Travail, la fusion utilise l'import TD3 s'il est disponible.
L'extraction conserve la méthode déclarée des lignes TD3 ; les autres offres
nécessitent toujours Ollama si leur extraction est relancée.
Relire les brouillons avant utilisation ; le prompt transmet désormais les niveaux
pour limiter les exagérations, ce qui ne garantit pas leur absence.

## Suivre les candidatures (étapes 15 et 16)

1. Saisir uniquement les candidatures réellement envoyées dans le dashboard.
2. Mettre à jour le statut et la date de première réponse ensemble, puis cliquer
   « Enregistrer ». Un refus est une réponse ; une candidature retirée sans retour ne l'est pas.
3. Exporter régulièrement le suivi JSON. Le navigateur conserve ses propres données
   par origine : localhost et GitHub Pages ont des suivis distincts.
4. Pour le contrôle Python, exporter le CSV et l'enregistrer sous
   `data/applications/applications.csv`. Remplacer le CSV après chaque nouvelle exportation.

```powershell
python scripts/monitor_applications.py --init
python scripts/monitor_applications.py
```

`--init` crée un suivi vide seulement si le fichier n'existe pas. Il ne crée aucune
candidature. Chaque contrôle ajoute une ligne dans `output/monitoring/history.jsonl`
et actualise `latest.json`. Une candidature « Envoyée » sans réponse depuis au moins
10 jours calendaires déclenche une relance ; les incohérences de dates ou de statut
sont signalées et produisent un code de sortie 1. Les journées sont calculées en
Europe/Paris. Le dashboard contrôle aussi ces relances à l'ouverture et à chaque
modification. Le contrôle Python est lancé manuellement après l'export du CSV.

Lancer le contrôle à plusieurs moments du projet et commenter ses résultats dans
le rapport. Deux passages techniques consécutifs sur un suivi vide ne permettent
pas de conclure à l'efficacité de la recherche.

## Vérifications et livrables

```powershell
python -B -m unittest discover -s tests -v
node --check docs/dashboard.js
node tests/dashboard.test.cjs
```

Les tests utilisent des cas synthétiques séparés des candidatures personnelles.
Le rapport de travail est dans [RAPPORT.md](RAPPORT.md) ; les éléments nécessitant
une validation personnelle y sont explicités. Les données de candidature, brouillons
et historiques de monitoring restent ignorés par Git. Le brief d'évaluation
`project1_internship_job_search.md` et le guide de choix des graphiques référencés
par le manuel ne sont pas présents : vérifier le rendu contre ces documents avant remise.
