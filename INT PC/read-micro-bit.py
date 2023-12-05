import serial
import re
from flata import Flata, where
from flata.storages import JSONStorage
import time

# Database
db = Flata('data/db.json', storage=JSONStorage)
sensor_data = db.table('sensor_data')

# Port série utilisé
port = '/dev/ttyACM0'

# Paramètres de la communication série
baudrate = 115200 

try:
    # Ouvrir le port série
    ser = serial.Serial(port, baudrate)

    while True:

        # Lire une ligne de données depuis le port série
        line = ser.readline().decode('utf-8').strip()

        resultat = {}

        # Expression régulière pour trouver des correspondances de lettres suivies de nombres
        matches = re.findall(r'([A-Z])(\d+)', line)

        # Vérifier le nombre de correspondances
        if len(matches) == 4:
            for match in matches:
                lettre = match[0]
                valeur = int(match[1])
                resultat[lettre] = valeur

            # Afficher la ligne de données lue
            print(resultat)

            date = time.time()

            # Ajouter des données au dictionnaire
            sensor_data.insert({f'{date}': resultat})

except serial.SerialException:
    print(f"Le port série {port} n'a pas pu être ouvert. Assurez-vous que le périphérique est correctement connecté.")
except KeyboardInterrupt:
    # Gérer l'interruption (Ctrl+C) pour fermer proprement le port série
    ser.close()
    print("Fermeture du port série.")