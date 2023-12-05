# Protocole de communication RF

Ce dépôt contient le code des 2 cartes Micro:bit communicant en RF pour le projet d'IoT. Il contient aussi une bibliothèques de fonctions utiles au formatage et envoi des données.

## Dossier info_meteo_screen

Ce dossier contient le code (main.cpp) de la carte Micro:bit qui possède les différents capteurs et l'écran OLED. Il contient aussi les dépendances requises à la compilation (bme280, tsl256x, ssd1306).

### Fonctionnement

La carte commence par générer un nombre aléatoire à l'aide de la fonction `keyGen()` de `protocole.h` puis l'envoie à l'autre carte. Elle attend ensuite le nombre généré par cette carte puis créé une clé commune avec la fonction `computeKey()` de `protocole.h`. Cette clé lui permettra plus tard de prouver son identité à la seconde carte. Ensuite, elle rentre dans une boucle où elle récupère chaque seconde les données des capteurs, envoie les données à la seconde carte, puis met à jour l'écran OLED. L'envoi des données se fait dans le format suivant: `<clé de session> <code> <valeur>` où code est un identifiant de la donnée mesurée (T pour température par exemple). Les données sont ensuite chiffrées avec la fonction `encrypt()` de `protocole.h`.\
Lors de la réception de données RF, si la session est déjà établie, la carte déchiffre les données avec la fonction `encrypt()` (A XOR B = C et C XOR B = A), vérifie que la clé de reçue est correcte, puis met à jour une variable globale `order` correspondant à l'ordre d'affichage des données.

## Dossier passerelle_microbit

Ce dossier contient le code (main.cpp) de la carte Micro:bit connectée en série à la passerelle.

### Fonctionnement

D'abord, la carte attend de recevoir le premier nombre alétoire généré par la première carte, puis elle génère son nombre alétoire et l'envoie. Ensuite, si elle reçoit des données via RF et que la session est déjà établie, elle déchiffre les données reçues, puis elle teste si la clé de session reçue est correcte. Si tel est le cas, elle écrit la série de mesures dans le format suivant sur son interface série: `<code><mesure>...<code><mesure>\n\r`.\
Enfin, elle vérifie toutes les secondes si des données lui sont envoyées en série, et les retransmet à la première carte après les avoir chiffrées.

## Dossier protocole

Ce dossier contient la bibliothèque de fonctions écrites pour le protocole RF.

> :warning: Il est IMPERATIF d'inclure ces sources dans le même dossier que les fichiers main.cpp ainsi que les autres dépendances lors de la compilation. Nous avons fait le choix de placer ce code dans un dossier à part afin de ne pas créer de duplicata.
