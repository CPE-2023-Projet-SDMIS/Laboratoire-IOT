from flask import Flask, request, jsonify
from flata import Flata, where
from flata.storages import JSONStorage
import serial

app = Flask(__name__)

apikey = "9bppmxzljdR8Ry81S9KtOsZAFYzv8F"

def error(tittle):
    error = {
        "errors": [
            {
                "title":  f"{tittle}",
            }
        ]
    }

    return jsonify(error)

@app.get('/api/sensor/data/get')
def get_data():

    userkey = request.args.get('apikey')
    if userkey is None:
        return error("ApiKey parameter is missing")

    if userkey == apikey:

        db = Flata('data/db.json', storage=JSONStorage)
        sensor_data = db.table('sensor_data')

        data = sensor_data.search(where('id') == len(sensor_data))

        cle = list(data[0].keys())[0]

        ds = data[0][cle]
        res = {"sensors":[]}
        for cle, valeur in ds.items():
            if cle == "T":
                res["sensors"].append({
                    "type" : "temperature",
                    "data" : valeur
                })
            if cle == "L":
                res["sensors"].append({
                    "type" : "lumiere",
                    "data" : valeur
                })
            if cle == "H":
                res["sensors"].append({
                    "type" : "humidite",
                    "data" : valeur
                })
            if cle == "P":
                res["sensors"].append({
                    "type" : "pression",
                    "data" : valeur
                })

        return jsonify(res)
    else:
        return error("Invalid ApiKey")
    
@app.route('/api/order/new', methods=['POST'])
def new_order():

    data = request.get_json()  # Récupérer les données JSON de la requête

    print(data)
    port = '/dev/ttyACM0'
    baudrate = 115200

    try:
        # Ouvrir le port série
        ser = serial.Serial(port, baudrate)

        # Envoie la chaîne via la liaison série
        ser.write(data['order_setting'].encode())

    except serial.SerialException:
        print(f"Le port série {port} n'a pas pu être ouvert. Assurez-vous que le périphérique est correctement connecté.")
    
    return jsonify({'message': 'Données reçues avec succès!'})
    
    
if __name__ == "__main__":

    app.run(host='0.0.0.0', port=8080, debug=True)