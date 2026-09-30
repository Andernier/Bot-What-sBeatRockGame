# RockBot — Mac Intel / macOS Monterey

Version adaptée au MacBook Air 2017, Intel i5, 8 Go, macOS 12.7.6.
Elle utilise Safari et un petit modèle Qwen3-0.6B local via llama.cpp. Aucun abonnement ni clé API. Pas d'Ollama, de Playwright, de Homebrew ou de navigateur à télécharger.

**Statut : code et tests hors ligne vérifiés. La compilation et l'exécution sur votre Mac restent à valider.** Les réglages visent Monterey : compilation locale pour Intel, cible macOS 12, GPU Metal et Accelerate désactivés. Cela ne constitue pas une garantie de compatibilité avec toutes les versions des outils Apple.

## 1. Préparer le Mac (une seule fois)

1. Téléchargez l'installateur « macOS 64-bit universal2 » de Python 3.12.10 :
   https://www.python.org/downloads/release/python-31210/
   Il prend en charge macOS 10.13 et ultérieur. Si vous avez déjà Python 3.12, gardez-le.
2. Installez Python, puis fermez et rouvrez Terminal.
3. Dans Terminal, entrez :

```sh
xcode-select --install
```

Terminez l'installation des outils Apple dans la fenêtre qui s'ouvre. Si les outils sont déjà installés, passez à la suite. Il n'est pas nécessaire d'installer tout Xcode depuis l'App Store. Cette étape peut prendre du temps et plusieurs Go.

4. Autorisez le pilotage de Safari avec la commande officielle :

```sh
/usr/bin/safaridriver --enable
```

macOS peut demander votre mot de passe dans Terminal. Ne le partagez pas dans la conversation. Si le pilote demande explicitement les droits administrateur, relancez uniquement cette commande avec `sudo` devant. Cette activation permet aux outils locaux de créer des sessions Safari automatisées ; le bot ne l'active pas à votre place.

Si Safari signale encore que l'automatisation est désactivée, ouvrez Safari → Préférences → Avancées → « Afficher le menu Développement », puis Développement → « Autoriser l'automatisation à distance ». Les libellés peuvent varier selon la version.

## 2. Installer le projet

Décompressez `rockbot-mac.zip`. Ouvrez Terminal, tapez `cd ` (avec un espace), glissez le dossier **rockbot-mac** depuis le Finder dans Terminal, puis appuyez sur Entrée.

```sh
bash installer.sh
```

Le script crée `.venv` dans ce dossier, installe les dépendances, compile le moteur pour le processeur Intel, puis télécharge le modèle officiel Qwen (environ 640 Mo). La compilation initiale peut être longue. Branchez le Mac au secteur. Le script ne change pas votre Python système et ne lance aucun essai sur le jeu.

Si une étape échoue, le script s'arrête. Envoyez les dernières lignes d'erreur ; ne poursuivez pas avec les commandes suivantes. Le script peut être relancé après correction, il réutilise les éléments déjà installés.

## 3. Vérifier séparément le modèle et Safari

Dans le même Terminal :

```sh
bash lancer.sh --check-model
```

Attendez une liste de propositions pour `rock`. Elles ne sont pas encore validées par le jeu. Le petit modèle peut proposer des réponses médiocres ; sa vitesse sur ce Mac n'a pas été mesurée.

Puis :

```sh
bash lancer.sh --check-safari
```

Safari s'ouvre sur le site, son titre s'affiche dans Terminal, puis la fenêtre automatisée se ferme. Aucun coup n'est soumis.

## 4. Premier essai autonome

```sh
bash lancer.sh --episodes 2 --max-tests 10
```

Le bot propose, soumet, lit le verdict et continue. Une défaite déclenche une nouvelle partie. Ne prenez pas la main dans la fenêtre Safari automatisée pendant la session ; Safari peut interrompre l'automatisation si vous intervenez.

Pour une session plus longue :

```sh
bash lancer.sh --episodes 20 --max-tests 200 --delay 10
```

Il utilise deux threads CPU par défaut. `--threads 1` réduit la concurrence CPU ; `--threads 4` est à expérimenter, sans garantie de gain. `Ctrl+C` arrête le bot en conservant sa mémoire. L'ordinateur doit rester éveillé et connecté au site.

## 5. Voir le record et garder l'apprentissage

```sh
bash lancer.sh --stats
```

Tout est stocké dans le sous-dossier `data` à côté du programme :

- `memory.sqlite3` : essais, verdicts, explications et contexte complet.
- `best_chain.json` : meilleure chaîne validée dans une partie, avec son score.
- `last_error.png` : capture si une erreur survient pendant la session Safari.

Ne supprimez pas `data` pour conserver l'apprentissage. On peut copier `memory.sqlite3` de l'ancienne version dans ce dossier, lorsque tous les bots sont arrêtés. Relancer le bot garde les connaissances mais recommence une partie depuis rock : une partie en cours n'est pas restaurée.

## Ce que signifie « il apprend »

Les réponses du modèle sont des hypothèses ; seul le verdict du site valide un lien. Le bot conserve aussi les refus et les explications. Il exclut un refus déjà observé dans le même contexte et empêche les répétitions de mots dans la chaîne complète.

Lorsque des liens sont connus, 75 % des décisions les privilégient selon leur fiabilité et la continuation déjà observée dans ce contexte ; 25 % explorent de nouvelles réponses. `--epsilon 0.4` augmente la part d'exploration. Le modèle reçoit une fenêtre des essais précédents pour l'objet courant. Le reste de la mémoire est utilisé par la sélection en Python.

Les poids de l'IA ne sont pas réentraînés. Le bot apprend par mémoire et exploration, sans garantie de progrès à chaque partie ou de record mondial. Qwen3-0.6B est un compromis pour ce Mac ; sa qualité de raisonnement est limitée. Les synonymes ne sont pas tous reconnus comme des répétitions.

## Limites et dépannage

- Un seul navigateur, un délai minimum et des plafonds d'essais. Les liens connus rejoués comptent aussi dans `--max-tests`.
- Une erreur réseau ou un verdict ambigu arrête la session sans être enregistré comme une défaite.
- Une demande de vérification ou une limite du site arrête le bot. Aucun contournement n'est prévu.
- `Python 3.12 manque` : installez Python depuis le lien ci-dessus puis rouvrez Terminal.
- Erreur de compilation : vérifiez les outils Apple et envoyez le message. La compilation réelle Monterey n'a pas pu être testée dans l'environnement Linux de préparation.
- Erreur Safari : vérifiez son autorisation d'automatisation et fermez une éventuelle autre session WebDriver.
- Erreur de certificat de pip : utilisez « Install Certificates.command » dans Applications → Python 3.12, puis relancez. Ne désactivez pas la vérification TLS.
- Modèle absent : relancez `bash installer.sh`.
- Verdict inconnu : regardez `data/last_error.png`. Le site peut avoir changé ; l'adaptateur devra alors être ajusté.

Pour les tests hors ligne, après installation :

```sh
.venv/bin/python -m unittest -v
```

Sources techniques consultées le 30 septembre 2026 :
- https://www.selenium.dev/documentation/webdriver/browsers/safari/
- https://pypi.org/project/llama-cpp-python/0.3.16/
- https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md
- https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/tree/main
- https://pypi.org/project/cmake/3.31.6/
- https://www.python.org/downloads/release/python-31210/
