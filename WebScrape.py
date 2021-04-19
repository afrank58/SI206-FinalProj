import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import sqlite3
import json

def get_player_towns_states(url_lst):

    tup_lst = []
    for url in url_lst:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        player_data = soup.find_all('div', class_ = 'sidearm-roster-player-details flex flex-align-center large-6 x-small-12 full columns')
    
        #translate_dict{'N.Y.': 'New York', 'Va.': 'Virgina', 'Mich.': 'Michigan', 'Ohio': 'Ohio', 'Md.': 'Maryland', 'Ill.': 'Illinois', 'Fla': 'Florida', 'Germany': 'Germany', 'Colo.': 'Colorado', 'Pa': 'Pennslyvania', 'La': 'Louisiana', 'Calif': 'California' , 'Ga': 'Georgia', 
        
        for player in player_data:
            player_name = player.find('h3').text.strip()
            hometown = player.find('span', class_ = 'sidearm-roster-player-hometown').text.strip().split(',')[0]
            homestate = player.find('span', class_ = 'sidearm-roster-player-hometown').text.strip().split(',')[1].replace(' ', '')
            tup_lst.append((player_name, hometown, homestate))
    

    return tup_lst 



def get_per_in_state(tup_lst):
    states = []
    for tup in tup_lst:
        states.append(tup[2])
    num_in_state = states.count('Mich.')
    per_in_state = num_in_state / len(tup_lst)
    return per_in_state



def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


def setUpSportsTable(cur, conn):
    sports = [('Basketball' , 1), ('Football', 2), ('Hockey', 3)]
    cur.execute('CREATE TABLE IF NOT EXISTS Sports (sport_id INTEGER, sport_name TEXT)')
    for sport in sports:
        cur.execute('INSERT INTO Sports (sport_id, sport_name) VALUES (?, ?)', (sport[1], sport[0]))
    
    conn.commit()



def setUpPlayersTable(tup_lst, cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Players (name TEXT, hometown TEXT, homestate TEXT)')
    for tup in tup_lst:
        cur.execute('INSERT INTO Players (name, hometown, homestate) VALUES (?, ?, ?)', (tup[0], tup[1], tup[2]))
    
    conn.commit()


def write_data_to_file(filename, cur, conn):
    path = os.path.dirname(os.path.abspath(__file__)) + os.sep
    outFile = open(path + filename, "w")

    percentage = get_per_in_state(get_player_towns_states(['https://mgoblue.com/sports/mens-basketball/roster', 'https://mgoblue.com/sports/football/roster', 'https://mgoblue.com/sports/mens-ice-hockey/roster']))

    outFile.write("Percentage of athletes that are from Michigan on the Men's Basketball, Football, and Hockey Teams. \n")
    outFile.write(str(percentage) + " of Michigan Men's Backetball, Football, and Hockey players are from the state of Michigan. \n")
    outFile.close()


def main():
    print(get_player_towns_states(['https://mgoblue.com/sports/mens-basketball/roster', 'https://mgoblue.com/sports/football/roster', 'https://mgoblue.com/sports/mens-ice-hockey/roster']))
    print(len(get_player_towns_states(['https://mgoblue.com/sports/mens-basketball/roster', 'https://mgoblue.com/sports/football/roster', 'https://mgoblue.com/sports/mens-ice-hockey/roster'])))
    print(get_per_in_state(get_player_towns_states(['https://mgoblue.com/sports/mens-basketball/roster', 'https://mgoblue.com/sports/football/roster', 'https://mgoblue.com/sports/mens-ice-hockey/roster'])))
    cur, conn = setUpDatabase('players.db')
    setUpPlayersTable(get_player_towns_states(['https://mgoblue.com/sports/mens-basketball/roster', 'https://mgoblue.com/sports/football/roster', 'https://mgoblue.com/sports/mens-ice-hockey/roster']), cur, conn)
    setUpSportsTable(cur, conn)
    write_data_to_file("Players.txt", cur, conn)

    
    conn.close()

    #making pie# Data to plot
    labels = ['In State Players', 'Out of State Players']
    sizes = [32.28, 67.72]
    colors = ['blue', 'yellow']
    #explode = (0.1, 0, 0, 0)  # explode 1st slice
    
    # Plot
    plt.pie(sizes, labels=labels, colors=colors,
            autopct='%1.1f%%', startangle=140)
    
    plt.axis('equal')
    plt.show()  



if __name__ == "__main__":
    main()