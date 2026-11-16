mask = 0xFE

class LSB:
    def __init__(self, x):
        self.state = x

    def bits(self, m):
        self.state = (self.state & mask) | m
        return self.state