import pygame
import os
from config import Config

class UI:
    """Chịu trách nhiệm vẽ tất cả các thành phần giao diện."""
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Segoe UI", 30)
        self.title_font = pygame.font.SysFont("Segoe UI Bold", 36)
        try:
            self.button_font = pygame.font.SysFont("Segoe UI Symbol", 24)
        except pygame.error:
            self.button_font = pygame.font.SysFont(None, 30)
        
        self.images = {}
        self.images_loaded = self._load_images()
        self.panel_x = 800

    def _load_images(self):
        try:
            # Các file ảnh nằm trong thư mục Photos cùng thư mục với file script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            photos_dir = os.path.join(script_dir, 'Photos')  # Thêm dòng này để chỉ định thư mục ảnh
            def load_img(file_name, alpha=False):
                path = os.path.join(photos_dir, file_name)
                image = pygame.image.load(path)
                return image.convert_alpha() if alpha else image.convert()

            boat_img = load_img(Config.ASSETS['boat'], True)
            wood_img = load_img(Config.ASSETS['wood'], True)
            gate_img = load_img(Config.ASSETS['gate'], True)
            forest_img = load_img(Config.ASSETS['forest'])
            water_img = load_img(Config.ASSETS['water'])

            self.images['bg_forest'] = pygame.transform.scale(forest_img, (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
            self.images['bg_water'] = pygame.transform.scale(water_img, (Config.MAP_SIZE * Config.CELL_SIZE, Config.MAP_SIZE * Config.CELL_SIZE))
            self.images['gate'] = pygame.transform.scale(gate_img, (Config.CELL_SIZE, Config.CELL_SIZE))
            self.images[1] = {"H": {2: pygame.transform.scale(boat_img, (Config.CELL_SIZE * 2, Config.CELL_SIZE))}}
            self.images['wood'] = {
                "H": {
                    2: pygame.transform.scale(wood_img, (Config.CELL_SIZE * 2, Config.CELL_SIZE)),
                    3: pygame.transform.scale(wood_img, (Config.CELL_SIZE * 3, Config.CELL_SIZE)),
                    4: pygame.transform.scale(wood_img, (Config.CELL_SIZE * 4, Config.CELL_SIZE)),
                },
                "V": {
                    2: pygame.transform.rotate(pygame.transform.scale(wood_img, (Config.CELL_SIZE * 2, Config.CELL_SIZE)), 90),
                    3: pygame.transform.rotate(pygame.transform.scale(wood_img, (Config.CELL_SIZE * 3, Config.CELL_SIZE)), 90),
                }
            }
            return True
        except pygame.error as e:
            print(f"Lỗi tải hình ảnh: {e}. Chương trình sẽ dùng màu sắc thay thế.")
            return False

    def draw_board(self, board_state, board_config):
        if not board_state: return
        
        self.screen.blit(self.images.get('bg_forest', pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))), (0, 0))
        board_area = pygame.Rect(20, 20, Config.MAP_SIZE * Config.CELL_SIZE, Config.MAP_SIZE * Config.CELL_SIZE)
        self.screen.blit(self.images.get('bg_water', pygame.Surface(board_area.size)), board_area.topleft)

        for r in range(Config.MAP_SIZE):
            for c in range(Config.MAP_SIZE):
                rect = pygame.Rect(board_area.x + c * Config.CELL_SIZE, board_area.y + r * Config.CELL_SIZE, Config.CELL_SIZE, Config.CELL_SIZE)
                pygame.draw.rect(self.screen, (0, 0, 0, 50), rect, 1)
        
        exit_pixel_x = board_area.x + board_config.exit_pos[1] * Config.CELL_SIZE
        exit_pixel_y = board_area.y + board_config.exit_pos[0] * Config.CELL_SIZE
        exit_rect = pygame.Rect(exit_pixel_x, exit_pixel_y, Config.CELL_SIZE, Config.CELL_SIZE)
        self.screen.blit(self.images.get('gate', pygame.Surface(exit_rect.size)), exit_rect.topleft)

        drawn_cars = set()
        for r in range(Config.MAP_SIZE):
            for c in range(Config.MAP_SIZE):
                car_id = board_state[r + 1][c + 1]
                if car_id > 0 and car_id not in drawn_cars:
                    drawn_cars.add(car_id)
                    car_info = board_config.get_vehicle(car_id)
                    if not car_info: continue
                    
                    positions = [(r_pos, c_pos) for r_pos, row in enumerate(board_state) for c_pos, val in enumerate(row) if val == car_id]
                    if not positions: continue
                    
                    top_r, left_c = min(p[0] for p in positions) - 1, min(p[1] for p in positions) - 1
                    pixel_x, pixel_y = board_area.x + left_c * Config.CELL_SIZE, board_area.y + top_r * Config.CELL_SIZE

                    if self.images_loaded:
                        img_key = 1 if car_id == 1 else 'wood'
                        image_to_draw = self.images.get(img_key, {}).get(car_info.orientation, {}).get(car_info.length)
                        if image_to_draw: self.screen.blit(image_to_draw, (pixel_x, pixel_y))
                    else:
                        color = (255, 80, 80) if car_id == 1 else (139, 69, 19)
                        w = Config.CELL_SIZE * car_info.length if car_info.orientation == "H" else Config.CELL_SIZE
                        h = Config.CELL_SIZE if car_info.orientation == "H" else Config.CELL_SIZE * car_info.length
                        pygame.draw.rect(self.screen, color, (pixel_x, pixel_y, w, h))

    def draw_panel(self, game_state):
        panel_width = Config.SCREEN_WIDTH - self.panel_x
        panel_rect = pygame.Rect(self.panel_x, 0, panel_width, Config.SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, (210, 215, 220), panel_rect)
        pygame.draw.line(self.screen, (150, 150, 150), (self.panel_x, 0), (self.panel_x, Config.SCREEN_HEIGHT), 2)

        self.screen.blit(self.title_font.render("Map Selection", True, (0,0,0)), (self.panel_x + 40, 50))
        map_text = self.font.render(Config.MAPS[game_state['map_idx']], True, (50,50,50))
        self.screen.blit(map_text, map_text.get_rect(center=(self.panel_x + 190, 120)))
        
        self.screen.blit(self.title_font.render("Algorithm", True, (0,0,0)), (self.panel_x + 40, 150))
        algo_text = self.font.render(Config.ALGORITHMS[game_state['algo_idx']], True, (50,50,50))
        self.screen.blit(algo_text, algo_text.get_rect(center=(self.panel_x + 190, 220)))

        self.screen.blit(self.title_font.render("Statistics", True, (0,0,0)), (self.panel_x + 40, 380))
        status = game_state['solve_status']
        if status == 'solving':
            self.screen.blit(self.font.render("Calculating, please wait...", True, (200,100,0)), (self.panel_x + 40, 430))
        elif status == 'ready':
            self.screen.blit(self.font.render("Ready to solve.", True, (0,100,200)), (self.panel_x + 40, 430))
        elif status == 'failed':
            self.screen.blit(self.font.render(f"{Config.ALGORITHMS[game_state['algo_idx']]} cannot solve this map.", True, (220,50,50)), (self.panel_x + 40, 430))
        elif status == 'success':
            info = game_state['solve_info']
            mem = info['memory']
            mem_text = f"{mem/(1024*1024):.2f} MB" if mem > 1024*1024 else f"{mem/1024:.2f} KB" if mem > 1024 else f"{mem} B"
            lines = [
                f"Search Time: {info['time']:.4f} s", f"Memory Used: {mem_text}",
                f"States Explored: {info['states']:,}", f"Solution Steps: {info['steps']}",
                f"Current Step: {game_state['current_step']} / {info['steps']}"
            ]
            for i, line in enumerate(lines):
                self.screen.blit(self.font.render(line, True, (0,0,0)), (self.panel_x + 40, 430 + i * 40))

    def draw_buttons(self, buttons, game_state):
        for name, rect in buttons.items():
            has_solution = bool(game_state['solution_steps'])
            is_playback = name in ["Play", "Pause", "Reset", "Back", "Next"]
            disabled = (game_state['solve_status'] == 'solving') or (is_playback and not has_solution) or \
                       (name == "Pause" and not game_state['play_mode']) or (name == "Play" and game_state['play_mode'])
            
            color = (100, 180, 100) if name == "Solve" and not disabled else (180, 180, 180) if disabled else (230, 230, 230)
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, (100,100,100), rect, 2, border_radius=8)
            
            text_map = {"map_left":"◀", "map_right":"▶", "algo_left":"◀", "algo_right":"▶", "Back":"⏮", "Next":"⏭", "Play":"▶", "Pause":"⏸", "Reset":"↺"}
            label = self.button_font.render(text_map.get(name, name), True, (50,50,50) if disabled else (0,0,0))
            self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_slider(self, slider_rect, handle_y):
        if not slider_rect: return
        self.screen.blit(self.font.render("Speed", True, (0,0,0)), (slider_rect.centerx - 30, slider_rect.bottom + 15))
        pygame.draw.rect(self.screen, (180,180,180), slider_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100,100,100), slider_rect, 2, border_radius=5)
        handle_rect = pygame.Rect(0,0,40,15)
        handle_rect.center = (slider_rect.centerx, handle_y)
        pygame.draw.rect(self.screen, (100,120,200), handle_rect, border_radius=5)
        pygame.draw.rect(self.screen, (20,40,100), handle_rect, 2, border_radius=5)