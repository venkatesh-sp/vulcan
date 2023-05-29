import random
import string
import os
import uuid


def generate_random_text(length):
    """Generate random text of a given length."""
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def generate_random_text_file(filename, num_lines, line_length):
    """Generate a random text file with a given number of lines and line length."""
    with open(filename, "w") as file:
        for _ in range(num_lines):
            line = generate_random_text(line_length)
            file.write(line + "\n")


num_lines = 10
line_length = 50

os.makedirs("text_files", exist_ok=True)

for _ in range(5001):
    uid = uuid.uuid4().hex
    file_name = f"{uid}.txt"
    generate_random_text_file(f"text_files/{file_name}", num_lines, line_length)
