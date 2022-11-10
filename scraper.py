import urllib.request
from bs4 import BeautifulSoup
import json
#from selenium import webdriver
#from selenium.webdriver.chrome.service import Service

'''
This function reads in a webpage and returns a list
of the lines in that webpage
Arg: url of the file to open
Return: list of strings
'''
def readWebpage(url):
    data = urllib.request.urlopen(url)
    lines = data.readlines()
    for x in range(len(lines)):
        lines[x] = lines[x].decode("utf-8")
        lines[x] = lines[x].replace("\n", "")
    return lines


'''
This function reads in a tfrrs search page
and returns a list of all the meet links 
contained in the search
Arg: url of the page
Return: list of strings
'''
def getMeetLinks(url):
    links = []
    data = urllib.request.urlopen(url)
    soup = BeautifulSoup(data, 'html.parser')
    tbody = soup.find_all('tbody')
    allA = tbody[0].find_all('a')
    for a in allA:
        if a.get('href') != "/results/xc/20453/Lewis__Clark_Time_Trials" and not "NJCAA" in a.get('href'):
            fullLink = "https://www.tfrrs.org" + a.get('href')
            links.append(fullLink)
    return links


'''
This function reads in a tfrrs race page
and returns a dictionary containing
relevant information about the meet
Arg: url of the page
Return: list of dictionary of all meet information
'''
def getRaceInfoFromPage(url):
    data = urllib.request.urlopen(url)
    soup = BeautifulSoup(data, 'html.parser')
    keys = ["name", "date", "venue", "location", "gender", "event", "team", "ind"]
    meet = soup.find_all("div", "page container")
    # event
    list = getRaceEvents(soup)
    genders = list[0]
    if len(genders) == 1:
        if genders[0] == "Men":
            mRace = list[1]
            mRace = singleGenderRace(soup, mRace)
            return mRace
        else:
            wRace = list[1]
            wRace = singleGenderRace(soup, wRace)
            return wRace
    else:
        mRace = list[1]
        wRace = list[2]
        womenFirst = list[3]
        list = bothGenderRace(soup, mRace, wRace, womenFirst)
        mRace = list[0]
        wRace = list[1]
        return [mRace, wRace]

def singleGenderRace(soup, race):
    # get race specifics
    race = getRaceNameSingle(soup, race)
    # date
    race = getRaceDateSingle(soup, race)
    # location
    race = getRaceLocationSingle(soup, race)
    # separate by team results and individual
    list = getTeamResultsFromPageSingle(soup)
    race["team"] = list[0]
    listTeams = list[1]
    year = race["date"][0:5]
    race["ind"] = getIndResultsFromPageSingle(soup, year, listTeams, race["name"])
    return race

def bothGenderRace(soup, mRace, wRace, womenFirst):
    # get race specifics
    list = getRaceName(soup, mRace, wRace)
    mRace = list[0]
    wRace = list[1]
    # date
    list = getRaceDate(soup, mRace, wRace)
    mRace = list[0]
    wRace = list[1]
    # location
    list = getRaceLocation(soup, mRace, wRace)
    mRace = list[0]
    wRace = list[1]
    # separate by team results and individual
    list = getTeamResultsFromPage(soup, womenFirst)
    mRace["team"] = list[0]
    wRace["team"] = list[1]
    listMTeams = list[2]
    listWTeams = list[3]
    year = mRace["date"][0:5]
    list = getIndResultsFromPage(soup, womenFirst, year, listMTeams, listWTeams, mRace["name"])
    mRace["ind"] = list[0]
    wRace["ind"] = list[1]
    return [mRace, wRace]

'''
This function takes a BS4 object of the tfrrs page
and returns the name of the race as a part of a given dictionary
Arg: BS4 object of the page, dictionary for men's race, dictionary for women's race
Return: list of dictionaries 
'''
def getRaceName(soup, men, women):
    name = soup.find("h3").contents[0]
    cleanName = name.strip()
    men["name"] = cleanName
    women["name"] = cleanName
    return [men, women]

'''
This function takes a BS4 object of the tfrrs page
and returns the date of the race as a part of a given dictionary
Arg: BS4 object of the page, dictionary for men's race, dictionary for women's race
Return: list of dictionaries 
'''
def getRaceDate(soup, men, women):
    date = convertDateToSQL(soup.find("div", "panel-heading-normal-text inline-block").contents[0])
    men["date"] = date
    women["date"] = date
    return [men, women]

