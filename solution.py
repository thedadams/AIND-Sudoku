assignments = []


def update_units_for_diagonal():
    UNITLIST.extend(DIAGONAL_UNITS)
    for diagonal in DIAGONAL_UNITS:
        for box in diagonal:
            UNITS[box].append(diagonal)
            PEERS[box].update(set(diagonal) - set([box]))


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    twins = []
    for box in BOXES:
        if len(values[box]) == 2:
            for other_box in PEERS[box]:
                if values[other_box] == values[box]:
                    twins.append([box, other_box])
    for box1, box2 in twins:
        if len(values[box1]) < 2 or len(values[box2]) < 2:
            continue
        for box in PEERS[box1] & PEERS[box2]:
            if len(values[box]) > 1:
                assign_value(values, box, values[box].replace(values[box1][0], "").replace(values[box1][1], ""))
    return values


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    values = dict()
    index = 0
    while index < len(BOXES):
        assign_value(values, BOXES[index], grid[index] if grid[index] != '.' else COLS)
        index += 1
    return values


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in values.keys())
    line = '+'.join(['-' * (width * 3)] * 3)
    for row in ROWS:
        print(''.join(values[row + col].center(width) + ('|' if col in '36' else '') for col in COLS))
        if row in 'CF':
            print(line)
    print()


def eliminate(values):
    only_one_value = [box for box in BOXES if len(values[box]) == 1]
    for box in only_one_value:
        for other_box in PEERS[box]:
            assign_value(values, other_box, values[other_box].replace(values[box], ""))
    return values


def only_choice(values):
    for unit in UNITLIST:
        for val in COLS:
            box_with_val = [box for box in unit if val in values[box]]
            if len(box_with_val) == 1:
                assign_value(values, box_with_val[0], val)
    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        num_solved_before = len([box for box in values if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        if any([len(val) == 0 for val in values.values()]):
            return None
        num_solved_after = len([box for box in values if len(values[box]) == 1])
        stalled = num_solved_before == num_solved_after
    return values


def solve(grid, diagonal=True):
    """
     Find the solution to a Sudoku grid.
     Args:
         grid(string): a string representing a sudoku grid.
             Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
     Returns:
         The string representing the final sudoku grid. False if no solution exists.
     """
    values = grid_values(grid)
    if diagonal:
        update_units_for_diagonal()
    return search(values)


def search(values):
    values = reduce_puzzle(values)
    if values is None:
        return None
    if all([len(values[b]) == 1 for b in values.keys()]):
        return values
    min_values = 10
    next_box = ""
    for b, vals in values.items():
        if len(vals) > 1 and len(vals) < min_values:
            min_values = len(vals)
            next_box = b

    for value in values[next_box]:
        new_values = values.copy()
        assign_value(new_values, next_box, value)
        possible_sol = search(new_values)
        if possible_sol is not None:
            return possible_sol

# Copying these utilities from the course because order matters to pass the test cases.
ROWS = 'ABCDEFGHI'
COLS = '123456789'
BOXES = cross(ROWS, COLS)
ROW_UNITS = [cross(r, COLS) for r in ROWS]
COL_UNITS = [cross(ROWS, c) for c in COLS]
SQUARE_UNITS = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
DIAGONAL_UNITS = [["".join(a) for a in zip(ROWS, COLS)], ["".join(a) for a in zip(ROWS, reversed(COLS))]]
UNITLIST = ROW_UNITS + COL_UNITS + SQUARE_UNITS
UNITS = dict((s, [u for u in UNITLIST if s in u]) for s in BOXES)
PEERS = dict((s, set(sum(UNITS[s], [])) - set([s])) for s in BOXES)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
