
import time
from datetime import datetime
import os
import csv
import glob
from selenium import webdriver
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

import requests
from urllib.parse import urlparse, urljoin


WAIT = 20
# Month abbreviation, day and year
nowtime = datetime.now().strftime("%b-%d-%Y %H-%M-%S")
print("today: ", nowtime)

# Creating a webdriver instance
# driver = webdriver.Chrome("chromedriver.exe")
# driver = webdriver.Chrome(ChromeDriverManager().install())

msacode_url = 'https://www.naics.com/business-lists/counts-by-msa/'
scrape_url = 'https://web.sba.gov/pro-net/search/dsp_dsbs.cfm'
data_url = 'https://web.sba.gov/dsbs/search/dsp_profilelist.cfm?RequestTimeout=180'

outdatafile = open(nowtime + '.csv', 'w', newline='', encoding="utf-8")
csv_data_writer = csv.writer(outdatafile)
outdatafileheaders = ['code', 'URL', 'This profile was last updated', 'Status', 'User ID', 'Name of Firm', 'Trade Name ("Doing Business As ...")', 'UEI', 'Address, line 1', 'Address, line 2', 'City', 'State', 'Zip', 'Phone Number', 'Fax Number', 'E-mail Address', 'WWW Page', 'E-Commerce Website', 'Contact Person', 'County Code (3 digit)', 'Congressional District', 'Metropolitan Statistical Area', 'CAGE Code', 'Year Established', 'Accepts Government Credit Card?', 'GSA Advantage Contract(s)', 'Legal Structure', 'Ownership and Self-Certifications', 'Current Principals', '"Business Development Servicing Office" (for certifications)', 'SBA 8(a) Case Number', 'SBA 8(a) Entrance Date', 'SBA 8(a) Exit Date', 'HUBZone Certified?', 'HUBZone Certification Date', '8(a) JV Entrance Date', '8(a) JV Exit Date', 'WOSB Certified?', 'WOSB Pending?', 'EDWOSB Certified?', 'EDWOSB Pending?', 'Non-Federal-Government Certifications', 'Capabilities Narrative', 'Special Equipment/Materials', 'Business Type Percentages', 'Construction Bonding Level (per contract)', 'Construction Bonding Level (aggregate)', 'Service Bonding Level (per contract)', 'Service Bonding Level (aggregate)', 'NAICS Codes with Size Determinations by NAICS', 'Keywords', 'Quality Assurance Standards', 'Electronic Data Interchange capable?', 'Exporter?', 'Export Business Activities', 'Exporting to', 'Desired Export Business Relationships', 'Description of Export Objective(s)', 'Name', 'Contract', 'Start', 'End', 'Value', 'Contact', 'Phone']
csv_data_writer.writerow(outdatafileheaders)


def Get_MSA_Code(url):

    code_1 = []
    code_2 = []

    txtfile = open('MSA_code.txt', 'w', encoding="utf-8")

    outcodefile = open('MSA code.csv', 'w', newline='', encoding="utf-8")
    csv_code_writer = csv.writer(outcodefile)

    # Opening URL
    page = requests.get(url)
    soup = BeautifulSoup(page.content,'html.parser')
    # print(soup.prettify()) # print the parsed data of html
    # print(soup)

    gdp_table = soup.find('table', attrs={'class': 'table table-striped'})
    gdp_table_data = gdp_table.find_all('tr')  # contains 2 rows

    # Get all the headings of Lists
    headings = []
    for th in gdp_table_data[0].find_all('th'):
        # remove any newlines and extra spaces from left and right
        headings.append(th.text.replace('\n', ' ').strip())
    csv_code_writer.writerow(headings)

    for tr in gdp_table_data:
        try:
            t_row = []
            tds = tr.find_all('td')
            if tds[0].text != '0000':
                code_1.append(tds[0].text)
            if tds[4].text != '0000':
                code_2.append(tds[4].text)
            for td in tds:
                t_row.append(td.text.replace('\n', ' ').strip())
            csv_code_writer.writerow(t_row)
        except:
            pass

    for code in code_1:
        txtfile.write(code)
        txtfile.write('\n')
    for code in code_2:
        txtfile.write(code)
        txtfile.write('\n')

    txtfile.close()
    outcodefile.close()

def Get_Profilehead(profilehead):

    index = 0
    index = profilehead.find(':')

    if index > 0:
        aprofilehead = profilehead[:index]
    else:
        aprofilehead = profilehead

    return aprofilehead

