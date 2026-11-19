# Hostel Room Allocation and Maintenance Complaint System
# Course: Computational Thinking and Programming (2026CSAE100)

import csv
import os

ROOMS_FILE = "rooms.csv"
STUDENTS_FILE = "students.csv"
COMPLAINTS_FILE = "complaints.csv"

CATEGORIES = ["Furniture", "Plumbing", "Electrical", "Cleaning", "Other"]
STATUSES = ["Pending", "In Progress", "Resolved"]
MENU = ["Allocate Room", "Log Complaint", "Update Complaint Status",
        "View Summary", "Exit"]


# ---------------- File handling ----------------

def load_rooms():
    rooms = []
    if not os.path.exists(ROOMS_FILE):
        # first run: make 10 rooms (101-105 hold 2 students, 201-205 hold 3)
        for n in range(101, 106):
            rooms.append({"room_no": str(n), "capacity": 2, "occupied": 0})
        for n in range(201, 206):
            rooms.append({"room_no": str(n), "capacity": 3, "occupied": 0})
        return rooms
    f = open(ROOMS_FILE, "r")
    reader = csv.DictReader(f)
    for row in reader:
        rooms.append({"room_no": row["room_no"],
                      "capacity": int(row["capacity"]),
                      "occupied": int(row["occupied"])})
    f.close()
    return rooms


def load_students():
    students = []
    if not os.path.exists(STUDENTS_FILE):
        return students
    f = open(STUDENTS_FILE, "r")
    reader = csv.DictReader(f)
    for row in reader:
        students.append(row)
    f.close()
    return students


def load_complaints():
    complaints = []
    if not os.path.exists(COMPLAINTS_FILE):
        return complaints
    f = open(COMPLAINTS_FILE, "r")
    reader = csv.DictReader(f)
    for row in reader:
        complaints.append(row)
    f.close()
    return complaints


def save_all(rooms, students, complaints):
    # three parallel lists: file name, its column names, and its records
    files = [ROOMS_FILE, STUDENTS_FILE, COMPLAINTS_FILE]
    columns = [["room_no", "capacity", "occupied"],
               ["enrollment", "name", "room_no"],
               ["id", "enrollment", "room_no",
                "category", "description", "status"]]
    tables = [rooms, students, complaints]

    # zip() walks the three lists together, one file at a time
    for filename, fieldnames, records in zip(files, columns, tables):
        f = open(filename, "w", newline="")
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
        f.close()


# ---------------- Helper functions ----------------

def find_student(students, enrollment):
    for s in students:
        if s["enrollment"] == enrollment:
            return s
    return None


def find_room(rooms, room_no):
    for r in rooms:
        if r["room_no"] == room_no:
            return r
    return None


def get_choice(low, high):
    # keeps asking until the user enters a number between low and high
    while True:
        try:
            choice = int(input("Enter your choice: "))
            if choice >= low and choice <= high:
                return choice
            else:
                print("Please enter a number from", low, "to", high)
        except ValueError:
            print("Invalid input! Please enter a number.")


# ---------------- Main features ----------------

def allocate_room(rooms, students):
    print("\n--- Room Allocation ---")
    enrollment = input("Enter enrollment number: ").strip().upper()
    if enrollment == "":
        print("Enrollment number cannot be empty.")
        return

    # a student can only have one room
    old = find_student(students, enrollment)
    if old is not None:
        print("This student already has room", old["room_no"])
        return

    name = input("Enter student name: ").strip()
    if name == "":
        print("Name cannot be empty.")
        return

    print("\nVacant rooms:")
    count = 0
    for r in rooms:
        if r["occupied"] < r["capacity"]:
            vacant = r["capacity"] - r["occupied"]
            print("Room", r["room_no"], "- vacant beds:", vacant)
            count = count + 1
    if count == 0:
        print("Sorry, the hostel is full!")
        return

    room_no = input("Enter room number to allot: ").strip()
    room = find_room(rooms, room_no)
    if room is None:
        print("Room does not exist.")
    elif room["occupied"] >= room["capacity"]:
        print("Room", room_no, "is full. Capacity exceeded, try another room.")
    else:
        room["occupied"] = room["occupied"] + 1
        students.append({"enrollment": enrollment, "name": name,
                         "room_no": room_no})
        print("Room", room_no, "allotted to", name)


