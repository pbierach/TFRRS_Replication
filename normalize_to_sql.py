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
    states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
              'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
              'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
              'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
              'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
    statesDict = {
        'Alaska': 'AK',
        'Alabama': 'AL',
        'Arkansas': 'AR',
        'Arizona': 'AZ',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'District of Columbia': 'DC',
        'Delaware': 'DE',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Iowa': 'IA',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Massachusetts': 'MA',
        'Maryland': 'MD',
        'Maine': 'ME',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Missouri': 'MO',
        'Mississippi': 'MS',
        'Montana': 'MT',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Nebraska': 'NE',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'Nevada': 'NV',
        'New York': 'NY',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Virginia': 'VA',
        'Vermont': 'VT',
        'Washington': 'WA',
        'Wisconsin': 'WI',
        'West Virginia': 'WV',
        'Wyoming': 'WY'
    }
    path_to_json = "/Users/pbierach/Desktop/tffrs_replication/json/meets/"
    locations = set()
    l = {}
    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
        with open(path_to_json + file_name) as json_file:
            data = json.load(json_file)
            for doc in data:
                loc = doc['location']
                if loc == 'None given':
                    locations.add('None given')
                    break
                comma = loc.find(",")
                if comma == -1:
                    locations.add('invalid format')
                city = loc[0:comma]
                state = loc[comma + 1:len(loc) + 1].strip()
                if state not in states:
                    try:
                        state = statesDict[state]
                    except:
                        locations.add('invalid format')
                        break
                if len(city) == 0:
                    locations.add('invalid format')
                elif len(city) <=2:
                    locations.add('invalid format')
                elif not city[0].isupper():
                    locations.add('invalid format')
                else:
                    locations.add(doc['location'])
    val = []
    i=1
    for element in locations:
        comma = element.find(",")
        city = element[0:comma]
        location = tuple([city, state])
        l[location] = i
        val.append(location)
        i+=1

    sql = "INSERT INTO location (city, state) VALUES (%s, %s)"
    cursor.executemany(sql, val)
    db.commit()
    print(cursor.rowcount, "record inserted.")
    return l



def main():
    print("Hello World!")
    db = connect()
    cursor = db.cursor()
    genderDict = {"men": 1, "women": 2}
    divDict = {"DI": 1, "DII": 2, "DIII": 3}
    gradeDict = {"FR-1": 1, "SO-2": 2, "JR-3": 3, "SR-4": 4}
    #populate_gender(db, cursor)
    #populate_division(db, cursor)
    #populate_grade_level(db, cursor)
    locationDict = populate_location(db, cursor)


    db.close()


if __name__ == '__main__':
    main()