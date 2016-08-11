#!/usr/bin/env python
import atexit
import itertools
import gc
import os
import json
import sys
import time
import datetime
import logging
import logging.config
import schedule
import socket
import select
import threading
from sense_hat import SenseHat
from pymongo import MongoClient
from pymongo.errors import PyMongoError


""" weather_station.py: application to measure temperature, humidity and
    pressure using a raspberry pi 3 with SenseHat I/O Card.
    It shall be located at /usr/local/bin/
"""

__author__ = "niklasad1"
__email__ = "niklasadolfsson1@gmail.com"
__date__ = "2016-08-30"
__status__ = "Finished, TODO: fix global variables"
__version__ = "1.0"


# global variables
sense = None
sock = None
m_local_client = None
db_local = None
logger = None


def read_sensors():
    global db_local
    logger.info('readsensor() threadid: {0}'
                .format(threading.current_thread()))
    obj = {
        "date": datetime.datetime.utcnow(),
        "temperature": sense.get_temperature(),
        "humidity": abs(sense.get_humidity()),
        "pressure": abs(sense.get_pressure())
    }
    try:
        db_local.volatile.insert_one(obj)
    except:
        logger.error('MongoDB insert() error')


def average_measurements():
    global db_local
    logger.info('average_measurements() threadid: {0}'
                .format(threading.current_thread()))
    measurements_dict = {}
    pipe = [
        {'$group': {
            '_id': None,
            'averageHumidity': {'$avg': '$humidity'},
            'averagePressure': {'$avg': '$pressure'},
            'averageTemperature': {'$avg': '$temperature'},
            'minHumidity': {'$min': '$humidity'},
            'minPressure': {'$min': '$pressure'},
            'minTemperature': {'$min': '$temperature'},
            'maxHumidity': {'$max': '$humidity'},
            'maxPressure': {'$max': '$pressure'},
            'maxTemperature': {'$max': '$temperature'}
        }}]

    for item in db_local.volatile.aggregate(pipeline=pipe):
        measurements_dict = item

    obj = {
        "date": datetime.datetime.utcnow(),
        "HumidityAverage": measurements_dict['averageHumidity'],
        "HumidityMax": measurements_dict['maxHumidity'],
        "HumidityMin": measurements_dict['minHumidity'],
        "PressureAverage": measurements_dict['averagePressure'],
        "PressureMax": measurements_dict['maxPressure'],
        "PressureMin": measurements_dict['minPressure'],
        "TemperatureAverage": measurements_dict['averageTemperature'],
        "TemperatureMax": measurements_dict['maxTemperature'],
        "TemperatureMin": measurements_dict['minTemperature'],
        "isSent": False
    }

    try:
        db_local.non_volatile.insert_one(obj)
    except:
        logger.error("Local MongoDB volatile insert()")

    # Erase temp DB
    try:
        db_local.volatile.drop()
    except:
        logger.error('MongoDB drop()')


def send_ext_db():
    global db_local
    logger.info('average_measurements() threadid: {0}'
                .format(threading.current_thread()))

    send_objs = [obj for obj in db_local.non_volatile.find()
                 if not obj['isSent']]
    if send_objs:
        try:
            with open('/etc/weatherstation/ws_config.json') as json_data:
                db_dict = json.load(json_data)
        except (OSError, IOError) as e:
                logger.error('External MongoDB credentials could not be \
                             parsed {0}'.format(e))
                return

        try:
            uri = db_dict["name"] + db_dict["user"] + ":" + db_dict["pwd"] + \
                  "@" + db_dict["url"]
            conn_ext = MongoClient(uri)
            db_ext = conn_ext.weatherstation.ws
        except PyMongoError as e:
            logger.error('Connection to external MongoDB failed: {0}'
                         .format(e))
            conn_ext.close()
            return

        for obj in send_objs:
            obj.pop('isSent', None)
            try:
                db_ext.insert_one(obj)
                db_local.non_volatile.update_one(
                    {'_id': obj['_id']},
                    {'$set': {'isSent': True}}
                )
            except PyMongoError as e:
                logger.error('obj {0} {1}'
                             .format(obj['_id'], e))
        conn_ext.close()


def LEDs_red():
    global sense
    for item in itertools.permutations(range(8), 2):
        sense.set_pixel(int(item[0]), int(item[1]), 255, 0, 0)


def LEDs_green():
    global sense
    for item in itertools.permutations(range(8), 2):
        sense.set_pixel(int(item[0]), int(item[1]), 0, 255, 0)


