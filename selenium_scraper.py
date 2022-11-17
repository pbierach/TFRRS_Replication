import urllib.request
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json

'''
This function takes a starting number and upper limit for a range
and gets all of the information for the meets listed
on search pages start to upper limit from tfrrs
Args: int, of start, int of upper limit 
Returns: 
'''
def getAllInfoFromRangeOfPages(start, limit):
    s = Service('/Users/pbierach/desktop/tfrrs_replication/chromedriver')
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options, service=s)
    links = []
    for i in range(start, limit):
        links.extend(getMeetLinks("https://www.tfrrs.org/results_search_page.html?page=" + str(i)
                     + "&search_query=&with_month=&with_sports=xc&with_states=&with_year="))
    for link in links:
        list = getRaceInfoFromPage(driver, link)
    return links

'''
This function reads in a tfrrs search page
and returns a list of all the meet links contained in the search
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
        if not "NCCAA" in a.get('href'):
            fullLink = "https://www.tfrrs.org" + a.get('href')
            links.append(fullLink)
    return links

'''
Reads in a tfrrs race page and returns a dictionary containing
relevant information about the meet
Arg: selenium webdriver, url of the page
Return: list of dictionary of all meet information
'''
def getRaceInfoFromPage(driver, url):
    print(url)
    driver.get(url)
    keys = ["name", "date", "venue", "location", "gender", "event", "team", "ind"]
    list = getRaceEvents(driver)
    genders = list[0]
    if len(genders) == 1:
        if genders[0] == "Men":
            mRace = list[1]
            mRace = singleGenderRace(driver, mRace)
            print("done")
            return mRace
        else:
            wRace = list[1]
            wRace = singleGenderRace(driver, wRace)
            print("done")
            return wRace
    else:
        mRace = list[1]
        wRace = list[2]
        womenFirst = list[3]
        list = bothGenderRace(driver, mRace, wRace, womenFirst)
        mRace = list[0]
        wRace = list[1]
        print("done")
        return [mRace, wRace]

'''
This function takes a webdirver and determines how 
many dictionaries will be required to represent the race
Arg: selenium webdriver
Return: list containing either gender of race and dictionary for race or 
        list containing 2 dictionaries for races and if women are first in results 
