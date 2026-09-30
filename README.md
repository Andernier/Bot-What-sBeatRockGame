# RockBot — recherche autonome de chaînes

Bot Python utilisant **Ollama local**, Chromium et SQLite. Pas de clé API ni de service d'IA payant. Il faut un ordinateur capable de faire tourner le modèle, de l'espace disque et une connexion au jeu. La vitesse dépend du matériel.

## Installation (Windows, macOS, Linux)

Installez Python 3.10 ou supérieur et Ollama depuis https://ollama.com/ .
Ouvrez un terminal dans ce dossier extrait, puis :

```sh
ollama pull qwen3:4b
python -m venv .venv
```

Activez l'environnement :

- Windows PowerShell : `.venv\Scripts\Activate.ps1`
- Windows cmd : `.venv\Scripts\activate.bat`
- macOS/Linux : `source .venv/bin/activate`

Puis :

```sh
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Sur les systèmes où `python` n'existe pas, utilisez `python3` (ou `py` sous Windows).
Gardez Ollama ouvert. Si son service n'est pas déjà démarré, lancez `ollama serve` dans un autre terminal.
Le modèle qwen3:4b représente environ 2,5 Go à télécharger ; l'exécution demande davantage de mémoire. Pour une petite machine, essayez `ollama pull qwen3:1.7b`, puis `--model qwen3:1.7b`. La qualité des réponses peut baisser.

## Premier essai

```sh
python bot.py --episodes 2 --max-tests 10
```

Un navigateur visible s'ouvre sur le jeu. Ne jouez pas manuellement dans cette fenêtre pendant l'exécution.
Ensuite, pour une session plus longue :

```sh
python bot.py --episodes 20 --max-tests 300 --delay 10
```

`Ctrl+C` arrête la session. Relancer la même commande conserve les connaissances ; une nouvelle partie repart de rock. Le bot ne restaure pas une partie interrompue en plein milieu.

## Ce qu'il apprend

- Chaque essai confirmé : chaîne complète, paire proposée, verdict, explication du site, date.
- Les refus sont exclus dans le même contexte. Dans un autre contexte, ils peuvent être réessayés.
- Les succès observés ailleurs fournissent des candidats, sans être considérés comme garantis.
- Par défaut, environ 75 % des décisions avec des liens connus privilégient leur fiabilité et la longueur de continuation déjà observée dans le contexte exact ; 25 % cherchent de nouvelles réponses (`--epsilon 0.25`).
- Le modèle reçoit les derniers essais pour l'élément courant, succès et refus compris.
- Les répétitions de mots dans une chaîne sont exclues (casse et espaces normalisés). Les synonymes ne sont pas détectés de façon certaine.

Il s'agit d'une mémoire d'expérience et d'une stratégie de recherche, pas d'un réentraînement des poids du modèle. L'amélioration n'est pas garantie à chaque partie. La plus longue chaîne possible n'est pas calculable exhaustivement avec des réponses libres.

## Résultats

```sh
python bot.py --stats
```

- `data/memory.sqlite3` : mémoire persistante, liens et explications.
- `data/best_chain.json` : meilleure chaîne entièrement confirmée dans une même partie (score = nombre de liens).
- `data/last_error.png` : capture de diagnostic si l'exécution échoue.

Gardez le dossier `data` pour conserver l'apprentissage. Utilisez `--data autre_dossier` pour une mémoire distincte. Les plafonds `--max-tests` (total de soumissions par lancement), `--episodes` et `--max-depth` bornent l'exploration. Le plafond d'essais inclut les liens connus rejoués.

## Limites et erreurs

Le bot utilise l'interface publique, une seule fenêtre et un délai entre soumissions. Il s'arrête devant un verdict inconnu, une limitation ou une demande de vérification. Il ne contourne pas ces contrôles. Un délai d'attente ou une erreur de connexion n'est jamais appris comme une défaite.

Les contrôles GO, next, play again, les paragraphes de victoire/défaite et le score ont été observés sur le site le 30 septembre 2026. Si le site change, l'adaptateur `Game` / `parse_verdict` peut nécessiter une modification. Les tests unitaires couvrent la mémoire contextuelle, le classement et la lecture des verdicts ; l'exécution complète avec Ollama et Playwright sur votre machine reste à valider. Aucun record réel n'est fourni avec le projet.

Ollama inaccessible : vérifiez que l'application tourne et que le modèle a été téléchargé. Modèle lent : essayez une taille plus petite. Verdict inconnu : consultez `last_error.png` ; le programme s'arrête pour ne pas polluer la mémoire.

## Tests hors ligne

```sh
python -m unittest -v
```

Références :
- https://docs.ollama.com/api/generate
- https://ollama.com/library/qwen3:4b
- https://playwright.dev/python/docs/intro
- https://www.whatbeatsrock.com/
