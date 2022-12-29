import mysql.connector
import json
import os
from pathlib import Path


def connect():
    db = mysql.connector.connect(
        host="35.239.77.128",
        user="root",
        password="",
        database="tfrrs_replication"
    )
    return db


# ---------------PRIMARY TABLES--------------------
def populate_gender(db, cursor):
    sql = "INSERT INTO gender (id, name) VALUES (%s, %s)"
    val = [(1, "men"),
           (2, "women")]
    cursor.executemany(sql, val)
    db.commit()
    print(cursor.rowcount, "record inserted.")


def populate_division(db, cursor):
    sql = "INSERT INTO division (id, name, initial) VALUES (%s, %s, %s)"
    val = [(1, "Division 1", "d1"),
           (2, "Division 2", "d2"),
           (3, "Division 3", "d3"),
           (4, "NAIA", "naia")]
    cursor.executemany(sql, val)
    db.commit()
    print(cursor.rowcount, "record inserted.")
    return {'d1': 1, 'd2': 2, 'd3': 3, 'naia': 4}


def populate_grade_level(db, cursor):
    sql = "INSERT INTO grade_level (id, year) VALUES (%s, %s)"
    val = [(1, "FR-1"),
           (2, "SO-2"),
           (3, "JR-3"),
           (4, "SR-4"),
           (5, "Invalid")]
    cursor.executemany(sql, val)
    db.commit()
    print(cursor.rowcount, "record inserted.")


def populate_event_distance(db, cursor):
    count = 0
    events = set()
    path_to_json = "/Users/pbierach/Desktop/tffrs_replication/json/meets/"
    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
        with open(path_to_json + file_name) as json_file:
            data = json.load(json_file)
            for doc in data:
                e = doc['event']
                digit = False
                for char in e:
                    if char.isdigit():
                        digit = True
                        break
                if digit:
                    events.add(e)
                else:
                    events.add("invalid format")
    eventDict = {}
    for i, elem in enumerate(events):
        val = [elem]
        sql = "INSERT INTO event_distance (distance) VALUES (%s)"
        cursor.execute(sql, val)
        count += 1
        eventDict[elem] = cursor.lastrowid
    db.commit()
    print(count, "record inserted into event.")
    return eventDict


def populate_state(db, cursor):
    count = 0
    stateList = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
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
    states = set()
    path_to_json = "/Users/pbierach/Desktop/tffrs_replication/json/meets/"
    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
        with open(path_to_json + file_name) as json_file:
            data = json.load(json_file)
            for doc in data:
                state = doc['state']
                if state in stateList:
                    states.add(state)
                else:
                    if state == 'None given':
                        states.add('None given')
                        break
                    elif len(state) > 2:
                        try:
                            state = statesDict[state]
                            states.add(state)
                        except:
                            states.add("invalid format")
    val = list(states)
    s = {}
    query = []
    for i, v in enumerate(val):
        query = [v]
        sql = "INSERT INTO state (name) VALUES (%s)"
        cursor.execute(sql, query)
        count += 1
        s[v] = cursor.lastrowid

    db.commit()
    print(count, "record inserted into state.")
    return s


def populate_school(db, cursor):
    count = 0
    s = {}
    schoolsSet = set()
    path_to_json = "/Users/pbierach/Desktop/tffrs_replication/json/schools/"
    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
        with open(path_to_json + file_name) as json_file:
            data = json.load(json_file)
            schoolList = data
            for school in schoolList:
                schoolsSet.add(school)

    schoolList = list(schoolsSet)
    query = []
    for i, school in enumerate(schoolList):
        query = [school]
        sql = "INSERT IGNORE INTO school (name) VALUES (%s)"
        cursor.execute(sql, query)
        count += 1
        s[school] = cursor.lastrowid

    db.commit()
    print(count, "record inserted into schools.")
    return s


# ---------------SECONDARY TABLES--------------------
def populate_conference(db, cursor, d):
    count = 0
    val = []
    c = {}
    path_to_json = "/Users/pbierach/Desktop/tffrs_replication/json/conf/"
    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
        with open(path_to_json + file_name) as json_file:
            data = json.load(json_file)
            div = data['division']
            name = data['name']
            for i, element in enumerate(name):
                val = tuple([0, element, d[div[i]]])
                sql = "INSERT IGNORE INTO conference (id, name, div_id) VALUES (%s, %s, %s)"
                cursor.execute(sql, val)
                count += 1
                c[element] = cursor.lastrowid
    db.commit()
    print(count, "record inserted into conference.")
    return c


