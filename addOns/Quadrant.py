

################## Galactic location ##################

class QuadrantSuperposition:
    def __init__(self, quadrants = []):
        self.__quadrants = quadrants
    
    def contains(self, x, y):
        for q in self.__quadrants:
            if q.contains(x, y):
                return True
        return False

class Quadrant:
    def __init__(self, x_range = [0,0], y_range = [0,0]):
        if len(x_range) != 2 or len(y_range) != 2:
            raise ValueError
        if x_range[0] > x_range[1] or y_range[0] > y_range [1]:
            print("Warning: Quadrant got at least one range in unexpected order")
        self.__min_x = x_range[0]
        self.__max_x = x_range[1]
        self.__min_y = y_range[0]
        self.__max_y = y_range[1]
    
    def contains(self, x, y):
        return x > self.__min_x and x < self.__max_x and y > self.__min_y and y < self.__max_y
        
    @property
    def min_x(self):
        return __min_x
        
    @property
    def max_x(self):
        return __max_x
        
    @property
    def min_y(self):
        return __min_y
        
    @property
    def max_y(self):
        return __max_y