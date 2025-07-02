import pygame
import os
import time
import psutil
import solvers # Import module solvers của bạn

# --- CẤU HÌNH TOÀN CỤC ---
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
ASSETS_DIR = "Photos"
ASSETS = {
    'boat': 'boat.png', 'wood': 'wood.png', 'gate': 'gate.png',
    'forest': 'forest.png', 'water': 'water.png'
}

# Danh sách các map và thuật toán
MAPS = ["Map 1", "Map 2", "Map 3", "Map 4", "Map 5", "Map 6", "Map 7", "Map 8", "Map 9", "Map 10"]
ALGORITHMS = ["BFS", "DFS", "UCS", "A*"]


class UI:
    """Chịu trách nhiệm vẽ tất cả các thành phần giao diện."""
    def __init__(self, screen, state):
        self.screen = screen
        self.state = state
        self.panel_x = 800

        self.font = pygame.font.SysFont("Segoe UI", 30)
        self.title_font = pygame.font.SysFont("Segoe UI Bold", 36)
        try:
            self.button_font = pygame.font.SysFont("Segoe UI Symbol", 24)
        except pygame.error:
            self.button_font = pygame.font.SysFont(None, 30)
        
        self.images = {}
        self.images_loaded = self._load_images()
        self._setup_ui_elements()

    def _load_images(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            assets_path = os.path.join(script_dir, ASSETS_DIR)
            
            def load_img(file_name, alpha=False):
                path = os.path.join(assets_path, file_name)
                image = pygame.image.load(path)
                return image.convert_alpha() if alpha else image.convert()

            boat_img = load_img(ASSETS['boat'], True)
            wood_img = load_img(ASSETS['wood'], True)
            gate_img = load_img(ASSETS['gate'], True)
            forest_img = load_img(ASSETS['forest'])
            water_img = load_img(ASSETS['water'])

            self.images['bg_forest'] = pygame.transform.scale(forest_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.images['bg_water'] = pygame.transform.scale(water_img, (MAP_SIZE * CELL_SIZE, MAP_SIZE * CELL_SIZE))
            self.images['gate'] = pygame.transform.scale(gate_img, (CELL_SIZE, CELL_SIZE))
            self.images[1] = {"H": {2: pygame.transform.scale(boat_img, (CELL_SIZE * 2, CELL_SIZE))}}
            self.images['wood'] = {
                "H": {l: pygame.transform.scale(wood_img, (CELL_SIZE * l, CELL_SIZE)) for l in [2, 3, 4]},
                "V": {l: pygame.transform.rotate(pygame.transform.scale(wood_img, (CELL_SIZE * l, CELL_SIZE)), 90) for l in [2, 3]}
            }
            return True
        except pygame.error as e:
            print(f"Lỗi tải hình ảnh: {e}. Chương trình sẽ dùng màu sắc thay thế.")
            return False

    def _setup_ui_elements(self):
        px = self.panel_x
        PANEL_PADDING_X, PANEL_PADDING_Y, GROUP_SPACING, ELEMENT_SPACING = 25, 40, 60, 15
        self.buttons = {}
        current_y = PANEL_PADDING_Y

        self.map_title_pos = (px + PANEL_PADDING_X, current_y)
        current_y += 45
        self.map_text_pos = (px + (SCREEN_WIDTH - px) / 2, current_y + ELEMENT_SPACING)
        self.buttons["map_left"] = pygame.Rect(px + PANEL_PADDING_X, current_y, 40, 40)
        self.buttons["map_right"] = pygame.Rect(SCREEN_WIDTH - PANEL_PADDING_X - 40, current_y, 40, 40)
        current_y += GROUP_SPACING

        self.algo_title_pos = (px + PANEL_PADDING_X, current_y)
        current_y += 45
        self.algo_text_pos = (px + (SCREEN_WIDTH - px) / 2, current_y + ELEMENT_SPACING)
        self.buttons["algo_left"] = pygame.Rect(px + PANEL_PADDING_X, current_y, 40, 40)
        self.buttons["algo_right"] = pygame.Rect(SCREEN_WIDTH - PANEL_PADDING_X - 40, current_y, 40, 40)
        current_y += GROUP_SPACING + 10

        self.buttons["Solve"] = pygame.Rect(px + PANEL_PADDING_X, current_y, (SCREEN_WIDTH - px) - 2 * PANEL_PADDING_X, 50)
        current_y += GROUP_SPACING + 20

        self.stats_title_pos = (px + PANEL_PADDING_X, current_y)
        self.stats_start_y = current_y + 50
        
        controls_y = SCREEN_HEIGHT - 160
        controls = ["Back", "Play", "Pause", "Next", "Reset"]
        control_button_width = 50
        total_controls_width = len(controls) * control_button_width + (len(controls) - 1) * 10
        start_x = px + ((SCREEN_WIDTH - px) - total_controls_width) / 2 + 20
        for i, name in enumerate(controls):
            self.buttons[name] = pygame.Rect(start_x + i * (control_button_width + 10), controls_y, control_button_width, 40)

        slider_y = controls_y + 60
        self.slider_rect = pygame.Rect(start_x, slider_y, total_controls_width, 20)
        pos_ratio = (self.state.step_delay - MIN_DELAY) / (MAX_DELAY - MIN_DELAY)
        self.slider_handle_x = self.slider_rect.left + (1 - pos_ratio) * self.slider_rect.width

    def draw(self):
        self.draw_board()
        self.draw_panel()
        self.draw_buttons()
        self.draw_slider()

    def draw_board(self):
        current_state_obj = self.state.current_state
        board_config = self.state.board

        self.screen.blit(self.images.get('bg_forest'), (0, 0))
        area = pygame.Rect(20, 20, CELL_SIZE * MAP_SIZE, CELL_SIZE * MAP_SIZE)
        self.screen.blit(self.images.get('bg_water', pygame.Surface(area.size)), area.topleft)

        for r in range(MAP_SIZE):
            for c in range(MAP_SIZE):
                pygame.draw.rect(self.screen, (0, 0, 0, 50), (area.x + c * CELL_SIZE, area.y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

        exit_x = area.x + (board_config.goal_position[1] - 1) * CELL_SIZE
        exit_y = area.y + (board_config.goal_position[0] - 1) * CELL_SIZE
        self.screen.blit(self.images.get('gate', pygame.Surface((CELL_SIZE, CELL_SIZE))), (exit_x, exit_y))

        for v in current_state_obj.objects.values():
            car_id = v.id
            top, left = min(v.positions)
            px, py = area.x + (left - 1)* CELL_SIZE, area.y + (top - 1) * CELL_SIZE
            img_key = 1 if car_id == 1 else 'wood'
            orientation_key = "V" if v.orientation == 0 else "H"
            img = self.images.get(img_key, {}).get(orientation_key, {}).get(v.length)
            
            if img:
                self.screen.blit(img, (px, py))
            else:
                color = (255, 80, 80) if car_id == 1 else (139, 69, 19)
                w = CELL_SIZE * v.length if orientation_key == "H" else CELL_SIZE
                h = CELL_SIZE if orientation_key == "H" else CELL_SIZE * v.length
                pygame.draw.rect(self.screen, color, (px, py, w, h))

    def draw_panel(self):
        px = self.panel_x
        pygame.draw.rect(self.screen, (240, 240, 240), (px, 0, SCREEN_WIDTH - px, SCREEN_HEIGHT))
        pygame.draw.line(self.screen, (200, 200, 200), (px, 0), (px, SCREEN_HEIGHT), 1)

        self.screen.blit(self.title_font.render("Maps Selection", True, (0, 0, 0)), self.map_title_pos)
        map_text = self.font.render(MAPS[self.state.map_index], True, (50, 50, 50))
        self.screen.blit(map_text, map_text.get_rect(center=self.map_text_pos))

        self.screen.blit(self.title_font.render("Algorithms", True, (0, 0, 0)), self.algo_title_pos)
        algo_text = self.font.render(ALGORITHMS[self.state.algo_index], True, (50, 50, 50))
        self.screen.blit(algo_text, algo_text.get_rect(center=self.algo_text_pos))

        self.screen.blit(self.title_font.render("Statistics", True, (0, 0, 0)), self.stats_title_pos)
        info = self.state
        if info.status == 'success':
            mem = info.peak_memory
            mem_text = f"{mem/(1024*1024):.2f} MB" if mem > 1024*1024 else f"{mem/1024:.2f} KB"
            lines = [
                f"Search Time: {info.search_time:.4f} s", f"Memory Used: {mem_text}",
                f"States Explored: {info.num_expanded:,}", f"Solution Steps: {len(info.solution_path)-1}",
                f"Current Step: {info.current_step} / {len(info.solution_path)-1}"
            ]
        elif info.status == 'failed': lines = [f"{ALGORITHMS[info.algo_index]} failed to solve."]
        elif info.status == 'solving': lines = ["Solving... please wait"]
        else: lines = ["Ready to solve."]

        for i, line in enumerate(lines):
            self.screen.blit(self.font.render(line, True, (0, 0, 0)), (self.stats_title_pos[0], self.stats_start_y + i * 35))

    def draw_buttons(self):
        text_map = {"map_left":"◀", "map_right":"▶", "algo_left":"◀", "algo_right":"▶", "Back":"⏮", "Next":"⏭", "Play":"▶", "Pause":"⏸", "Reset":"↺"}
        for name, rect in self.buttons.items():
            disabled = self.state.status == 'solving' or \
                       (name in ["Play", "Pause", "Back", "Next", "Reset"] and not self.state.solution_path) or \
                       (name == "Play" and self.state.play_mode) or \
                       (name == "Pause" and not self.state.play_mode)
            
            color = (100, 180, 100) if name == "Solve" else (230, 230, 230)
            if disabled: color = (180, 180, 180)
            
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, (150, 150, 150), rect, 1, border_radius=8)
            
            text_color = (100, 100, 100) if disabled else (0, 0, 0)
            label = (self.font if name == "Solve" else self.button_font).render(text_map.get(name, name), True, text_color)
            self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_slider(self):
        if not self.slider_rect: return
        pos_ratio = (self.state.step_delay - MIN_DELAY) / (MAX_DELAY - MIN_DELAY)
        self.slider_handle_x = self.slider_rect.left + (1 - pos_ratio) * self.slider_rect.width

        pygame.draw.rect(self.screen, (200, 200, 200), self.slider_rect, border_radius=5)
        pygame.draw.rect(self.screen, (150, 150, 150), self.slider_rect, 1, border_radius=5)
        
        handle = pygame.Rect(0, 0, 15, 30); handle.center = (self.slider_handle_x, self.slider_rect.centery)
        pygame.draw.rect(self.screen, (100, 120, 200), handle, border_radius=5)
        pygame.draw.rect(self.screen, (20, 40, 100), handle, 1, border_radius=5)
        
        speed_label = self.font.render("Speed", True, (0, 0, 0))
        self.screen.blit(speed_label, speed_label.get_rect(midright=(self.slider_rect.left - 15, self.slider_rect.centery)))

class GameState:
    """Quản lý tất cả trạng thái và logic của một phiên chơi."""
    def __init__(self, game_map, map_index=0, algo_index=3): # Mặc định A*
        self.map_index = map_index
        self.algo_index = algo_index
        self.step_delay = DEFAULT_STEP_DELAY
        
        self.solution_path = []
        self.current_step = 0
        self.play_mode = False
        self.status = 'ready'  # ready | solving | success | failed
        
        self.search_time = 0
        self.peak_memory = 0
        self.num_expanded = 0

        self.board = type('Board', (), {'goal_position': self._find_goal_position(game_map)})()
        self.current_state = solvers.State(game_map, solvers.get_objects_info(game_map))

    def _find_goal_position(self, game_map):
        for i, row in enumerate(game_map):
            for j, val in enumerate(row):
                if val == -2: return (i, j)
        return (-1, -1)

    def solve(self):
        """Chạy thuật toán giải và cập nhật trạng thái."""
        solution_path, expanded_nodes, search_time, memory_used = solvers.solve(self.current_state.game_map, ALGORITHMS[self.algo_index])
        
        if solution_path:
            self.solution_path = solution_path
            self.status = 'success'
            self.current_step = 0
            self.current_state = self.solution_path[0]
            self.search_time = search_time
            self.peak_memory = memory_used
            self.num_expanded = expanded_nodes
        else:
            self.solution_path = []
            self.status = 'failed'
