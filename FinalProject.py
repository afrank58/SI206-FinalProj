import requests
import os
import sqlite3
import json 

#By Ava Frank, Alex Lepore, Hannah Triester

def get_NCAA_data(season):
#"""This function"""
    
    api_key = '9ad7109d6cb248aab6b22acefe9f5c90'
    base_url = 'https://fly.sportsdata.io/v3/cbb/scores/json/TeamSeasonStats/{}'
    request_url = base_url.format(api_key, season)
    

    r = requests.get(request_url)
    data = r.content
    #list1 = json.loads(data)
    print(data)
    return data

def get_hockey_data():

    base_url = 'https://api.sportradar.us/ncaamh-{}{}/games/{}/{}/schedule.{}?api_key={}'
    request_url = base_url.format(access_level, version, season_year, ncaamh_season, format, api_key)

    #include a sleep for 5 mins 
#def setUpDatabase(db_name):
#"""Takes the name of a database, a string, as an input. 
#Returns the cursor and connection to the database."""


def main():
    season = get_NCAA_data('2018')
    

if __name__ == '__main__':
    main()
