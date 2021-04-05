import sqlite3
import random
import names
import datetime

db_connection = sqlite3.connect('hotel.db')
cursor = db_connection.cursor()

creation_queries = ["""
    CREATE TABLE IF NOT EXISTS guests(
        guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
        surname TEXT NOT NULL,
        name TEXT NOT NULL,
        second_name TEXT,
        age INTEGER NOT NULL,
        passport_number INTEGER);""", """
    CREATE TABLE IF NOT EXISTS rooms (
       room_number INTEGER PRIMARY KEY,
       quantity INTEGER NOT NULL,
       price REAL NOT NULL,
       description TEXT);""", """
    CREATE TABLE IF NOT EXISTS procedures(
        procedure_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        duration_mins INTEGER NOT NULL);""", """
    CREATE TABLE IF NOT EXISTS guest_rooms(
        unnecessary_column INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_id INTEGER NOT NULL,
        room_number INTEGER NOT NULL,
        date_start DATE NOT NULL,
        date_end DATE NOT NULL,
        FOREIGN KEY (guest_id) REFERENCES guests(guest_id),
        FOREIGN KEY (room_number) REFERENCES rooms(room_number));""", """
    CREATE TABLE IF NOT EXISTS guest_procedures(
        unneccessary_column INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_id INTEGER NOT NULL,
        procedure_id INTEGER NOT NULL,
        date DATE NOT NULL,
        FOREIGN KEY (guest_id) REFERENCES guests(guest_id),
        FOREIGN KEY (procedure_id) REFERENCES procedures(procedure_id));
    """]

# let our db work with foreign keys
cursor.execute("PRAGMA foreign_keys=ON")
db_connection.commit()

for query in creation_queries:
  cursor.execute(query)

# rooms
numbers = list(range(100, 1000))
basic_cost = 5000
rooms = []

for number in numbers:
  quantity = random.randint(1, 4)
  rooms.append((number, quantity, float(quantity * basic_cost)))

cursor.executemany("INSERT INTO rooms(room_number, quantity, price) VALUES (?,?,?)", rooms)

# guests
guests = []
for i in range(10000):
  guests.append((names.get_last_name(), names.get_first_name(), random.randint(10, 100)))

cursor.executemany("INSERT INTO guests (surname, name, age) VALUES (?, ?, ?)", guests)

# procedures
procedure_names = ["Ванна индивидуальная с радоновой водой","Горизонтальное подводное вытяжение позвоночника",
"Ванна индивидуальная травяная",
"Циркулярный душ",
"Мануальная терапия, кинезитерапия (взрослый)"]
procedures = []

for name in procedure_names:
  procedures.append((name, "{:.2f}".format(basic_cost // random.randint(10, 50)), random.randint(30, 90)))

cursor.executemany("INSERT INTO procedures (name, price, duration_mins) VALUES (?, ?, ?)", procedures)

# guest_rooms
guest_rooms = []
cursor.execute("SELECT room_number FROM rooms", )
rooms_set = cursor.fetchall()

cursor.execute("SELECT guest_id FROM guests", )
guests_set = cursor.fetchall()

for element_set in guests_set:
  for i in range(random.randint(1, 3)):
    start_date = datetime.date(year = 2020, month = 1, day = 1).toordinal()
    end_date = datetime.date(year = 2020, month = 12, day = 28).toordinal()
    random_day = datetime.date.fromordinal(random.randint(start_date, end_date))
    random_day_end = datetime.date.fromordinal(random.randint(random_day.toordinal() + 3, random_day.toordinal() + 14))
    guest_rooms.append((element_set[0], random.choice(rooms_set)[0], random_day, random_day_end))
  
cursor.executemany("INSERT INTO guest_rooms (guest_id, room_number, date_start, date_end) VALUES (?, ?, ?, ?)", guest_rooms)

# guest_procedures
guest_procedures = []
cursor.execute("SELECT guest_id, date_start, date_end FROM guest_rooms", )
guest_living_set = cursor.fetchall()

for element_set in guest_living_set:
  start_date = datetime.datetime.strptime(element_set[1], "%Y-%m-%d").toordinal()
  end_date = datetime.datetime.strptime(element_set[2], "%Y-%m-%d").toordinal()
  random_day = datetime.date.fromordinal(random.randint(start_date, end_date))
  guest_procedures.append((element_set[0], random.randint(1, 5), random_day))

cursor.executemany("INSERT INTO guest_procedures (guest_id, procedure_id, date) VALUES (?, ?, ?)", guest_procedures)

db_connection.commit()

# check lines
cursor.execute("SELECT COUNT(*) FROM rooms", )
print("rooms: ", cursor.fetchone()[0])
cursor.execute("SELECT COUNT(*) FROM guests", )
print("guests: ", cursor.fetchone()[0])
cursor.execute("SELECT COUNT(*) FROM procedures", )
print("procedures: ", cursor.fetchone()[0])
cursor.execute("SELECT COUNT(*) FROM guest_rooms", )
print("guest_rooms: ", cursor.fetchone()[0])
cursor.execute("SELECT COUNT(*) FROM guest_procedures", )
print("guest_procedures: ", cursor.fetchone()[0])