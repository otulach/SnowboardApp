import requests
from bs4 import BeautifulSoup
import pandas as pd
import os.path
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import date

# Scraping all urls that lead to main page of every athlete
def getURLS(biographiesURL):
    page = requests.get(biographiesURL)
    allAthletes = BeautifulSoup(page.content, "html.parser")
    athleteRows = allAthletes.find_all("a", class_="table-row")
    
    urls = []
    for row in athleteRows:
        urls.append(row.get('href') + "&type=result&categorycode=&sort=&place=&disciplinecode=&position=&limit=1000")
    return urls

# Offset makes it uneasy to scrape all athletes, so this will deal with it.
def concatURLS(baseUrl):
    allUrls = []
    for offset in [0, 1000, 2000, 3000]:
        urls = getURLS(baseUrl + '&offset=' + str(offset))
        allUrls.extend(urls)
    
    return allUrls

# Making a DataFrame with results of single athlete
def tableAthlete(url): 
    page = requests.get(url)
    athlete = BeautifulSoup(page.content, "html.parser") 
    racesRows = athlete.find_all("a", class_="table-row")
    
    df = pd.DataFrame(columns=['Name', 'Gender', 'Date', 'Location', 'Country', 'Nation', 'Category', 'Discipline', 'Position', 'FIS Points'])
    
    try:
        name = athlete.find("h1", class_="athlete-profile__name").text
        listName = name.split()
        name = listName[1].lower().capitalize() + " " + listName[0].lower().capitalize()
        genderBar = athlete.find("li", id="Gender")
        gender = genderBar.find("span", class_="profile-info__value").text
        nation = athlete.find("span", class_="country__name").text
        print(name)
    except:
        return df
    
    for row in racesRows:
        try:
            date = row.find("div", class_="g-xs-4 g-sm-4 g-md-4 g-lg-4 justify-left").text
            location = row.find("div", class_="g-md g-lg justify-left hidden-sm-down").text
            country = row.find("span", class_="country__name-short").text
            category = row.find("div", class_="g-md-5 g-lg-5 justify-left hidden-sm-down").text
            discipline = row.find("div", class_="g-md-3 g-lg-3 justify-left hidden-sm-down").text
            position = row.find("div", class_="g-xs-24 g-sm g-md g-lg justify-right").text
            pointsFIS = row.find("div", class_="g-xs-24 g-sm-8 g-md-8 g-lg-8 justify-right").text
                
            df.loc[len(df.index)] = [name, gender, date, location, country, nation, category, discipline, position, pointsFIS] 
        except:
            print()
        
    return(df)
   
# Creating a CSV file for every active athlete!!
def createAthletes(): 
    try:
        os.mkdir("AthletesCSV")
    except:
        print("Directory AthletesCSV already exists.")
    
    overallFrame = pd.DataFrame(columns=['Date', 'Location', 'Country', 'Category', 'Discipline', 'Gender'])
    for singleAthleteURL in concatURLS("https://www.fis-ski.com/DB/snowboard/snowboard-alpine/biographies.html?lastname=&firstname=&sectorcode=SB&gendercode=&birthyear=&skiclub=&skis=&nationcode=&fiscode=&status=O&search=true&limit=1000"):
        dataFrame = tableAthlete(singleAthleteURL)
        if not dataFrame.empty:
            athleteName = dataFrame.Name.unique()[0].replace(" ", "")
            dataFrame.to_csv(os.path.join("AthletesCSV",athleteName + ".csv"))
            overallFrame = pd.concat([overallFrame, dataFrame])

# Creating a arrow structure, for faster funcioning of the app
    arrowFrame = pa.Table.from_pandas(overallFrame)
    pq.write_table(arrowFrame, "AthletesCSV/allathletes.parquet", compression=None)
       
# Scraping all urls of race bundles 
def getRaceURLS(races):
    racesPage = requests.get(races)
    allRaces = BeautifulSoup(racesPage.content, "html.parser")
    raceRows = allRaces.find_all("div", class_="table-row reset-padding")
    
    urls = []
    for row in raceRows:
        raceURL = row.find("a", class_="pr-1 g-lg-1 g-md-1 g-sm-2 hidden-xs justify-left").get('href')
        urls.append(raceURL)
    return urls
    
# Making a DataFrame with information from one race bundle
def tableRaces(url): 
    page = requests.get(url)
    race = BeautifulSoup(page.content, "html.parser")
    racesRows = race.find_all("div", class_="container g-row px-sm-1 px-xs-0")
    
    df = pd.DataFrame(columns=['Date', 'Location', 'Country', 'Category', 'Discipline', 'Gender'])
    
    try:
        name = race.find("h1", class_="heading heading_l2 heading_off-sm-style heading_plain event-header__name").text
        listName = name.split()
        location = listName[0].lower().capitalize()
        country  = listName[1][1:-1]
    except:
        return df
    
    print(location)
    for row in racesRows:
        try:
            date = row.find("div", class_="timezone-date").get('data-date')
            category = row.find("a", class_="g-lg-2 g-xs-2 justify-center hidden-sm-down").text
            discipline = row.find("div", class_="clip").text.strip()
            
            gender = row.find("div", class_="gender__inner").text.strip()
            if gender == "M":
                gender = "Male"
            else:
                gender = "Female"
                
            df.loc[len(df.index)] = [date, location, country, category, discipline, gender] 
        except:
            print()
        
    return(df)

# Concatenating Dataframes into one containing races from the whole year an exporting it!!
def createRacesBySeason(season): 
    df = pd.DataFrame(columns=['Date', 'Location', 'Country', 'Category', 'Discipline', 'Gender'])
    
    for bundleURL in getRaceURLS(season):
        dataFrame = tableRaces(bundleURL)
        if not dataFrame.empty:
            df = pd.concat([df, dataFrame])
            
    seasonName = df.iloc[0]['Date'][0:4]        
    df.to_csv("SeasonsCSV" + seasonName + ".csv", index=False)
    
year = 1995
last = int(date.today().year)
while year < last:
    yearURL = 'https://www.fis-ski.com/DB/snowboard/snowboard-alpine/calendar-results.html?eventselection=&place=&sectorcode=SB&seasoncode='+ str(year) +'&categorycode=&disciplinecode=PSL,PGS,GS,SL,PRT&gendercode=&racedate=&racecodex=&nationcode=&seasonmonth=X-'+ str(year) +'&saveselection=-1&seasonselection='
    createRacesBySeason(year)

createAthletes()