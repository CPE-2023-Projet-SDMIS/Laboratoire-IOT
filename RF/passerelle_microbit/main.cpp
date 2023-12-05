/*
The MIT License (MIT)

Copyright (c) 2016 British Broadcasting Corporation.
This software is provided by Lancaster University by arrangement with the BBC.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
*/

#include "MicroBit.h"
#include "protocole.h"
#include <string>
#include <map>

MicroBit uBit;

bool session = false;
std::string sessionKey;

// Gestion des données reçues en série
void serialDataReceived(){

    // Si la session est OK et qu'on reçoit des données, on les transmert à l'autre carte
    if (session == true) {
        ManagedString s = uBit.serial.read(uBit.serial.getRxBufferSize(), ASYNC);
        
        if (s.length() > 0)
        {
            std::string plain = sessionKey + " " + s.toCharArray();
            std::string toSend = encrypt(plain);
            uBit.radio.datagram.send(toSend.c_str());
        }
    }
}

// Gestion des données reçues en RF
void onData(MicroBitEvent)
{
    // Si la session est OK on déchiffre les données reçues sinon on met en place la session
    if (session == true){
        ManagedString s = uBit.radio.datagram.recv();

        // Dechiffrement des données
        std::string encryptedData = s.toCharArray();
        std::string decryptedData = encrypt(encryptedData);

        std::string rcvKey = decryptedData.substr(0, 11);

        // Test si sessionKey OK => on envoie les données en série
        if(strcmp(rcvKey.c_str(), sessionKey.c_str()) ==0) {
            std::string code = decryptedData.substr(12, 1);
            std::string data = decryptedData.substr(14);
            if (code == "w") {
                data = "\n\r";
                uBit.serial.printf(data.c_str());
            } else {
                uBit.serial.printf(code.c_str());
                uBit.serial.printf(data.c_str());
            }
        }
        
    } else {
        session = true;
        ManagedString s = uBit.radio.datagram.recv();

        int key1 = keyGen(&uBit);
        std::string key1Str = to_string(key1);

        std::string key2Str(s.toCharArray());
        sessionKey = computeKey(&uBit, s.toCharArray(), key1Str);

        uBit.sleep(1000);
        uBit.radio.datagram.send(key1Str.c_str());
    }

}

int main()
{
    // Initialise the micro:bit runtime.
    uBit.init();
    uBit.radio.enable();
    uBit.radio.setGroup(8);

    uBit.messageBus.listen(MICROBIT_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM, onData);
    uBit.serial.printf("Debut\n\r");

    // Check des données reçues en série toutes les secondes
    while (1)
    {
        serialDataReceived();
        uBit.sleep(1000);
    }
}
