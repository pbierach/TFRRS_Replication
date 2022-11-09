import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

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
        else:
            wRace = list[1]
    else:
        mRace = list[1]
        wRace = list[2]
        womenFirst = list[3]

    #-----------------------------------

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
    list = getIndResultsFromPage(soup, womenFirst, year, listMTeams, listMTeams)
    mRace["ind"] = list[0]
    wRace["ind"] = list[1]
    return [mRace, wRace]

#CHANGE
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

#CHANGE
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

#CHANGE
'''
This function takes a BS4 object of the tfrrs page
and returns the venue and location of the race as a part of a given dictionary
Arg: BS4 object of the page, dictionary for men's race, dictionary for women's race
Return: list of dictionaries 
'''
def getRaceLocation(soup, men, women):
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

    men["venue"] = venue
    women["venue"] = venue
    men["location"] = place
    women["location"] = place
    return [men, women]

'''
This function takes a BS4 object of the tfrrs page
and returns the race events as a part of a given dictionary
Arg: BS4 object of the page, dictionary for men's race, dictionary for women's race
Return: list of dictionaries 
'''
def getRaceEvents(soup):
    keys = ["name", "date", "venue", "location", "gender", "event", "team", "ind"]
    eventList = soup.find_all("ol", "inline-list pl-0 pt-5 events-list")[0].find_all("a")
    genders = []
    #only one gender
    if len(eventList) == 1:
        if any("Women" in name for name in eventList[0].text):
            genders = ["Women"]
            wRace = dict.fromkeys(keys)
            wRace["gender"] = "women"
            wEvent = eventList[0].text
            # CHANGE BECAUSE NOT ALL END WITH 'S
            # WOMEN AND MEN NOT JUST WOMEN'S/MEN'S
            endOfGender = wEvent.find("s") + 1
            wEvent = wEvent[endOfGender:].strip()
            wRace["event"] = wEvent
            return [genders, wRace]

        elif "Men" in eventList[0].text or "Men's" in eventList[0].text:
            genders = ["Men"]
            mRace = dict.fromkeys(keys)
            mRace["gender"] = "women"
            mEvent = eventList[0].text
            # CHANGE BECAUSE NOT ALL END WITH 'S
            # WOMEN AND MEN NOT JUST WOMEN'S/MEN'S
            endOfGender = mEvent.find("s") + 1
            mEvent = mEvent[endOfGender:].strip()
            mRace["event"] = mEvent
            return [genders, mRace]

        else:
            genders = ["Men", "Women"]
            womenFirst = True
            mRace = dict.fromkeys(keys)
            wRace = dict.fromkeys(keys)
            mRace["gender"] = "men"
            wRace["gender"] = "women"
            if(any("Women" in name for name in eventList[0].text)):
                wEvent = eventList[0].text
                #CHANGE BECAUSE NOT ALL END WITH 'S
                #WOMEN AND MEN NOT JUST WOMEN'S/MEN'S
                endOfGender = wEvent.find("s") + 1
                wEvent = wEvent[endOfGender:].strip()
                wRace["event"] = wEvent

                mEvent = eventList[1].text
                endOfGender = mEvent.find("s") + 1
                mEvent = mEvent[endOfGender:].strip()
                mRace["event"] = mEvent
            else:
                womenFirst = False
                mEvent = eventList[0].text
                endOfGender = mEvent.find("s") + 1
                mEvent = mEvent[endOfGender:].strip()
                mRace["event"] = mEvent

                wEvent = eventList[1].text
                endOfGender = wEvent.find("s") + 1
                wEvent = wEvent[endOfGender:].strip()
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
def getIndResultsFromPage(soup, womenFirst, year, mTeams, wTeams):
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
    mInd = scrapeIndResults(mResults, mInd, year, mTeams)
    wInd = scrapeIndResults(wResults, wInd, year, wTeams)
    return [mInd, wInd]

'''
This function takes a BS4 object of the tfrrs individual results 
and returns them as a part of a given dictionary
Arg: BS4 object of team html lines, dictionary for individual results
Return: updated dict for team results 
'''
def scrapeIndResults(results, ind, currYear, listOfTeamNames):
    listOfTeamNames.append("Thaddeus Stevens")
    year = ["FR-1","SO-2","JR-3","SR-4"]
    yearToGrade = {"Freshman":"FR-1", "Sophomore":"SO-2", "Junior":"JR-3", "Senior":"SR-4" }
    dateToGrade = {4:"FR-1",3:"SO-2",2:"JR-3",1:"SR-4"}
    i = 0
    noGrade = False
    while i < len(results)-1:
        if results[i] == "0":
            #skip place for now until DNS/DNF is determined
            i += 1
            name = ""
            # check for name and stop at year in school (if given)
            # checks if still on name (given that year is in standard format (i.e. SR-4))
            while results[i][0].isalpha() and not (results[i][-1].isdigit()):
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
                if any(sub in name for name in listOfTeamNames) and sub != "St.":
                    noGrade = True
                    break
                else:
                    name = name + results[i] + " "
                    i += 1
            ind["name"].append(name.strip())
            school = ""
            i += 1
            # find school name
            while results[i][0].isalpha() and "DN" not in results[i]:
                if results[i] == "DQ":
                    break
                school = school + results[i] + " "
                i += 1
            ind["team"].append(school.strip())
            ind["place"].append(results[i])
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
            while results[i][0].isalpha() and not (results[i][-1].isdigit()) :
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
                if any(sub in name for name in listOfTeamNames) and sub != "St.":
                    noGrade = True
                    break
                else:
                    name = name + results[i] + " "
                    i += 1
            ind["name"].append(name.strip())
            school = ""
            if noGrade == False:
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
            if i < len(results)-1 and len(results[i]) <= 3:
                if int(results[i]) != 0 and ( int(results[i]) != place+1 or int(results[i]) == place ):
                    i += 1
            #skip any splits that the data may have
            while i < len(results)-1 and len(results[i]) > 6:
                i += 1
            noGrade = False
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
This fucntion takes an upper limit for a range
and gets all of the information for the meets listed
on search pages 1 to upper limit from tfrrs
Args: int of upper limit 
Returns: 
'''
def getAllInfoFromRangeOfPages(limit):
    links = []
    for i in range(1, limit):
        links.extend(getMeetLinks("https://www.tfrrs.org/results_search_page.html?page=" + str(i)
                     + "&search_query=&with_month=&with_sports=xc&with_states=&with_year="))

    print(links)
    for i in range(len(links)):
        list = getRaceInfoFromPage(links[i])
        print(list[0])
        print(list[1])


def main():
    getAllInfoFromRangeOfPages(2)
    #getRaceInfoFromPage("https://www.tfrrs.org/results/xc/20662/NJCAA_Division_III_Cross_Country_Championship")
    #getRaceInfoFromPage("https://www.tfrrs.org/results/xc/19936/North_Coast_Athletic_Conference")


main()
