import heapq
import time
import tracemalloc

# Object class represents boat and wood logs
class Object:
    # Constructor
    def __init__(self, id, length, orientation, positions):
        # id of an object
        self.id = id 
        # length of an object (2 or 3)
        self.length = length 
        # orientation of an object (0: vertical | 1: horizontal)
        self.orientation = orientation
        #store the positions (cells) that the object is in
        self.positions = set(positions)
        
        # vertical
        if self.orientation == 0:
            self.max_bound = max(row for row, col in self.positions)
            self.min_bound = min(row for row, col in self.positions)
        # horizontal
        else:
            self.max_bound = max(col for row, col in self.positions)
            self.min_bound = min(col for row, col in self.positions)
        
# State class represents a state in the puzzle
class State:
    # Constructor
    def __init__(self, game_map, objects, gn = 0, parent = None):
        # The puzzle map
        self.game_map = game_map
        # Object array to store all objects in the map
        self.objects = objects
        # Total cost from the initial state
        self.gn = gn
        # Heristic function's value
        self.hn = 0
        # A-star algorithm's total cost: fn = gn + hn
        self.fn = 0
        # store the parent state of the current state
        self.parent = parent
        # store the information of the current's state map as unchangable tuple
        self.map_tuple = tuple(map(tuple, self.game_map))
        
    # Check if the current state is the goal state
    def is_goal(self, goal_position):
        main_object = self.objects[1]
        return goal_position in main_object.positions
            
    # comparision method for the priority queue to check
    def __lt__(self, other_state):
        return self.fn <  other_state.fn
    
    # hash current map_tuple for quick look up
    def __hash__(self):
        return hash(self.map_tuple)
    
    # check if 2 map_tuple are equal
    def __eq__(self, other_state):
        return self.map_tuple == other_state.map_tuple
    
    # calculate heuristic function
    # h(n) = number of objects blocking the main object (boat)
    def calc_heuristic(self, goal_position):
        main_object = self.objects[1]
        goal_row, goal_col = goal_position
        blocking_object = set() # avoid duplicate
        
        # vertical case
        if main_object.orientation == 0:
            if goal_row > main_object.max_bound:
                for row in range(main_object.max_bound + 1, goal_row):
                    if self.game_map[row][goal_col] > 1:
                        blocking_object.add(self.game_map[row][goal_col])
                manhattan_distance = goal_row - main_object.max_bound
            else:
                for row in range(goal_col + 1, main_object.min_bound):
                    if self.game_map[row][goal_col] > 1:
                        blocking_object.add(self.game_map[row][goal_col])
                manhattan_distance = main_object.min_bound - goal_row
        # horizontal case
        else:
            if goal_col > main_object.max_bound:
                for col in range(main_object.max_bound + 1, goal_col):
                    if self.game_map[goal_row][col] > 1:
                        blocking_object.add(self.game_map[goal_row][col])
                manhattan_distance = goal_col - main_object.max_bound
            else:
                for col in range(goal_col + 1, main_object.min_bound):
                    if self.game_map[goal_row][col] > 1:
                        blocking_object.add(self.game_map[goal_row][col])
                manhattan_distance = main_object.min_bound - goal_col
        
        # Calculate f(n)
        # self.hn = 0
        # for object_id in blocking_object:
        #     self.hn += self.objects[object_id].length
        # self.hn += manhattan_distance
        self.hn = manhattan_distance + len(blocking_object)
        self.fn = self.hn + self.gn
        
