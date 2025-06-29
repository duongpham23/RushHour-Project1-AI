from collections import deque
import heapq

class Solver:
    """Chứa logic của các thuật toán tìm kiếm."""
    def __init__(self, board_config):
        self.board_config = board_config

    def solve(self, start_state, algorithm):
        if algorithm == "BFS": return self._bfs(start_state)
        if algorithm == "DFS": return self._dfs(start_state)
        if algorithm == "UCS": return self._ucs(start_state)
        if algorithm == "A*": return self._astar(start_state)
        return None, 0

    def _is_goal(self, state):
        exit_r, exit_c = self.board_config.exit_pos
        exit_r_exp, exit_c_exp = exit_r + 1, exit_c + 1
        if 0 <= exit_r_exp < len(state) and 0 <= exit_c_exp < len(state[0]):
            # Kiểm tra xem xe 1 có ở vị trí thoát không
            if self.board_config.exit_orientation == 'H':
                return state[exit_r_exp][exit_c_exp-1] == 1
            else:
                return state[exit_r_exp-1][exit_c_exp] == 1
        return False

    def _get_car_positions(self, state, car_id):
        return [(r, c) for r, row in enumerate(state) for c, val in enumerate(row) if val == car_id]

    def _get_all_cars(self, state):
        return sorted(list(set(val for row in state for val in row if val > 0)))

    def _move_car(self, state, car_id, direction):
        positions = self._get_car_positions(state, car_id)
        if not positions: return None
        
        moves = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
        dr, dc = moves[direction]
        
        car = self.board_config.get_vehicle(car_id)
        if not car: return None
        
        is_horizontal = car.orientation == "H"
        is_vertical = car.orientation == "V"

        if (dc != 0 and not is_horizontal) or (dr != 0 and not is_vertical): return None

        new_positions = [(r + dr, c + dc) for r, c in positions]
        
        for r, c in new_positions:
            if not (0 <= r < len(state) and 0 <= c < len(state[0])): return None
            if state[r][c] not in (0, car_id):
                if car_id == 1 and state[r][c] == -2: continue
                return None

        new_state = [row[:] for row in state]
        for r, c in positions: new_state[r][c] = 0
        for r, c in new_positions: new_state[r][c] = car_id
        return new_state

    def _heuristic(self, state):
        pos = self._get_car_positions(state, 1)
        if not pos: return float('inf')
        exit_r, exit_c = self.board_config.exit_pos[0] + 1, self.board_config.exit_pos[1] + 1
        if self.board_config.exit_orientation == "H":
            return abs(exit_c - max(c for r, c in pos))
        else:
            return abs(exit_r - max(r for r, c in pos))

    def _bfs(self, start_state):
        serialize = lambda s: tuple(tuple(row) for row in s)
        queue = deque([(start_state, [])])
        visited = {serialize(start_state)}
        while queue:
            current, path = queue.popleft()
            if self._is_goal(current): return path + [current], len(visited)
            for car_id in self._get_all_cars(current):
                for d in ["up", "down", "left", "right"]:
                    new = self._move_car(current, car_id, d)
                    if new and serialize(new) not in visited:
                        visited.add(serialize(new))
                        queue.append((new, path + [current]))
        return None, len(visited)

    def _dfs(self, start_state):
        serialize = lambda s: tuple(tuple(row) for row in s)
        stack = [(start_state, [])]
        visited = {serialize(start_state)}
        while stack:
            current, path = stack.pop()
            if self._is_goal(current): return path + [current], len(visited)
            for car_id in self._get_all_cars(current):
                for d in ["up", "down", "left", "right"]:
                    new = self._move_car(current, car_id, d)
                    if new and serialize(new) not in visited:
                        visited.add(serialize(new))
                        stack.append((new, path + [current]))
        return None, len(visited)

    def _ucs(self, start_state):
        serialize = lambda s: tuple(tuple(row) for row in s)
        heap = [(0, start_state, [])]
        cost_map = {serialize(start_state): 0}
        while heap:
            cost, current, path = heapq.heappop(heap)
            if cost > cost_map.get(serialize(current), float('inf')): continue
            if self._is_goal(current): return path + [current], len(cost_map)
            for car_id in self._get_all_cars(current):
                for d in ["up", "down", "left", "right"]:
                    new = self._move_car(current, car_id, d)
                    if new:
                        new_cost = cost + 1
                        new_ser = serialize(new)
                        if new_cost < cost_map.get(new_ser, float('inf')):
                            cost_map[new_ser] = new_cost
                            heapq.heappush(heap, (new_cost, new, path + [current]))
        return None, len(cost_map)

    def _astar(self, start_state):
        serialize = lambda s: tuple(tuple(row) for row in s)
        heap = [(self._heuristic(start_state), 0, start_state, [])]
        cost_map = {serialize(start_state): 0}
        while heap:
            f, g, current, path = heapq.heappop(heap)
            if g > cost_map.get(serialize(current), float('inf')): continue
            if self._is_goal(current): return path + [current], len(cost_map)
            for car_id in self._get_all_cars(current):
                for d in ["up", "down", "left", "right"]:
                    new = self._move_car(current, car_id, d)
                    if new:
                        new_g = g + 1
                        new_ser = serialize(new)
                        if new_g < cost_map.get(new_ser, float('inf')):
                            cost_map[new_ser] = new_g
                            new_f = new_g + self._heuristic(new)
                            heapq.heappush(heap, (new_f, new_g, new, path + [current]))
        return None, len(cost_map)