def MSA_Data(url, code):

    # print ('MSA_Data URL:', url, code)

    # try:
    outdatafilerow = []

    print ('website loading now...')

    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content,'html.parser')

        if 'Request timed out waiting to execute' in soup.text:
            print ('Website loading error:', soup.text)
            MSA_Data(url, code)
    except:
        for i in range(WAIT):
            print(f'[green][+][/green] Website is too busy. Waiting for {WAIT-i} seconds', end="\r")
            time.sleep(1)
        MSA_Data(url, code)

    outdatafilerow.append(code)
    outdatafilerow.append(url)

    # f = open('test1.html', 'r', encoding="utf8")
    # soup = BeautifulSoup(f, 'html.parser')
    # # print(soup)

    try:
        datasets = soup.find_all("div",{"data-role":"collapsible"})

        # for dataset in datasets:
        #     print('dataset:', dataset)

        # dataset[0]
        profiles = datasets[0].find_all("div",{"class":"profileline"})
        for profile in profiles:        
            # try: 
            #     profilehead = profile.find("div",{"class":"profilehead"}).text
            #     aprofilehead = Get_Profilehead(profilehead)            
            #     outdatafileheaders.append(aprofilehead)
            # except:
            #     if headerflag == 0:
            #         outdatafileheaders.append(' ')
            #     pass
            try:
                profileinfo = profile.find("div",{"class":"profileinfo"}).text
                outdatafilerow.append(profileinfo)                    
            except:
                outdatafilerow.append(' ')
                pass
            print ('profile 0:', profileinfo)

        # dataset[1]
        profiles = datasets[1].find_all("div",{"class":"profileline"})
        profileheads = datasets[1].find_all("h3")
        profileinfos = datasets[1].find_all("div",{"class":"indent_same_as_profilehead"})

        infoindex = 0
        frameindex = 0
        while infoindex < 2:
            # try:
            #     profilehead = profiles[infoindex].find("div",{"class":"profilehead"}).text
            #     aprofilehead = Get_Profilehead(profilehead)
            #     outdatafileheaders.append(aprofilehead)
            # except:
            #     if headerflag == 0:
            #         outdatafileheaders.append(' ')
            #     pass
            try:
                profileinfo = profiles[infoindex].find("div",{"class":"profileinfo"}).text
                outdatafilerow.append(profileinfo)                    
            except:
                outdatafilerow.append(' ')
                pass 
            infoindex += 1
            print ('profile 1:', profileinfo)

        while frameindex < 2:
            # try:
            #     profilehead = profileheads[frameindex].text
            #     aprofilehead = Get_Profilehead(profilehead)
            #     outdatafileheaders.append(aprofilehead)
            # except:
            #     if headerflag == 0:
            #         outdatafileheaders.append(' ')
            #     pass
            try:
                profileinfo = profileinfos[frameindex].text
                outdatafilerow.append(profileinfo)                    
            except:
                outdatafilerow.append(' ')
                pass
            frameindex += 1
            print ('profile 1:', profileinfo)
        
        while infoindex < len(profiles):
            # try:
            #     profilehead = profiles[infoindex].find("div",{"class":"profilehead"}).text
            #     aprofilehead = Get_Profilehead(profilehead)
            #     outdatafileheaders.append(aprofilehead)
            # except:
            #     if headerflag == 0:
            #         outdatafileheaders.append(' ')
            #     pass
            try:
                profileinfo = profiles[infoindex].find("div",{"class":"profileinfo"}).text
                outdatafilerow.append(profileinfo)                    
            except:
                outdatafilerow.append(' ')
                pass 
            infoindex += 1
            print ('profile 1:', profileinfo)

        # try:
        #     profilehead = profileheads[len(profileheads)-1].text
        #     aprofilehead = Get_Profilehead(profilehead)
        #     outdatafileheaders.append(aprofilehead)
        # except:
        #     if headerflag == 0:
        #         outdatafileheaders.append(' ')
        #     pass   
        try:
            profileinfo = profileinfos[len(profileinfos)-1].text
            outdatafilerow.append(profileinfo)                    
        except:
            outdatafilerow.append(' ')
            pass     
        print ('profile 1:', profileinfo)
        
        # dataset[4]
        profiles = datasets[4].find_all("div",{"class":"profileline"})
        # profileheads = datasets[4].find_all("h3")
        profileinfos = datasets[4].find_all("div",{"class":"indent_same_as_profilehead"})

        infoindex = 0
        frameindex = 0

        while frameindex < 3:
            # try:
            #     profilehead = profileheads[frameindex].text
            #     if headerflag == 0:
            #         aprofilehead = Get_Profilehead(profilehead)
            #         outdatafileheaders.append(aprofilehead)
            # except:
            #     if headerflag == 0:
            #         outdatafileheaders.append(' ')
            #     pass
            try:
                profileinfo = profileinfos[frameindex].text
                outdatafilerow.append(profileinfo)                    
            except:
                outdatafilerow.append(' ')
                pass
            frameindex += 1
            print ('profile 4:', profileinfo)
        
        while infoindex < 4:
            # try:
            #     profilehead = profiles[infoindex].find("div",{"class":"profilehead"}).text
            #     aprofilehead = Get_Profilehead(profilehead)
            #     outdatafileheaders.append(aprofilehead)
            # except:
            #     if headerflag == 0:
            #         outdatafileheaders.append(' ')
            #     pass
            try:
                profileinfo = profiles[infoindex].find("div",{"class":"profileinfo"}).text
                outdatafilerow.append(profileinfo)                    
            except:
                outdatafilerow.append(' ')
                pass 
            infoindex += 1
            print ('profile 4:', profileinfo)

        while frameindex < len(profileinfos):
            # try:
            #     profilehead = profileheads[frameindex].text
            #     if headerflag == 0:
            #         aprofilehead = Get_Profilehead(profilehead)
            #         outdatafileheaders.append(aprofilehead)
            # except:
            #     if headerflag == 0:
            #         outdatafileheaders.append(' ')
            #     pass
            try:
                profileinfo = profileinfos[frameindex].text
                outdatafilerow.append(profileinfo)                    
            except:
                outdatafilerow.append(' ')
                pass
            frameindex += 1
            print ('profile 4:', profileinfo)

        while infoindex < len(profiles):
            # try:
            #     profilehead = profiles[infoindex].find("div",{"class":"profilehead"}).text
            #     aprofilehead = Get_Profilehead(profilehead)
            #     outdatafileheaders.append(aprofilehead)
            # except:
            #     if headerflag == 0:
            #         outdatafileheaders.append(' ')
            #     pass
            try:
                profileinfo = profiles[infoindex].find("div",{"class":"profileinfo"}).text
                outdatafilerow.append(profileinfo)                    
            except:
                outdatafilerow.append(' ')
                pass 
            infoindex += 1
            print ('profile 4:', profileinfo)

        # dataset[5]
        profiles = datasets[5].find_all("div",{"class":"profileline"})
        for profile in profiles:        
            # try: 
            #     profilehead = profile.find("div",{"class":"profilehead"}).text
            #     aprofilehead = Get_Profilehead(profilehead)            
            #     outdatafileheaders.append(aprofilehead)
            # except:
            #     if headerflag == 0:
            #         outdatafileheaders.append(' ')
            #     pass
            try:
                profileinfo = profile.find("div",{"class":"profileinfo"}).text
                outdatafilerow.append(profileinfo)                    
            except:
                outdatafilerow.append(' ')
                pass
            print ('profile 5:', profileinfo)

        # dataset[6]
        profiles = datasets[6].find_all("div",{"class":"profileline"})
        for profile in profiles:        
            # try: 
            #     profilehead = profile.find("div",{"class":"profilehead"}).text
            #     aprofilehead = Get_Profilehead(profilehead)            
            #     outdatafileheaders.append(aprofilehead)
            # except:
            #     if headerflag == 0:
            #         outdatafileheaders.append(' ')
            #     pass
            try:
                profileinfo = profile.find("div",{"class":"profileinfo"}).text
                outdatafilerow.append(profileinfo)                    
            except:
                outdatafilerow.append(' ')
                pass
            print ('profile 6:', profileinfo)


        # print ('outdatafileheaders:', outdatafileheaders)
        # csv_data_writer.writerow(outdatafileheaders)
        csv_data_writer.writerow(outdatafilerow)

        flag = 1

    except:
        # for i in range(WAIT):
        #     print(f'[green][+][/green] Website is too busy. Waiting for {WAIT-i} seconds', end="\r")
        #     time.sleep(1)
        # MSA_Data(url, code)
        flag = 0
        pass

    return flag

