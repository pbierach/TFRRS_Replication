import urllib.request

import selenium.common.exceptions
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from difflib import SequenceMatcher
import json

'''
This function takes a starting number and upper limit for a range
and gets all of the information for the meets listed
on search pages start to upper limit from tfrrs
Args: int, of start, int of upper limit 
Returns: 
'''
def getAllInfoFromRangeOfPages(start, limit, c ,r):
    s = Service('/Users/pbierach/desktop/tfrrs_replication/chromedriver')
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options, service=s)
    links = []
    allRaces = []
    for i in range(start, limit):
        links.extend(getMeetLinks("https://www.tfrrs.org/results_search_page.html?page=" + str(i)
                     + "&search_query=&with_month=&with_sports=xc&with_states=&with_year="))
    for i, link in enumerate(links):
        if i % 30 == 0 and i != 0:
            print("Page done.")
        results = getRaceInfoFromPage(driver, link, c, r)
        if type(results) == dict:
            allRaces.append(results)
        elif type(results) == list:
            allRaces.append(results[0])
            allRaces.append(results[1])
    return allRaces

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
        href = a.get('href')
        nccaa = "NCCAA" in href
        njcaa = "NJCAA" in href
        if not nccaa ^ njcaa:
            fullLink = "https://www.tfrrs.org" + href
            links.append(fullLink)
    return links

'''
Reads in a tfrrs race page and returns a dictionary containing
relevant information about the meet
Arg: selenium webdriver, url of the page
Return: list of dictionary of all meet information
'''
def getRaceInfoFromPage(driver, url, c, r):
    try:
        driver.get(url)
        list = getRaceEvents(driver)
        genders = list[0]
        if len(genders) == 1:
            if genders[0] == "Men":
                mRace = list[1]
                mRace = singleGenderRace(driver, mRace, c, r)
                return mRace
            else:
                wRace = list[1]
                wRace = singleGenderRace(driver, wRace, c, r)
                return wRace
        else:
            mRace = list[1]
            wRace = list[2]
            womenFirst = list[3]
            list = bothGenderRace(driver, mRace, wRace, womenFirst, c, r)
            mRace = list[0]
            wRace = list[1]
            return [mRace, wRace]
    except:
        print(url)

'''
This function takes a webdirver and determines how 
many dictionaries will be required to represent the race
Arg: selenium webdriver
Return: list containing either gender of race and dictionary for race or 
        list containing 2 dictionaries for races and if women are first in results 
'''
def getRaceEvents(driver):
    keys = ["name", "date", "state", "gender", "event", "conference", "regional", "national", "team", "ind"]
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

def bothGenderRace(driver, mRace, wRace, womenFirst, c, r):
    # get race specifics
    mRace = getRaceName(driver, mRace, c, r)
    wRace = getRaceName(driver, wRace, c, r)
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

def singleGenderRace(driver, race, c, r):
    # get race specifics
    race = getRaceName(driver, race, c, r)
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
def getRaceName(driver, race, c, r):
    name = driver.find_element(By.CLASS_NAME, "panel-title").text
    race["name"] = name
    race["conference"] = False
    race["national"] = False
    race["regional"] = False
    speicalMeetFound = False
    if "Championships" in name or "Championship" in name:
        for n in c['name']:
            if n in name:
                speicalMeetFound = True
                race["conference"] = True
                break
        for n in r['name']:
            if n in name:
                speicalMeetFound = True
                race["regional"] = True
                break
        if speicalMeetFound is False and ("Division I" in name or "Division II" in name or "Division III" in name or "NAIA" in name):
            race["national"] = True
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
        race["state"] = "None given"
    else:
        venue = ""
        place = ""
        #find separator of date and place
        endOfDate = header.text.find("|")+1
        #determine end of string
        endOfLocation = header.text.find("\n")
        if endOfLocation == -1:
            endOfLocation = len(header.text)
        #isolate the location
        location = header.text[endOfDate:endOfLocation]

        #isolate name of place
        comma = location.find(",")
        lastWhiteSpace = 0
        for i, char in enumerate(location[0:comma]):
            if char == ' ':
                lastWhiteSpace = i
        #isolate city, state
        place = location[lastWhiteSpace: comma+1]
        state = location[comma+1:len(location)].strip()
        for i, char in enumerate(state):
            if char == ' ':
                lastWhiteSpace = i
        #indicates zipcode
        if state[-1].isdigit():
            state = state[0:lastWhiteSpace]
        #sometimes state is listed twice
        list = state.split()
        race['state'] = list[0]
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

    #separate relevant data for each section
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
                    if tag.text != '\xa0':
                        scorers.append(tag.text)
                    else:
                        break
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
            if int(grade)-int(currYear) <=5 and int(grade)-int(currYear) >=0:
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

