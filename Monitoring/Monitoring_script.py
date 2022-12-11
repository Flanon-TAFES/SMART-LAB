# user library
import sys
import time
import bme280

# influx configuration
from influxdb import InfluxDBClient

ifuser = "grafana"
ifpass = "Flanon"
ifdb = "home"
ifhost = "127.0.0.1"
ifport = 8086

cnt = 0

while cnt <= 10:
    cnt += 1

    # read enviroment data
    outtemp, pressure, humidity = bme280.readBME280All()

    time.sleep(1)
    print(time.strftime("%Y/%m/%d-%H:%M:%S;") + ("[%8d]: T:%3.2f, P:%5.2f, H:%3.2f" %(cnt, float(outtemp), float(pressure), float(humidity))))
    # o.write (("%16.8f;%16.8f;%3.1f;%4.3f;\r\n" % (float(data),float(reflevel),float(temp),float(ppm))))
    # o.close()

    # convert json data to point
    body = [
        {
            "measurement": "environment",
            "fields": {
                "outtemp": float(outtemp),
                "pressure": float(pressure),
                "humidity": float(humidity)
            }
        }
    ]

    # connect to influxdb
    ifclient = InfluxDBClient(ifhost, ifport, ifuser, ifpass, ifdb)

    # write the measurement
    ifclient.write_points(body)

