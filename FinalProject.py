import requests
import json
import tweepy 
import sqlite3	
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
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
    """Takes the name of a database, a string, as input. Returns the cursor connection to 
    the database."""

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def get_data_lst(cur, conn):
     """Takes in the database cursor and connection as an input. Gets a list of names from 
    the Player database. Returns a list of tuples of athlete name, Twitter user ID, 
    and the user's follower count."""

    cur.execute('SELECT name FROM Players') 
    
    #this will be swithced to player_id and then select from player_id

    existing_player_names = cur.fetchall() #list of tuples
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
    """Takes in the database cursor and connection as inputs. Returns nothing. Creates the
    Player_ID table and fills it with the player names and their player_ids. The player_id
    are unique identification numbers for each player."""

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
     """This function takes in a the list of tuples returned in get_data_lst, the database 
    cursor, and the database connection as inputs. Returns nothing. Creates the 
    Michigan_Twitter_Data table and fills it with the player_id, user_id of a Twitter user 
    that Tweets about that athlete, and that user's follower count."""

    cur.execute('CREATE TABLE IF NOT EXISTS Michigan_Twitter_Data (player_id INTEGER, user_id INTEGER, follower_count INTEGER)')
    #cur.execute('SELECT name FROM Players') 

    for tup in tup_lst:
        cur.execute('SELECT player_id FROM Player_ID WHERE name =?', (tup[0],))
        player_id = cur.fetchone()[0]

        cur.execute("INSERT INTO Michigan_Twitter_Data (player_id, user_id, follower_count) VALUES (?,?,?)", (player_id, tup[1], tup[2]))

        conn.commit()

def calc_avg_followers(cur, conn):
    """Takes in the database cursor and connection as inputs. Returns a dictionary of 
    player_ids as the key and the average follower count for a user that Tweets about them."""

    cur.execute("SELECT player_id, follower_count FROM Michigan_Twitter_Data")
    players = cur.fetchall()
    
    #lst_followers = []

    follower_dict = {}
    for tup in players:

        player_id = tup[0]
        follower_count = tup[1]

        if player_id not in follower_dict:
            follower_dict[player_id] = []
        follower_dict[player_id].append(follower_count)
    
    avg_dict = {}
    for key in follower_dict:
        total = sum(follower_dict[key])
        avg = total/(len(follower_dict[key]))
        avg_dict[key] = avg
    print(avg_dict)
    return avg_dict


   
            
def write_data_to_file(filename, cur, conn):
     """Takes in a filename (string), the database cursor, and the database connection
    as inputs. Returns nothing. Creates a file and writes the return values of the 
    calc_avg_followers function to the file."""

    path = os.path.dirname(os.path.abspath(__file__)) + os.sep
    outFile = open(path + filename, "w")

    #need for loop here bc otherwise won't be able to get every player_id

    avg_followers = calc_avg_followers(cur, conn)

    for item in avg_followers:
        outFile.write(f" The average amount of followers of a Twitter user that Tweets about the Michigan athlete with a player id = {str(item)} is {str(avg_followers[item])}. \n")
    
    outFile.close()


   
    
def main():
    """Takes nothing as input and returns nothing. Calls the functions setUpDatabase(),
    set_up_athlete_table(), get_data(), get_data_lst(), calc_avg_followers(), 
    write_data_to_file() and includes the code for the scatterplot visualization graph."""
    
    cur, conn = setUpDatabase('players.db')
    set_up_athlete_table(cur, conn)
    get_data(get_data_lst(cur, conn), cur, conn)
    get_data_lst(cur, conn)
    calc_dictionary = calc_avg_followers(cur, conn)
    write_data_to_file("AverageFollowers.txt", cur, conn)

    keys = []
    players = []
    for item in calc_dictionary:
        keys.append(item)
        players.append(calc_dictionary[item])

    #make scatterplot 

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x = keys,
        y = players,
        marker = dict(color="rgb(55, 83, 109)", size=12),
        mode = 'markers',
        name = 'Average Followers',
     ))

    fig2.update_layout(title = "Average Amount of Followers of a Twitter User that Tweets About Michigan Men's Football, Hockey, and Basketball Players",
    xaxis_title = "Michigan Player ID", yaxis_title = "Average Twitter Followers of User Tweeting")

    fig2.show()

    
    
    

if __name__ == '__main__':
    main()