def populate_region(db, cursor, d):
    count = 0
    r = {}
    path_to_json = "/Users/pbierach/Desktop/tffrs_replication/json/region/"
    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
        with open(path_to_json + file_name) as json_file:
            data = json.load(json_file)
            div = data['division']
            name = data['name']
            for i, element in enumerate(name):
                val = tuple([0, element, d[div[i]]])
                sql = "INSERT IGNORE INTO region (id, name, div_id) VALUES (%s, %s, %s)"
                cursor.execute(sql, val)
                count += 1
                r[element] = cursor.lastrowid

    db.commit()
    print(count, "record inserted into region.")
    return r


# ---------------3RD-ARY TABLE--------------------
def populate_meet(db, cursor, s):
    count = 0
    meet = {}
    path_to_json = "/Users/pbierach/Desktop/tffrs_replication/json/meets/"
    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
        with open(path_to_json + file_name) as json_file:
            data = json.load(json_file)
            for doc in data:
                name = doc['name']
                day = doc['date']
                if len(day) > 10:
                    day = day[0:11]
                state = doc['state']
                if len(state) == 2:
                    state = state.upper()
                elif len(state) == 3:
                    if state[2] == ',' or state[2] == ')':
                        state = state[0:2]
                if len(state) > 2:
                    if state == "None given":
                        break
                    elif state == "invalid format":
                        break
                    else:
                        state = "invalid format"
                try:
                    properFormat = s[state]
                except:
                    properFormat = 'invalid format'
                    properFormat = s[properFormat]
                c = doc['conference']
                r = doc['regional']
                n = doc['national']
                val = tuple([0, name, day, properFormat, c, r, n])
                sql = "INSERT INTO meet (id, name, day_hosted, sid, conference, regional, national) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, val)
                count += 1
                key = name + ', ' + day
                meet[key] = cursor.lastrowid

    db.commit()
    print(count, "record inserted into meet.")
    return meet


def populate_team(db, cursor, dD, sD):
    count = 0
    val = None
    team = {}
    mSet = set()
    wSet = set()
    path_to_json = "/Users/pbierach/Desktop/tffrs_replication/json/conf/"
    with open(path_to_json + 'conf.json') as json_file:
        data = json.load(json_file)
        reg = data['name']
        # go through each conf to get list of mens and womens teams
        for i, name in enumerate(reg):
            mSchools = data['teams'][i + i]
            gender = 1
            for sName in mSchools:
                if sName not in mSet:
                    mSet.add(sName)
                    school = sName.upper()
                    div = data['division'][i]
                    val = tuple([0, sD[school], gender, dD[div]])
                    sql = "INSERT INTO team (id, school_id, g_id, div_id) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, val)
                    count += 1
                    db.commit()
                    key = school + ": " + str(gender)
                    team[key] = cursor.lastrowid
            wSchools = data['teams'][i + i + 1]
            gender = 2
            for sName in wSchools:
                if sName not in wSet:
                    wSet.add(sName)
                    school = sName.upper()
                    div = data['division'][i]
                    val = tuple([0, sD[school], gender, dD[div]])
                    sql = "INSERT INTO team (id, school_id, g_id, div_id) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, val)
                    count += 1
                    db.commit()
                    key = school + ": " + str(gender)
                    team[key] = cursor.lastrowid

    print(count, " record inserted into teams.")
    return team


# ---------------4TH-ARY TABLE--------------------
def populate_team_to_region(db, cursor, teamD, regD, schoolD, divD):
    val = []
    path_to_json = "/Users/pbierach/Desktop/tffrs_replication/json/region/"
    with open(path_to_json + 'region.json') as json_file:
        data = json.load(json_file)
        reg = data['name']
        # go through each conf to get list of mens and womens teams
        print(",", end=" ")
        for i, name in enumerate(reg):
            gender = 1
            mSchools = data['teams'][i + i]
            d = data['division'][i]
            div = divD[d]
            for sName in mSchools:
                school = sName.upper()
                region = regD[name]
                key = school + ": " + str(gender)
                try:
                    team = teamD[key]
                except:
                    sid = schoolD[school]
                    sql = "INSERT IGNORE INTO team (id, school_id, g_id, div_id) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, [0, sid, 1, div])
                    db.commit()
                    print('"' + key + '": ' + str(cursor.lastrowid), end=', ')
                val.append([team, region])

            gender = 2
            wSchools = data['teams'][i + i + 1]
            for sName in wSchools:
                school = sName.upper()
                region = regD[name]
                key = school + ": " + str(gender)
                try:
                    team = teamD[key]
                except:
                    sid = schoolD[school]
                    sql = "INSERT IGNORE INTO team (id, school_id, g_id, div_id) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, [0, sid, 2, div])
                    db.commit()
                    print('"' + key + "': " + str(cursor.lastrowid), end=', ')
                val.append([team, region])
    print("}")
    sql = "INSERT IGNORE INTO team_to_region (team_id, region_id) VALUES (%s, %s)"
    cursor.executemany(sql, val)
    db.commit()
    print(cursor.rowcount, "record inserted into team_to_region.")


