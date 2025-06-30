import heapq
import time
import copy

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
        
# State class represents a state in the puzzle
class State:
    # Constructor
    def __init__(self, map, objects, gn = 0, parent = None):
        # The puzzle map
        self.map = map
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
        self.map_tuple = tuple(map(tuple, self.map))
        
    # Check if the current state is the goal state
    def is_goal(self, goal_position):
        main_object = self.objects[1]
        goal_row, goal_col = goal_position
        
        # vertical case
        if main_object.orientation == 0:
            upper_most_row = min(row for row, col in main_object.positions)
            lower_most_row = max(row for row, col in main_object.positions)
            
            if upper_most_row == goal_row or lower_most_row == goal_row:
                return True
            else:
                return False
        # horizontal case    
        else:
            left_most_col = min(col for row, col in main_object.positions)
            right_most_col = max(col for row, col in main_object.positions)
            
            if right_most_col == goal_col or left_most_col == goal_col:
                return True
            else:
                return False
            
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
        main_object_row, main_object_col = next(iter(main_object.positions))
        goal_row, goal_col = goal_position
        blocking_object = set() # avoid duplicate
        
        # vertical case
        if main_object.orientation == 0:
            if goal_row > main_object_row:
                for row in range(main_object_row + 1, goal_row):
                    if self.map[row][goal_col] > 1:
                        blocking_object.add(self.map[row][goal_col])
            else:
                for row in range(goal_row + 1, main_object_row):
                    if self.map[row][goal_col] > 1:
                        blocking_object.add(self.map[row][goal_col])
        # horizontal case
        else:
            if goal_col > main_object_col:
                for col in range(main_object_col + 1, goal_col):
                    if self.map[goal_row][col] > 1:
                        blocking_object.add(self.map[goal_row][col])
            else:
                for col in range(goal_col + 1, main_object_col):
                    if self.map[goal_row][col] > 1:
                        blocking_object.add(self.map[goal_row][col])
        
        self.hn = len(blocking_object)
        self.fn = self.hn + self.gn
        
# Get objects' information of the initial map
def get_objects_info(map):
    map_row_count = len(map)
    map_col_count = len(map[0])
    objects = {}
    visited_objects = set()
    
    for i in range(map_row_count):
        for j in range(map_col_count):
            object_id = map[i][j]
            
            if object_id > 0 and object_id not in visited_objects:
                # mark as visited
                visited_objects.add(object_id)
                object_positions = []
                
                # Check for vertical orientation
                if map[i + 1][j] == object_id:
                    object_orientation = 0
                    object_length = 0
                    temp_i = i
                    while map[temp_i][j] == object_id:
                        object_positions.append((temp_i, j))
                        object_length += 1
                        temp_i += 1
                # check for horizontal orientation
                elif map[i][j + 1] == object_id:
                    object_orientation = 1
                    object_length = 0
                    temp_j = j
                    while map[i][temp_j] == object_id:
                        object_positions.append((i, temp_j))
                        object_length += 1
                        temp_j += 1
                        
                objects[object_id] = Object(object_id, object_length, object_orientation, object_positions)
    
    return objects

# Generate child states of the current state
def generate_child_state(current_state):
    frontier = []
    
    for object_id, object in current_state.objects.items():
        cost = object.length
        
        # vertical case
        if object.orientation == 0:
            upper_most_row = min(row for row, col in object.positions)
            lower_most_row = max(row for row, col in object.positions)
            col = list(object.positions)[0][1]
            
            # move up
            if current_state.map[upper_most_row - 1][col] == 0 or current_state.map[upper_most_row - 1][col] == -2:
                # create and modify new state's map
                new_map = copy.deepcopy(current_state.map)
                new_map[lower_most_row][col] = 0
                new_map[upper_most_row - 1][col] = object_id
                # create and modify new state's objects dict
                new_objects = copy.deepcopy(current_state.objects)
                new_objects[object_id].positions.remove((lower_most_row, col))
                new_objects[object_id].positions.add((upper_most_row - 1, col))
                
                # Add to frontier
                frontier.append(State(new_map, new_objects, current_state.gn + cost, current_state))
                
            # move down
            if current_state.map[lower_most_row + 1][col] == 0 or current_state.map[lower_most_row + 1][col] == -2:
                # create and modify new state's map
                new_map = copy.deepcopy(current_state.map)
                new_map[upper_most_row][col] = 0
                new_map[lower_most_row + 1][col] = object_id
                # create and modify new state's objects dict
                new_objects = copy.deepcopy(current_state.objects)
                new_objects[object_id].positions.remove((upper_most_row, col))
                new_objects[object_id].positions.add((lower_most_row + 1, col))
                
                # Add to frontier
                frontier.append(State(new_map, new_objects, current_state.gn + cost, current_state))
        # horizontal case
        else:
            left_most_col = min(col for row, col in object.positions)
            right_most_col = max(col for row, col in object.positions)
            row = list(object.positions)[0][0]
            
            # move left
            if current_state.map[row][left_most_col - 1] == 0 or current_state.map[row][left_most_col - 1] == -2:
                # create and modify new state's map
                new_map = copy.deepcopy(current_state.map)
                new_map[row][right_most_col] = 0
                new_map[row][left_most_col - 1] = object_id
                # create and modify new state's objects dict
                new_objects = copy.deepcopy(current_state.objects)
                new_objects[object_id].positions.remove((row, right_most_col))
                new_objects[object_id].positions.add((row, left_most_col - 1))
                
                # add to frontier
                frontier.append(State(new_map, new_objects, current_state.gn + cost, current_state))
            
            # move right
            if current_state.map[row][right_most_col + 1] == 0 or current_state.map[row][right_most_col + 1] == -2:
                # create and modify new state's map
                new_map = copy.deepcopy(current_state.map)
                new_map[row][left_most_col] = 0
                new_map[row][right_most_col + 1] = object_id
                # create and modify new state's objects dict
                new_objects = copy.deepcopy(current_state.objects)
                new_objects[object_id].positions.remove((row, left_most_col))
                new_objects[object_id].positions.add((row, right_most_col + 1))
                
                # add to frontier
                frontier.append(State(new_map, new_objects, current_state.gn + cost, current_state))
                
    return frontier
    
# A-star solver
def A_star_solver(map):
    # find goal's position
    goal_pos = (-1, -1)
    for i in range(len(map)):
        for j in range(len(map[0])):
            if map[i][j] == -2:
                goal_pos = (i, j)
                break
        
        if goal_pos != (-1, -1):
            break
        
    # Initial step for A-star sover
    initial_objects = get_objects_info(map)
    intitial_state = State(map, initial_objects)
    intitial_state.calc_heuristic(goal_pos)
    
    # Initialize Frontier and Expansion order
    frontier = [intitial_state]
    expansion_order = set()
    
    # Solve
    solution_steps = []
    while frontier != []:
        # using priority queue to get the state with lowest(fn value) in the Frontier
        current_state = heapq.heappop(frontier)
        
        # Check for goal
        if current_state.is_goal(goal_pos):
            solved_steps = []
            temp_state = current_state
            while temp_state != None:
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
            is_existed = False
            for frontier_state in frontier:
                if child_state == frontier_state and child_state.fn >= frontier_state.fn:
                    is_existed = True
                    break
            if not is_existed:
                heapq.heappush(frontier, child_state)
    
    # Return result
    if solution_steps != []:
        return solution_steps
    else:
        print('No solution')
        return None