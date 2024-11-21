def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

def rotate_number(n):
    rotations = []
    num_digits = 0
    temp = n
    while temp > 0:  # Calculate the number of digits
        num_digits += 1
        temp //= 10
    factor = 10 ** (num_digits - 1)  # Calculate the factor for rotation
    for _ in range(num_digits):
        rotations.append(n)
        last_digit = n % 10  # Get the last digit
        n = (last_digit * factor) + (n // 10)  # Rotate the number
    return rotations

def is_rotational_prime(n):
    rotations = rotate_number(n)
    for rotation in rotations:
        if not is_prime(rotation):
            return False
    return True

# Input from the user
num = int(input("Enter a number: "))
if is_rotational_prime(num):
    print(f"{num} is a Rotational prime.")
else:
    print(f"{num} is not a Rotational prime.")