'''
This function takes a BS4 object of the tfrrs page
and returns the venue and location of the race as a part of a given dictionary
Arg: BS4 object of the page, dictionary for men's race, dictionary for women's race
Return: list of dictionaries 
'''
def getRaceLocation(soup, men, women):
    location = soup.find_all("div", "panel-heading-normal-text inline-block")
    check = str(location[1])
    if check.count("\n") == 1:
        men["venue"] = "None given"
        women["venue"] = "None given"
        men["location"] = "None given"
        women["location"] = "None given"
    else:
        venue = ""
        place = ""
        ifPlace = False
        for div in location:
            if (ifPlace):
                venue = div.text
                venue = venue.strip()
            ifPlace = True


        locationIndex = venue.find("\n")
        location = venue[locationIndex+1:len(venue)].strip()
        venue = venue[0:locationIndex]
        cut = None
        for i, char in enumerate(location):
            if char.isdigit():
                cut = i
                break
        place = location[0:cut].strip()
        while place.find("\n") > 0:
            newLine = place.find("\n")
            place = place[newLine:len(place)].strip()

        men["venue"] = venue
        women["venue"] = venue
        men["location"] = place
        women["location"] = place
    return [men, women]

'''
This function takes a BS4 object of the tfrrs page
and determines how many dictionaries will be required to represent the race
Arg: BS4 object of the page
Return: list containing either gender of race and dictionary for race or 
        list containing 2 dictionaries for races and if women are first in results 
'''
def getRaceEvents(soup):
    keys = ["name", "date", "venue", "location", "gender", "event", "team", "ind"]
    eventList = soup.find_all("ol", "inline-list pl-0 pt-5 events-list")[0].find_all("a")
    parenthEvent = soup.find_all("h3", "font-weight-500")
    genders = []
    # case: only one gender
    if len(eventList) == 1:
        # case: single gender is womens
        if "Women" in eventList[0].text:
            genders = ["Women"]
            wRace = dict.fromkeys(keys)
            wRace["gender"] = "women"
            wEvent = parenthEvent[0].text
            openP = wEvent.find("(") + 1
            closeP = wEvent.find(")")
            wEvent = wEvent[openP:closeP]
            wRace["event"] = wEvent
            return [genders, wRace]

        # case: single gender is men's
        elif "Men" in eventList[0].text:
            genders = ["Men"]
            mRace = dict.fromkeys(keys)
            mRace["gender"] = "Men"
            mEvent = parenthEvent[0].text
            openP = mEvent.find("(") + 1
            closeP = mEvent.find(")")
            mEvent = mEvent[openP:closeP]
            mRace["event"] = mEvent
            return [genders, mRace]
    # case: both genders
    else:
        genders = ["Men", "Women"]
        womenFirst = True
        mRace = dict.fromkeys(keys)
        wRace = dict.fromkeys(keys)
        mRace["gender"] = "men"
        wRace["gender"] = "women"
        # case: women are first
        if "Women" in eventList[0].text:
            mEvent = parenthEvent[2].text
            openP = mEvent.find("(") + 1
            closeP = mEvent.find(")")
            mEvent = mEvent[openP:closeP]
            mRace["event"] = mEvent
            wEvent = parenthEvent[0].text
            openP = wEvent.find("(") + 1
            closeP = wEvent.find(")")
            wEvent = wEvent[openP:closeP]
            wRace["event"] = wEvent

        # case: women are second
        else:
            womenFirst = False
            mEvent = parenthEvent[0].text
            openP = mEvent.find("(") + 1
            closeP = mEvent.find(")")
            mEvent = mEvent[openP:closeP]
            mRace["event"] = mEvent
            wEvent = parenthEvent[2].text
            openP = wEvent.find("(") + 1
            closeP = wEvent.find(")")
            wEvent = wEvent[openP:closeP]
            wRace["event"] = wEvent

    return [genders, mRace, wRace, womenFirst]

