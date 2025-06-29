import pygame
import sys
import time
import psutil

from config import Config
from board import Board
from solver import Solver
from ui import UI

class Game:
    """Lớp điều khiển chính, kết nối các thành phần và quản lý vòng lặp game."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption("Rush Hour - AI Algorithm Visualizer")
        self.clock = pygame.time.Clock()
        self.running = True

        self.ui = UI(self.screen)
        
        self.current_map_index = 0
        self.current_algo_index = 0
        
        self.play_mode = False
        self.solve_status = 'ready'
        self.solution_steps = []
        self.current_step = 0
        self.last_step_time = 0
        self.solve_info = {"time": 0, "memory": 0, "steps": 0, "states": 0}

        self.step_delay = Config.DEFAULT_STEP_DELAY
        self.dragging_slider = False
        
        self._setup_ui_elements()
        self._reset_level()

    def _setup_ui_elements(self):
        self.buttons = {}
        panel_x = self.ui.panel_x
        self.buttons["map_left"] = pygame.Rect(panel_x + 40, 100, 40, 40)
        self.buttons["map_right"] = pygame.Rect(panel_x + 300, 100, 40, 40)
        self.buttons["algo_left"] = pygame.Rect(panel_x + 40, 200, 40, 40)
        self.buttons["algo_right"] = pygame.Rect(panel_x + 300, 200, 40, 40)
        self.buttons["Solve"] = pygame.Rect(panel_x + 40, 280, 300, 60)
        y_playback = 680
        controls = ["Back", "Play", "Pause", "Next", "Reset"]
        for i, name in enumerate(controls):
            self.buttons[name] = pygame.Rect(panel_x + 40 + i * 65, y_playback, 60, 40)

        slider_x, slider_y, slider_h = Config.SCREEN_WIDTH - 70, 430, 200
        self.slider_rect = pygame.Rect(slider_x, slider_y, 20, slider_h)
        pos_ratio = (self.step_delay - Config.MIN_DELAY) / (Config.MAX_DELAY - Config.MIN_DELAY)
        self.slider_handle_y = self.slider_rect.top + (pos_ratio * self.slider_rect.height)

    def _reset_level(self):
        self.board = Board(self.current_map_index + 1)
        self.solver = Solver(self.board)
        self.board_state = self.board.get_expanded_grid()
        self.solution_steps = []
        self.current_step = 0
        self.play_mode = False
        self.solve_status = 'ready'
        self.solve_info = {"time": 0, "memory": 0, "steps": 0, "states": 0}

    def _solve_puzzle(self):
        self.solve_status = 'solving'
        self.render()

        process = psutil.Process()
        mem_before = process.memory_info().rss
        start_time = time.time()
        
        result, states_explored = self.solver.solve(self.board.get_expanded_grid(), Config.ALGORITHMS[self.current_algo_index])
        
        end_time = time.time()
        mem_after = process.memory_info().rss
        
        self.solve_info = {
            "time": end_time - start_time, "memory": max(0, mem_after - mem_before),
            "steps": len(result) - 1 if result else 0, "states": states_explored
        }
        
        if result:
            self.solution_steps = result
            self.solve_status = 'success'
        else:
            self.solution_steps = []
            self.solve_status = 'failed'
        
        self.current_step = 0
        self.board_state = self.solution_steps[0] if self.solution_steps else self.board.get_expanded_grid()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: self._handle_mouse_down(event.pos)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1: self.dragging_slider = False
            if event.type == pygame.MOUSEMOTION: self._handle_mouse_motion(event.pos)

    def _handle_mouse_down(self, pos):
        if self.solve_status == 'solving': return
        handle_hitbox = pygame.Rect(0,0,50,25); handle_hitbox.center = (self.slider_rect.centerx, self.slider_handle_y)
        if handle_hitbox.collidepoint(pos): self.dragging_slider = True
        elif self.slider_rect.collidepoint(pos): self._update_slider(pos[1])
        else: self._handle_button_click(pos)

    def _handle_mouse_motion(self, pos):
        if self.dragging_slider: self._update_slider(pos[1])

    def _update_slider(self, y_pos):
        self.slider_handle_y = max(self.slider_rect.top, min(self.slider_rect.bottom, y_pos))
        pos_ratio = (self.slider_handle_y - self.slider_rect.top) / self.slider_rect.height
        self.step_delay = Config.MIN_DELAY + pos_ratio * (Config.MAX_DELAY - Config.MIN_DELAY)

    def _handle_button_click(self, pos):
        for name, rect in self.buttons.items():
            if rect.collidepoint(pos):
                if name == "map_left": self.current_map_index = (self.current_map_index - 1) % len(Config.MAPS); self._reset_level()
                elif name == "map_right": self.current_map_index = (self.current_map_index + 1) % len(Config.MAPS); self._reset_level()
                elif name == "algo_left": self.current_algo_index = (self.current_algo_index - 1) % len(Config.ALGORITHMS); self._reset_level()
                elif name == "algo_right": self.current_algo_index = (self.current_algo_index + 1) % len(Config.ALGORITHMS); self._reset_level()
                elif name == "Solve": self._solve_puzzle()
                elif self.solution_steps:
                    if name == "Play" and not self.play_mode: self.play_mode = True; self.last_step_time = pygame.time.get_ticks()
                    elif name == "Pause": self.play_mode = False
                    elif name == "Reset": self.current_step = 0; self.board_state = self.solution_steps[0]; self.play_mode = False
                    elif name == "Back" and self.current_step > 0: self.current_step -= 1; self.board_state = self.solution_steps[self.current_step]; self.play_mode = False
                    elif name == "Next" and self.current_step < len(self.solution_steps) - 1: self.current_step += 1; self.board_state = self.solution_steps[self.current_step]; self.play_mode = False
                break

    def update(self):
        if self.play_mode and self.solution_steps:
            if pygame.time.get_ticks() - self.last_step_time > self.step_delay:
                if self.current_step < len(self.solution_steps) - 1:
                    self.current_step += 1
                    self.board_state = self.solution_steps[self.current_step]
                    self.last_step_time = pygame.time.get_ticks()
                else:
                    self.play_mode = False

    def render(self):
        self.ui.draw_board(self.board_state, self.board)
        game_state_for_ui = {
            'map_idx': self.current_map_index, 'algo_idx': self.current_algo_index,
            'solve_status': self.solve_status, 'solve_info': self.solve_info,
            'current_step': self.current_step, 'solution_steps': self.solution_steps,
            'play_mode': self.play_mode
        }
        self.ui.draw_panel(game_state_for_ui)
        self.ui.draw_buttons(self.buttons, game_state_for_ui)
        self.ui.draw_slider(self.slider_rect, self.slider_handle_y)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()