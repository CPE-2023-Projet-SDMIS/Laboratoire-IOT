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
import json
from pymongo import MongoClient

HOST           = "0.0.0.0"
UDP_PORT       = 10000
MICRO_COMMANDS = ["TL" , "LT"]
FILENAME        = "values.json"
LAST_VALUE      = ""

# Variables base de donnÃ©es MongoDB
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "votre_base_de_donnees"
MONGO_COLLECTION = "votre_collection"

client = MongoClient(MONGO_HOST, MONGO_PORT)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]



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
                                socket.sendto(LAST_VALUE, self.client_address)
                                '''
                                data_to_send = {
                                "temperature": 25.5,
                                "luminosite": 60.2,
                                "status": "OK"
                                }
                                # Convertissez le dictionnaire en chaîne JSON
                                LAST_VALUE = json.dumps(data_to_send)
                                # Envoyez la chaîne JSON au client
                                socket.sendto(LAST_VALUE.encode("utf-8"), self.client_address)
                                ''' 
                        else:
                                print("Unknown message: ",data.decode("utf-8"))

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    def run(self):
        server_thread = threading.Thread(target=self.serve_forever)
        server_thread.daemon = True

        try:
            server_thread.start()
            print("Server started at {} port {}".format(HOST, UDP_PORT))
            while ser.isOpen():
                if ser.inWaiting() > 0:
                    data_str = ser.read(ser.inWaiting())
                    f.write(data_str)
                    LAST_VALUE = data_str
                    #print(data_str)
        except (KeyboardInterrupt, SystemExit):
            self.shutdown()
            self.server_close()
            f.close()
            ser.close()
            exit()



# send serial message 
SERIALPORT = "COM5"
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
    data_to_send = json.dumps({'command': msg}) +"\n"
    data_to_send = data_to_send.encode('utf-8')
    ser.write(data_to_send)
    print("Message <" + msg + "> sent to micro-controller.")

    # Enregistrement MongoDB
    collection.insert_one({'command': msg, 'timestamp': time.time()})



# Main program logic follows:
if __name__ == '__main__':
        initUART()
        f= open(FILENAME,"a")
        print ('Press Ctrl-C to quit.')

        server = ThreadedUDPServer((HOST, UDP_PORT), ThreadedUDPRequestHandler)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True

        try:
                server_thread.start()
                print("Server started at {} port {}".format(HOST, UDP_PORT))
                while ser.isOpen() : 
    
                        # time.sleep(100)
                        if (ser.inWaiting() > 0): # if incoming bytes are waiting 
                                user_input = input("Please enter a character or a string: ") #Send input to uBit
                                sendUARTMessage(user_input)#Send input to uBit
                                data_str = ser.read(ser.inWaiting())
                                # f.write(data_str.decode('utf-8'))
                                LAST_VALUE = data_str
                                print(LAST_VALUE)
                        # if (ser.inWaiting() > 0): # if incoming bytes are waiting 
                        #         data_str = ser.read(ser.inWaiting()) 
                        #         # Convertir les données en format JSON
                        #         data_json = json.dumps({"message": data_str})
                        #         LAST_VALUE = data_json
                        #         MongoDBHandler.write_to_mongodb(data_json)
        except (KeyboardInterrupt, SystemExit):
                server.shutdown()
                server.server_close()
                ser.close()
                exit()