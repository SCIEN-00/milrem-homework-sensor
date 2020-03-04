import socket

controller_IP = "127.0.0.1"
controller_port = 12345
sensor_port = 12345
bufferSize = 10

try:
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    s.bind((controller_IP, controller_port))
    print(f"UDP server up and listening")
    while True:
        # Received data format: (uint8 'sensor number', uint8 'value type', uint64 'reading') → payload length: 10B
        received_bytes = s.recvfrom(bufferSize)
        data = received_bytes[0]  # address = received_bytes[1]
        sensor_nr = data[0]
        value_type = data[1]
        sensor_reading = int.from_bytes(data[2:], byteorder='little')
        clientMsg = "sensor ID: {} type: {} value: {}".format(
            sensor_nr, value_type, sensor_reading)
        print(clientMsg)

except KeyboardInterrupt:
    print(f"Listening stopped.")