def Get_MSA_Data_From_Code(code):
    
    idx = 1
    failidx = 0
    while 1:
        tradenamefile = open('./tradenamefolder/tradename_' + code + '.txt', 'r+')
        tradeurls = tradenamefile.readlines()
        print ('remain files:', code, len(tradeurls)-1)        

        if len(tradeurls) == 0:
            break

        flag = 0
        tradeurl = tradeurls[0].replace('\n', '')
        tradeurl = tradeurl.replace(' ', '')

        print (code, idx, tradeurl)

        flag = MSA_Data(tradeurl, code)
        
        if flag == 0:
            failidx += 1
            if failidx <= 30:
                failidx = 0
                flag = 1

        if flag == 1:
            tradenamefile.seek(0)
            # truncate the file
            tradenamefile.truncate()

            # start writing lines except the first line
            # lines[1:] from line 2 to last line
            tradenamefile.writelines(tradeurls[1:])

            idx += 1

        tradenamefile.close()    

def Check_TradeURL(code):

    print('Checking TradeURL...')

    tradenamefile = open('tradename_' + code + '.txt', 'r')
    tradeurls = tradenamefile.readlines()
    if len(tradeurls) == 0:
        return 1
    for tradeurl in tradeurls:        
        index = tradeurl.find('&')
        name = tradeurl.split('SAM_UEI=')[-1].strip()
        if name == '':
            print ('Check TradeURL Error:', code, tradeurl)
            return 1

    return 0

