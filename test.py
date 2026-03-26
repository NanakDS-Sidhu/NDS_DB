import unittest
import subprocess

def run_script(commands):
    """
    Spawns the database process, feeds it the commands, 
    and returns the output as a single string.
    """
    process = subprocess.Popen(
        ["python3", "REPL.py"], # Make sure your main file is named db.py
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    # Join commands with a newline and send them to the process
    input_data = "\n".join(commands) + "\n"
    stdout, stderr = process.communicate(input_data)
    return stdout

class TestDatabase(unittest.TestCase):
    
    def test_inserts_and_retrieves_row(self):
        result = run_script([
            "insert 1 user1 person1@example.com",
            "select",
            ".exit",
        ])
        self.assertIn("Executed.", result)
        self.assertIn("(1, user1, person1@example.com)", result)

    def test_table_full(self):
        # Python ranges are exclusive at the top, so 1 to 1401
        script = [f"insert {i} user{i} person{i}@example.com" for i in range(1, 1402)]
        script.append(".exit")
        result = run_script(script)
        self.assertIn("Error: Table full.", result)

    def test_max_length_strings(self):
        long_username = "a" * 32
        long_email = "a" * 255
        result = run_script([
            f"insert 1 {long_username} {long_email}",
            "select",
            ".exit",
        ])
        self.assertIn("Executed.", result)
        self.assertIn(f"(1, {long_username}, {long_email})", result)

    def test_strings_too_long(self):
        long_username = "a" * 33
        long_email = "a" * 256
        result = run_script([
            f"insert 1 {long_username} {long_email}",
            "select",
            ".exit",
        ])
        self.assertIn("String is too long.", result)

    def test_negative_id(self):
        result = run_script([
            "insert -1 cstack foo@bar.com",
            "select",
            ".exit",
        ])
        self.assertIn("ID must be positive.", result)

if __name__ == '__main__':
    unittest.main()