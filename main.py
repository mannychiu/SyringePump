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


class Syringe():
    def __init__(self, port, addr=b'\x01'):
        # default address is 1, default baudrate is 9600
        self.port = port
        self.addr = addr
        self.serial = serial.Serial(
            port=self.port, baudrate=9600, bytesize=8, stopbits=1, parity=serial.PARITY_EVEN)

    def send_command(self, b):
        flag = b"\xE9"
        addr = self.addr
        lenb = len(b).to_bytes(1, byteorder="little")
        first = bxor(innerXOR(b), bxor(addr, lenb))
        command = flag + addr + lenb + b + first
        print(command)
        self.serial.flushOutput()
        self.serial.write(command)
        self.serial.flushOutput()
        time.sleep(0.8)
        print(s.read_all())

    def run(self):
        send_command(b'CWX'+b'\x01')

    def stop(self):
        send_command(b'CWX'+b'\x02')

    def close(self):
        self.stop()
        self.serial.close()

    def reconnect(self):
        self.serial = serial.Serial(
            port=self.port, baudrate=9600, bytesize=8, stopbits=1, parity=serial.PARITY_EVEN)

    def setFlowRate(self, volume=2000, flowrate=100):
        # default volume to deliver is 20 ml, the unit of volume is 0.01ml. the unit of flowrate is 0.01 ml/min
        send_command(b'CWT'+b'\x01' + volume.to_bytes(2, byteorder='little') +
                     b'\x05'+flowrate.to_bytes(2, byteorder='little')+b'\x0C')

    def schedule(self, t, a5, a4, a3, a2, a1, a0):
        # t in sec, res in ml/min
        res = a5 * math.pow(t, 5) + a4 * math.pow(t, 4) + a3 * \
            math.pow(t, 3) + a2 * math.pow(t, 2) + a1 * t + a0
        if res > 9999:
            print("not allowed")
            return -1
        return int(res*100)

    def runWithSchedule(self, a5, a4, a3, a2, a1, a0, end_time):
        # end_time in sec
        start = time.time()
        onGoing = time.time() - start
        self.run()
        while onGoing <= end_time:
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
if __name__ == "__main__":
    sp = Syringe(port="/dev/ttyUSB0")
    sp.runWithSchedule(0, 0, 0, 0, -1.0/15.0, 10, end_time=120)
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