def populate_team_results(db, cursor, meetD, teamD):
    count = 0
    nameChange = {'Western State': 'WESTERN COLORADO', 'Metro State': 'MSU DENVER',
                  'Trinidad State JC': 'TRINIDAD STATE',
                  'Dixie State': 'UTAH TECH'}
    id = 1
    val = []
    trDict = {}
    path_to_json = "/Users/pbierach/Desktop/tffrs_replication/json/meets/"
    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
        with open(path_to_json + file_name) as json_file:
            data = json.load(json_file)
            for doc in data:
                key = doc['name'] + ', ' + doc['date']
                try:
                    meet_id = meetD[key]
                except:
                    break
                gender = doc['gender']
                if gender == 'Men':
                    gender = 1
                else:
                    gender = 2
                teamResults = doc['team']
                placeList = teamResults['place']
                teamList = teamResults['team']
                pointList = teamResults['points']
                scorerList = teamResults['scorers']
                sList = [None, None, None, None, None, None, None]
                for i, elem in enumerate(placeList):
                    for j, score in enumerate(scorerList[i]):
                        sList[j] = score
                    try:
                        #check to see if school has had a name change since meet
                        name = nameChange[teamList[i]]
                    except:
                        name = teamList[i]
                    teamKey = name.upper() + ": " + str(gender)
                    try:
                        teamId = teamD[teamKey]
                    except:
                        #if team doesnt exist its not getting added
                        break
                    place = placeList[i]
                    if not place[0].isdigit():
                        place = None
                    info = (0, teamId, meet_id, place, pointList[i], sList[0], sList[1], sList[2], sList[3],
                            sList[4], sList[5], sList[6])
                    val = info
                    sql = "INSERT IGNORE INTO team_results (id, team_id, meet_id, place, points, s1, s2, s3, s4, s5, s6, s7) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, val)
                    count += 1
                    key = str(meet_id) + ":" + str(placeList[i])
                    trDict[key] = cursor.lastrowid
                    id += 1

    db.commit()
    print(count, "record inserted into team_result.")
    return trDict


def populate_athletes(db, cursor, teamD):
    count = 0
    val = []
    athDict = {}
    path_to_json = "/Users/pbierach/Desktop/tffrs_replication/json/meets/"
    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
        with open(path_to_json + file_name) as json_file:
            print('----------------'+file_name+'--------------------')
            data = json.load(json_file)
            for doc in data:
                print(doc['name'].upper() + " " + doc['date'])
                gender = doc['gender']
                if gender == 'Men':
                    gender = 1
                else:
                    gender = 2
                indResults = doc['ind']
                placeList = indResults['place']
                nameList = indResults['name']
                teamList = indResults['team']
                # id, first, last, and team
                for i, elem in enumerate(placeList):
                    name = nameList[i]
                    space = name.find(" ")
                    first = name[0:space]
                    last = name[space + 1:len(name)]
                    team = teamList[i]
                    if "Unattached" in team or 'unattached' in team:
                        team = 'unattached'
                    try:
                        teamId = teamD[team.upper() + ": " + str(gender)]
                    except:
                        teamId = None
                    val = (0, first, last, teamId, gender)
                    sql = "INSERT IGNORE INTO athlete (id, first_name, last_name, team_id, g_id) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, val)
                    count += 1
                    db.commit()
                    key = name + ": " + str(teamId)
                    athDict[key] = cursor.lastrowid
    print(count, " record inserted into athlete.")
    return athDict