'''
def getRaceEvents(driver):
    keys = ["name", "date", "venue", "location", "gender", "event", "team", "ind"]
    eventList = driver.find_element(By.ID, 'quick-links-list')
    parenthEvent = driver.find_elements(By.CLASS_NAME, 'custom-table-title.custom-table-title-xc')
    #parenthEvent = parenthEvent.find_elements(By.CLASS_NAME, 'custom-table-title custom-table-title-xc')
    parenthList = set()
    for el in parenthEvent:
        if "Individual" in el.text and not "(0 Mile)" in el.text:
            parenthList.add(el.text)
    parenthList = list(parenthList)
    #one gender
    if len(parenthList) == 1:
        # case: single gender is womens
        if "Women" in parenthList[0]:
            genders = ["Women"]
            wRace = dict.fromkeys(keys)
            wRace["gender"] = "women"
            wEvent = parenthList[0]
            openP = wEvent.find("(") + 1
            closeP = wEvent.find(")")
            wEvent = wEvent[openP:closeP]
            wRace["event"] = wEvent
            return [genders, wRace]

        # case: single gender is men's
        elif "Men" in parenthList[0]:
            genders = ["Men"]
            mRace = dict.fromkeys(keys)
            mRace["gender"] = "Men"
            mEvent = parenthList[0]
            openP = mEvent.find("(") + 1
            closeP = mEvent.find(")")
            mEvent = mEvent[openP:closeP]
            mRace["event"] = mEvent
            return [genders, mRace]
        else:
            genders = ["Not specified"]
            race = dict.fromkeys(keys)
            race["gender"] = genders[0]
            event = parenthList[0]
            openP = event.find("(") + 1
            closeP = event.find(")")
            event = event[openP:closeP]
            race["event"] = event
            return [genders, race]

    #both genders
    else:
        #women are first in results reporting
        if "Women" in parenthList[0]:
            womenFirst = True
            genders = ["Men", "Women"]
            wRace = dict.fromkeys(keys)
            wRace["gender"] = "women"
            wEvent = parenthList[0]
            openP = wEvent.find("(") + 1
            closeP = wEvent.find(")")
            wEvent = wEvent[openP:closeP]
            wRace["event"] = wEvent

            mRace = dict.fromkeys(keys)
            mRace["gender"] = "Men"
            mEvent = parenthList[1]
            openP = mEvent.find("(") + 1
            closeP = mEvent.find(")")
            mEvent = mEvent[openP:closeP]
            mRace["event"] = mEvent
            return [genders, mRace, wRace, womenFirst]
        #men are first in results reporting
        else:
            womenFirst = False
            genders = ["Men", "Women"]
            wRace = dict.fromkeys(keys)
            wRace["gender"] = "women"
            wEvent = parenthList[1]
            openP = wEvent.find("(") + 1
            closeP = wEvent.find(")")
            wEvent = wEvent[openP:closeP]
            wRace["event"] = wEvent

            mRace = dict.fromkeys(keys)
            mRace["gender"] = "Men"
            mEvent = parenthList[0]
            openP = mEvent.find("(") + 1
            closeP = mEvent.find(")")
            mEvent = mEvent[openP:closeP]
            mRace["event"] = mEvent
            return [genders, mRace, wRace, womenFirst]

def bothGenderRace(driver, mRace, wRace, womenFirst):
    # get race specifics
    mRace = getRaceName(driver, mRace)
    wRace = getRaceName(driver, wRace)
    # date
    mRace = getRaceDate(driver, mRace)
    wRace = getRaceDate(driver, wRace)
    # location
    mRace = getRaceLocation(driver, mRace)
    wRace = getRaceLocation(driver, wRace)
    # separate by team results and individual
    year = mRace["date"][0:4]
    list = getBothResultsFromPage(driver, womenFirst, year)
    mRace["team"] = list[0]
    wRace["team"] = list[1]
    mRace["ind"] = list[2]
    wRace["ind"] = list[3]
    return [mRace, wRace]

def singleGenderRace(driver, race):
    # get race specifics
    race = getRaceName(driver, race)
    # date
    race = getRaceDate(driver, race)
    # location
    race = getRaceLocation(driver, race)
    # separate by team results and individual
    year = race["date"][0:5]
    list = getSingleResultsFromPage(driver, year)
    race["team"] = list[0]
    race["ind"] = list[1]
    return race

'''
This function takes a selenium webdriver of a tfrrs page
and returns the name of the race as a part of a given dictionary
Arg: selenium webdriver of the page, dictionary for men's race, dictionary for women's race
Return: list of dictionaries 
'''
def getRaceName(driver, race):
    name = driver.find_element(By.CLASS_NAME, "panel-title").text
    race["name"] = name
    return race

'''
This function takes a BS4 object of the tfrrs page
and returns the date of the race as a part of a given dictionary
Arg: BS4 object of the page, dictionary for men's race, dictionary for women's race
Return: list of dictionaries 
'''
def getRaceDate(driver, race):
    smallHeader = driver.find_element(By.CLASS_NAME, 'col-lg-8')
    endOfDate = smallHeader.text.find("|")
    date = smallHeader.text[0:endOfDate].strip()
    race["date"] = convertDateToSQL(date)
    return race

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

    year = date[(dayIndex + 1):length].strip()
    month = monthDict[date[0:monthIndex]]
    day = date[monthIndex:dayIndex]
    day = day.strip()
    if len(day) == 1:
        day = "0" + day
    return year + "-" + month + "-" + day

'''
This function takes a BS4 object of the tfrrs page
and returns the venue and location of the race as a part of a given dictionary
Arg: BS4 object of the page, dictionary for men's race, dictionary for women's race
Return: list of dictionaries 
'''
def getRaceLocation(driver, race):
    header = driver.find_element(By.CLASS_NAME, 'col-lg-8')
    if len(header.text) < 21:
        race["venue"] = "None given"
        race["location"] = "None given"
    else:
        venue = ""
        place = ""
        endOfDate = header.text.find("|")+1
        endOfLocation = header.text.find("\n")
        location = header.text[endOfDate:endOfLocation]
        if location[-1].isdigit():
            location = location[0:len(location)-6]
        secondLastWhite = 0
        lastWhiteSpace = 0
        for i, char in enumerate(location):
            if char == ' ':
                secondLastWhite = lastWhiteSpace
                lastWhiteSpace = i
        venue = location[0:secondLastWhite].strip()
        place = location[secondLastWhite: len(location)].strip()
        race["venue"] = venue
        race["location"] = place
    return race

'''
This function takes a tfrrs page and returns team 
and individual results as a part of a given dictionary
Arg: driver, boolean if Women's results were first on page
Return: list of dictionaries 
'''
def getBothResultsFromPage(driver, womenFirst, year):
    tKeys = ["place", "team", "points", "scorers"]
    iKeys = ["place", "name", "year", "team", "time"]
    mTeam = dict.fromkeys(tKeys)
    wTeam = dict.fromkeys(tKeys)
    mInd = {iKeys[0]: [], iKeys[1]: [], iKeys[2]: [], iKeys[3]: [], iKeys[4]: []}
    wInd = {iKeys[0]: [], iKeys[1]: [], iKeys[2]: [], iKeys[3]: [], iKeys[4]: []}

    #separate relevant data for the each section
    page = driver.page_source
    html = BeautifulSoup(page, 'html.parser')
    results = html.find_all("tbody", "color-xc")
    if womenFirst:
        wtResultsRaw = results[0]
        mtResultsRaw = results[2]
        wiResultsRaw = results[1]
        miResultsRaw = results[3]
    else:
        wtResultsRaw = results[2]
        mtResultsRaw = results[0]
        wiResultsRaw = results[3]
        miResultsRaw = results[1]

    # get team data from relevant html
    mTeam = scrapeTeamResults(mtResultsRaw, mTeam)
    wTeam = scrapeTeamResults(wtResultsRaw, wTeam)

    # get individual data from relevant html
    mInd = scrapeIndResults(miResultsRaw, mInd, year)
    wInd = scrapeIndResults(wiResultsRaw, wInd, year)
    return [mTeam, wTeam, mInd, wInd]

'''
This function takes a BS4 object of the tfrrs team results 
and returns them as a part of a given dictionary
Arg: BS4 object of team html lines, dictionary for team results
Return: updated dict for team results
'''
def scrapeTeamResults(results, team):
    listOfPlaces = []
    listOfTeams = []
    listOfPoints = []
    listOfScorers = []
    tr = results.find_all("tr")
    for t in tr:
        items = 0
        scorers = []
        for tag in t:
            if tag.text != "\n":
                items += 1
                if items == 1:
                    listOfPlaces.append(tag.text)
                elif items == 2:
                    currTeam = tag.text
                    currTeam = currTeam.replace("\n","")
                    listOfTeams.append(currTeam.strip())
                elif items == 5:
                    listOfPoints.append(tag.text)
                elif items > 5:
                    scorers.append(tag.text)
        listOfScorers.append(scorers)
    team["place"] = listOfPlaces
    team["team"] = listOfTeams
    team["points"] = listOfPoints
    team["scorers"] = listOfScorers
    return team

'''
This function takes a BS4 object of the tfrrs individual results 
and returns them as a part of a given dictionary
Arg: BS4 object of team html lines, dictionary for individual results
Return: updated dict for team results 
'''
def scrapeIndResults(results, ind, currYear):
    tr = results.find_all("tr")
    for t in tr:
        items = 0
        for line in t:
            if line.text != "\n":
                items += 1
                if items == 1:
                    #place
                    ind["place"].append(line.text)
                elif items == 2:
                    #name
                    nameRaw = line.text
                    nameRaw = nameRaw.replace("\n", "")
                    ind["name"].append(nameRaw.strip())
                elif items == 3:
                    #check year format
                    ind["year"].append(checkGradeFormat(line.text, currYear))
                elif items == 4:
                    teamRaw = line.text
                    teamRaw = teamRaw.replace("\n", "")
                    ind["team"].append(teamRaw.strip())
                elif items == 6:
                    ind["time"].append(line.text)
                    break
    return ind

'''
Takes a string that represents the grade of a runner and returns
it in a standard format of (FR-1, SO-2, JR-3, SR-4)
Args: grade string, integer of year of race
Returns: a standardized grade string
'''
def checkGradeFormat(grade, currYear):
    year = ["FR-1", "SO-2", "JR-3", "SR-4"]
    yearToGrade = {"Freshman": "FR-1", "Sophomore": "SO-2", "Junior": "JR-3", "Senior": "SR-4"}
    dateToGrade = {4: "FR-1", 3: "SO-2", 2: "JR-3", 1: "SR-4", 0: "SR-4"}
    #standard grade format
    if grade in year:
        return grade
    else:
        # written out as a year (i.e. 2024)
        if grade[0].isdigit():
            if int(grade)-int(currYear) >=5 and int(grade)-int(currYear) <=0:
                return dateToGrade[int(grade)-int(currYear)]
        elif grade == "Freshman" or grade == "Sophomore" or grade == "Junior" or grade == "Senior":
        # written out as a string
            return yearToGrade[grade]
        else:
            return "None given"

'''
This function takes a tfrrs page and returns team 
and individual results as two dictionaries
Arg: driver, current year
Return: list of dictionaries 
'''
def getSingleResultsFromPage(driver, year):
    keys = ["place", "team", "points", "scorers"]
    iKeys = ["place", "name", "year", "team", "time"]
    team = dict.fromkeys(keys)
    ind = {iKeys[0]: [], iKeys[1]: [], iKeys[2]: [], iKeys[3]: [], iKeys[4]: []}
    # separate relevant data for the team section
    page = driver.page_source
    html = BeautifulSoup(page, 'html.parser')
    results = html.find_all("tbody", "color-xc")
    tResultsRaw = results[0]
    iResultsRaw = results[1]
    # get data from relevant html
    team = scrapeTeamResults(tResultsRaw, team)
    ind = scrapeIndResults(iResultsRaw, ind, year)
    return [team, ind]

def createJSONObjects(list):
    with open("meets.json", "w") as final:
        json.dump(list, final)

def main():
    s = Service('/Users/pbierach/desktop/tfrrs_replication/chromedriver')
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options, service=s)
    #print(getAllInfoFromRangeOfPages(1, 6))
    #getRaceInfoFromPage(driver, 'https://www.tfrrs.org/results/xc/20794/American_Midwest_Conference_Cross_Country_Championships')
    #list = getRaceInfoFromPage(driver, 'https://www.tfrrs.org/results/xc/20453/Lewis__Clark_Time_Trials')
    #print(list[0])
    #print(list[1])
    #getRaceInfoFromPage(driver, "https://www.tfrrs.org/results/xc/21209/Alverno_College_Home_Meet")
    #getRaceInfoFromPage("https://www.tfrrs.org/results/xc/20823/NCAA_Division_III_Niagara_Region_Cross_Country_Championships")



main()