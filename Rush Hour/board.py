from config import Config

class Vehicle:
    """Đại diện cho một xe (thuyền hoặc gỗ) trên bàn cờ."""
    def __init__(self, id, x, y, length, orientation):
        self.id = id
        self.x = x
        self.y = y
        self.length = length
        self.orientation = orientation

class Board:
    """Quản lý trạng thái của bàn cờ, bao gồm các xe và các thao tác."""
    def __init__(self, level):
        self.size = Config.MAP_SIZE
        self.vehicles = []
        self.exit_pos = (0, 0)
        self.exit_orientation = "H"
        self._load_level(level)

    def _load_level(self, level):
        """Tải cấu hình xe cho một màn chơi cụ thể."""
        config = Config.CAR_CONFIGS.get(level, Config.CAR_CONFIGS[1])
        self.vehicles = []
        for car_id, car_info in config.items():
            self.vehicles.append(Vehicle(car_id, car_info['x'], car_info['y'], car_info['length'], car_info['dir']))
        
        main_car = self.get_vehicle(1)
        if main_car:
            self.exit_orientation = main_car.orientation
            if self.exit_orientation == "H":
                self.exit_pos = (main_car.y, self.size)
            else:
                self.exit_pos = (self.size, main_car.x)

    def get_vehicle(self, vehicle_id):
        """Lấy một đối tượng Vehicle bằng ID."""
        for v in self.vehicles:
            if v.id == vehicle_id:
                return v
        return None

    def get_grid(self):
        """Tạo ra một ma trận 6x6 từ danh sách xe."""
        grid = [[0] * self.size for _ in range(self.size)]
        for v in self.vehicles:
            for i in range(v.length):
                row = v.y + (i if v.orientation == "V" else 0)
                col = v.x + (i if v.orientation == "H" else 0)
                if 0 <= row < self.size and 0 <= col < self.size:
                    grid[row][col] = v.id
        return grid

    def get_expanded_grid(self):
        """Tạo ra một ma trận 8x8 với viền bao quanh."""
        grid = self.get_grid()
        expanded = [[-1] * (self.size + 2) for _ in range(self.size + 2)]
        for r, row_data in enumerate(grid):
            for c, cell_val in enumerate(row_data):
                expanded[r + 1][c + 1] = cell_val
        
        exit_r, exit_c = self.exit_pos
        expanded_r, expanded_c = exit_r + 1, exit_c + 1
        if 0 <= expanded_r < self.size + 2 and 0 <= expanded_c < self.size + 2:
            expanded[expanded_r][expanded_c] = -2
        return expanded