stack = []

input_string = input("Enter a string containing brackets: ")

for char in input_string:
    if char in '{[(':
        stack.append(char)
    elif char in '}])':
        if len(stack) == 0:
            print("false")
            break
        top = stack[-1]
        if (top == '{' and char == '}') or (top == '[' and char == ']') or (top == '(' and char == ')'):
            stack.pop()
        else:
            print("false")
            break
else:
    if len(stack) == 0:
        print("true")
    else:
        print("false")