'''
This function takes a BS4 object of the tfrrs page
and returns team scores as a part of a given dictionary
Arg: url of the page, boolean if Women's results were first on page
Return: list of dictionaries 
'''
def getTeamResultsFromPage(soup, womenFirst):
    keys = ["place", "team", "points", "scorers"]
    mTeam = dict.fromkeys(keys)
    wTeam = dict.fromkeys(keys)
    #separate relevant data for the team section
    teamResults = soup.find_all("tbody", "color-xc")
    if len(teamResults) > 2:
        if womenFirst:
            wResults = teamResults[0].text.split()
            mResults = teamResults[2].text.split()
        else:
            mResults = teamResults[0].text.split()
            wResults = teamResults[2].text.split()

        #get data from relevant html
        list = scrapeTeamResults(mResults, mTeam)
        mTeam = list[0]
        nameOfMenTeams = list[1]
        list = scrapeTeamResults(wResults, wTeam)
        wTeam = list[0]
        nameOfWomenTeams = list[1]
        return [mTeam, wTeam, nameOfMenTeams, nameOfWomenTeams]

'''
This function takes a BS4 object of the tfrrs team results 
and returns them as a part of a given dictionary
Arg: BS4 object of team html lines, dictionary for team results
Return: updated dict for team results, and list of team names 
'''
def scrapeTeamResults(results, team):
    listOfPlaces = []
    listOfTeams = []
    listOfPoints = []
    listOfScorers = []
    i = 0
    while i+7 <= len(results)-1:
        #team place
        listOfPlaces.append(results[i])
        i += 1
        #get name
        name = ""
        while results[i][0].isalpha() or results[i][0] == "(" or results[i][0] == "&" or results[i][0] == "-":
            name += " " + results[i]
            i += 1
        listOfTeams.append(name.strip())
        #score is always 2 lines away from the end of name
        i += 2
        listOfPoints.append(results[i])
        i += 1
        #get the scores of the runners that ran (not always top 7)
        scorers = []
        #if statement that checks if last team is being checked so it can avoid an out of bounds error
        if i + 10 >= len(results):
            while i <= len(results)-1:
                scorers.append(results[i])
                i += 1
        else:
            while i+2 < len(results)-1 and results[i+2].isdigit():
                scorers.append(results[i])
                i += 1
        listOfScorers.append(scorers)
        i += 1

    team["place"] = listOfPlaces
    team["team"] = listOfTeams
    team["points"] = listOfPoints
    team["scorers"] = listOfScorers
    return [team, listOfTeams]

'''
This function takes a BS4 object of the tfrrs and returns
individual performances as a part of a given dictionary
Arg: url of the page, boolean if Women's results were first on page
Return: list of dictionaries 
'''
def getIndResultsFromPage(soup, womenFirst, year, mTeams, wTeams, meetName):
    keys = ["place", "name", "year", "team", "time"]
    mInd = {keys[0]: [], keys[1]: [], keys[2]: [], keys[3]: [], keys[4]: []}
    wInd = {keys[0]: [], keys[1]: [], keys[2]: [], keys[3]: [], keys[4]: []}

    teamResults = soup.find_all("tbody", "color-xc")
    if womenFirst:
        wResults = teamResults[1].text.split()
        mResults = teamResults[3].text.split()
    else:
        mResults = teamResults[1].text.split()
        wResults = teamResults[3].text.split()

    # get data from relevant html
    allTeams = set(mTeams).union(set(wTeams))
    allTeams = list(allTeams)
    mInd = scrapeIndResults(mResults, mInd, year, allTeams, meetName)
    wInd = scrapeIndResults(wResults, wInd, year, allTeams, meetName)
    return [mInd, wInd]