'''
This function scrapes the indoor conference/region lists
in order to create dictionaries for all conferences and regions in each division
Arg: none
Return: list of dictionaries representing conferences and regions 
'''
def getConfLists():
    divisions = ['d1', 'd2', 'd3', 'naia']
    s = Service('/Users/pbierach/desktop/tfrrs_replication/chromedriver')
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options, service=s)
    conferences = {
        'division': [],
        'name': [],
        'teams': [],
        'gender': 'men'
    }
    regions = {
        'division': [],
        'name': [],
        'teams': [],
        'gender': 'men'
    }
    for div in divisions:
        link = "https://www.tfrrs.org/directory_tab.html?outdoor=0&tab="+div+"&year=2022"
        driver.get(link)
        ul = driver.find_element(By.CLASS_NAME, "list-unstyled.pl-24.mt-5")
        list = getConfNames(ul, div, conferences, regions)
        conferences = list[0]
        regions = list[1]

    return [conferences, regions]

'''
This function takes the list of conference/region names 
from a page and scrapes the name of all the individual conf/regions
Arg: selenium html element of list of conf/region, current division, dictionary of conference and region
Return: list of updated dictionaries representing conferences and regions 
'''
def getConfNames(htmlElem, div, c, r):
    lines = htmlElem.find_elements(By.TAG_NAME, "li")
    qualListLine = 0
    for li in lines:
        if qualListLine == 0:
            qualListLine += 1
        elif "Region" in li.text:
            line = li.text.replace("w | m", "")
            line = line.replace("DI", "Division I")
            line = line.replace("DII", "Division II")
            line = line.replace("DIII", "Division III")
            r['division'].append(div)
            r['name'].append(line.strip())
        else:
            line = li.text.replace("w | m", "")
            c['division'].append(div)
            c['name'].append(line.strip())
    return [c, r]

'''
This function navigates to a given conference or region page on the tfrrs site
Arg: name of requested conference/region
Return: selenium chrome driver on requested conference/region's page  
'''
def goToConfRegionPage(name):
    s = Service('/Users/pbierach/desktop/tfrrs_replication/chromedriver')
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options,service=s)
    driver.get('https://www.tfrrs.org/')
    links = []
    confButton = driver.find_elements(By.CLASS_NAME, 'waves-effect.waves-classic')
    #reveal conference search field
    webdriver.ActionChains(driver).move_to_element(confButton[1]).perform()
    #click on conference search, input conference/region, search
    searchInput = driver.find_element(By.ID, 'conference_search')
    searchInput.send_keys(name)
    searchInput.send_keys(Keys.ENTER)
    return driver

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

'''
This function scrapes the indoor conference/region lists
in order to create dictionaries for all conferences and regions in each division
Arg: conference/region's page on tfrrs (as selenium webDriver), dictionaries for men and women
Return: list of updated dictionaries representing conferences and regions 
'''
def scrapeConfRegionPage(driver, m, w, hrefs):
    tableData = driver.find_element(By.CLASS_NAME, "tablesaw.table-striped.table-bordered.table-hover.tablesaw-columntoggle")
    tableEntries = tableData.find_elements(By.TAG_NAME, "a")
    i = 0
    while i < len(tableEntries)-1:
        if i+1 < len(tableEntries):
            curr = tableEntries[i].get_attribute('href')
            next = tableEntries[i+1].get_attribute('href')
            same = similar(curr[30:len(curr)], next[30:len(next)])
            if same > 0.8:
                hrefs.append(curr)
                i = i + 2
            else:
                hrefs.append(tableEntries[i].get_attribute("href"))
                i = i + 1
    teamTable = tableData.text.split("\n")
    firstElement = 0
    wTeams = []
    mTeams = []
    for elem in teamTable:
        if firstElement == 0:
            firstElement += 1
        elif elem[0] == " ":
            wTeams.append(elem.strip())
        else:
            separated = elem.split(" ")
            oneTeam = list(dict.fromkeys(separated))
            team = ""
            for string in oneTeam:
                team = team + string + " "
            wTeams.append(team.strip())
            mTeams.append(team.strip())
    m['teams'].append(mTeams)
    w['teams'].append(wTeams)
    return [m, w, hrefs]

