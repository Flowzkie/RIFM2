
#Import 

import time 
from flask import Flask, jsonify, request, render_template, url_for, redirect 
import RPi.GPIO as GPIO
import board
import adafruit_dht

GPIO.setwarnings(False)
dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)
TRIG = 4
ECHO = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup (21, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)



#Flask

app = Flask(__name__)



#Main Homepage 
@app.route('/')
def index():
    return render_template('index.html')



#Real-Time
@app.route('/updateStat', methods =['GET','POST'])
def updateStatus():
 #Ultrasonic
   while True:
    
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)
    GPIO.output(TRIG,False)
    
    time.sleep(0.2)
    GPIO.output(TRIG,True)
    time.sleep(0.00001)
    GPIO.output(TRIG,False)
    while GPIO.input(ECHO)==0:
        pulse_start=time.time()
    while GPIO.input(ECHO)==1:
        pulse_end=time.time()
    pulse_duration=pulse_end-pulse_start
    distance=pulse_duration*17150
    distance=round(distance,2)
    print ("distance:",distance,"cm")
    time.sleep(2) 
    
      

#Temperature and Humidity
    while True:
        try:
         # Print the values to the serial port
            temperature_c = dhtDevice.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = dhtDevice.humidity
            print(
                "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                    temperature_f, temperature_c, humidity
                )
            )
        except RuntimeError as error:
         # Errors happen fairly often, DHT's are hard to read, just keep going
         print(error.args[0])
         time.sleep(2)
         continue
        except Exception as error:
         dhtDevice.exit()
         raise error
         
        time.sleep(2)

               
        if distance > 7:
            status = 'ABNORMALLY HIGH'
            pump = 'ON'
            GPIO.output(21,GPIO.HIGH)
            GPIO.output(26,GPIO.LOW)
            return jsonify(distance=distance,temperature_c=temperature_c,humidity=humidity, status=status,pump=pump)
            
        elif distance < 7 and distance > 6:
            status = 'NORMAL'
            pump = 'OFF'
            GPIO.output(21,GPIO.LOW)
            GPIO.output(26,GPIO.LOW)
            return jsonify(distance=distance,temperature_c=temperature_c,humidity=humidity, status=status,pump=pump)
        else:
            status = 'ABNORMALLY LOW'
            pump = 'ON'
            GPIO.output(26,GPIO.HIGH)
            GPIO.output(21,GPIO.LOW)
            return jsonify(distance=distance,temperature_c=temperature_c,humidity=humidity, status=status, pump=pump)
            
        

 

   
     



if __name__ == '__main__':
        app.run(host = '0.0.0.0', debug = True)

