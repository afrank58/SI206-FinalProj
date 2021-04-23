import requests
import json
import tweepy 
import sqlite3	
import csv		
import os
#from bball import get_data 


#By Ava Frank, Alex Lepore, Hannah Triester


consumer_key= '76KntzpWtWkqrIhMF8BahWTRu'
consumer_secret= 'SkLOr5wQJYU8hqIIuKlTF0yk8LUYxrXHYOI7nZnhrHSJldyemq'
access_token= '1172625851008999424-O2vpJqLNTyLb8PCJZQUaqlnaRtBOcZ'
access_token_secret='MfO4h0941bI5XBd4L7uWa1qZG7GskDufR4Xa9WDP1kigG'


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser(), wait_on_rate_limit=True)


#url = 'https://api.twitter.com/2/tweets'

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def get_data_lst(cur, conn):
    cur.execute('SELECT name FROM Players') 
    
    #this will be swithced to player_id and then select from player_id

    existing_player_names = cur.fetchall()
    lst_names = []
    for item in existing_player_names:
        lst_names.append(item[0])
    
    tup_lst = []
    for name in lst_names:
        data_for_athletes = api.search(q= name,count=100) #put into for loop and name called from cur.fetchall
        #print(data_for_athletes)
#table with player and tweet id and number people that follow person, create id for players 

        for i in data_for_athletes['statuses']:
            follower_count = i['user']['followers_count']
            user_id = i['user']['id']

            tup_lst.append((name, user_id, follower_count)) #has length of 1070
    return tup_lst
    #print(len(tup_lst))
    
    
def set_up_athlete_table(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Player_ID (player_id INTEGER, name TEXT)')
    cur.execute('SELECT name FROM Players')
    players_name_tup = cur.fetchall()
    players_name_lst = []
    lst_tup = []
    x = 0
    for name in players_name_tup:
        players_name_lst.append(name[0])
    #need to create a list of tuples with (name, value)
    for player in players_name_lst:
        lst_tup.append((player, x))
        x += 1
    #print(lst_tup)
    for tup in lst_tup:
        cur.execute("INSERT INTO Player_ID (player_id, name) VALUES (?,?)", (tup[1], tup[0]))
    conn.commit()


def get_data(tup_lst, cur, conn):
    """This function takes in a players name from the database as a parameter and returns a dictionary with the amount of followers each Tweeter 
    that mentions that athletes name has"""

    cur.execute('CREATE TABLE IF NOT EXISTS Michigan_Twitter_Data (player_id INTEGER, user_id INTEGER, follower_count INTEGER)')
    #cur.execute('SELECT name FROM Players') 

    for tup in tup_lst:
        cur.execute('SELECT player_id FROM Player_ID WHERE name =?', (tup[0],))
        player_id = cur.fetchone()[0]

        cur.execute("INSERT INTO Michigan_Twitter_Data (player_id, user_id, follower_count) VALUES (?,?,?)", (player_id, tup[1], tup[2]))

        conn.commit()

def calc_avg_followers(cur, conn):
    cur.execute("SELECT player_id, follower_count FROM Michigan_Twitter_Data")
    players = cur.fetchall()
    lst_followers = []
    for idx in range(len(players) + 1):
        if players[idx][0] == players[idx+1][0]:
            lst_followers.append(players[idx][1])
    print(lst_followers)
            



   
    
def main():
    cur, conn = setUpDatabase('players.db')
    set_up_athlete_table(cur, conn)
    get_data(get_data_lst(cur, conn), cur, conn)
    get_data_lst(cur, conn)
    calc_avg_followers(cur, conn)
    
    
    
   
    
    

if __name__ == '__main__':
    main()