# Get objects' information of the initial map
def get_objects_info(game_map):
    game_map_row_count = len(game_map)
    game_map_col_count = len(game_map[0])
    objects = {}
    visited_objects = set()
    
    for i in range(game_map_row_count):
        for j in range(game_map_col_count):
            object_id = game_map[i][j]
            
            if object_id > 0 and object_id not in visited_objects:
                # mark as visited
                visited_objects.add(object_id)
                object_positions = []
                
                # Check for vertical orientation
                if i + 1 < game_map_row_count and game_map[i + 1][j] == object_id:
                    object_orientation = 0
                    object_length = 0
                    temp_i = i
                    while temp_i < game_map_row_count and game_map[temp_i][j] == object_id:
                        object_positions.append((temp_i, j))
                        object_length += 1
                        temp_i += 1
                # check for horizontal orientation
                elif j + 1 < game_map_col_count and game_map[i][j + 1] == object_id:
                    object_orientation = 1
                    object_length = 0
                    temp_j = j
                    while temp_j < game_map_col_count and game_map[i][temp_j] == object_id:
                        object_positions.append((i, temp_j))
                        object_length += 1
                        temp_j += 1
                        
                objects[object_id] = Object(object_id, object_length, object_orientation, object_positions)
    
    return objects

# Generate child states of the current state
def generate_child_state(current_state):
    frontier = []
    game_map_row_count = len(current_state.game_map)
    game_map_col_count = len(current_state.game_map[0])
    
    for object_id, object in current_state.objects.items():
        cost = object.length
        
        # vertical case
        if object.orientation == 0:
            col = list(object.positions)[0][1]
            
            # move up
            if object.min_bound - 1 >= 0 and current_state.game_map[object.min_bound - 1][col] == 0 or current_state.game_map[object.min_bound - 1][col] == -2:
                # create and modify new state's map
                new_game_map = [list(row) for row in current_state.game_map]
                new_game_map[object.max_bound][col] = 0
                new_game_map[object.min_bound - 1][col] = object_id
                # create and modify new state's objects dict
                new_objects = current_state.objects.copy()
                new_positions = object.positions.copy()
                new_positions.remove((object.max_bound, col))
                new_positions.add((object.min_bound - 1, col))
                new_objects[object_id] = Object(object_id, object.length, object.orientation, new_positions)
                
                # Add to frontier
                frontier.append(State(new_game_map, new_objects, current_state.gn + cost, current_state))
                
            # move down
            if object.max_bound + 1 < game_map_row_count and current_state.game_map[object.max_bound + 1][col] == 0 or current_state.game_map[object.max_bound + 1][col] == -2:
                # create and modify new state's game_map
                new_game_map = [list(row) for row in current_state.game_map]
                new_game_map[object.min_bound][col] = 0
                new_game_map[object.max_bound + 1][col] = object_id
                # create and modify new state's objects dict
                new_objects = current_state.objects.copy()
                new_positions = object.positions.copy()
                new_positions.remove((object.min_bound, col))
                new_positions.add((object.max_bound + 1, col))
                new_objects[object_id] = Object(object_id, object.length, object.orientation, new_positions)
                
                # Add to frontier
                frontier.append(State(new_game_map, new_objects, current_state.gn + cost, current_state))
        # horizontal case
        else:
            row = list(object.positions)[0][0]
            
            # move left
            if object.min_bound - 1 >= 0 and current_state.game_map[row][object.min_bound - 1] == 0 or current_state.game_map[row][object.min_bound - 1] == -2:
                # create and modify new state's map
                new_game_map = [list(row) for row in current_state.game_map]
                new_game_map[row][object.max_bound] = 0
                new_game_map[row][object.min_bound - 1] = object_id
                # create and modify new state's objects dict
                new_objects = current_state.objects.copy()
                new_positions = object.positions.copy()
                new_positions.remove((row, object.max_bound))
                new_positions.add((row, object.min_bound - 1))
                new_objects[object_id] = Object(object_id, object.length, object.orientation, new_positions)
                
                # add to frontier
                frontier.append(State(new_game_map, new_objects, current_state.gn + cost, current_state))
            
            # move right
            if object.max_bound + 1 < game_map_col_count and current_state.game_map[row][object.max_bound + 1] == 0 or current_state.game_map[row][object.max_bound + 1] == -2:
                # create and modify new state's game_map
                new_game_map = [list(row) for row in current_state.game_map]
                new_game_map[row][object.min_bound] = 0
                new_game_map[row][object.max_bound + 1] = object_id
                # create and modify new state's objects dict
                new_objects = current_state.objects.copy()
                new_positions = object.positions.copy()
                new_positions.remove((row, object.min_bound))
                new_positions.add((row, object.max_bound + 1))
                new_objects[object_id] = Object(object_id, object.length, object.orientation, new_positions)
                
                # add to frontier
                frontier.append(State(new_game_map, new_objects, current_state.gn + cost, current_state))
                
    return frontier
    
