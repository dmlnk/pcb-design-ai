class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return 'Point: (%s, %s)' % (self.x, self.y)

    def __eq__(self, other):
        return True if (self.x == other.x and self.y == other.y) else False
