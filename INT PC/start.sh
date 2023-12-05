#!/bin/bash

# On se place dans le l'environnement virtuel python
source _env/bin/activate

# Lancer le script serial_listener.py
python3 read-micro-bit.py &

# Lancer l'API Flask avec la commande flask
python3 api.py