# A-star solver
def A_star_solver(game_map):
    # Start tracking search time, memory used, expanded node count
    tracemalloc.start()
    start_time = time.time()
    expanded_nodes = 0
    
    # find goal's position
    goal_pos = (-1, -1)
    for i in range(len(game_map)):
        for j in range(len(game_map[0])):
            if game_map[i][j] == -2:
                goal_pos = (i, j)
                break
        
        if goal_pos != (-1, -1):
            break
        
    # Initial step for A-star sover
    initial_objects = get_objects_info(game_map)
    intitial_state = State(game_map, initial_objects)
    intitial_state.calc_heuristic(goal_pos)
    
    # Initialize Frontier and Expansion order
    frontier = [intitial_state]
    expansion_order = set()
    frontier_cost = dict()  # (key: current_state, value: cost)
    frontier_cost[intitial_state] = 0  # Chi phí ban đầu là 0
    
    # Solve
    solution_steps = []
    while frontier != []:
        # using priority queue to get the state with lowest(fn value) in the Frontier
        current_state = heapq.heappop(frontier)
        expanded_nodes += 1
        
        # Check for goal
        if current_state.is_goal(goal_pos):
            solved_steps = []
            temp_state = current_state
            while temp_state:
                solved_steps.append(temp_state)
                temp_state = temp_state.parent
            solution_steps = solved_steps[::-1]
            break
        
        # add state to the Expansion order list to avoid revisting
        expansion_order.add(current_state)
        
        # generate child states
        child_states = generate_child_state(current_state)
        for child_state in child_states:
            if child_state in expansion_order:
                continue
            
            # add to frontier
            child_state.calc_heuristic(goal_pos)
            if child_state not in frontier_cost or child_state.fn < frontier_cost[child_state]:
                # Nếu trạng thái con chưa tồn tại trong frontier, thêm vào
                frontier_cost[child_state] = child_state.fn
                heapq.heappush(frontier, child_state)
    
    # Calculate search time, memory used
    search_time = time.time() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Return result
    if solution_steps != []:
        return solution_steps, expanded_nodes, search_time, peak_memory
    else:
        return [], expanded_nodes, search_time, peak_memory

def ucs_solver(game_map):
    # Theo dõi thời gian tìm kiếm, bộ nhớ đã sử dụng
    start_time = time.time()
    tracemalloc.start()

    initial_objects = get_objects_info(game_map)
    initial_state = State(game_map, initial_objects)

    expansion = set()  # Sử dụng set để lưu trạng thái đã mở rộng
    frontier = [initial_state]  # Sử dụng danh sách để lưu trạng thái trong frontier
    frontier_cost = dict()  # (key: current_state, value: cost)
    frontier_cost[initial_state] = 0  # Chi phí ban đầu là 0

    # find goal's position
    goal_pos = (-1, -1)
    for i in range(len(game_map)):
        for j in range(len(game_map[0])):
            if game_map[i][j] == -2:
                goal_pos = (i, j)
                break
        
        if goal_pos != (-1, -1):
            break

    solution_steps = []  # Danh sách để lưu các bước giải quyết
    while frontier:
        current_state = heapq.heappop(frontier)  # Lấy trạng thái có chi phí thấp nhất
        frontier_cost.pop(current_state, None)  # Xóa trạng thái khỏi frontier_cost
        expansion.add(current_state)  # Thêm trạng thái hiện tại vào tập đã mở rộng

        # Check for goal
        if current_state.is_goal(goal_pos):
            temp_state = current_state
            while temp_state:
                solution_steps.insert(0, temp_state)  # Thêm trạng thái vào đầu danh sách
                temp_state = temp_state.parent

            break  # Thoát khỏi vòng lặp nếu tìm thấy đích

        # Get children states
        children_states = generate_child_state(current_state)

        for child_state in children_states:
            if child_state in expansion:
                continue

            child_state.fn = child_state.gn
            if child_state not in frontier_cost or child_state.fn < frontier_cost[child_state]:
                # Nếu trạng thái con chưa tồn tại trong frontier, thêm vào
                frontier_cost[child_state] = child_state.fn
                heapq.heappush(frontier, child_state)

    # Tính toán thời gian tìm kiếm và bộ nhớ đã sử dụng
    time_taken = time.time() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()  # Lấy thông tin bộ nhớ đã sử dụng
    tracemalloc.stop()

    if not solution_steps:
        return [], len(expansion), time_taken, peak_memory  # Trả về None nếu không tìm thấy đường đi

    return solution_steps, len(expansion), time_taken, peak_memory