'''
This function takes a BS4 object of the tfrrs individual results 
and returns them as a part of a given dictionary
Arg: BS4 object of team html lines, dictionary for individual results
Return: updated dict for team results 
'''
def scrapeIndResults(results, ind, currYear, listOfTeamNames, meetName):
    thaddeusMeets = ["Region XIX Championships", "NJCAA Division III Cross Country Championship"]
    sharedWords = ["St.", "Angel", "Diego", "Santiago", "Frank", "Francis"]
    if meetName in thaddeusMeets:
        listOfTeamNames.append("Thaddeus Stevens")
    year = ["FR-1","SO-2","JR-3","SR-4"]
    yearToGrade = {"Freshman":"FR-1", "Sophomore":"SO-2", "Junior":"JR-3", "Senior":"SR-4" }
    dateToGrade = {4:"FR-1",3:"SO-2",2:"JR-3",1:"SR-4",0:"SR-4"}
    nonScorers = 0
    i = 0
    noGrade = False
    while i < len(results)-1:
        if results[i] == "0":
            #skip place for now until DNS/DNF is determined
            i += 1
            name = ""
            # check for name and stop at year in school (if given)
            # checks if still on name (given that year is in standard format (i.e. SR-4))
            while results[i][0].isalpha() and not (results[i][-1].isdigit()) and results[i] != "Unattached":
                # this logical path first assumes that dealing with year and not name
                # if its in standard form append it to the dict
                if results[i] in year:
                    ind["year"].append(results[i])
                    break
                else:
                    # written out as a string
                    if len(results[i]) > 4 and (results[i].upper() == "FRESHMAN" or results[i].upper() == "SOPHOMORE" or results[i].upper() == "JUNIOR" or results[i].upper() == "SENIOR"):
                        ind["year"].append(yearToGrade[results[i]])
                        break
                    elif len(results[i]) == 4 and results[i][0] == "2":
                        # kept as year of graduation
                        diff = int(results[i]) - int(currYear)
                        ind["year"].append(dateToGrade[diff])
                        break
                # in case of no grade listed, check if name is in list of team names to stop
                sub = results[i]
                if any(sub in name for name in listOfTeamNames) and not (sub in sharedWords) or sub[0:3] == "UNA":
                    noGrade = True
                    break
                else:
                    name = name + results[i] + " "
                    i += 1
            ind["name"].append(name.strip())
            school = ""
            i += 1
            # find school name
            while (results[i][0].isalpha() or results[i][0] == "&") and "DN" not in results[i]:
                if results[i] == "DQ":
                    break
                school = school + results[i] + " "
                i += 1
            ind["team"].append(school.strip())
            ind["place"].append(results[i])
            ind["time"].append(results[i])
            while len(results[i]) != 1 and i < len(results)-1:
                i += 1
        else:
            #first element is place
            place = int(results[i])
            ind["place"].append(results[i])
            i += 1
            name = ""
            #check for name and stop at year in school (if given)
            #checks if still on name (given that year is in standard format (i.e. SR-4))
            while results[i][0].isalpha() and not (results[i][-1].isdigit()) and results[i] != "Unattached" :
                #this logical path first assumes that dealing with year and not name
                #if its in standard form append it to the dict
                if results[i] in year:
                    ind["year"].append(results[i])
                    break
                else:
                    # written out as a string
                    if len(results[i]) > 4 and (results[i].upper() == "FRESHMAN" or results[i].upper() == "SOPHOMORE" or results[i] == "JUNIOR" or results[i] == "SENIOR"):
                        ind["year"].append(yearToGrade[results[i]])
                        break
                    elif len(results[i]) == 4 and results[i][0] == "2":
                        # kept as year of graduation
                        diff = int(results[i]) - int(currYear)
                        ind["year"].append(dateToGrade[diff])
                        break
                #in case of no grade listed, check if name is in list of team names to stop
                sub = results[i]
                if any(sub in name for name in listOfTeamNames) and not (sub in sharedWords) or sub[0:3] == "UNA":
                    noGrade = True
                    break
                else:
                    name = name + results[i] + " "
                    i += 1
            ind["name"].append(name.strip())
            school = ""
            if noGrade == False:
                if results[i] in year:
                    ind["year"].append(results[i])
                else:
                    # written out as a string
                    if len(results[i]) > 4 and (results[i].upper() == "FRESHMAN" or results[i].upper() == "SOPHOMORE" or results[i] == "JUNIOR" or results[i] == "SENIOR"):
                        ind["year"].append(yearToGrade[results[i]])
                    elif len(results[i]) == 4 and results[i][0] == "2":
                        # kept as year of graduation
                        diff = int(results[i]) - int(currYear)
                        ind["year"].append(dateToGrade[diff])
                i += 1

            #find school name
            while results[i][0].isalpha()  or results[i][0] == "(" or results[i][0] == "&" or results[i][0] == "-":
                school = school + results[i] + " "
                i += 1
            ind["team"].append(school.strip())
            #skip avg mile time
            i += 1
            ind["time"].append(results[i])
            i += 1
            #skip potential score
            #runner is a nonscorer but has splits
            if i < len(results) - 1 and len(results[i]) > 6:
                nonScorers += 1
                while i < len(results) - 1 and len(results[i]) > 6:
                    i += 1
            elif i < len(results)-1 and len(results[i]) <= 3:
                #score
                #splits come and mess something up
                if len(results[i+1]) > 3 and results[i+1][0].isdigit():
                    i+=1
                    while i < len(results) - 1 and len(results[i]) > 6:
                        i += 1
                # there's a tie
                if i < len(results)-1 and int(results[i]) == place and int(results[i+1]) == place:
                    #skip score (on place)
                    i += 1
                    #process person normally
                    # first element is place
                    place = int(results[i])
                    ind["place"].append(results[i])
                    i += 1
                    name = ""
                    # check for name and stop at year in school (if given)
                    # checks if still on name (given that year is in standard format (i.e. SR-4))
                    while results[i][0].isalpha() and not (results[i][-1].isdigit()) and results[i] != "Unattached":
                        # this logical path first assumes that dealing with year and not name
                        # if its in standard form append it to the dict
                        if results[i] in year:
                            ind["year"].append(results[i])
                            break
                        else:
                            # written out as a string
                            if len(results[i]) > 4 and (
                                    results[i].upper() == "FRESHMAN" or results[i].upper() == "SOPHOMORE" or results[i] == "JUNIOR" or results[i] == "SENIOR"):
                                ind["year"].append(yearToGrade[results[i]])
                                break
                            elif len(results[i]) == 4 and results[i][0] == "2":
                                # kept as year of graduation
                                diff = int(results[i]) - int(currYear)
                                ind["year"].append(dateToGrade[diff])
                                break
                        # in case of no grade listed, check if name is in list of team names to stop
                        sub = results[i]
                        if any(sub in name for name in listOfTeamNames) and not (sub in sharedWords) or sub[0:3] == "UNA":
                            noGrade = True
                            break
                        else:
                            name = name + results[i] + " "
                            i += 1
                    ind["name"].append(name.strip())
                    school = ""
                    if noGrade == False:
                        if results[i] in year:
                            ind["year"].append(results[i])
                        else:
                            # written out as a string
                            if len(results[i]) > 4 and (
                                    results[i].upper() == "FRESHMAN" or results[i].upper() == "SOPHOMORE" or results[i] == "JUNIOR" or results[i] == "SENIOR"):
                                ind["year"].append(yearToGrade[results[i]])
                            elif len(results[i]) == 4 and results[i][0] == "2":
                                # kept as year of graduation
                                diff = int(results[i]) - int(currYear)
                                ind["year"].append(dateToGrade[diff])
                        i += 1

                    # find school name
                    while results[i][0].isalpha() or results[i][0] == "(" or results[i][0] == "&" or results[i][0] == "-":
                        school = school + results[i] + " "
                        i += 1
                    ind["team"].append(school.strip())
                    # skip avg mile time
                    i += 1
                    ind["time"].append(results[i])
                    i += 1
                    #skip score
                    if int(results[i]) == place or int(results[i]) == place+1:
                        i += 1
                #no tie
                else:
                    if i == len(results)-1:
                        break
                    #normal scoring
                    if int(results[i]) == place or int(results[i]) == place - nonScorers and place+1 != int(results[i]):
                        i += 1
                    #non-scoring individual and results[i] is next persons place
                    elif int(results[i]) == place+1 :
                        nonScorers += 1
            #skip any splits that the data may have
            while i < len(results)-1 and len(results[i]) > 6:
                i += 1
            noGrade = False
    return ind

