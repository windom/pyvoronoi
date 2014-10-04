import binascii
import struct
import functools
import time


class SimpleEq:

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


def make_progressbar(steps, timeit=False):
    step = [0, 0]

    if timeit:
        ctime = time.time()
        times = [ctime, ctime]

    def do_step():
        step[0] += 1
        percent = int(step[0]/steps*10)
        if percent > step[1]:
            progress_msg = "... {}/{} done".format(step[0], steps)
            step[1] = percent

            if timeit:
                ctime = time.time()
                section_time = ctime - times[1]
                total_time = ctime-times[0]
                remaining_time = total_time * (steps-step[0])/step[0]
                times[1] = ctime

                progress_msg += "\t\t\t{:.2f} secs, {:.2f} secs remaining" \
                        .format(section_time, remaining_time)

            print(progress_msg)

            if timeit and step[0]== steps:
                print("Processing took {:.2f} seconds".format(ctime-times[0]))

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
