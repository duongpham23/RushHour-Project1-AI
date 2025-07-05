# filepath: d:\Documents\VSCode\Cơ sở AI\Rush hour github\RushHour-Project1-AI\Source\main.py
import pygame
import sys
import os
import json
import gui
import solvers
import time
import threading

def load_all_maps_from_file(filename="maps.txt"):
    """Tải tất cả các map từ một file JSON duy nhất."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    maps_file_path = os.path.join(script_dir, "Map", filename)
    
    try:
        with open(maps_file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)
        # Giả sử file JSON là một list, mỗi phần tử có key "data" chứa ma trận map
        all_maps = [map_item["data"] for map_item in data]
        return all_maps
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file map tại '{maps_file_path}'")
        return None
    except (json.JSONDecodeError, KeyError, TypeError):
        print(f"Lỗi: File map '{maps_file_path}' có cấu trúc không hợp lệ hoặc không phải JSON.")
        return None

class Game:
    """Lớp điều khiển chính, quản lý vòng lặp và sự kiện."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((gui.SCREEN_WIDTH, gui.SCREEN_HEIGHT))
        pygame.display.set_caption("Rush Hour AI Solver")
        
        self.all_maps = load_all_maps_from_file()
        if not self.all_maps:
            self.running = False
            return

        self.game_state = gui.GameState(self.all_maps[0], map_index=0)
        self.ui = gui.UI(self.screen, self.game_state)
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.dragging_slider = False

    def run(self):
        """Vòng lặp chính của game."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Xử lý tất cả input từ người dùng."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_mouse_down(event.pos)
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging_slider = False
            
            if event.type == pygame.MOUSEMOTION and self.dragging_slider:
                self._update_slider(event.pos[0])

    def _handle_mouse_down(self, pos):
        # Không cho phép click khi đang giải
        if self.game_state.status == 'solving':
            return

        # Kiểm tra click vào các nút
        for name, rect in self.ui.buttons.items():
            if rect.collidepoint(pos):
                self._handle_button_click(name)
                return # Thoát sau khi xử lý một nút

        # Kiểm tra click vào thanh trượt
        handle_hitbox = pygame.Rect(0, 0, 25, 40)
        handle_hitbox.center = (self.ui.slider_handle_x, self.ui.slider_rect.centery)
        if handle_hitbox.collidepoint(pos):
            self.dragging_slider = True
        elif self.ui.slider_rect.collidepoint(pos):
            self._update_slider(pos[0])

    def _update_slider(self, x_pos):
        self.ui.slider_handle_x = max(self.ui.slider_rect.left, min(self.ui.slider_rect.right, x_pos))
        pos_ratio = (self.ui.slider_handle_x - self.ui.slider_rect.left) / self.ui.slider_rect.width
        self.game_state.step_delay = gui.MAX_DELAY - pos_ratio * (gui.MAX_DELAY - gui.MIN_DELAY)

    def _handle_button_click(self, name):
        gs = self.game_state # Viết tắt cho gọn

        if name == "map_left":
            new_idx = (gs.map_index - 1) % len(self.all_maps)
            self.game_state = gui.GameState(self.all_maps[new_idx], map_index=new_idx, algo_index=gs.algo_index)
            self.ui.state = self.game_state # Cập nhật state cho UI
            gs.status = 'ready' # Reset trạng thái khi đổi map
        elif name == "map_right":
            new_idx = (gs.map_index + 1) % len(self.all_maps)
            self.game_state = gui.GameState(self.all_maps[new_idx], map_index=new_idx, algo_index=gs.algo_index)
            self.ui.state = self.game_state
            gs.status = 'ready' # Reset trạng thái khi đổi map
        elif name == "algo_left":
            gs.algo_index = (gs.algo_index - 1) % len(gui.ALGORITHMS)
            self.game_state = gui.GameState(self.all_maps[gs.map_index], map_index=gs.map_index, algo_index=gs.algo_index)
            self.ui.state = self.game_state # Cập nhật state cho UI
        elif name == "algo_right":
            gs.algo_index = (gs.algo_index + 1) % len(gui.ALGORITHMS)
            self.game_state = gui.GameState(self.all_maps[gs.map_index], map_index=gs.map_index, algo_index=gs.algo_index)
            self.ui.state = self.game_state # Cập nhật state cho UI
        elif name == "Solve" and gs.status == 'ready':
            gs.status = 'solving'
            solve_thread = threading.Thread(target=gs.solve) # Chạy giải thuật trong một luồng riêng
            solve_thread.start()
        
        # Các nút điều khiển animation
        elif gs.solution_path:
            if name == "Play" and not gs.play_mode:
                gs.play_mode = True
                gs.last_step_time = time.time() * 1000 # Chuyển sang ms
            elif name == "Pause":
                gs.play_mode = False
            elif name == "Reset":
                gs.current_step = 0
                gs.current_state = gs.solution_path[0]
                gs.play_mode = False
            elif name == "Back" and gs.current_step > 0:
                gs.current_step -= 1
                gs.current_state = gs.solution_path[gs.current_step]
                gs.play_mode = False
            elif name == "Next" and gs.current_step < len(gs.solution_path) - 1:
                gs.current_step += 1
                gs.current_state = gs.solution_path[gs.current_step]
                gs.play_mode = False

    def update(self):
        """Cập nhật trạng thái cho animation."""
        gs = self.game_state
        if gs.play_mode and gs.solution_path:
            now = time.time() * 1000
            if now - getattr(gs, 'last_step_time', 0) > gs.step_delay:
                if gs.current_step < len(gs.solution_path) - 1:
                    gs.current_step += 1
                    gs.current_state = gs.solution_path[gs.current_step]
                    gs.last_step_time = now
                else:
                    gs.play_mode = False

    def draw(self):
        """Vẽ tất cả mọi thứ lên màn hình."""
        self.ui.draw()
        pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    if game.running:
        game.run()
