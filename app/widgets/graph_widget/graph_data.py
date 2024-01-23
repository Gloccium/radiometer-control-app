class GraphData:
    def __init__(self, ax, offset, lines, lines_b):
        self.ax = ax
        self.lines = lines
        self.lines_b = lines_b
        self.offset = offset
        self.x1, self.y1, self.x2, self.y2 = [], [], [], []
        self.x1_b, self.y1_b, self.x2_b, self.y2_b = [], [], [], []
        self.first_full = False
        self.second_full = True
        self.is_first_iteration = True
        self.last_scaled_y_value = 0
