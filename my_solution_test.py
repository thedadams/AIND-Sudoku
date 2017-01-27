import solution
import unittest


class TestSodukoSolutions(unittest.TestCase):
    """
    In the Slack channel, @hug0 posted some hard Sudoku puzzles.
    Then @letyrodri posted the solutions.
    I downloaded these files and tested my code to see if I could solve them.
    """

    def test_hard_sodukos(self):
        "Test the examples."
        puzzles = open("hard_sudokus.txt", 'r')
        solved = open("hard_sudokus_sols.txt", 'r')
        for puzzle, sol in zip(puzzles, solved):
            self.assertEqual(solution.grid_values(sol), solution.solve(puzzle, False))
        puzzles.close()
        solved.close()


if __name__ == '__main__':
    unittest.main()
