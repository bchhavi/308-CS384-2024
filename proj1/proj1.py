import pandas as pd
import math
from openpyxl import Workbook

########################################### PART 1 ##########################################################################

class SeatingArrangement:
    def __init__(self, buffer_size=5, sparse=False):
        self.students_data = {}
        self.exam_schedule = {}
        self.rooms = {}
        self.buffer_size = buffer_size  
        self.sparse = sparse  

    def load_input(self, students_file, exam_tt_file, room_capacity_file):
        students_df = pd.read_csv(students_file)
        students_df.columns = students_df.columns.str.strip()

        if 'course_code' in students_df.columns and 'rollno' in students_df.columns and 'register_sem' in students_df.columns:
            for _, row in students_df.iterrows():
                course = row['course_code']
                roll_no = row['rollno']
                sem_no = row['register_sem']
                if course not in self.students_data:
                    self.students_data[course] = []
                self.students_data[course].append((roll_no, sem_no, course))
        else:
            print("Error: Required columns missing in students_file.")
            return

        exam_tt_df = pd.read_csv(exam_tt_file)
        exam_tt_df.columns = exam_tt_df.columns.str.strip()

        if 'Date' in exam_tt_df.columns and 'Day' in exam_tt_df.columns:
            for _, row in exam_tt_df.iterrows():
                date = row['Date']
                day = row['Day']
                if 'Morning' in row and pd.notna(row['Morning']):
                    morning_courses = row['Morning'].split(';')
                    for course in [c.strip() for c in morning_courses]:
                        self.exam_schedule[course] = (date, day, "Morning")
                if 'Evening' in row and pd.notna(row['Evening']):
                    evening_courses = row['Evening'].split(';')
                    for course in [c.strip() for c in evening_courses]:
                        self.exam_schedule[course] = (date, day, "Evening")
        else:
            print("Error: 'Date' or 'Day' column is missing in exam_tt_file.")
            return

        room_capacity_df = pd.read_csv(room_capacity_file)
        room_capacity_df.columns = room_capacity_df.columns.str.strip()

        if 'room_no' in room_capacity_df.columns and 'capacity' in room_capacity_df.columns:
            for _, row in room_capacity_df.iterrows():
                room = row['room_no']
                capacity = row['capacity']
                if room not in self.rooms:
                    self.rooms[room] = capacity
        else:
            print("Error: 'room_no' or 'capacity' column is missing in room_capacity_file.")
            return

    def arrange_seating(self):
        arrangement = []

        sorted_courses = sorted(self.students_data.items(), key=lambda x: len(x[1]), reverse=True)

        def room_sort_key(room):
            room_no = room[0]
            if room_no.isdigit():
                return (int(room_no) // 100, -self.rooms[room_no])
            else:
                numeric_part = ''.join(filter(str.isdigit, room_no))
                return (999, -self.rooms[room_no])

        sorted_rooms = sorted(self.rooms.items(), key=room_sort_key)
        room_allocation_counter = {}

        for course, students in sorted_courses:
            total_students = len(students)
            students_allocated = 0
            date, day, shift = self.exam_schedule.get(course, (None, None, None))

            if not date or not shift:
                continue

            if date not in room_allocation_counter:
                room_allocation_counter[date] = {"Morning": 0, "Evening": 0}

            for i in range(room_allocation_counter[date][shift], len(sorted_rooms)):
                room, capacity = sorted_rooms[i]
                if students_allocated >= total_students:
                    break
                available_seats = capacity - self.buffer_size
                if available_seats <= 0:
                    available_seats = capacity
                if self.sparse:
                    max_per_course = math.ceil(available_seats / 2)
                else:
                    max_per_course = available_seats

                students_for_room = min(max_per_course, total_students - students_allocated)
                allocated_students = students[students_allocated:students_allocated + students_for_room]
                roll_list = ";".join([s[0] for s in allocated_students])
                arrangement.append({
                    'Date': date,
                    'Day': day,
                    'Shift': shift,
                    'course_code': course,
                    'Room': room,
                    'Allocated_students_count': students_for_room,
                    'Roll_list (semicolon separated)': roll_list
                })
                students_allocated += students_for_room
                room_allocation_counter[date][shift] = i + 1

        arrangement.sort(key=lambda x: pd.to_datetime(x['Date'], dayfirst=True))
        return arrangement

    def write_output(self, output_file_csv, output_file_excel, arrangement):
        df = pd.DataFrame(arrangement)
        df.to_csv(output_file_csv, index=False)
        df.to_excel(output_file_excel, index=False)
        print(f"Seating arrangement written to {output_file_csv} and {output_file_excel}")

students_file = '/content/ip_1.csv'  
exam_tt_file = '/content/ip_2.csv'  
room_capacity_file = '/content/ip_3.csv' 
output_file_csv = '/content/op_1.csv'  
output_file_excel = '/content/op_1.xlsx'  
buffer_size = int(input("Enter buffer size (0 for no buffer): "))
sparse_option = input("Enter seating arrangement type ('dense' or 'sparse'): ").strip().lower() == 'sparse'
seating = SeatingArrangement(buffer_size=buffer_size, sparse=sparse_option)
seating.load_input(students_file, exam_tt_file, room_capacity_file)
arrangement = seating.arrange_seating()
seating.write_output(output_file_csv, output_file_excel, arrangement)


########################################### PART 2 ##########################################################################

att_fp = "/content/op_1.xlsx"  
st_fp = "/content/ip_4.csv" 
att_data = pd.read_excel(att_fp)
att_data.columns = att_data.columns.str.strip()  
st_info = pd.read_csv(st_fp)
st_info.columns = st_info.columns.str.strip() 
st_info['Roll'] = st_info['Roll'].astype(str).str.strip() 
roll_to_name = dict(zip(st_info['Roll'], st_info['Name']))
wb = Workbook()
wb.remove(wb.active)

for _, att_record in att_data.iterrows():
    att_date = pd.to_datetime(att_record['Date']).strftime("%d_%m_%Y") 
    courseid = att_record['course_code']
    classno = att_record['Room']
    sess = att_record['Shift'].lower()  
    sheet_identifier = f"{att_date}{courseid}{classno}_{sess}"
    rollcol = 'Roll_list (semicolon separated)'  
    roll = att_record[rollcol].split(';') if pd.notna(att_record[rollcol]) else []
    sheet = wb.create_sheet(title=sheet_identifier[:31])
    sheet['A1'] = 'Roll No'
    sheet['B1'] = 'Name'
    sheet['C1'] = 'Signature'
    index = 2
    for r in roll:
      cleaned_roll = r.strip()
      sheet[f'A{index}'] = cleaned_roll
      sheet[f'B{index}'] = roll_to_name.get(cleaned_roll, "Unknown")
      sheet[f'C{index}'] = ''
      index += 1

out_fp = "Attendance_Sheet.xlsx" 
wb.save(out_fp)