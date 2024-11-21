def add_or_update_student(a, b, c):
    b = b.lower()
    c[b] = a

def calculate_average(a):
    return sum(a) / len(a) if a else 0

def print_students_with_average(c):
    d = {}
    for b, a in c.items():
        d[b] = calculate_average(a)
    for b, a in d.items():
        print(f"{b.capitalize()} - Average: {a:.2f}")

def get_average(e):
    return calculate_average(e[1])

def sort_students_by_grades(c):
    d = list(c.items())
    for i in range(len(d)):
        for j in range(i + 1, len(d)):
            if get_average(d[i]) < get_average(d[j]):
                d[i], d[j] = d[j], d[i]
    return d

def main():
    c = {}
    
    while True:
        print("\nOptions:")
        print("1. Add or update student grades")
        print("2. Print all students with their average grades")
        print("3. Sort students by average grades")
        print("4. Exit")
        
        e = input("Enter your choice (1-4): ")
        
        if e == '1':
            b = input("Enter student name: ")
            a = list(map(int, input("Enter grades separated by spaces: ").split()))
            add_or_update_student(a, b, c)
        
        elif e == '2':
            print("\nStudent averages:")
            print_students_with_average(c)
        
        elif e == '3':
            d = sort_students_by_grades(c)
            print("\nSorted students by average grade (descending):")
            for b, a in d:
                avg = get_average((b, a))
                print(f"{b.capitalize()} - Average: {avg:.2f}")
        
        elif e == '4':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()