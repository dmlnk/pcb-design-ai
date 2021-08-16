import random
class Path:

    def __init__(self, start, end):
        self.segments = [] 
        self.start = start
        self.end = end
        self.color = '#%06x' % random.randint(0, 255 ** 3 - 1)

    def __str__(self):
        return 'Path from(%s, %s) to (%s, %s)\n' % (self.start.x, self.start.y, self.end.x, self.end.y)