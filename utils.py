class SimpleEq:

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

log_enabled = True

def log(msg, *args):
    if log_enabled:
        print(msg.format(*args))
