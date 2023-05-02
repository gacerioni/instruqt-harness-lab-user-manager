import csv
import sys
import time


import pandas as pd
from student import Student
from custom_exceptions import NoAvailableStudentSlots

# I'll remove these consts before releasing it
CSV_DB = "students.csv"
DEFAULT_PWD = "nyKujrC75qHL"
CSV_COLUMNS: list[str] = ["email", "password", "harness_project", "is_taken", "slot_time_taken"]


def get_student_list(csv_student_file):
    student_list = []
    with open(csv_student_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            student = Student(email=row["email"], password=get_student_password(),
                              harness_project=row["harness_project"], is_taken=row["is_taken"],
                              slot_time_taken=row["slot_time_taken"])
            student_list.append(student)
            line_count += 1
        print(f'Processed {line_count} lines.')

        return student_list


def get_student_password(email="p1901@harness.labs"):
    return "nyKujrC75qHL"


def mark_student_as_taken(email):
    epoch_time = int(time.time())
    # Reading the CSV file and set the index to the "ID" column
    df = pd.read_csv(CSV_DB, index_col="email", dtype=object)

    # updating a cell based on the index (ID) and column.
    df.at[email, 'is_taken'] = '1'
    df.at[email, 'slot_time_taken'] = epoch_time

    # Reset index to 0,1,2,...
    df = df.reset_index()

    # writing the changes into the file.
    df.to_csv(CSV_DB, index=False)


def get_available_student_slot():
    # Load the students list
    students_list = get_student_list(CSV_DB)

    try:
        # Filter the students that are free
        avail_student_slots = [stu for stu in students_list if stu.is_taken == '0']

        if not bool(avail_student_slots):
            raise NoAvailableStudentSlots
        else:
            print("Found available student slots!")
            for slots in avail_student_slots:
                print("Student {} is available!".format(slots.email))
    except NoAvailableStudentSlots:
        print("Exception occurred: No student slots are available!")
        sys.exit(1)

    # We have some available slots. Let me take one for you.
    final_student_slot = avail_student_slots[0]
    # and then we mark is as taken
    mark_student_as_taken(avail_student_slots[0].email)

    return final_student_slot
