# BMP280 via I2C. De compensatie is de formule uit de Bosch-datasheet.
# main.py importeert dit bestand alleen als SIMULEER_SENSOR False is.

import struct
import time

REG_ID = 0xD0
REG_RESET = 0xE0
REG_CTRL = 0xF4
REG_CONFIG = 0xF5
REG_CALIB = 0x88
REG_DATA = 0xF7
CHIP_ID = 0x58


def compenseer(kalibratie, adc_t, adc_p):
    dig_t1, dig_t2, dig_t3, dig_p1, dig_p2, dig_p3, dig_p4, dig_p5, dig_p6, dig_p7, dig_p8, dig_p9 = kalibratie

    var1 = (adc_t / 16384.0 - dig_t1 / 1024.0) * dig_t2
    var2 = (adc_t / 131072.0 - dig_t1 / 8192.0) ** 2 * dig_t3
    t_fine = var1 + var2
    temperatuur = t_fine / 5120.0

    var1 = t_fine / 2.0 - 64000.0
    var2 = var1 * var1 * dig_p6 / 32768.0
    var2 = var2 + var1 * dig_p5 * 2.0
    var2 = var2 / 4.0 + dig_p4 * 65536.0
    var1 = (dig_p3 * var1 * var1 / 524288.0 + dig_p2 * var1) / 524288.0
    var1 = (1.0 + var1 / 32768.0) * dig_p1
    if var1 == 0.0:
        return temperatuur, 0.0

    druk = 1048576.0 - adc_p
    druk = (druk - var2 / 4096.0) * 6250.0 / var1
    var1 = dig_p9 * druk * druk / 2147483648.0
    var2 = druk * dig_p8 / 32768.0
    druk = druk + (var1 + var2 + dig_p7) / 16.0
    return temperatuur, druk / 100.0


class BMP280:
    def __init__(self, i2c, addr):
        self.i2c = i2c
        self.addr = addr
        ruw = i2c.readfrom_mem(addr, REG_CALIB, 24)
        self.kalibratie = struct.unpack("<HhhHhhhhhhhh", ruw)
        i2c.writeto_mem(addr, REG_RESET, b"\xb6")
        time.sleep(0.01)
        i2c.writeto_mem(addr, REG_CTRL, b"\x27")
        i2c.writeto_mem(addr, REG_CONFIG, b"\xa0")

    def lees(self):
        data = self.i2c.readfrom_mem(self.addr, REG_DATA, 6)
        adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        return compenseer(self.kalibratie, adc_t, adc_p)


def start(sda_pin, scl_pin):
    from machine import I2C, Pin

    i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=100000)
    for addr in (0x76, 0x77):
        try:
            if i2c.readfrom_mem(addr, REG_ID, 1)[0] != CHIP_ID:
                continue
        except OSError:
            continue
        return BMP280(i2c, addr)
    return None
