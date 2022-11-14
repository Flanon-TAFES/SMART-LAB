#user library
import sys
import Gpib
import time
import bme280

# influx configuration
from influxdb import InfluxDBClient

ifuser = "grafana"
ifpass = "Flanon"
ifdb   = "home"
ifhost = "127.0.0.1"
ifport = 8086

#instrument
measurement_name = "HP3458A"
measurement_name2 = "HP34401A"

#from datetime import datetime
#time=datetime.now()

#instrument configuration
inst = Gpib.Gpib(0,24, timeout=60) # 3458A GPIB Address = 24
inst.clear()

inst2 = Gpib.Gpib(0,23, timeout=60) # 34401A GPIB Address = 23
inst2.clear()

#instrument setup
inst.write("PRESET NORM")
inst.write("OFORMAT ASCII")
inst.write("DCV 10")
inst.write("TARM HOLD")
inst.write("TRIG AUTO")
inst.write("NPLC 100")
inst.write("AZERO ON")
inst.write("LFILTER ON")
inst.write("NRDGS 1,AUTO")
inst.write("MEM OFF")
inst.write("END ALWAYS")
inst.write("NDIG 9")
inst.write("DISP OFF,\"  \"")

inst2.write("*RST")
inst2.write("VOLT:DC:NPLC 100")
inst2.write("DISP OFF")

cnt = 0
tread = 2
temp = 38.5
reflevel = 6.1682500 #7.18484700 #6.1682500
reflevel2 = 10.00000
ppm = 0

inst.write("TEMP?")
temp = float(inst.read())

while cnt <= 10000000:
    cnt+=1
    #with open('10v_3458_nplc100_mm_08451_opt002.csv', 'a') as o:
    tread = tread - 1
    
    #read internal temperature of 3458A
    if (tread == 0):
        tread = 100
        inst.write("TARM SGL,1")
        inst.write("TEMP?")
        temp = inst.read()

        #inst2.write("READ?")

    #if (tread % 5  == 0):
        #inst.write("BEEP")
    
    #trigger instrument
    inst.write("TARM SGL,1")
    inst2.write("READ?")
    
    #read instrument
    data = inst.read()
    data2 = inst2.read()
    
    #read enviroment data
    outtemp,pressure,humidity = bme280.readBME280All()
    
    #print data to terminal
    ppm = ((float(data) / reflevel)-1)*1E6

    ppm2 = ((float(data2) / reflevel2)-1)*1E6
    #inst.write("DISP OFF \"%3.3f ppm\"" % float(ppm))

    time.sleep(1)
    print (time.strftime("%Y/%m/%d-%H:%M:%S;") + ("[%8d]: %2.8f v, dev %4.4f ppm, T:%3.1f, T:%3.2f, P:%5.2f, H:%3.2f" % (cnt, float(data),float(ppm),float(temp),float(outtemp),float(pressure),float(humidity))))
    #o.write (("%16.8f;%16.8f;%3.1f;%4.3f;\r\n" % (float(data),float(reflevel),float(temp),float(ppm))))
    #o.close()
    print (time.strftime("%Y/%m/%d-%H:%M:%S;") + ("[%8d]: %2.8f v, dev %4.4f ppm, T:%3.2f, P:%5.2f, H:%3.2f" % (cnt, float(data2),float(ppm2),float(outtemp),float(pressure),float(humidity))))

    #convert json data to point
    body = [
        {
            "measurement": measurement_name,
            #"time": time,
            "fields": {
                "voltage": float(data),
                "ppmdev": float(ppm),
                "temp": float(temp),
                "outtemp": float(outtemp),
                "pressure": float(pressure),
                "humidity": float(humidity)
            }
        }
    ]

    body2 = [
        {
            "measurement": measurement_name2,
            #"time": time,
            "fields": {
                "voltage": float(data2),
                "ppmdev": float(ppm2),
                "outtemp": float(outtemp),
                "pressure": float(pressure),
                "humidity": float(humidity)
            }
        }
    ]

    # connect to influxdb
    ifclient = InfluxDBClient(ifhost,ifport,ifuser,ifpass,ifdb)

    # write the measurement
    ifclient.write_points(body)

    ifclient.write_points(body2)
