assignments = []


def update_units_for_diagonal():
    """
    If we are doing a diagonal sudoku, then we update
    the units and peers to include the diagonals.
    """
    # Add the diagonals to the unit list.
    UNITLIST.extend(DIAGONAL_UNITS)
    # For every box in the diagonals, we update the units and peers dict.
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
    twins = []
    for box in BOXES:
        if len(values[box]) == 2:
            # We have a possible twin.
            for other_box in PEERS[box]:
                if values[other_box] == values[box]:
                    # We found a twin for this box.
                    twins.append([box, other_box])

    # Eliminate the naked twins as possibilities for their peers
    for box1, box2 in twins:
        # If we already removed a value for a naked twin, then we no longer have a naked twin.
        if len(values[box1]) < 2 or len(values[box2]) < 2:
            continue

        # For all common peers, we remove the twin values.
        for box in PEERS[box1] & PEERS[box2]:
            if len(values[box]) > 1:
                assign_value(values, box, values[box].replace(
                    values[box1][0], "").replace(values[box1][1], ""))
    return values


def hidden_twins(values):
    """
    Eliminate values using the hidden twins strategy.
    Args:
        values(dict): The soduko puzzle in dictionary form.
    Returns:
        the values dictionary with any hidden twins turned into naked twins.
    """
    # Start the same as only choice.
    for unit in UNITLIST:
        for digit in COLS:
            with_digit = [b for b in unit if digit in values[b]]
            # See if we found a possible hidden pair, and not a naked pair.
            if len(with_digit) == 2 and (len(values[with_digit[0]]) > 2 or len(values[with_digit[1]]) > 2):
                for digit2 in values[with_digit[0]]:
                    if digit2 != digit and digit2 in values[with_digit[1]] and len([b for b in unit if digit2 in values[b]]) == 2:
                        # We found a hidden pair so we turn it into a naked pair.
                        assign_value(values, with_digit[0], digit + digit2)
                        assign_value(values, with_digit[1], digit + digit2)
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
    # Loop through the string and add the values.
    # If we get a '.', then we set the value to be '123456789'
    while index < len(BOXES):
        values[BOXES[index]] = grid[index] if grid[index] != '.' else COLS
        index += 1
    return values


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    # Taken for the online course to avoid the calculations.
    width = 1 + max(len(values[s]) for s in values.keys())
    line = '+'.join(['-' * (width * 3)] * 3)
    for row in ROWS:
        print(''.join(values[row + col].center(width) +
                      ('|' if col in '36' else '') for col in COLS))
        if row in 'CF':
            print(line)
    print()


def eliminate(values):
    """
    Find all boxes that have only one possibility, then remove that value
    from all of its peers.
    Args:
        values(dict): The sudoku in dictionary form.
    """
    # Find all the boxes that have only one possible value.
    only_one_value = [box for box in BOXES if len(values[box]) == 1]
    for box in only_one_value:
        # Eliminate this value from all peers.
        for other_box in PEERS[box]:
            assign_value(values, other_box, values[other_box].replace(values[box], ""))
    return values


def only_choice(values):
    """
    If a box is the only one in its unit that can have a certain value, we assign its value.
    Args:
        values(dict): The soduko in dictionary form.
    Returns:
        The soduko in dictionary form.
    """
    for unit in UNITLIST:
        for val in COLS:
            # All boxes with this possible value.
            box_with_val = [box for box in unit if val in values[box]]
            # If there is only one such box, then it must get this value.
            if len(box_with_val) == 1:
                assign_value(values, box_with_val[0], val)
    return values


def reduce_puzzle(values):
    """
    Use constraint propagation to reduce the soduko puzzle.
    Args:
        values(dict): The soduko in dictionary form.
    Returns:
        values(dict):
        The reduced soduko puzzle, if we didn't run into a problem.
        None if we can't find a solution.
    """
    stalled = False
    # While we haven't stalled, keep reducing.
    while not stalled:
        # How many boxes are solved now.
        num_solved_before = len([box for box in values if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        # Add my hidden_twins implementation.
        values = hidden_twins(values)
        values = naked_twins(values)
        # If we reduced any box down to no possibilities, then we don't have a solution.
        if any([len(val) == 0 for val in values.values()]):
            return None
        # How many boxes are solved now.
        num_solved_after = len([box for box in values if len(values[box]) == 1])
        # If we didn't change the number of solved boxes, then we have stalled.
        stalled = num_solved_before == num_solved_after
    return values


def solve(grid, diagonal=True):
    """
     Find the solution to a Sudoku grid.
     Args:
         grid(string): a string representing a sudoku grid.
             Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
     Returns:
         The solved soduko puzzle in dictionary form or None if there is no solution.
     """
    values = grid_values(grid)
    if diagonal:
        update_units_for_diagonal()
    return search(values)


def search(values):
    """
    Combine constraint propagation with DFS to solve the puzzle.
    Args:
        values(dict): The soduko is dictionary form.
    Returns:
        The solved puzzle in dictionary form if we found a solution
        None if we don't find one.
    """
    # Constraint propagation first.
    values = reduce_puzzle(values)
    # If we ran into a problem, then we return None.
    if values is None:
        return None
    # If all boxes have only one value, then we found a solution.
    if all([len(values[b]) == 1 for b in values.keys()]):
        return values
    # Find a box that is not solved with the smallest number of possible values.
    min_values = 10
    next_box = ""
    for b, vals in values.items():
        if len(vals) > 1 and len(vals) < min_values:
            min_values = len(vals)
            next_box = b

    # For each value for the next box, we try to solve.
    for value in values[next_box]:
        new_values = values.copy()
        assign_value(new_values, next_box, value)
        # Try this soluion
        possible_sol = search(new_values)
        # If we didn't get None, then we have a solution.
        if possible_sol is not None:
            return possible_sol
    return None


# Do this once now to avoid doing it many times.
ROWS = 'ABCDEFGHI'
COLS = '123456789'
BOXES = cross(ROWS, COLS)
ROW_UNITS = [cross(r, COLS) for r in ROWS]
COL_UNITS = [cross(ROWS, c) for c in COLS]
SQUARE_UNITS = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
# The diagonal units.
DIAGONAL_UNITS = [["".join(a) for a in zip(ROWS, COLS)], ["".join(a)
                                                          for a in zip(ROWS, reversed(COLS))]]
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
