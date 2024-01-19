class GraphData:
    def __init__(self, ax, lines, offset):
        self.ax = ax
        self.lines = lines
        self.offset = offset
        self.x1, self.y1, self.x2, self.y2 = [], [], [], []
        self.first_full = False
        self.second_full = True
        self.is_first_iteration = True
        self.last_scaled_y_value = 0