########################################################################################################################
########################################################################################################################

'''
This function takes a BS4 object of the tfrrs page
and returns the name of the race as a part of a given dictionary
Arg: BS4 object of the page, dictionary for men's race, dictionary for women's race
Return: list of dictionaries 
'''
def getRaceNameSingle(soup, race):
    name = soup.find("h3").contents[0]
    cleanName = name.strip()
    race["name"] = cleanName
    return race

'''
This function takes a BS4 object of the tfrrs page
and returns the date of the race as a part of a given dictionary
Arg: BS4 object of the page, dictionary for men's race, dictionary for women's race
Return: list of dictionaries 
'''
def getRaceDateSingle(soup, race):
    date = convertDateToSQL(soup.find("div", "panel-heading-normal-text inline-block").contents[0])
    race["date"] = date
    return race

'''
This function takes a BS4 object of the tfrrs page
and returns the venue and location of the race as a part of a given dictionary
Arg: BS4 object of the page, dictionary for men's race, dictionary for women's race
Return: list of dictionaries 
'''
def getRaceLocationSingle(soup, race):
    location = soup.find_all("div", "panel-heading-normal-text inline-block")
    venue = ""
    place = ""
    ifPlace = False
    for div in location:
        if (ifPlace):
            venue = div.text
            venue = venue.strip()
        ifPlace = True


    locationIndex = venue.find("\n")
    location = venue[locationIndex+1:len(venue)].strip()
    venue = venue[0:locationIndex]
    cut = None
    for i, char in enumerate(location):
        if char.isdigit():
            cut = i
            break
    place = location[0:cut].strip()
    while place.find("\n") > 0:
        newLine = place.find("\n")
        place = place[newLine:len(place)].strip()

    race["venue"] = venue
    race["location"] = place
    return race

