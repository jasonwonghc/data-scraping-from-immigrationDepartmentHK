import argparse
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

monthMap={
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}

base_url = "https://www.immd.gov.hk/"
menuUrl = "https://www.immd.gov.hk/eng/message_from_us/stat_menu.html"
base_index = 2; 

def getListOfLinks(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup.select(".main-container a")

def getDelta(url):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        total_arrival = soup.find("td", headers="Total_Arrival").decode_contents().replace(',', '')
        total_departure = soup.find("td", headers="Total_Departure").decode_contents().replace(',', '')
        return int(total_arrival) - int(total_departure)
    except: 
        return 0
    

def scrapingAll():
    total = 0
    list = getListOfLinks(menuUrl)
    links = []
    for link in list:
        [linkMonth, linkYear, *rest] = link.decode_contents().split()
        target_url = base_url + link.get('href')
        targetList = getListOfLinks(target_url)
        for date in targetList:
            links.append(base_url + date.get('href'))
    with ThreadPoolExecutor(max_workers=min(100, len(links))) as executor:
        for result in executor.map(getDelta, links):
            total += result    
    return total

def scrapingByYear(year):
    total = 0
    list = getListOfLinks(menuUrl)
    links = []
    for link in list:
        print(link.decode_contents())
        [linkMonth, linkYear, *rest] = link.decode_contents().split()
        if(int(linkYear) > year): break;
        if(int(linkYear) == year):
            target_url = base_url + link.get('href')
            targetList = getListOfLinks(target_url)
            for date in targetList:
                links.append(base_url + date.get('href'))
                # total += getDelta(base_url + date.get('href'))
                # print(total)
    with ThreadPoolExecutor(max_workers=min(100, len(links))) as executor:
        for result in executor.map(getDelta, links):
            total += result
    return total
    
def scrapingByYearAndMonth(year, month):
    total = 0
    list = getListOfLinks(menuUrl)
    for link in list:
        [linkMonth, linkYear, *rest] = link.decode_contents().split()
        if(monthMap[linkMonth] == month and int(linkYear) == year):
            target_url = base_url + link.get('href')
            targetList = getListOfLinks(target_url)
            for date in targetList:
                total += getDelta(base_url + date.get('href'))
            
            return total
        
    return total
        
def main(args):
    totalNumbers = 0
    if(args.year and args.month): 
        print('Scraping data from all data on ', args.month, args.year)
        totalNumbers = scrapingByYearAndMonth(args.year, args.month)
    elif(args.year): 
        print('Scraping data from all data in ', args.year)
        totalNumbers = scrapingByYear(args.year)
    else: 
        print('Scraping data from all data')
        totalNumbers = scrapingAll()
    
    print("Total population numbers: ", totalNumbers)

if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument('--year', type=int)
   parser.add_argument('--month', type=int)
   args = parser.parse_args()
   main(args)