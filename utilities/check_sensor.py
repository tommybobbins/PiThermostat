#!/usr/bin/python
import smbus
i2c_ch = 1
# TMP102 address on the I2C bus
i2c_address = 0x48
# Register addresses
reg_temp = 0x00
reg_config = 0x01
# Calculate the 2's complement of a number
def twos_comp(val, bits):
  if (val & (1 << (bits - 1))) != 0:
    val = val - (1 << bits)
  return val

# Read temperature registers and calculate Celsius
def read_temp():
  # Read temperature registers
  val = bus.read_i2c_block_data(i2c_address, reg_temp, 2)
  temp_c = (val[0] << 4) | (val[1] >> 5)
  # Convert to 2s complement (temperatures can be negative)
  temp_c = twos_comp(temp_c, 12)
  # Convert registers value to temperature (C)
  temp_c = temp_c * 0.0625
  return temp_c

# Initialize I2C (SMBus)
bus = smbus.SMBus(i2c_ch)
# Read the CONFIG register (2 bytes)
val = bus.read_i2c_block_data(i2c_address, reg_config, 2)
# Set to 4 Hz sampling (CR1, CR0 = 0b10)
val[1] = val[1] & 0b00111111
val[1] = val[1] | (0b10 << 6)
# Write 4 Hz sampling back to CONFIG
bus.write_i2c_block_data(i2c_address, reg_config, val)
# Read CONFIG to verify that we changed it
val = bus.read_i2c_block_data(i2c_address, reg_config, 2)


temperature = read_temp()
print(round(temperature, 2), "C")