'''
Driver function to gather and scrape names and teams of all conferences and regions at
d1, d2, d3, and naia levels 
Arg: none
Return: list of dictionaries representing conferences and regions 
'''
def confRegionDriver():
    teamHrefs = []
    list = getConfLists()
    mConf = list[0]
    wConf = mConf.copy()
    wConf['gender'] = 'women'
    mRegions = list[1]
    wRegions = mRegions.copy()
    wRegions['gender'] = 'women'
    for name in mConf["name"]:
        driver = goToConfRegionPage(name)
        list = scrapeConfRegionPage(driver, mConf, wConf, teamHrefs)
        mConf = list[0]
        wConf = list[1]
        teamHrefs = list[2]

    for name in mRegions["name"]:
        driver = goToConfRegionPage(name)
        list = scrapeConfRegionPage(driver, mRegions, wRegions, teamHrefs)
        mRegions = list[0]
        wRegions = list[1]
        teamHrefs = list[2]

    #call to team page scraping
    schools = schoolInfoDriver(teamHrefs, mConf)
    return [mConf, wConf, mRegions, wRegions, schools]

'''
Driver function to gather and scrape team information at the d1, d2, d3, and naia levels 
Arg: link to school pages on tfrrs, dictionary of conference information
Return: dictionary representing schools 
'''
def schoolInfoDriver(schoolLinks, conf):
    schools = {
        'name': [],
        'division': [],
        'region': [],
        'conference': []
    }
    s = Service('/Users/pbierach/desktop/tfrrs_replication/chromedriver')
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options, service=s)
    for link in schoolLinks:
        driver.get(link)
        schools = scrapeSchoolPage(driver, schools, conf)
    return schools

'''
Scraper function to gather team information from a tfrrs page  
Arg: selenium driver at a tfrrs school page, dictionary of school information, dictionary of conference information 
Return: list of dictionaries representing conferences and regions 
'''
def scrapeSchoolPage(driver, schools, c):
    try:
        schools['name'].append(driver.find_element(By.ID, 'team-name').text)
    except selenium.common.exceptions.NoSuchElementException:
        print(driver.current_url)
        schools['name'].append('error')
    finally:
        groups = driver.find_element(By.CLASS_NAME, 'panel-heading-normal-text').text
        groupList = groups.split(",")
        cList = []
        rList = []
        div = "?"
        for g in groupList:
            for name in c['name']:
                if name in g:
                    cList.append(g)
                    break
            else:
                g = g.strip()
                space = g.find(" ")
                div = g[0:space]
                rList.append(g)
        schools['division'].append(div)
        schools['region'].append(rList)
        schools['conference'].append(cList)
        return schools

'''
Function to create a json object   
Arg: list to be converted, given name for .json file 
Return: none 
'''
def createJSONObject(list, fileName):
    with open("/Users/pbierach/Desktop/tffrs_replication/json/meets/"+fileName, "w") as final:
        json.dump(list, final)

def assembleconferenceRegionSchools():
    print("Starting conference/region/school scrape")
    list = confRegionDriver()
    print("conference/region/school scrape finished")

    mC = list[0]
    print("Started conversion to json for Men's Conferences")
    createJSONObject(mC, "men-conf.json")
    print("Finished conversion to json for Men's Conferences")

    wC = list[1]
    print("Started conversion to json for Women's Conferences")
    createJSONObject(wC, "women-conf.json")
    print("Finished conversion to json for Women's Conferences")

    mR = list[2]
    print("Started conversion to json for Men's Regions")
    createJSONObject(mR, "men-region.json")
    print("Finished conversion to json for Men's Regions")

    wR = list[3]
    print("Started conversion to json for Women's Regions")
    createJSONObject(wR, "women-region.json")
    print("Finished conversion to json for Women's Regions")

    schools = list[4]
    print("Started conversion to json for schools")
    createJSONObject(schools, "schools.json")
    print("Finished conversion to json for schools")

def assembleMeets():
    list = getConfLists()
    mConf = list[0]
    mRegions = list[1]
    i = 1
    while i < 296:
        start = i
        end = i + 5
        print("Starting scraping meet results from pages" + str(start)+"-"+str(end))
        list = getAllInfoFromRangeOfPages(start, end, mConf, mRegions)
        print("Done scraping meet results")
        createJSONObject(list, "meets" + str(start) + "-" + str(end) + ".json")
        i = end + 1


def main():
    #assembleconferenceRegionSchools()
    assembleMeets()



main()