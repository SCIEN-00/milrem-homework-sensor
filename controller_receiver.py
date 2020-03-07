import socket, threading, time, sched, traceback, asyncio
from enum import IntEnum
from ctypes import *
from datetime import datetime
import threading


class ValueType(IntEnum):
    """Value data type identifier"""
    NONE = 0x0000
    FIELD_INT8 = 0x0001
    FIELD_INT16 = 0x0002
    FIELD_INT32 = 0x0003
    FIELD_INT64 = 0x0004
    FIELD_UINT8 = 0x0005
    FIELD_UINT16 = 0x0006
    FIELD_UINT32 = 0x0007
    FIELD_UINT64 = 0x0008
    FIELD_FLOAT = 0x0009
    FIELD_DOUBLE = 0x000A
    FIELD_CHARARRAY = 0x000B
    FIELD_CHAR = 0x000C
    FIELD_BOOL = 0x000D
    FIELD_EMCY = 0x000E


ValueTypeToCtype = {
    ValueType.FIELD_BOOL: c_bool,
    ValueType.FIELD_INT8: c_int8,
    ValueType.FIELD_INT16: c_int16,
    ValueType.FIELD_INT32: c_int32,
    ValueType.FIELD_INT64: c_int64,
    ValueType.FIELD_UINT8: c_uint8,
    ValueType.FIELD_UINT16: c_uint16,
    ValueType.FIELD_UINT32: c_uint32,
    ValueType.FIELD_UINT64: c_uint64,
    ValueType.FIELD_FLOAT: c_float,
    ValueType.FIELD_DOUBLE: c_double,
    ValueType.FIELD_CHAR: c_char
}

controller_IP = "127.0.0.1"
controller_port = 12345
sensor_port = 12345
bufferSize = 10
with open("sensor data.csv", "a+") as f:
    f.write("Date time,sensor ID,value\n")
now = datetime.now()
last_ten_que = [] * 10
sensors_last_readings = [[], [], [], [], [], [], [], [], [], []]
sensor_nr = 0


def average_of_ten():
    threading.Timer(1.0, average_of_ten).start()
    if len(sensors_last_readings[sensor_nr]) >= 10:
        print("Sensor ", sensor_nr, "average of ten is: ",
              sum(sensors_last_readings[sensor_nr]) / 10)
    return


def last_ten(s_nr, s_reading):
    global sensor_nr
    sensor_nr = s_nr
    sensors_last_readings[s_nr].append(s_reading)
    sensors_last_readings[s_nr] = sensors_last_readings[s_nr][-10:]
    #print(sensors_last_readings[s_nr])
    return


def listening():
    try:
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        s.bind((controller_IP, controller_port))
        average_of_ten()

        print(f"UDP server up and listening")
        while True:
            # Received data format: (uint8 'sensor number', uint8 'value type', uint64 'reading') → payload length: 10B
            received_bytes = s.recvfrom(bufferSize)
            data = received_bytes[0]  # address = received_bytes[1]

            sensor_nr = data[0]
            #value_type = ValueType(data[1]).name
            sensor_reading = int.from_bytes(data[2:], byteorder='little')

            threading.Thread(target=last_ten(sensor_nr, sensor_reading),
                             daemon=True).start
            with open("sensor data.csv", "a+") as f:
                f.write("{},{},{}".format(datetime.now(), sensor_nr,
                                          sensor_reading) + '\n')

    except (KeyboardInterrupt, SystemExit):
        print(f"Listening stopped.")
        exit()


if __name__ == '__main__':
    listening()
