class Segment:

    def __init__(self, direction, step):
        self.direction = direction
        self.step = step

    def __str__(self):
        return 'Segment: (%s, %d)' % (self.direction, self.step)
