import binascii
import struct
import functools


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


def deferred(func):
    @functools.wraps(func)
    def decorated(*args, **kwargs):
        deferrable = args[0]
        if deferrable.flushing:
            func(*args, **kwargs)
        else:
            deferrable.queue_call(func, args, kwargs)
    return decorated


class Deferrable:
    def __init__(self):
        self.calls = []
        self.flushing = False

    def queue_call(self, func, args, kwargs):
        self.calls.append((func, args, kwargs))

    def flush_calls(self):
        self.flushing = True
        for func, args, kwargs in self.calls:
            func(*args, **kwargs)
        self.flushing = False
