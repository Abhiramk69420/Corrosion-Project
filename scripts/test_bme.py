import bme280
import smbus2

port = 1
address = 0x76
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus,address)
data = bme280.sample(bus,address,calibration_params)

print("Temperature:", data.temperature)
print("Humidity:", data.humidity)
print("Pressure:",data.pressure)
