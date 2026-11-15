# Smart Internship Match — Rapport de projet

## 1. Objectif et données utilisées

Mon objectif est de disposer d'un outil d'aide à la décision pour ma recherche de stage. Je souhaite comparer les offres avec mes compétences, repérer les points à travailler, préparer mes candidatures et suivre les réponses. Le dashboard m'aide à choisir mes prochaines actions, mais la décision reste la mienne.

J'ai renseigné un profil de 29 compétences avec un niveau autoévalué de 1 à 5 et des preuves issues de mes cours, projets et expériences. Mon jeu de données local contient 19 offres Indeed collectées avec JobSpy, structurées avec Ollama, puis classées selon leur correspondance avec mon profil. Parmi ces offres, 18 possèdent au moins une compétence extraite et une n'en possède aucune.

L'API France Travail ne fonctionnant pas dans mon cas, j'utilise le fichier `jobs_sample(1).csv` fourni dans le cadre du TD3 comme remplacement technique pour poursuivre le pipeline. Il contient 531 annonces : 431 issues d'Indeed et 100 de LinkedIn. Je les identifie sous la source `td3_sample` en conservant la plateforme d'origine. Je ne les présente pas comme des résultats de l'API France Travail.

Les 19 offres précédemment traitées sont conservées : le jeu local combiné contient donc 550 lignes, sans dédoublonnage entre les deux acquisitions. Des annonces communes peuvent être présentes. Le CSV contient aussi des emplois hors stage : le classement ne suffit pas à déterminer leur pertinence pour ma recherche.

Les résultats structurés des 19 offres initiales restent disponibles, mais leurs descriptions brutes ne sont plus présentes dans la fusion actuelle à la suite d'une erreur de traitement lors de l'intégration. L'analyse des trois offres ci-dessous avait été réalisée avant cette erreur. Une nouvelle extraction de ces annonces nécessiterait de récupérer leurs textes ; les résultats existants sont conservés sans les réinventer.

Ollama n'étant pas joignable lors de l'intégration du CSV, j'utilise pour ces 531 lignes une détection de mentions techniques par vocabulaire fixe, distincte de l'extraction IA des 19 offres initiales. Les missions, l'expérience et la rémunération des lignes TD3 ne sont pas extraites et restent non renseignées. Cette méthode facilite la démonstration du matching, mais ne permet pas d'affirmer qu'une technologie citée est une compétence exigée.

Mon fichier public `docs/data/matches.json` reste vide : les annonces du TD3 proviennent également de plateformes de recrutement et ne deviennent pas des données ouvertes par leur utilisation en cours. Pour consulter le jeu combiné et ses indications de provenance dans le dashboard, j'importe le fichier `matches_all_local.json` actualisé.

## 2. Définition de mon KPI de correspondance — CM2

J'utilise deux indicateurs complémentaires :

- **La couverture** : nombre de compétences de l'offre présentes dans mon profil, divisé par le nombre de compétences uniques extraites pour cette offre.
- **Le score** : somme des niveaux des compétences correspondantes, divisés par 5, puis divisée par le nombre de compétences uniques de l'offre.

Ces deux valeurs sont comprises entre 0 et 1 et affichées en pourcentage. Une compétence manquante contribue zéro au score. Lorsqu'aucune compétence n'a été extraite, les deux indicateurs valent zéro par manque d'information.

Par exemple, si une offre demande deux compétences que je possède aux niveaux 1/5 et 3/5, ma couverture est de 100 %, mais mon score est de 40 %. Je distingue ainsi la présence d'une compétence de mon niveau de pratique.

Pour éviter de manquer des correspondances à cause de la présentation, je neutralise la casse et les espaces répétés. Je supprime les doublons pour qu'une compétence répétée ne pèse pas davantage dans le calcul. Je conserve les libellés de mon profil pour retrouver les preuves utilisées dans les brouillons.

Mon score reste une approximation : mes niveaux sont autoévalués et les exigences ont toutes le même poids. Le calcul ne distingue pas les compétences obligatoires des atouts, ni les alternatives entre technologies. Il ne rapproche pas encore les synonymes comme `Unity` et `Unity 3D`. Je dois donc examiner les annonces avant de conclure qu'une offre correspond ou non à mon profil.

