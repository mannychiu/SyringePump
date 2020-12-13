import serial
import time
import math


def bxor(b1, b2):  # use xor for bytes
    result = bytearray()
    for b1, b2 in zip(b1, b2):
        result.append(b1 ^ b2)
    return result


def innerXOR(b):
    first = b[0]
    for byte in b[1:]:
        first ^= byte
    return bytes([first])


def send_command(s, b):
    flag = b"\xE9"
    addr = b"\x02"
    lenb = len(b).to_bytes(1, byteorder="little")
    first = bxor(innerXOR(b), bxor(addr, lenb))
    command = flag + addr + lenb + b + first
    print(command)
    s.flushOutput()
    s.write(command)
    s.flushOutput()
    time.sleep(0.8)
    print(s.read_all())
    return


class Syringe():
    def __init__(self, port):
        self.port = port
        self.serial = serial.Serial(
            port=self.port, baudrate=9600, bytesize=8, stopbits=1, parity=serial.PARITY_EVEN)

    def run(self):
        send_command(self.serial, b'CWX'+b'\x01')

    def stop(self):
        send_command(self.serial, b'CWX'+b'\x02')

    def close(self):
        self.serial.close()

    def reconnect(self):
        self.serial = serial.Serial(
            port=self.port, baudrate=9600, bytesize=8, stopbits=1, parity=serial.PARITY_EVEN)

    def setFlowRate(self, volume=2000, flowrate=100):
        # default volume to purge is 20 ml, the unit of flowrate is 0.01 ml/min
        send_command(self.serial, b'CWT'+b'\x01' +
                     volume.to_bytes(2, byteorder='little')+b'\x05'+flowrate.to_bytes(2, byteorder='little')+b'\x0C')

    def schedule(self, t, a5, a4, a3, a2, a1, a0):
        res = a5 * math.pow(t, 5) + a4 * math.pow(t, 4) + a3 * \
            math.pow(t, 3) + a2 * math.pow(t, 2) + a1 * t + a0
        if res > 9999:
            print("not allowed")
            return -1
        return int(res*100)

    def runWithSchedule(self, a5, a4, a3, a2, a1, a0):
        start = time.time()
        onGoing = time.time() - start
        self.run()
        while onGoing <= 120:
            rate = self.schedule(onGoing, a5, a4, a3, a2, a1, a0)
            if rate > 0:
                print(rate)
                self.setFlowRate(flowrate=rate)
            else:
                print("rate is less than 0")
                break
            onGoing = time.time() - start
        self.stop()


# Open serial port
# s = serial.Serial('/dev/ttyACM0',115200)
if __name__ == "__main__":
    sp = Syringe(port="/dev/ttyUSB0")
    sp.runWithSchedule(0, 0, 0, 0, -1.0/15.0, 10)
    # sp.setFlowRate(volume=6000, flowrate=1000)  # unit = 0.01ml/min
    # time.sleep(2)
    # sp.run()
   # time.sleep(60)  # unit=s
   # sp.run()
    # time.sleep(2)
   # sp.setFlowRate(flowrate=200)  # unit = 0.01ml/min
   # time.sleep(5)  # unit=s
   # sp.setFlowRate(flowrate=300)  # unit = 0.01ml/min
   # time.sleep(5)  # unit=s
   # sp.setFlowRate(flowrate=400)  # unit = 0.01ml/min
   # time.sleep(5)  # unit=s
   # sp.setFlowRate(flowrate=500)  # unit = 0.01ml/min
   # time.sleep(3)  # unit=s
    # sp.stop()
    sp.close()

# Wake up
