import sqlite3
import matplotlib.pyplot as plt
import numpy as np

connection = sqlite3.connect('hotel.db')
cursor = connection.cursor()


# Линейный график
cursor.execute("""SELECT strftime('%m', date_start), COUNT(guest_id) as counter
                FROM guest_rooms
                GROUP BY strftime('%m', date_start);""")

arrival_data = cursor.fetchall()
months = []
arrives = []

for line in arrival_data:
    months.append(line[0])
    arrives.append(line[1])

arrives_for_medians = np.full(np.size(arrives), np.mean(arrives))

plt.title('Сравнение спроса на номера по месяцам')
# график заселений по месяцам
plt.plot(months, arrives, 'm--', linewidth=3)
# медиана
plt.plot(months, arrives_for_medians, 'b-.', linewidth=1)
plt.xlabel("Месяц, номер")
plt.ylabel("Число заселяющихся гостей")
plt.show()


# Столбчатая диаграмма
cursor.execute("""SELECT procedures.procedure_id, COUNT(guest_id)
                FROM guest_procedures
                LEFT JOIN procedures ON procedures.procedure_id=guest_procedures.procedure_id
                GROUP BY procedures.procedure_id""")

procedures_data = cursor.fetchall()
procedure_ids = []
procedure_usings = []

for line in procedures_data:
    procedure_ids.append(line[0])
    procedure_usings.append(line[1])

plt.bar(procedure_ids, procedure_usings)
plt.title('Сравнение спроса на процедуры')
plt.xlabel("Номер процедуры")
plt.ylabel("Количество проделанных процедур")
plt.show()


# Многорядная столбчатая сложенная диаграмма
series1 = []
series2 = []

periods = ["0 AND '03'", "'04' AND '06'", "'07' AND '09'", "'10' AND '12'"]

for period in periods:
    cursor.execute("""SELECT sum(rooms.price) / 1000000
        FROM rooms
        LEFT JOIN guest_rooms ON rooms.room_number=guest_rooms.room_number
        WHERE strftime('%m', guest_rooms.date_start) BETWEEN """ + period)

    series1.append(cursor.fetchone())

for period in periods:
    cursor.execute("""SELECT sum(procedures.price) / 1000000
                FROM procedures
                LEFT JOIN guest_procedures ON procedures.procedure_id=guest_procedures.procedure_id
                WHERE strftime('%m', guest_procedures.date) BETWEEN """ + period)

    series2.append(cursor.fetchone())

for i in range(4):
    series1[i] = series1[i][0]
    series2[i] = series2[i][0]

index = np.arange(4)
plt.title('Соотношение доходов с процедур и сдачи номеров')
plt.bar(index, series1, color='r')
plt.bar(index, series2, color='b', bottom=np.array(series1))
plt.xticks(index, ['Квартал 1', 'Квартал 2', 'Квартал 3', 'Квартал 4'])
plt.xlabel("Кварталы")
plt.ylabel("Выручка, млн. рублей")
plt.show()


# Многорядная столбчатая диаграмма
series = [[], [], []]

age_categories = ["guests.age < 18", "guests.age >= 18 AND guests.age < 60",
                  "guests.age >= 60"]

for i in range(len(age_categories)):
    cursor.execute("""
    SELECT COUNT(guest_id)
    FROM (SELECT guest_procedures.procedure_id, guest_procedures.guest_id
    FROM guest_procedures
    LEFT JOIN guests ON guests.guest_id=guest_procedures.guest_id
    WHERE (""" + age_categories[i] + """)) AS A
    GROUP BY A.procedure_id""")

    series[i] = cursor.fetchall()
    for j in range(5):
        series[i][j] = series[i][j][0]

index = np.arange(5)
bw = 0.1

plt.title('Распределение популярности процедур по возрастам')
plt.bar(index, series[0], bw, color='r')
plt.bar(index+bw, series[1], bw, color='g')
plt.bar(index+2*bw, series[2], bw, color='b')
plt.xticks(index+2*bw, ['1', '2', '3', '4', '5'])
plt.xlabel("Процедура, №")
plt.ylabel("Обращения, количество")
plt.show()

# Круговая диаграмма
series = []
for category in age_categories:
    cursor.execute("""SELECT COUNT(guest_rooms.guest_id)
                    FROM guest_rooms
                    LEFT JOIN guests ON guests.guest_id = guest_rooms.guest_id
                    WHERE (""" + category + """);""")

    series.append(cursor.fetchone()[0])

labels = ["До 18 лет", "18-60 лет", "60+ лет"]
plt.pie(series, labels=labels)
plt.axis('equal')
plt.title('Распределение гостей по возрастам')
plt.show()