import socket, threading, time, sched, traceback, asyncio
from enum import IntEnum
from ctypes import *
from datetime import datetime
import threading
from threading import Thread


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
sensor_port = 12346
bufferSize = 10
with open("sensor data.csv", "a+") as f:
    f.write("Date time,sensor ID,value\n")
now = datetime.now()
last_ten_que = [] * 10
sensors_last_readings = [[], [], [], [], [], [], [], [], [], []]
sensor_nr = 0
time_updated = None
incoming_time = None


def average_of_ten():
    threading.Timer(1.0, average_of_ten).start()
    global time_updated
    global incoming_time
    if len(sensors_last_readings[sensor_nr]
           ) >= 10 and time_updated == incoming_time:
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


class Packet(Structure):
    _pack_ = True
    _fields_ = [('sensor_id', c_uint8), ('kind', c_uint8)]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<Packet: sensor_id: {}, kind: {}".format(
            self.sensor_id, self.kind)


def request_info():
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    while True:
        try:
            requ = input(
            )  #insert format: "0...9"",""0...2" (sensor nr,requested data)
            #print("Input was: ", requ[0], requ[2])
            packet = Packet(sensor_id=int(requ[0]), type=int(requ[2]))
            bytes(packet)
            print("Sending", sizeof(packet), "B of data:", bytes(packet))
            s.sendto(bytes(packet), (controller_IP, sensor_port))
        except (KeyboardInterrupt):
            print("Sending requests disabled.")
            return


def listening():
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    s.bind((controller_IP, controller_port))
    average_of_ten()
    global time_updated
    global incoming_time

    print("UDP server up and listening")
    while True:
        try:
            # Received data format: (uint8 'sensor number', uint8 'value type', uint64 'reading') → payload length:     10B
            time_updated = datetime.now()
            received_bytes = s.recvfrom(bufferSize)
            incoming_time = datetime.now(
            )  # get the time when data was acquired
            time_updated = incoming_time
            data = received_bytes[0]  # address = received_bytes[1]
            sensor_nr = data[0]
            #value_type = ValueType(data[1]).name
            sensor_reading = int.from_bytes(data[2:], byteorder='little')

            threading.Thread(target=last_ten(sensor_nr, sensor_reading),
                             daemon=True).start
            with open("sensor data.csv", "a+") as f:
                f.write("{},{},{}".format(incoming_time, sensor_nr,
                                          sensor_reading) + '\n')
        except (KeyboardInterrupt, SystemExit):
            print(f"Listening stopped.")
            exit()


if __name__ == '__main__':
    Thread(target=listening).start()
    Thread(target=request_info).start()
