import mysql.connector
import json
import os

def connect():
    db = mysql.connector.connect(
        host="35.239.77.128",
        user="root",
        password="Elansing890-",
        database="tfrrs_replication"
    )
    return db

def populate_gender(db, cursor):
    sql = "INSERT INTO gender (id, name) VALUES (%s, %s)"
    val = [(1, "men"),
           (2, "women")]
    cursor.executemany(sql, val)
    db.commit()
    print(cursor.rowcount, "record inserted.")

def populate_division(db, cursor):
    sql = "INSERT INTO division (id, name, initial) VALUES (%s, %s, %s)"
    val = [(1, "Division 1", "DI"),
           (2, "Division 2", "DII"),
           (3, "Division 3", "DIII")]
    cursor.executemany(sql, val)
    db.commit()
    print(cursor.rowcount, "record inserted.")

def populate_grade_level(db, cursor):
    sql = "INSERT INTO grade_level (id, year) VALUES (%s, %s)"
    val = [(1, "FR-1"),
           (2, "SO-2"),
           (3, "JR-3"),
           (4, "SR-4")]
    cursor.executemany(sql, val)
    db.commit()
    print(cursor.rowcount, "record inserted.")

def populate_event_distance(db, cursor):
    path_to_json = "/Users/pbierach/Desktop/tffrs_replication/json/meets"
    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
        with open(path_to_json + file_name) as json_file:
            data = json.load(json_file)


def populate_location(db, cursor):
    path_to_json = "/Users/pbierach/Desktop/tffrs_replication/json/meets/"
    locations = set()
    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
        with open(path_to_json + file_name) as json_file:
            data = json.load(json_file)
            for doc in data:
                loc = doc['location']
                comma = loc.find(",")
                city = loc[0:comma]
                if len(city) == 0:
                    print(doc['name'] + " " + doc['date'])
                elif len(city) <=2:
                    print(doc['name'] + " " + doc['date'])
                elif not city[0].isupper():
                    print(doc['name'] + " " + doc['date'])
                else:
                    locations.add(doc['location'])
    val = []
    for element in locations:
        comma = element.find(",")
        city = element[0:comma]
        state = element[comma+1:len(element)+1].strip()
        val.append(tuple([city, state]))

    sql = "INSERT INTO location (city, state) VALUES (%s, %s)"
    cursor.executemany(sql, val)
    db.commit()
    print(cursor.rowcount, "record inserted.")



def main():
    print("Hello World!")
    db = connect()
    cursor = db.cursor()
    #populate_gender(db, cursor)
    #populate_division(db, cursor)
    #populate_grade_level(db, cursor)
    populate_location(db, cursor)


    db.close()


if __name__ == '__main__':
    main()