'''
This function takes a BS4 object of the tfrrs page
and returns team scores as a part of a given dictionary
Arg: url of the page, boolean if Women's results were first on page
Return: list of dictionaries 
'''
def getTeamResultsFromPageSingle(soup):
    keys = ["place", "team", "points", "scorers"]
    team = dict.fromkeys(keys)
    #separate relevant data for the team section
    teamResults = soup.find_all("tbody", "color-xc")
    results = teamResults[0].text.split()
    #get data from relevant html
    list = scrapeTeamResults(results, team)
    team = list[0]
    nameOfTeams = list[1]
    return [team, nameOfTeams]

'''
This function takes a BS4 object of the tfrrs and returns
individual performances as a part of a given dictionary
Arg: url of the page, boolean if Women's results were first on page
Return: list of dictionaries 
'''
def getIndResultsFromPageSingle(soup, year, teams, name):
    keys = ["place", "name", "year", "team", "time"]
    ind = {keys[0]: [], keys[1]: [], keys[2]: [], keys[3]: [], keys[4]: []}

    teamResults = soup.find_all("tbody", "color-xc")
    results = teamResults[1].text.split()

    # get data from relevant html
    ind = scrapeIndResults(results, ind, year, teams, name)
    return ind



'''
This fucntion takes a date in the format of "Month Day, Year" and 
converts it into "yyyy-mm-dd" 
Args: string of a date
Returns: a string formatted for SQL
'''
def convertDateToSQL(date):
    monthDict = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'Jun': '06',
                 'July': '07', 'August': '08',
                 'September': '09', 'October': '10', 'November': '11', 'December': '12'}
    length = len(date)
    monthIndex = date.find(" ")
    dayIndex = date.find(",")

    year = date[(dayIndex + 1):length]
    month = monthDict[date[0:monthIndex]]
    day = date[monthIndex:dayIndex]
    day = day.strip()
    if len(day) == 1:
        day = "0" + day
    return year + "-" + month + "-" + day

'''
This function takes a starting number and upper limit for a range
and gets all of the information for the meets listed
on search pages start to upper limit from tfrrs
Args: int, of start, int of upper limit 
Returns: 
'''
def getAllInfoFromRangeOfPages(start, limit):
    links = []
    for i in range(start, limit):
        links.extend(getMeetLinks("https://www.tfrrs.org/results_search_page.html?page=" + str(i)
                     + "&search_query=&with_month=&with_sports=xc&with_states=&with_year="))

    meetDicts = []
    for i in range(len(links)):
        print(links[i])
        list = getRaceInfoFromPage(links[i])
        if type(list) is dict:
            meetDicts.append(list)
        else:
            meetDicts.append(list[0])
            meetDicts.append(list[1])

    createJSONObjects(meetDicts)
def createJSONObjects(list):
    with open("meets.json", "w") as final:
        json.dump(list, final)

def main():
    getAllInfoFromRangeOfPages(1,2)
    #getAllInfoFromRangeOfPages(2,4)
    #getRaceInfoFromPage("https://www.tfrrs.org/results/xc/20802/Golden_State_AC_Cross_Country_Championships")
    #getRaceInfoFromPage("https://www.tfrrs.org/results/xc/21188/NE_10_Cross-Country_Run_Championship")


main()
