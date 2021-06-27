def get_next(currentHead, nextMove):
    """
    return the coordinate of the head if our snake goes that way
    """
    futureHead = currentHead.copy()
    if nextMove == 'left':
        futureHead['x'] = currentHead['x'] - 1
    if nextMove == 'right':
        futureHead['x'] = currentHead['x'] + 1
    if nextMove == 'up':
        futureHead['y'] = currentHead['y'] + 1
    if nextMove == 'down':
        futureHead['y'] = currentHead['y'] - 1
    return futureHead

def get_all_moves(coord):
    # return a list of all coordinates reachable from this point
    return [{'x' : coord['x'] + 1, 'y':coord['y']}, {'x' : coord['x'] - 1, 'y':coord['y']}, {'x' : coord['x'], 'y':coord['y'] + 1}, {'x' : coord['x'], 'y':coord['y'] - 1}]

def get_safe_moves(possible_moves, body, board):
    safe_moves = []

    for guess in possible_moves:
        guess_coord = get_next(body[0], guess)
        if avoid_walls(guess_coord, board["width"], board["height"]) and avoid_snakes(guess_coord, board["snakes"]):
            safe_moves.append(guess)
        elif len(body) > 1 and guess_coord == body[-1] and guess_coord not in body[:-1]:
            safe_moves.append(guess)
    return safe_moves


def avoid_walls(future_head, board_width, board_height):
    result = True

    x = int(future_head["x"])
    y = int(future_head["y"])

    if x < 0 or y < 0 or x >= board_width or y >= board_height:
        result = False

    return result

def avoid_consumption(future_head, snake_bodies, my_snake):
    if len(snake_bodies) < 2:
        return True

    my_length = my_snake['length']
    for snake in snake_bodies:
        if snake == my_snake:
            continue
        if future_head in get_all_moves(snake['head']) and future_head not in snake['body'][1:-1] and my_length <= snake['length']:
            return False
    return True

def avoid_hazards(future_head, hazards):
    return future_head not in hazards

def avoid_snakes(future_head, snake_bodies):
    for snake in snake_bodies:
        if future_head in snake["body"][:-1]:
            return False
    return True


def get_minimum_moves(start_coord, targets):
    moves = []
    for coord in targets:
        moves.append(abs(coord['x'] - start_coord['x']) + abs(coord['y'] - start_coord['y']))
    return moves

def at_wall(coord, board):
    return coord['x'] <= 0 or coord['y'] <= 0 or coord['x'] >= board['width'] - 1 or coord['y'] >= board['height'] - 1

def get_future_head_positions(body, turns, board):
    turn = 0
    explores = {}
    explores[0] = [body[0]]
    while turn < turns:
        turn += 1
        explores[turn] = []
        for explore in explores[turn-1]:
            next_path = get_safe_moves(['left', 'right', 'up', 'down'], [explore], board)
            for path in next_path:
                explores[turn].append(get_next(explore, path))

    return explores[turns]

def retrace_path(path, origin):
    val = []
    next_moves = [move for move in get_all_moves(origin) if move in path]
    while next_moves:
        step = []
        for coord in next_moves:
            val.append(coord)
            step += [move for move in get_all_moves(coord) if move in path and move not in step and move not in val]
        next_moves = step
    return val

def get_str(coord):
    return f"{coord['x']}:{coord['y']}"

def get_moves_towards(start_coord, end_coord):
    ans = []
    if end_coord['x'] > start_coord['x']:
        ans.append('right')
    if end_coord['x'] < start_coord['x']:
        ans.append('left')
    if end_coord['y'] > start_coord['y']:
        ans.append('up')
    if end_coord['y'] < start_coord['y']:
        ans.append('down')
    return ans

def get_smart_moves(possible_moves, body, board, my_snake):
    smart_moves = []
    all_moves = ['up' 'down', 'left', 'right']
    avoid_moves = []
    enemy_snakes = [snake for snake in board['snakes'] if snake['id'] != my_snake['id']]

    safe_moves = get_safe_moves(possible_moves, body, board)

    safe_coords = {}
    next_coords = {}
    eating_snakes = []
    collision_threats = []
    collision_targets = {}
    food_step = {}
    dead_ends = {}

    for guess in safe_moves:
        safe_coords[guess] = []
        guess_coord = get_next(body[0], guess)
        next_coords[guess] = guess_coord
        explore_edge = [guess_coord]
        all_coords = [guess_coord]
        next_explore = []

        explore_step = 1
        food_step[guess] = {}

        for _ in body[:-1]:
            next_explore.clear()
            explore_step += 1

            if len(explore_edge) == 0 and guess not in dead_ends:
                dead_ends[guess] = explore_step
            for explore in explore_edge:
                if explore in board['food']:
                    food_step[guess][get_str(explore)] = explore_step - 1
                safe = get_safe_moves(all_moves, [explore], board)
                for safe_move in safe:
                    guess_coord_next = get_next(explore, safe_move)
                    if guess_coord_next not in all_coords:
                        next_explore.append(guess_coord_next)
                # for other snakes
                snake_collide = [coord for coord in get_all_moves(explore) if not avoid_snakes(coord, enemy_snakes)]
                if snake_collide:
                    for coord in snake_collide:
                        for snake in enemy_snakes:
                            if coord in snake['body']:
                                if coord == snake['head']:
                                    # bumping heads with a snake
                                    if snake['length'] >= my_snake['length']:
                                        collision_threats.append(snake['id'])
                                    elif snake['id'] not in collision_targets:
                                        collision_targets[snake['id']] = explore_step
                                    elif collision_targets[snake['id']] > explore_step:
                                        collision_targets[snake['id']] = explore_step

                all_coords += next_explore.copy()
                all_coords.append(explore)
            explore_edge = next_explore.copy()

        safe_coords[guess] += list(map(dict, frozenset(frozenset(coord.items() for coord in all_coords))))

    for path in safe_coords.keys():
        guess_coord = get_next(body[0], path)
        if((len(safe_coords[path]) >= len(body) or
            any(snake['body'][-1] in safe_coords[path] for snake in
                [snake for snake in board['snaked'] if snake['id']])) and
        avoid_consumption(guess, board['snakes'], my_snake) and
        avoid_hazards(guess_coord, board['hazards'])):
            smart_moves.append(path)
