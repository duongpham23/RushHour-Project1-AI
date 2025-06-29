class Config:
    """Lớp tĩnh chứa tất cả các hằng số và cấu hình của game."""
    # Kích thước màn hình
    SCREEN_WIDTH, SCREEN_HEIGHT = 1250, 800
    
    # Thuộc tính bàn cờ
    MAP_SIZE = 6
    CELL_SIZE = 110
    
    # Tốc độ animation
    DEFAULT_STEP_DELAY = 500
    MIN_DELAY = 50
    MAX_DELAY = 1000

    # Tên file hình ảnh
    ASSETS = {
        'boat': 'boat.png', 'wood': 'wood.png', 'gate': 'gate.png',
        'forest': 'forest.png', 'water': 'water.png'
    }

    # Danh sách các map và thuật toán
    MAPS = ["Map 1", "Map 2", "Map 3", "Map 4", "Map 5", "Map 6", "Map 7", "Map 8"]
    ALGORITHMS = ["BFS", "DFS", "UCS", "A*"]

    # Cấu hình xe cho từng map
    CAR_CONFIGS = {
        1: {
            1: {"x": 0, "y": 2, "length": 2, "dir": "H"}, 2: {"x": 0, "y": 3, "length": 2, "dir": "H"},
            3: {"x": 1, "y": 4, "length": 2, "dir": "V"}, 4: {"x": 2, "y": 4, "length": 2, "dir": "H"},
            5: {"x": 2, "y": 5, "length": 2, "dir": "H"}, 6: {"x": 3, "y": 1, "length": 3, "dir": "V"},
            7: {"x": 4, "y": 1, "length": 3, "dir": "V"}, 8: {"x": 5, "y": 1, "length": 3, "dir": "V"},},
        2: {
            1: {"x": 0, "y": 2, "length": 2, "dir": "H"}, 2: {"x": 0, "y": 3, "length": 3, "dir": "H"},
            3: {"x": 1, "y": 4, "length": 2, "dir": "V"}, 4: {"x": 2, "y": 4, "length": 2, "dir": "H"},
            5: {"x": 2, "y": 5, "length": 2, "dir": "H"}, 6: {"x": 4, "y": 2, "length": 2, "dir": "V"},
            7: {"x": 4, "y": 0, "length": 2, "dir": "V"}, 8: {"x": 1, "y": 0, "length": 2, "dir": "V"},
            9: {"x": 6, "y": 2, "length": 3, "dir": "V"},},
        3: {
            1: {"x": 0, "y": 2, "length": 2, "dir": "H"}, 2: {"x": 4, "y": 4, "length": 2, "dir": "H"},
            3: {"x": 3, "y": 3, "length": 2, "dir": "V"}, 4: {"x": 4, "y": 0, "length": 3, "dir": "V"},},
        4: {
            1: {"x": 0, "y": 2, "length": 2, "dir": "H"}, 2: {"x": 0, "y": 3, "length": 4, "dir": "H"},
            3: {"x": 3, "y": 4, "length": 2, "dir": "H"}, 4: {"x": 3, "y": 5, "length": 2, "dir": "H"},
            5: {"x": 4, "y": 2, "length": 2, "dir": "V"}, 6: {"x": 4, "y": 0, "length": 2, "dir": "V"},
            7: {"x": 1, "y": 0, "length": 2, "dir": "V"}, 8: {"x": 6, "y": 2, "length": 3, "dir": "V"},},
        5: {
            1: {"x": 1, "y": 2, "length": 2, "dir": "H"}, 2: {"x": 1, "y": 3, "length": 2, "dir": "V"},
            3: {"x": 0, "y": 5, "length": 3, "dir": "H"}, 4: {"x": 0, "y": 0, "length": 3, "dir": "V"},
            5: {"x": 0, "y": 0, "length": 3, "dir": "H"}, 6: {"x": 1, "y": 1, "length": 2, "dir": "H"},
            7: {"x": 3, "y": 0, "length": 3, "dir": "V"}, 8: {"x": 3, "y": 3, "length": 2, "dir": "H"},
            9: {"x": 4, "y": 4, "length": 2, "dir": "V"}, 10: {"x": 5, "y": 2, "length": 3, "dir": "V"},
            11: {"x": 4, "y": 1, "length": 2, "dir": "H"},},
        6: {
            1: {"x": 0, "y": 2, "length": 2, "dir": "H"}, 2: {"x": 2, "y": 1, "length": 2, "dir": "V"},
            3: {"x": 3, "y": 3, "length": 2, "dir": "V"}, 4: {"x": 3, "y": 5, "length": 2, "dir": "H"},
            5: {"x": 1, "y": 4, "length": 2, "dir": "V"}, 6: {"x": 0, "y": 4, "length": 2, "dir": "V"},
            7: {"x": 5, "y": 4, "length": 2, "dir": "V"}, 8: {"x": 4, "y": 3, "length": 2, "dir": "H"},
            9: {"x": 4, "y": 0, "length": 3, "dir": "V"}, 10: {"x": 5, "y": 1, "length": 2, "dir": "V"},
            11: {"x": 6, "y": 1, "length": 3, "dir": "V"},},
        7: {
            1: {"x": 2, "y": 2, "length": 2, "dir": "H"}, 2: {"x": 1, "y": 2, "length": 2, "dir": "V"},
            3: {"x": 0, "y": 2, "length": 2, "dir": "V"}, 4: {"x": 1, "y": 0, "length": 2, "dir": "V"},
            5: {"x": 0, "y": 0, "length": 2, "dir": "H"}, 6: {"x": 4, "y": 0, "length": 2, "dir": "V"},
            7: {"x": 5, "y": 0, "length": 3, "dir": "V"}, 8: {"x": 6, "y": 0, "length": 2, "dir": "V"},
            9: {"x": 3, "y": 3, "length": 2, "dir": "V"}, 10: {"x": 4, "y": 4, "length": 2, "dir": "H"},
            11: {"x": 4, "y": 5, "length": 2, "dir": "H"}, 12: {"x": 0, "y": 4, "length": 2, "dir": "V"},},
        8: { 
            1: {"x": 2, "y": 2, "length": 2, "dir": "H"}, 2: {"x": 0, "y": 0, "length": 2, "dir": "H"},
            3: {"x": 4, "y": 1, "length": 2, "dir": "H"}, 4: {"x": 2, "y": 3, "length": 2, "dir": "H"},
            5: {"x": 3, "y": 4, "length": 2, "dir": "H"}, 6: {"x": 0, "y": 5, "length": 2, "dir": "H"},
            7: {"x": 0, "y": 2, "length": 2, "dir": "V"}, 8: {"x": 1, "y": 1, "length": 2, "dir": "V"},
            9: {"x": 2, "y": 4, "length": 2, "dir": "V"}, 10: {"x": 3, "y": 0, "length": 2, "dir": "V"},
            11: {"x": 4, "y": 2, "length": 2, "dir": "V"}, 12: {"x": 5, "y": 2, "length": 2, "dir": "V"},}
    }