# ---------------5TH-ARY TABLE--------------------
def populate_ind_results(db, cursor, meetD, eventD, gradeD, athD, teamD):
    indRDict = {}
    path_to_json = "/Users/pbierach/Desktop/tffrs_replication/json/meets/"
    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
        with open(path_to_json + file_name) as json_file:
            data = json.load(json_file)
            for doc in data:
                results = doc['ind']
                meetKey = doc['name'] + ", " + doc['date']
                event = eventD['event']
                try:
                    meet = meetD[meetKey]
                except:
                    break
                for i, res in enumerate(results):
                    place = results['place'][i]
                    time = results['time'][i]
                    sql = "INSERT IGNORE INTO ind_results (meet_id, place, finish_time, race_distance) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, [meet, place, time, event])
                    db.commit()

                    if doc['gender'] == 'Men':
                        teamId = results['team'][i] + ": 1"
                    else:
                        teamId = results['team'][i] + ": 2"
                    athKey = results['name'][i] + ": " + teamId
                    ath = athD[athKey]
                    try:
                        grade = gradeD[results['grade'][i]]
                    except:
                        grade = 5
                    sql = "INSERT IGNORE INTO athlete_to_result (indres_id, ath_id, grade_id) VALUES (%s, %s, %s)"
                    cursor.execute(sql, [cursor.lastrowid, ath, grade])
                    key = str(meet) + ", " + str(place) + ", " + str(doc['gender'])
                    indRDict[key] = cursor.lastrowid
    print(cursor.rowcount, "record inserted into ind_results.")


def createDBAndFK(path):
    print("Starting from scratch!")
    db = connect()
    cursor = db.cursor()
    genderDict = {"men": 1, "women": 2}
    jsonpath = path / ('gender.json')
    jsonpath.write_text(json.dumps(genderDict))
    gradeDict = {"FR-1": 1, "SO-2": 2, "JR-3": 3, "SR-4": 4, "Invalid": 5}
    jsonpath = path / ('grade.json')
    jsonpath.write_text(json.dumps(gradeDict))
    populate_gender(db, cursor)
    divDict = populate_division(db, cursor)
    jsonpath = path / ('division.json')
    jsonpath.write_text(json.dumps(divDict))
    populate_grade_level(db, cursor)
    stateDict = populate_state(db, cursor)
    jsonpath = path / ('state.json')
    jsonpath.write_text(json.dumps(stateDict))
    eventDict = populate_event_distance(db, cursor)
    jsonpath = path / ('event.json')
    jsonpath.write_text(json.dumps(eventDict))
    schoolDict = populate_school(db, cursor)
    jsonpath = path / ('school.json')
    jsonpath.write_text(json.dumps(schoolDict))

    confDict = populate_conference(db, cursor, divDict)
    regDict = populate_region(db, cursor, divDict)
    jsonpath = path / ('conf.json')
    jsonpath.write_text(json.dumps(confDict))
    jsonpath = path / ('region.json')
    jsonpath.write_text(json.dumps(regDict))

    meetDict = populate_meet(db, cursor, stateDict)
    jsonpath = path / ('meet.json')
    jsonpath.write_text(json.dumps(meetDict))
    teamDict = populate_team(db, cursor, divDict, schoolDict)
    jsonpath = path / ('team.json')
    jsonpath.write_text(json.dumps(teamDict))

    populate_team_to_region(db, cursor, teamDict, regDict, schoolDict, divDict)

    trDict = populate_team_results(db, cursor, meetDict, teamDict)
    jsonpath = path / ('team_results.json')
    jsonpath.write_text(json.dumps(trDict))
    athDict = populate_athletes(db, cursor, teamDict)
    jsonpath = path / ('athletes.json')
    jsonpath.write_text(json.dumps(athDict))

    db.close()


def populateFromPoint(dicts):
    path = Path('/Users/pbierach/Desktop/tffrs_replication/json/foreign_keys/')
    print("Starting from point!")
    db = connect()
    cursor = db.cursor()

    teamDict = populate_team(db, cursor, dicts[0], dicts[2]) #div and school
    jsonpath = path / ('team.json')
    jsonpath.write_text(json.dumps(teamDict))

    #populate_team_to_region(db, cursor, teamDict, regDict, schoolDict, divDict) #team, reg, school, div

    #trDict = populate_team_results(db, cursor, meetDict, teamDict) # meet and team
    jsonpath = path / ('team_results.json')
    #jsonpath.write_text(json.dumps(trDict))
    athDict = populate_athletes(db, cursor, teamDict)
    jsonpath = path / ('athletes.json')
    jsonpath.write_text(json.dumps(athDict))

    db.close()

def main():
    scratch = True
    if scratch:
        path = Path('/Users/pbierach/Desktop/tffrs_replication/json/foreign_keys/')
        createDBAndFK(path)
    else:
        path = '/Users/pbierach/Desktop/tffrs_replication/json/foreign_keys/'
        i = 0
        # order of dictionaries:
        # div, state, grade, meet, gender, region, event school, conf
        fkDicts = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
        for file_name in [file for file in os.listdir(path) if file.endswith('.json')]:
            with open(path + file_name) as json_file:
                data = json.load(json_file)
                fkDicts[i] = data
            i = i + 1
        populateFromPoint(fkDicts)


if __name__ == '__main__':
    main()