def dfs_solver(game_map):
    # Bắt đầu đo thời gian và bộ nhớ
    start_time = time.time()
    tracemalloc.start()

    # Tìm goal
    goal_pos = (-1, -1)
    for i in range(len(game_map)):
        for j in range(len(game_map[0])):
            if game_map[i][j] == -2:
                goal_pos = (i, j)
                break
        if goal_pos != (-1, -1):
            break

    # Khởi tạo trạng thái ban đầu
    initial_objects = get_objects_info(game_map)
    initial_state = State(game_map, initial_objects)

    frontier = [initial_state]  # Stack cho DFS
    expansion = set()
    solution_steps = []

    while frontier:
        current_state = frontier.pop()

        # Goal test
        if current_state.is_goal(goal_pos):
            temp = current_state
            while temp:
                solution_steps.insert(0, temp)
                temp = temp.parent
            break

        if current_state in expansion:
            continue
        expansion.add(current_state)

        # Sinh các trạng thái con
        children = generate_child_state(current_state)
        for child in reversed(children):  # reversed để duyệt đúng thứ tự
            if child not in expansion:
                frontier.append(child)

    # Đo thời gian và bộ nhớ
    time_taken = time.time() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if not solution_steps:
        return [], len(expansion), time_taken, peak_memory

    return solution_steps, len(expansion), time_taken, peak_memory

def bfs_solver(game_map):
    tracemalloc.start()
    start_time = time.time()
    expanded_nodes = 0
    
    # Find goal position 
    goal_pos = (-1, -1)
    for i in range(len(game_map)):
        for j in range(len(game_map[0])):
            if game_map[i][j] == -2:
                goal_pos = (i, j)
                break
        if goal_pos != (-1, -1):
            break
    
    initial_objects = get_objects_info(game_map)
    initial_state = State(game_map, initial_objects)
    
    frontier = [initial_state]
    expansion = set()
    frontier_states = {initial_state}  
    
    solution_steps = []
    
    # BFS main loop 
    while frontier:
        # BFS: lấy phần tử đầu tiên (FIFO) 
        current_state = frontier.pop(0)
        frontier_states.discard(current_state)
        expansion.add(current_state)
        expanded_nodes += 1
        
        # Check for goal 
        if current_state.is_goal(goal_pos):
            temp_state = current_state
            while temp_state:
                solution_steps.insert(0, temp_state)
                temp_state = temp_state.parent
            break
        
        child_states = generate_child_state(current_state)
        
        for child_state in child_states:
            # Chỉ thêm vào frontier nếu chưa được expand và chưa có trong frontier
            if child_state not in expansion and child_state not in frontier_states:
                frontier.append(child_state)
                frontier_states.add(child_state)
    
    # Calculate search time và memory 
    search_time = time.time() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if solution_steps:
        return solution_steps, expanded_nodes, search_time, peak_memory
    else:
        return [], expanded_nodes, search_time, peak_memory

def solve(game_map, algorithm='A*'):
    if algorithm == 'A*':
        return A_star_solver(game_map)
    elif algorithm == 'UCS':
        return ucs_solver(game_map)
    elif algorithm == 'DFS':
        return dfs_solver(game_map)
    elif algorithm == 'BFS':
        return bfs_solver(game_map)