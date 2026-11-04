# YouTube Downloader

Enregistrez sur votre ordinateur une vidéo ou une playlist YouTube, en vidéo (MP4) ou en audio (MP3). **Aucune installation nécessaire.**

## [⬇️ Télécharger la dernière version](../../releases/latest)

Sur cette page, dans la partie **Assets**, prenez le fichier de votre système :

| Votre ordinateur | Fichier à télécharger |
| --- | --- |
| Windows | `YouTube-Downloader-Windows.exe` |
| Mac à puce Apple (M1, M2…) | `YouTube-Downloader-macOS.zip` |
| Linux | `YouTube-Downloader-Linux` |

Le fichier pèse environ 100 Mo, car il contient tout ce qu'il faut pour fonctionner. L'ouverture peut prendre quelques secondes.

## Ouvrir l'application

### Windows

1. Téléchargez le fichier. Si le navigateur vous avertit, choisissez **… → Conserver**.
2. Double-cliquez sur le fichier.
3. Si le message « Windows a protégé votre ordinateur » s'affiche, cliquez sur **Informations complémentaires**, puis sur **Exécuter quand même**.

### macOS (Mac à puce Apple uniquement)

1. Téléchargez le fichier, puis double-cliquez dessus pour le décompresser.
2. Glissez **YouTube-Downloader** dans le dossier **Applications**.
3. Ouvrez l'application. Le premier lancement est bloqué par macOS :
   - **macOS 14 et avant** : faites un clic droit sur l'application, puis **Ouvrir**, puis encore **Ouvrir**.
   - **macOS 15 et après** : ouvrez **Réglages Système → Confidentialité et sécurité**, descendez en bas de la page et cliquez sur **Ouvrir quand même**.

### Linux

1. Rangez le fichier à son emplacement définitif (par exemple dans votre dossier personnel), car le raccourci du menu pointera vers cet endroit.
2. Rendez-le exécutable : clic droit → **Propriétés → Permissions** → cochez **Autoriser l'exécution**. Vous pouvez aussi utiliser la commande `chmod +x YouTube-Downloader-Linux`.
3. Double-cliquez dessus. L'application apparaît ensuite dans le menu des applications, et un raccourci avec son icône est créé sur le Bureau.
4. Utilisez désormais ce raccourci : le fichier téléchargé garde une icône générique, car Linux ne permet pas d'en intégrer une dans un exécutable. Au premier clic, si le système demande une confirmation, choisissez **Lancer quand même** ou **Marquer comme exécutable**.

## Pourquoi ces avertissements ?

L'application n'est pas signée, car la signature auprès de Microsoft et d'Apple est payante. Votre système ne connaît donc pas son auteur et préfère vous prévenir. Le code est public : vous pouvez le lire sur cette page.

## Utiliser l'application

1. Collez l'adresse de la vidéo ou de la playlist.
2. Vérifiez le **dossier de destination** (par défaut, votre dossier de téléchargements).
3. Choisissez **Vidéo** ou **Audio**.
4. Pour une playlist, cochez **Cette adresse est une playlist**. Vous pouvez aussi lui donner un nom.
5. Cliquez sur **Lancer le téléchargement** et suivez l'avancement dans le journal d'activité.

## Vos fichiers, les mises à jour et la désinstallation

- **Vos fichiers** : les vidéos et les musiques sont enregistrées dans le dossier que vous choisissez. L'application n'enregistre ni compte ni réglage.
- **Mettre à jour** : téléchargez la dernière version et remplacez l'ancien fichier. Vos vidéos et vos musiques ne sont pas touchées. Si les téléchargements cessent de fonctionner, essayez d'abord cette mise à jour : YouTube change régulièrement son fonctionnement.
- **Désinstaller** : supprimez le fichier de l'application (sur Mac, mettez l'application à la corbeille). Vos vidéos et vos musiques restent en place.
- **Linux uniquement** : supprimez aussi le raccourci du Bureau. Pour retirer l'application du menu, supprimez ces deux fichiers :
  - `~/.local/share/applications/youtube-downloader.desktop`
  - `~/.local/share/icons/hicolor/512x512/apps/youtube-downloader.png`

## En cas de problème

- **Le téléchargement échoue** : lisez le message dans le journal d'activité, vérifiez votre connexion et essayez d'abord une seule vidéo.
- **« Certificate verify failed »** : il s'agit en général d'un problème de réseau. Essayez une autre connexion.

## Mention légale

**Important** : cet outil est destiné à un usage légal, personnel et autorisé uniquement. Télécharger du contenu YouTube sans les droits, l'autorisation ou une base légale valable peut enfreindre les conditions de YouTube et le droit d'auteur applicable.

Il vous appartient de vérifier que vous avez le droit de télécharger et d'utiliser chaque contenu. L'auteur n'approuve pas le téléchargement ni la redistribution non autorisés de contenus protégés.

## Pour les développeurs

Lancer depuis les sources (Tkinter doit être disponible, par exemple avec `sudo apt install python3-tk` sous Debian/Ubuntu) :

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python "YouTube downloader.py"
```

Publier une version : GitHub Actions construit les trois exécutables et les ajoute à la Release à chaque tag `v*`.

```bash
git tag vX.Y && git push origin vX.Y
```

yt-dlp est figé dans chaque exécutable : publiez une nouvelle version dès que YouTube casse les téléchargements.

## À propos

- **Auteur** : J. Jifferson Delly
- **Portfolio** : https://dellyjifferson.engineer
- **Réalisé avec** : Python, Tkinter, yt-dlp, FFmpeg (via imageio-ffmpeg)
- **Licence** : voir le fichier [LICENSE](LICENSE)