## 3. Dashboard et justification des représentations — CM1/CM2

J'ai conservé la page de vérification JSON demandée à l'étape 15 et ajouté un dashboard séparé. Il s'adresse à moi en tant que candidat et couvre les trois catégories d'indicateurs demandées dans le manuel.

### Qualité du pipeline

| Indicateur et représentation | Décision que je peux prendre | Justification |
| --- | --- | --- |
| Nombre d'offres et de sources, sous forme de cartes | Déterminer si je dois élargir ma collecte | Une valeur simple se lit directement, sans graphique supplémentaire. |
| Offres par source, en barres horizontales | Identifier une dépendance à une source | La longueur des barres facilite la comparaison des volumes entre sources. |
| Offres sans compétence extraite, sous forme de carte | Repérer un besoin de relecture | Ce décompte mesure la complétude de l'extraction, sans le confondre avec un taux d'erreur de l'IA. |

Je n'affiche pas de taux d'erreur d'extraction chiffré : la revue limitée de trois offres ne constitue pas une mesure représentative des 19 annonces.

### Pertinence de ma recherche

| Indicateur et représentation | Décision que je peux prendre | Justification |
| --- | --- | --- |
| Distribution des scores en cinq intervalles fixes | Voir si plusieurs pistes présentent une correspondance intéressante | Les barres montrent la répartition des offres, qu'une moyenne pourrait masquer. |
| Fréquence des compétences manquantes, en barres horizontales | Choisir une compétence à approfondir | Les barres permettent de comparer les fréquences tout en gardant les libellés longs lisibles. |
| Compétences correspondantes, en étiquettes avec leur fréquence | Choisir les atouts à mettre en avant | Les étiquettes associent chaque compétence au nombre d'offres qui la demandent. |
| Part des offres avec une couverture d'au moins 30 %, sous forme de carte | Estimer le nombre de pistes à examiner pour la rédaction | Le seuil est cohérent avec celui utilisé pour sélectionner les brouillons ; il ne mesure pas mes chances de recrutement. |
| Liste filtrable, avec score et couverture | Choisir une annonce à examiner en détail | Chaque résultat rapproche les indicateurs des missions et des compétences de l'offre. |

Les graphiques résument le jeu actif complet ; les filtres agissent sur la liste. Je peux rechercher un poste ou une compétence, sélectionner une source et fixer une couverture minimale.

Je conserve la rémunération comme information descriptive plutôt que comme graphique central : seules 5 des 19 offres traitées initialement comportent une rémunération chiffrée extraite. Les 531 lignes TD3 n'ont pas été analysées pour ce champ. Les valeurs absentes ne doivent pas être interprétées comme une absence de rémunération.

### Résultats de mes candidatures

| Indicateur et représentation | Décision que je peux prendre | Justification |
| --- | --- | --- |
| Candidatures envoyées, sous forme de carte | Suivre mes démarches réalisées | Je compte uniquement les candidatures enregistrées dans mon suivi. |
| Taux de réponse, sous forme de carte | Observer si mes candidatures obtiennent des retours | Je divise les candidatures ayant une date de première réponse par le nombre de candidatures envoyées. Un refus compte comme une réponse. |
| Candidatures actuellement en entretien ou acceptées, sous forme de carte | Identifier les démarches qui ont progressé | Cet indicateur décrit le statut actuel ; il ne représente pas un historique de tous les entretiens. |
| Liste des candidatures à relancer | Identifier ma prochaine action | La liste me permet de retrouver les candidatures concernées, au-delà d'un simple total. |

Le suivi ne contient encore aucune candidature. Le taux de réponse reste donc indéfini et s'affiche avec un tiret. Je ne peux pas encore conclure sur l'efficacité de ma recherche. Les relances constituent un indicateur de qualité du suivi, au-delà du seul objectif d'envoyer davantage de candidatures.

## 4. Utilisation de l'IA et analyse de ses erreurs — CM5

J'utilise Ollama pour structurer le texte des annonces et proposer des paragraphes de motivation à partir des preuves de mon profil. Le calcul des scores, le suivi des candidatures et le monitoring reposent sur des règles déterministes.

