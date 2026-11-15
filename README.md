# Smart Internship Match

Projet suivant `TP_1_STUDENT_MANUAL_smart_internship_match.md`.

## Démarrage rapide

Prérequis : Python 3 installé. Le serveur du dashboard utilise uniquement la
bibliothèque standard de Python ; Ollama et une clé API ne sont pas nécessaires
pour consulter les résultats déjà générés.

1. Ouvrir un terminal PowerShell dans le dossier `smart-internship-match`.
2. Lancer le serveur :

```powershell
python scripts/serve_dashboard.py
```

3. Ouvrir **<http://127.0.0.1:8000/dashboard.html>** dans le navigateur.
4. Garder le terminal ouvert pendant la consultation. Pour arrêter le serveur,
   appuyer sur **Ctrl+C** dans ce terminal.

Si la commande `python` n'est pas reconnue sous Windows, utiliser
`py scripts/serve_dashboard.py`.

Le dashboard charge automatiquement les offres disponibles, restaure le suivi
et affiche dix résultats à la fois avec « Voir plus ». Aucun fichier à sélectionner.

### Si les offres ne s'affichent pas

Vérifier la présence de `data/offers/matches_all_local.json`. S'il manque, placer
le CSV du TD3 `jobs_sample(1).csv` à la racine du projet et générer les résultats :

```powershell
python scripts/import_td3.py --input "jobs_sample(1).csv"
python scripts/match_offers.py
```

Recharger ensuite la page. Le CSV et les résultats privés ne sont pas inclus
dans le dépôt : une nouvelle copie du projet doit disposer du CSV localement.

Si le port 8000 est occupé, lancer `python scripts/serve_dashboard.py --port 8001`
et ouvrir <http://127.0.0.1:8001/dashboard.html>.

Utiliser ce serveur dédié pour charger les données locales : ouvrir le HTML
directement ou lancer `python -m http.server` ne fournit pas le point d'accès
privé nécessaire au chargement automatique.

## Fonctionnement du dashboard

Ce serveur local charge directement
`data/offers/matches_all_local.json`, sans copier ce fichier dans le site public.
Les offres sont aussi conservées dans le navigateur pour les ouvertures suivantes.
Les listes montrent dix éléments, puis proposent « Voir plus ».

Le suivi est sauvegardé automatiquement dans le navigateur. Une candidature
« TEST FICTIF » apparaît au premier lancement si le suivi est vide ; elle simule
un envoi onze jours plus tôt. Elle ne remplace pas des candidatures existantes et
ne revient pas après suppression. Un bandeau signale les indicateurs de simulation.

Les relances sont calculées automatiquement à l'ouverture et après chaque
modification. Les 200 derniers contrôles sont conservés dans le navigateur, avec
leur date, leur déclencheur et les alertes. Aucun import ou export manuel n'est
nécessaire. Le stockage reste propre au navigateur et à l'adresse du site.

GitHub Pages sert uniquement `docs/data/matches.json`, actuellement vide. Il ne
peut pas lire les fichiers privés de l'ordinateur : pour charger les 550 lignes
locales automatiquement, utiliser le serveur ci-dessus. La page `docs/index.html`
conserve la vérification JSON demandée dans le manuel.

## Source de remplacement TD3

L'authentification France Travail échoue avec `invalid_client` dans le journal
fourni. Le fichier `jobs_sample(1).csv` du TD3 sert de remplacement technique :
531 annonces, dont 431 Indeed et 100 LinkedIn, y compris des emplois hors stage.
Elles ne sont pas présentées comme issues de France Travail.

```powershell
python scripts/import_td3.py --input "jobs_sample(1).csv"
python scripts/match_offers.py
```

Le jeu combiné compte 550 lignes avec les 19 offres précédemment extraites. La
provenance TD3 et les plateformes restent affichées. Les compétences des lignes
TD3 sont des mentions détectées par vocabulaire fixe, sans appel Ollama ; missions,
expérience et rémunération ne sont pas extraites pour ces lignes. Le fichier CSV
et les offres privées restent ignorés par Git. Un nouvel import remplace les
lignes TD3 sans les dupliquer.

Les extractions des 19 annonces initiales restent disponibles, mais leurs textes
bruts ne sont plus disponibles dans la fusion après une erreur d'intégration.
Des sauvegardes précèdent désormais les réécritures des fichiers fusionné et structuré.

## Pipeline France Travail et Ollama

```powershell
python -m pip install -r requirements.txt
python scripts/fetch_offers.py
python scripts/merge_offer_sources.py
python scripts/extract_offers.py
python scripts/match_offers.py
python scripts/draft_cv.py
```

La collecte exige les variables `FRANCETRAVAIL_CLIENT_ID` et
`FRANCETRAVAIL_CLIENT_SECRET`, ou les Secrets du workflow GitHub. L'extraction IA et
la rédaction exigent Ollama et `qwen3:8b`. Les lignes TD3 conservent leur méthode
par vocabulaire fixe ; la fusion peut utiliser cette source sans fichier API.
Les brouillons doivent être relus avant utilisation.

## Monitoring Python et rapport

Le contrôle CSV reste utilisable séparément du monitoring automatique du navigateur :

```powershell
python scripts/monitor_applications.py --init
python scripts/monitor_applications.py
```

Il lit `data/applications/applications.csv` et conserve ses traces sous
`output/monitoring/`. La démonstration fictive du 15 novembre possède deux états
CSV séparés sous `data/applications/demo-2026-11-15/`, avec un historique distinct
sous `output/monitoring/demo-2026-11-15/`. Ces traces de test ne sont pas des
résultats de candidatures réelles. Le rapport figure dans [RAPPORT.md](RAPPORT.md).