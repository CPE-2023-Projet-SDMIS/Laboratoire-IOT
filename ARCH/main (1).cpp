#include "MicroBit.h"
 
MicroBit uBit;
 
void onData(MicroBitEvent)
{
    ManagedString s = uBit.radio.datagram.recv();
    uBit.serial.send(s);
}
 
void onRx(MicroBitEvent)
{
    ManagedString rx = uBit.serial.read(2);
    uBit.display.scroll(rx);
    //uBit.radio.datagram.send(rx);
}
 
void serialDataReceived(){
 
    ManagedString s = uBit.serial.read(uBit.serial.getRxBufferSize(), ASYNC);
 
    if (s.length() > 0)
    {
        uBit.radio.datagram.send(s.toCharArray());
        if(s.toCharArray()=="LT")
        {
            uBit.display.scroll("LT");
        }
        else if(s.toCharArray()=="TL")
        {
            uBit.display.scroll("TL");
        }
        //uBit.display.scroll("TX");
    }
 
}
 
int main() {
    uBit.init();
    uBit.messageBus.listen(MICROBIT_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM, onData);
    uBit.serial.setRxBufferSize(uBit.serial.getRxBufferSize());//Buffer propre
    uBit.serial.eventOn("\n");
    uBit.messageBus.listen(MICROBIT_ID_SERIAL, MICROBIT_SERIAL_EVT_RX_FULL, onRx);
    uBit.radio.enable();
    uBit.radio.setGroup(12);
    while(1)
    {
        serialDataReceived();
        uBit.sleep(1000);
    }
 
    release_fiber();
}