# def Get_URL_From_Code(url, code):

#     print ('MSA code:', code)
    
#     # try:
#     driver.get(url)
#     pageSource = driver.page_source
    
#     soup = BeautifulSoup(pageSource, 'html.parser')

#     if 'Request timed out waiting to execute' in soup.text:
#         print ('Website loading error:', soup.text)
#         Get_URL_From_Code(url, code)

#     print('website main page')
#     time.sleep(5)

#     flag = 0

#     try:
#         code = str(code)
#         codeinput = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID, 'EltMsa')))
#         codeinput.clear()
#         codeinput.send_keys(code)
#         time.sleep(5)

#         select = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "EltNumberOfRows"))))
#         select.select_by_visible_text("Show All")
#         print('select click')

#         searchbutton = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//input[@value='Search Using These Criteria']")))
#         print('search table loading...')
#         searchbutton.click()
#         time.sleep(5)

#         pageSource = driver.page_source
#         # print(pageSource)
#         soup = BeautifulSoup(pageSource, 'html.parser')
#         # print(soup)
#         print('website table page')
        
#         if 'Error. Insufficient search criteria were entered.' in soup.text:
#             print ('Website loading error:', soup.text)
#             return 1

#         # time.sleep(5)

#         tradenamefile = open('./tradenamefolder/tradename_' + code + '.txt', 'w', encoding="utf-8")
#         # tradenamefile = open('tradename.txt', 'w', encoding="utf-8")

#         table = soup.find("table",{"id":"ProfileTable"})
#         trs = table.find_all("tr")
#         for tr in trs:
#             try:
#                 tds = tr.find_all("td")
#                 tradename = tds[1].find('a').get('href')
#                 tradename = tradename.split('SAM_UEI=')[-1].strip()
#                 if tradename != '':
#                     tradeurl = 'https://web.sba.gov/pro-net/search/dsp_profile.cfm?RequestTimeout=60&SAM_UEI=' + tradename
#                     # print(code, tradeurl)
#                     tradenamefile.write(tradeurl)
#                     tradenamefile.write('\n')
#             except:
#                 pass

#         tradenamefile.close()
#         flag = 1
#     except:
#         flag = 0
#         pass

#     return flag

# def Get_MSA_URL(url):

#     while 1:
#         txtfile = open('MSA_code.txt', 'r+')
#         lines = txtfile.readlines()
#         if len(lines) == 0:
#             break

#         flag = 0
#         code = lines[0].replace('\n', '')
#         code = code.replace(' ', '')
#         flag = Get_URL_From_Code(url, code)
#         # Get_MSA_Data_From_Code(code)

#         if flag == 1:
#             txtfile.seek(0)
#             # truncate the file
#             txtfile.truncate()

#             # start writing lines except the first line
#             # lines[1:] from line 2 to last line
#             txtfile.writelines(lines[1:])

#         txtfile.close()

def Get_MSA_Data():

    url_files = glob.glob('tradenamefolder/*.txt')

    for file in url_files:
        code = file.split('tradename_')[-1].split('.')[0].strip()
        Get_MSA_Data_From_Code(code)

        os.remove(file)

if __name__ == '__main__':

    print ('Scraping start...')

    # if not os.path.exists('MSA_code.txt'):
    #     Get_MSA_Code(msacode_url)

    # if not os.path.exists('tradenamefolder'):
    #     os.mkdir('tradenamefolder')

    print ('Get MSA data from link...')
    # Get_MSA_URL(scrape_url)

    Get_MSA_Data()

    # driver.close()
    outdatafile.close()

    # os.remove('MSA_code.txt')

    print ('Successfully! Thank you!')
    
