from bs4 import BeautifulSoup
import urllib.request
import csv
import re

csvout = "out.csv"

all_sports_base = "http://www.virginiasports.com"

# get lists of sports and their hrefs
r = urllib.request.urlopen(all_sports_base).read()
soup = BeautifulSoup(r, "html.parser")

# get href to roster for each sport
sports = soup.find_all("a", href=re.compile("^/sport"), text="Roster")

# There are repeated sports (listed both on men's and women's section, so we use a set here to prevent duplicates)
all_sports_links = set()
all_sports_names = set()
all_sports_roster = {}

# Get link for each sport
# there are only 19 sports because track and cross country athletes are all listed on one page
for sport in sports:
    link = sport.get("href")
    all_sports_links.add(link)

count = 1
for sport_link in all_sports_links:
    # read url to specific sport
    x = urllib.request.urlopen(all_sports_base + sport_link).read()

    sportname = sport_link.split("/")[2]
    print("SPORT NAME: %s" % sportname)

    soup_sport = BeautifulSoup(x, "html.parser")
    roster = []
    for name_element in soup_sport.find_all("tr", class_="player-row"):
        # exclude coaches
        if "http://onlyfans.cstv.com" not in name_element.a.get("href"):
            player = {}
            player["name"] = name_element.a.get_text()

            # get url to player info (includes name, hometown, high school and other stats -- varies by sport)
            player_info_link = name_element.a.get("href")
            y = urllib.request.urlopen(all_sports_base + player_info_link).read()
            soup = BeautifulSoup(y, "html.parser")

            # check if hometown and high school are provided (hometown and high school are always the second and third elements
            infoExists = len(soup.find_all("font", color="#FFFFFF"))

            player["hometown"] = soup.find_all("font", color="#FFFFFF")[1].text.split(":")[
                1] if infoExists >= 2 else "Not provided"
            player["highschool"] = soup.find_all("font", color="#FFFFFF")[2].text.split(":")[
                1] if infoExists >= 3 else "Not provided"
            roster.append(player)

            print("Added data for %s" % player["name"])
    print(roster)
    print("Sport %d/%d complete" % (count, len(all_sports_links)))
    count += 1
    all_sports_roster[sportname] = roster

# write to csv
with open(csvout, 'w') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(["Sport", "Name", "Hometown", "High School"])
    for sportName, roster in all_sports_roster.items():
        for athlete in roster:
            csvwriter.writerow([sportName, athlete["name"], athlete["hometown"], athlete["highschool"]])