L'analyse assistée des trois premières offres du classement initial de 19 annonces, avant l'ajout du TD3, et de leurs brouillons a fait ressortir les problèmes suivants :

| Cas examiné | Erreur ou limite observée | Conséquence pour ma recherche |
| --- | --- | --- |
| Développement IA Python / JavaScript | Le brouillon affirme une maîtrise de Python alors que mon profil indique un niveau de 1/5 et des bases acquises en cours. | Je dois présenter honnêtement mes bases. La couverture de 100 % ne signifie pas que j'ai le niveau demandé dans l'annonce. |
| Observabilité des réseaux | L'extraction omet notamment les bases en embarqué/temps réel et l'anglais technique. Le score compte séparément des langages présentés comme des alternatives. | Je dois revenir au texte original avant d'interpréter le classement. |
| Développement de tests en VR | `Unity 3D` est considéré comme manquant alors que mon profil contient `Unity`. Le brouillon attribue aussi à mon expérience des réalisations décrites dans les missions de l'offre, sans preuve correspondante. | L'offre est pénalisée par le vocabulaire du matching. Je dois retirer les réalisations non justifiées du paragraphe de motivation. |

Cette comparaison porte sur les descriptions sauvegardées localement, sans vérifier que les annonces sont toujours ouvertes. Elle met en évidence des limites réelles, mais ne permet pas de généraliser un taux d'erreur à toutes les offres.

Le prompt de rédaction transmet désormais mes niveaux et demande de ne pas transformer les missions futures en expériences déjà réalisées. Des propositions corrigées ont été préparées à partir de mes preuves. Je dois encore les relire et les valider personnellement avant utilisation : ces précautions ne garantissent pas l'absence d'erreurs dans les réponses de l'IA.

## 5. Confidentialité et publication — CM6

Les annonces Indeed et LinkedIn du CSV TD3 suivent les mêmes règles de non-publication que les autres annonces JobSpy. Je conserve le CSV et sa conversion JSON en local, ignorés par Git.

Je sépare les données publiques de celles réservées à mon usage personnel. Les offres Indeed sont marquées `publishable: false` et exclues du fichier public, conformément au manuel. Les fichiers intermédiaires, les brouillons, les candidatures et les journaux de monitoring sont ignorés par Git.

L'import du fichier local dans le dashboard me permet de consulter mes offres sans les envoyer au serveur. Mon suivi de candidatures reste dans le stockage du navigateur ; je peux l'exporter pour le sauvegarder. Mon profil de compétences fait en revanche partie du dépôt : je dois tenir compte de sa visibilité lorsque je renseigne les preuves associées à mes expériences.

## 6. Suivi et monitoring — CM4

Mon tableau de suivi contient l'offre, l'entreprise, le poste, la date d'envoi, le statut et la date de première réponse. Je le mets à jour à partir des démarches réellement effectuées.

J'ai retenu la règle suivante : une candidature envoyée depuis au moins dix jours calendaires, toujours au statut « Envoyée » et sans réponse enregistrée, doit être signalée comme une relance à envisager. Le contrôle ne contacte pas le recruteur : je décide moi-même de la suite à donner.

Le dashboard applique ce contrôle à l'ouverture et après chaque modification. Pour conserver une trace datée, j'exporte le suivi en CSV, puis je lance `monitor_applications.py`. Le script enregistre le résultat dans un historique local et signale également les incohérences de dates, de statuts ou les doublons.

Deux exécutions techniques ont été réalisées le 14 novembre 2026 :

| Exécution, heure de Paris | Candidatures contrôlées | Relances détectées | Erreurs de données |
| --- | --- | --- | --- |
| 16 h 22 | 0 | 0 | 0 |
| 16 h 24 | 0 | 0 | 0 |

Ces deux passages sur un suivi vide vérifient le fonctionnement du contrôle, mais ne permettent pas d'observer l'évolution de ma recherche. Pour compléter l'objectif de monitoring du manuel, je dois le relancer à plusieurs moments du projet avec mes candidatures réelles et consigner ce qu'il aura détecté.