def log_complaint(students, complaints):
    print("\n--- Log a Complaint ---")
    enrollment = input("Enter enrollment number: ").strip().upper()
    student = find_student(students, enrollment)
    if student is None:
        print("Student not found. Please get a room allotted first.")
        return

    print("\nComplaint categories:")
    # enumerate() gives the number and the category together
    for i, cat in enumerate(CATEGORIES, start=1):
        print(str(i) + ".", cat)
    choice = get_choice(1, len(CATEGORIES))
    category = CATEGORIES[choice - 1]

    description = input("Describe the problem: ").strip()
    if description == "":
        print("Description cannot be empty.")
        return

    # new id = number of complaints + 1
    new_id = str(len(complaints) + 1)
    complaints.append({"id": new_id,
                       "enrollment": enrollment,
                       "room_no": student["room_no"],
                       "category": category,
                       "description": description,
                       "status": "Pending"})
    print("Complaint registered successfully. Complaint ID:", new_id)


def show_complaints(complaints):
    print("\nID | Room | Category   | Status      | Description")
    print("-" * 60)
    for c in complaints:
        print(c["id"], "|", c["room_no"], "|", c["category"], "|",
              c["status"], "|", c["description"])


def update_status(complaints):
    print("\n--- Update Complaint Status ---")
    if len(complaints) == 0:
        print("No complaints have been registered yet.")
        return

    show_complaints(complaints)
    cid = input("\nEnter complaint ID to update: ").strip()

    found = None
    for c in complaints:
        if c["id"] == cid:
            found = c
    if found is None:
        print("Complaint ID not found.")
        return

    print()
    # enumerate() numbers the statuses: 1. Pending, 2. In Progress, ...
    for i, status in enumerate(STATUSES, start=1):
        print(str(i) + ".", status)
    choice = get_choice(1, len(STATUSES))
    found["status"] = STATUSES[choice - 1]
    print("Complaint", cid, "is now", found["status"])


# ---------------- Summary report ----------------

def view_summary(rooms, complaints):
    print("\n========== HOSTEL SUMMARY REPORT ==========")
    print("Room No | Capacity | Persons Present | Occupancy")
    total_capacity = 0
    total_occupied = 0
    for r in rooms:
        percent = r["occupied"] / r["capacity"] * 100
        print(r["room_no"], "    |", r["capacity"], "       |",
              r["occupied"], "               |", round(percent), "%")
        total_capacity = total_capacity + r["capacity"]
        total_occupied = total_occupied + r["occupied"]

    overall = total_occupied / total_capacity * 100
    print("\nTotal beds:", total_capacity)
    print("Beds occupied:", total_occupied)
    print("Beds vacant:", total_capacity - total_occupied)
    print("Overall occupancy:", round(overall, 1), "%")

    # count complaints for each status (one count per item in STATUSES)
    status_counts = []
    for status in STATUSES:
        n = 0
        for c in complaints:
            if c["status"] == status:
                n = n + 1
        status_counts.append(n)

    print("\nTotal complaints:", len(complaints))
    # zip() pairs each status name with its count
    for status, n in zip(STATUSES, status_counts):
        print(status + ":", n)

    # count complaints by category using a dictionary
    by_category = {}
    for c in complaints:
        cat = c["category"]
        if cat in by_category:
            by_category[cat] = by_category[cat] + 1
        else:
            by_category[cat] = 1
    if len(by_category) > 0:
        print("\nComplaints by category:")
        for cat in by_category:
            print(cat, ":", by_category[cat])
    print("==========================================")


# ---------------- Main program ----------------

def main():
    rooms = load_rooms()
    students = load_students()
    complaints = load_complaints()
    print("Data loaded:", len(students), "students,",
          len(complaints), "complaints.")

    while True:
        print("\n=== HOSTEL MANAGEMENT SYSTEM ===")
        # enumerate() numbers the menu options from 1
        for i, option in enumerate(MENU, start=1):
            print(str(i) + ".", option)
        choice = get_choice(1, len(MENU))

        if choice == 1:
            allocate_room(rooms, students)
        elif choice == 2:
            log_complaint(students, complaints)
        elif choice == 3:
            update_status(complaints)
        elif choice == 4:
            view_summary(rooms, complaints)
        else:
            save_all(rooms, students, complaints)
            print("All data saved. Goodbye!")
            break


main()