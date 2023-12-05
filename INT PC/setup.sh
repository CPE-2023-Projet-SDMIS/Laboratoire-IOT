#!/bin/bash

# Initialisation environement virtuel
python3 -m venv _env

# On se place dans le l'environnement virtuel python
source _env/bin/activate

# On install toutes les dépendances python nécessaire
pip install -r requirements.txt