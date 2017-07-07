from urllib.request import urlopen
from bs4 import BeautifulSoup
import gzip
from ftplib import FTP


TCM_URL = "http://www.tcm.com/schedule/?ecid=mainnav2schedule"
html = urlopen(TCM_URL)
bsObj = BeautifulSoup(html, 'html.parser')
all_titledata = bsObj.findAll("div", {"class":"titleData"})
selected_movies = {}
for title_data in all_titledata:
    title_string = title_data.find("strong").text
    if title_string[-5:] == ', The':
        title_string = 'The ' + title_string[:-5]
    if title_string[-3:] == ', A':
        title_string = 'A ' + title_string[:-3]
    time_data = title_data.parent
    time_data = time_data.find_previous_sibling('div', {'class':'timeColumn'}).find('div', {'class':'timeData'})
    time_string = time_data.text.strip()
    selected_movies[title_string] = time_string

    

movie_ratings = {}

## Downloads .gz file to current directory
with open('ratings.gz', 'wb') as f:
    ftp = FTP('ftp.fu-berlin.de')
    ftp.login()
    ftp.cwd('/pub/misc/movies/database')
    ftp.retrbinary('RETR ratings.list.gz', lambda data: f.write(data))
    
with gzip.open('ratings.gz', 'rt', encoding = 'latin-1') as f:

    header1 = True
    header2 = True
    
    for line in f:
        if line.strip() == 'MOVIE RATINGS REPORT':
            header1 = False
            continue
        if header1 == False and line.strip() == 'New  Distribution  Votes  Rank  Title':
            header2 = False
            continue
        if header2 == False and (line.strip() == '' or line.split()[3][0] != '\"'):
            if line == "\n": break
            average_rating = float(line.split()[2])
            s = line.split()[3:]  #This is written in two lines because the movie's title may have spaces
            movie_name = " ".join(s[:-1])
            movie_ratings[movie_name.lower()] = average_rating
for movie, time in selected_movies.items():
    try:
        print(movie)
        print('Time: ' + time)
        print('Rating: ' + str(movie_ratings[movie.lower()]))
    except KeyError as err:
        print('Movie not found: ' + str(err))
    print()