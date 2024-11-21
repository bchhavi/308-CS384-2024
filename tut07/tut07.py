import re

# Step 1: Create the input.txt file
passwords = """abc12345
abc
123456789
abcdefg$
abcdefgABHD!@313
abcdefgABHD$$!@313
"""

with open('input.txt', 'w') as f:
    f.write(passwords)

# Function to validate a single password
def validate_password(password, criteria):
    if len(password) < 8:
        print(f"'{password}' - Invalid password. Less than 8 Characters.")
        return False
    
    checks = {
        1: r'[A-Z]',  # Uppercase letters
        2: r'[a-z]',  # Lowercase letters
        3: r'[0-9]',  # Numbers
        4: r'[!@#]'    # Special characters (!, @, #)
    }
    
    for criterion in criteria:
        if not re.search(checks[criterion], password):
            print(f"'{password}' - Invalid password. Missing ", end="")
            if 1 in criteria and not re.search(checks[1], password):
                print("Uppercase letters, ", end="")
            if 2 in criteria and not re.search(checks[2], password):
                print("Lowercase letters, ", end="")
            if 3 in criteria and not re.search(checks[3], password):
                print("Numbers, ", end="")
            if 4 in criteria and not re.search(checks[4], password):
                print("Special characters, ", end="")
            print()
            return False

    print(f"'{password}' - Valid password.")
    return True

# Function to validate passwords from the input file
def validate_password_from_file(filename, criteria):
    valid_count = 0
    invalid_count = 0

    with open(filename, 'r') as file:
        for password in file:
            password = password.strip()
            if validate_password(password, criteria):
                valid_count += 1
            else:
                invalid_count += 1

    print(f"Total Valid Passwords: {valid_count}")
    print(f"Total Invalid Passwords: {invalid_count}")

# Step 2: Get user criteria and validate
print("Select criteria to check:")
print("1 - Uppercase letters (A-Z)")
print("2 - Lowercase letters (a-z)")
print("3 - Numbers (0-9)")
print("4 - Special characters (!, @, #)")
criteria_input = input("Enter your criteria (comma-separated, e.g., 1,3,4): ")
criteria = list(map(int, criteria_input.split(',')))

# Validate passwords from input.txt
validate_password_from_file('input.txt', criteria)