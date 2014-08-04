import binascii
import struct

class SimpleEq:

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


def make_progressbar(steps):
    step = [0, 0]

    def do_step():
        step[0] += 1
        percent = int(step[0]/steps*10)
        if percent > step[1]:
            print("... {}/{} done".format(step[0], steps))
            step[1] = percent

    return do_step

def rgb_to_hex(*rgb):
    return "#" + binascii.hexlify(struct.pack('BBB', *rgb)).decode('ascii')
