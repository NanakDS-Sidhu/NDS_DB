import unittest
import subprocess
import os

def run_script(commands):
    """
    Spawns the database process, feeds it the commands, 
    and returns the output. Now it includes the filename argument!
    """
    process = subprocess.Popen(
        ["python3", "REPL.py", "test.db"], # Added "test.db" argument
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    input_data = "\n".join(commands) + "\n"
    stdout, stderr = process.communicate(input_data)
    return stdout

class TestDatabase(unittest.TestCase):
    
    def setUp(self):
        """
        This runs automatically before EACH test.
        It ensures we start with a fresh database file every time.
        """
        if os.path.exists("test.db"):
            os.remove("test.db")

    # ... [Keep your existing tests here: test_inserts_and_retrieves_row, etc.] ...

    def test_keeps_data_after_closing_connection(self):
        """
        Tests that data is actually saved to the hard drive.
        We run the script once to insert, and a SECOND time to select.
        """
        # First connection: Insert a row
        result1 = run_script([
            "insert 1 user1 person1@example.com",
            ".exit",
        ])
        self.assertIn("Executed.", result1)

        # Second connection: Open the same file and read the row
        result2 = run_script([
            "select",
            ".exit",
        ])
        self.assertIn("(1, user1, person1@example.com)", result2)

if __name__ == '__main__':
    unittest.main()