def init():
    global logger
    global sense
    global sock
    global db_local
    global m_client_local

    # init logger
    formatter = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=formatter, filename='/var/log/weatherstation',
                        level=logging.WARNING)
    logger = logging.getLogger('WeatherStationLogger')

    # Sensor Board
    try:
        sense = SenseHat()
        sense.low_light = True
        sense.clear()
        LEDs_green()
    except OSError:
        logger.error('SenseHat OSError: device not detected or I2C problem')
    except ValueError:
        logger.error('SenseHat ValueError', sys.exc_info()[0])
    except:
        logger.error('SenseHat Unexpected error:', sys.exc_info()[0])

    # UDP listening socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP,INET
        sock.setblocking(0)
        server_addr = ('localhost', 50000)  # tuple of IP addr and Port no
        sock.bind(server_addr)
        #  sock.listen(5)  # backlog is 5 connections
    except socket.error, (value, message):
        if sock:
            sock.close()
        logger.error('Socket error' + message)
    except:
        logger.error('Socket Unexpected error:', sys.exc_info()[0])

    # MongoDB Local
    try:
        m_client_local = MongoClient('localhost:27017')
        db_local = m_client_local.weatherstation
    except PyMongoError, e:
        logger.error('Local Mongodb error {0}' .format(e))

    schedule.every(1).seconds.do(run_thread, read_sensors)
    schedule.every(1).hour.do(run_thread, send_ext_db)
    schedule.every().day.at("23:59").do(run_thread, average_measurements)


@atexit.register
def exit_handler():
    global sense
    global sock
    global m_client_local
    global logger

    logger.info('GRACEFUL SHUTDOWN')
    schedule.clear()
    sense.clear()
    sock.close()
    m_client_local.close()
    del sense, sock, logger, m_client_local


def run_thread(func):
    try:
        j_thread = threading.Thread(name='periodic_thread', target=func)
        j_thread.start()
    except:
        logger.error('threading exception', sys.exc_info()[0])


def read_socket(socket):
    logger.info('read_socket() threadid: {0}'
                .format(threading.current_thread()))
    if(socket):
        udp_packet = [s.recv(1024) for s in socket]
        payload = udp_packet[0]
        logger.info('payload: {0}' .format(payload))

        if(payload.startswith('READ_DB_TO_USB /')):
            payload_list = payload.split()
            read_db_to_usb(payload_list[1])

        else:
            logger.warning('Incorrect payload format: {0}' .format(payload))
            return
    else:
        return


def read_db_to_usb(path):
    logger.info('read_db_to_usb() threadid: {0}'
                .format(threading.current_thread()))
    file_path = os.path.join(path, 'measurements.csv')
    status = False
    try:
        f = open(file_path, 'w+')
        os.chmod(file_path, 0o666)
        status = True
    except IOError as (errno, strerror):
            logger.error('I/O error({0}): {1}'.format(errno, strerror))
    except ValueError:
            logger.error('No valid integer in line')
    except:
            logger.error('Unexpected error:', sys.exc_info()[0])

    # file was opened correct continue
    if(status):
        try:
            e = threading.Event()
        except:
            logger.warning('Event could not be allocated')
        try:
            t = threading.Thread(name='copy_usb_thread', target=indicate_copy,
                                 args=(e, ))
            t.start()
        except:
            logger.warning('signal_copy thread could not be allocated')

        # no critical error if the threads could not be allocated
        f.write('Date\tHumidityAverage\tHumidityMax\tHumidityMin\t'
                'PressureAverage\tPressureMax\tPressureMin\t'
                'TemperatureAverage\tTemperatureMax\tTemperatureMin\n')
        for item in db_local.volatile.find():
            f.write(str(item['date']) + '\t' +
                    str(item['HumidityAverage']) + '\t' +
                    str(item['HumidityMax']) + '\t' +
                    str(item['HumidityMin']) + '\t' +
                    str(item['PressureAverage']) + '\t' +
                    str(item['PressureMax']) + '\t' +
                    str(item['PressureMin']) + '\t' +
                    str(item['TemperatureAverage']) + '\t' +
                    str(item['TemperatureMax']) + '\t' +
                    str(item['TemperatureMin']) + '\n')
        f.close()
        e.set()
    LEDs_green()


def indicate_copy(e):
    logger.info('signal_copy() threadid: {0}'
                .format(threading.current_thread()))
    bool = False
    while not e.isSet():
        if bool:
            LEDs_green()
        else:
            LEDs_red()
        time.sleep(0.2)
        bool = not bool


def main():
    init()
    gc.enable()
    while(True):
        schedule.run_pending()
        readable, writable, exceptional = select.select([sock], [], [], 1)
        read_socket(readable)


if __name__ == '__main__':
    main()
