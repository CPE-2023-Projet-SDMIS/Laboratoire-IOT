# Program to control passerelle between Android application
# and micro-controller through USB tty
import time
import argparse
import signal
import sys
import socket
import socketserver
import serial
import threading
import pymongo 
import json
from pymongo import MongoClient

HOST           = "0.0.0.0"
UDP_PORT       = 10000
MICRO_COMMANDS = ["TL" , "LT"]
FILENAME        = "values.txt"
LAST_VALUE      = ""

#data = " ".join(sys.argv[1:])

#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Envoyer les données JSON au client
#sock.sendto(data_json.encode("utf-8"), (HOST, UDP_PORT))

#print("Sent:     {}".format(data_json))

class MongoDBHandler():
        def write_to_mongodb(data):
            client = pymongo.MongoClient("mongodb://localhost:27017")
            db = client["Archi_IoT"]
            collection = db["DataSrv"]
            collection.insert_one({"data": data})
            client.close()

        def read_from_mongodb():
            client = pymongo.MongoClient("mongodb://localhost:27017")
            db = client["Archi_IoT"]
            collection = db["DataSrv"]
            document = collection.find_one({}, sort=[("_id", pymongo.DESCENDING)])
            client.close()
            if document:
                return document["data"]
            return ""



class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        current_thread = threading.current_thread()
        print("{}: client: {}, wrote: {}".format(current_thread.name, self.client_address, data))
        if data != "":
                        if data.decode("utf-8") in MICRO_COMMANDS: # Send message through UART
                                sendUARTMessage(data)         
                        elif data.decode("utf-8") == "getValues()": # Sent last value received from micro-controller
                                #Code de base
                                #socket.sendto(LAST_VALUE, self.client_address)
                                #Code test
                                # TODO: Create last_values_received as global variable    
                                # Créez un dictionnaire avec des données spécifiques
                                data_to_send = {
                                "temperature": 25.5,
                                "luminosite": 60.2,
                                "status": "OK"
                                }
                                # Convertissez le dictionnaire en chaîne JSON
                                LAST_VALUE = json.dumps(data_to_send)
                                # Envoyez la chaîne JSON au client
                                socket.sendto(LAST_VALUE.encode("utf-8"), self.client_address)  
                        else:
                                print("Unknown message: ",data.decode("utf-8"))

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


# send serial message 
SERIALPORT = ""
BAUDRATE = 115200
ser = serial.Serial()

def initUART():        
        # ser = serial.Serial(SERIALPORT, BAUDRATE)
        ser.port=SERIALPORT
        ser.baudrate=BAUDRATE
        ser.bytesize = serial.EIGHTBITS #number of bits per bytes
        ser.parity = serial.PARITY_NONE #set parity check: no parity
        ser.stopbits = serial.STOPBITS_ONE #number of stop bits
        ser.timeout = None          #block read

        # ser.timeout = 0             #non-block read
        # ser.timeout = 2              #timeout block read
        ser.xonxoff = False     #disable software flow control
        ser.rtscts = False     #disable hardware (RTS/CTS) flow control
        ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
        #ser.writeTimeout = 0     #timeout for write
        print ('Starting Up Serial Monitor')
        try:
                ser.open()
        except serial.SerialException:
                print("Serial {} port not available".format(SERIALPORT))
                exit()



def sendUARTMessage(msg):
    ser.write(msg)
    print("Message <" + msg + "> sent to micro-controller." )
    


# Main program logic follows:
if __name__ == '__main__':
        #initUART() Cette ligne est à décommenter après
        print ('Press Ctrl-C to quit.')

        server = ThreadedUDPServer((HOST, UDP_PORT), ThreadedUDPRequestHandler)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True

        try:
                server_thread.start()
                print("Server started at {} port {}".format(HOST, UDP_PORT))
                server_thread.join() #Ligne qu'il faut supprimer après
                #A décommenter plus tard
                '''
                while ser.isOpen() : 
                        # time.sleep(100)
                        if (ser.inWaiting() > 0): # if incoming bytes are waiting 
                                data_str = ser.read(ser.inWaiting()) 
                                # Convertir les données en format JSON
                                data_json = json.dumps({"message": data_str})
                                LAST_VALUE = data_json
                                MongoDBHandler.write_to_mongodb(data_json)
                '''
        except (KeyboardInterrupt, SystemExit):
                server.shutdown()
                server.server_close()
                ser.close()
                exit()