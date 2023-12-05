#include "MicroBit.h"
#include "bme280.h"
#include "tsl256x.h"
#include "ssd1306.h"
#include "protocole.h"
#include <string>
#include <map>

MicroBit uBit;

// I2C
MicroBitI2C i2c(I2C_SDA0,I2C_SCL0);
MicroBitPin P1(MICROBIT_ID_IO_P1, MICROBIT_PIN_P1, PIN_CAPABILITY_DIGITAL_OUT);
ssd1306 screen(&uBit, &i2c, &P1);

// Gestion de la session
bool isSessionOk = false;
ManagedString key2;
std::string session;

// Gestion de l'ordre d'affichage
std::string order = "TLHP";

// Réception de la clé 2 et gestion de l'ordre d'affichage sur l'écran
void onData(MicroBitEvent) {

    // Si on a pas de session c'est qu'on a reçu la seconde clé
    if(!isSessionOk) {
        key2 = uBit.radio.datagram.recv();
        uBit.serial.printf("Meteo key 2 received: %s\r\n", key2.toCharArray());
        isSessionOk = true;
    } else { // Sinon c'est une maj de l'ordre => déchiffrement des données
        ManagedString s = uBit.radio.datagram.recv();
        std::string decryptedData = encrypt(s.toCharArray());
        std::string rcvKey = decryptedData.substr(0, 11);

        uBit.serial.printf("Meteo data received: %s\r\n", decryptedData.c_str());

        // Test si sessionKey OK => on maj l'ordre
        if(strcmp(rcvKey.c_str(), session.c_str()) == 0) {
            uBit.serial.printf("Meteo order received: %s\r\n", decryptedData.c_str());
            order = decryptedData.substr(12);
        } else {
            uBit.serial.printf("Meteo data received but wrong key: %s\r\n", s.toCharArray());
        }
    }

}

// Affiche les données sur l'écran et les envoie par RF
void display_rf_loop(bme280 bme, tsl256x tsl, std::string order) {

    screen.clear();

    // INIT BME
    uint32_t pressure = 0;
    int32_t temp = 0;
    uint16_t humidite = 0;

    // Init TSL
    uint16_t comb =0;
    uint16_t ir = 0;
    uint32_t lux = 0;

    // Récupération des valeurs
    bme.sensor_read(&pressure, &temp, &humidite);
    int tempInt = bme.compensate_temperature(temp);
    int pressInt = bme.compensate_pressure(pressure)/100;
    int humiInt = bme.compensate_humidity(humidite);
    tsl.sensor_read(&comb, &ir, &lux);

    // Récupération de l'ordre
    int tempOrder = order.find('T') + 1;
    int humOrder = order.find('H') + 1;
    int pressOrder = order.find('P') + 1;
    int lumOrder = order.find('L') + 1;

    // Affichage BME
    ManagedString line = "Temp:" + ManagedString(tempInt/100) + "." + ManagedString(tempInt%100) +" C\r\n";
    screen.display_line(tempOrder,0,line.toCharArray());

    line = "Humi:" + ManagedString(humiInt/100) + "." + ManagedString(humiInt%100)+" rH\r\n";
    screen.display_line(humOrder,0,line.toCharArray());

    line = "Press:" + ManagedString(pressInt) +" hPa\r\n";
    screen.display_line(pressOrder,0,line.toCharArray());

    // Affichage TSL
    line = "Lux:" + ManagedString((int)lux) + "\r\n";
    screen.display_line(lumOrder,0,line.toCharArray());

    // Send data
    char tempChar = 'T';
    char lumChar = 'L';
    char humChar = 'H';
    char pressChar = 'P';

    map<char, std::string> data;

    data[tempChar] = to_string(tempInt/100);
    data[lumChar] = to_string(lux);
    data[pressChar] = to_string(pressInt);
    data[humChar] = to_string(humiInt);
    uBit.serial.printf("Send data\r\n");

    sendRf(&uBit, session, data);

    // Update screen
    screen.update_screen();

}

int main() {

    // Init Micro:bit et capteurs
    uBit.init();
    uBit.radio.enable();
    uBit.radio.setGroup(8);
    bme280 bme(&uBit,&i2c);
    tsl256x tsl(&uBit,&i2c);

    // Met l'écran à 0
    screen.clear();
    screen.update_screen();

    // Génère la première clé
    int key1 = keyGen(&uBit);
    std::string key1Str = to_string(key1);
    uBit.serial.printf("Meteo key 1 generated: %d\r\n", key1);

    uBit.radio.datagram.send(key1Str.c_str());
    uBit.serial.printf("Meteo key 1 sent\r\nWaiting for key 2...\r\n");


    // Attend la clé pour initier la connection et l'ordre d'affichage si la session existe déjà
    uBit.messageBus.listen(MICROBIT_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM, onData);

    while(!isSessionOk) {
        uBit.serial.printf("Meteo still waiting...\r\n");
        uBit.sleep(1000);
    }

    // Connection ok
    uBit.serial.printf("Meteo connection ok\r\n");
    std::string key2Str(key2.toCharArray());
    session = computeKey(&uBit, key1Str, key2Str);
    uBit.serial.printf("Meteo session key: %s\r\n", session.c_str());

    // Boucle de traitement
    while(1) {

        // Affichage
        uBit.serial.printf("Meteo refresh screen\r\n");
        display_rf_loop(bme, tsl, order);
        uBit.sleep(1000);
    }

    release_fiber();
}
