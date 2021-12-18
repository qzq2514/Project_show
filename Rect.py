class Rect():
    def __init__(self, name, xmin, ymin, xmax, ymax,
                 conf=0.0, mid_y = 0):
        self.name = name
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.conf = conf
        self.mid_y = (self.ymin + self.ymax) // 2
        self.area = (xmax-xmin) * (ymax-ymin)

