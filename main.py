import asyncio
from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
import logging
import logging
import struct
#import matplotlib.pyplot as plt
#import matplotlib.animation as animation
import random  # Replace this with your real data source
import datetime as dt
import threading
import numpy as np
import time
from datetime import datetime

logger = logging.getLogger(__name__)
UU_RESPIRATORY_UUID =  "d67b5503-a25c-4395-bd21-f92823d91442" 
#UU_TRIGGER_UUID = "84b45e35-140a-4d32-92c6-386d8bff160d"
BATTERY_LEVEL_UUID =    "00002A19-0000-1000-8000-00805f9b34fb"
SAMPLETIME = 16 #Freq: 16Mhz/8K OSR 128
MAC_SAADC = "DA:8C:38:0C:36:29" #"DA:88:4A:1C:07:70"
#MAC_TRIGGERBOX = "FB:41:2A:F4:5E:AA"

class uutrack_reader:
    
    def __init__(self):
        self.CSC = 0
        self.semaphore = asyncio.Semaphore(0)        
        self.counter = 0    
        self.starttime : time
        
    
    async def notification_handler(self, sender, data : bytearray):
        if self.counter == 0:
             self.starttime = time.time()                
        adc_values = struct.iter_unpack("<h", data)                
        for adc_value in adc_values:            #14 bit values            
            #if(self.counter % 100 == 0):            
            print(f'#: {self.counter:<8} time: {self.counter*SAMPLETIME:<8} value: {adc_value[0]:<8}')
            self.counter+=1            
            if(self.counter == 500):
                print("stopping, sample ended")
                self.semaphore.release()
                    
    def on_disconnect(self, client):
        print("ble disconnect detected")
        self.semaphore.release()
              
    async def makeconnectiontodevice(self, address : str, UUID : str, ble_lock : asyncio.Lock):
        async with ble_lock:
            client = BleakClient(address, disconnected_callback=self.on_disconnect, timeout=20)
            
            try:
                await client.connect()
                print("connected to device")
                await client.start_notify(UUID, self.notification_handler)
                await self.semaphore.acquire()
                    
            except Exception as e:
                print(e)
            finally:
                await client.disconnect()
                print(f'disconnected ')
    

class datacollector:    
    def __init__(self):
        self.task_triggerbox : asyncio.Task | None = None        
        self.ble_lock = asyncio.Lock()
    async def app(self):    
        the_reader = uutrack_reader()                
        await asyncio.create_task(the_reader.makeconnectiontodevice(MAC_SAADC, UU_RESPIRATORY_UUID, self.ble_lock))        

def ble_connect():
    collectior = datacollector()
    #asyncio.gather(*())
    asyncio.run(collectior.app())    

def main(): 
    t = threading.Thread(target=ble_connect)
    t.start()
    #plotter()

if __name__ == "__main__":    
    main()




