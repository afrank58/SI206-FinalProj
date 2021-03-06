import matplotlib
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import sqlite3
import json



def get_player_towns_states(tup_lst):

    final_tup_lst = []
    for tup in tup_lst:
        r = requests.get(tup[1])
        soup = BeautifulSoup(r.text, 'html.parser')

        player_data = soup.find_all('div', class_ = 'sidearm-roster-player-details flex flex-align-center large-6 x-small-12 full columns')
            
        for player in player_data:
            player_sport = tup[0]
            player_name = player.find('h3').text.strip()
            hometown = player.find('span', class_ = 'sidearm-roster-player-hometown').text.strip().split(',')[0]
            homestate = player.find('span', class_ = 'sidearm-roster-player-hometown').text.strip().split(',')[1].replace(' ', '')
            final_tup_lst.append((player_sport, player_name, hometown, homestate))
    

    return final_tup_lst 



def get_players_in_state(tup_list):
    in_state_players = []
    for tup in tup_list:
        if tup[3] == "Mich.":
            in_state_players.append(tup)
    return in_state_players 



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
    cur.execute('CREATE TABLE IF NOT EXISTS Players (sport_id TEXT, name TEXT, hometown TEXT, homestate TEXT)')
    for x in range (0, 25):
        cur.execute('SELECT * FROM Players')
        lst = cur.fetchall()
        length = len(lst)
        if length == 158:
            break
        cur.execute('SELECT sport_id FROM Sports WHERE sport_name =?', (tup_lst[length][0],))
        sport_id = cur.fetchone()[0]
        cur.execute('INSERT INTO Players (sport_id, name, hometown, homestate) VALUES (?, ?, ?, ?)', (sport_id, tup_lst[length][1], tup_lst[length][2], tup_lst[length][3]))
    
    conn.commit()



def get_per_in_state(cur, conn):
    states_list = []
    cur.execute('SELECT homestate FROM Players')
    states = cur.fetchall()
    for state in states:
        states_list.append(state)
    count = 0 
    for tup in states:
        if tup[0] == "Mich.":
            count += 1
    per_in_state = count / len(states_list)

    return per_in_state



def counting_in_state_players(in_state_tup_list):
    d = {}
    basketball = [] 
    football = []
    hockey = [] 
    for tup in in_state_tup_list:
        if 'Basketball' in tup:
            basketball.append(tup)
        if 'Football' in tup:
            football.append(tup)
        if 'Hockey' in tup:
            hockey.append(tup)
    d['Basketball'] = len(basketball)
    d['Football'] = len(football)
    d['Hockey'] = len(hockey)
    print(d)
    return d 



def write_data_to_file(filename, cur, conn):
    path = os.path.dirname(os.path.abspath(__file__)) + os.sep
    outFile = open(path + filename, "w")
    percentage = get_per_in_state(cur, conn)
    outFile.write("Percentage of athletes that are from Michigan on the Men's Basketball, Football, and Hockey Teams: \n")
    outFile.write(str(percentage) + " of Michigan Men's Basketball, Football, and Hockey players are from the state of Michigan. \n")
    outFile.write('\n')
    outFile.write('Number of in state players on each of the three teams: \n')
    list_tups = [('Basketball', 'https://mgoblue.com/sports/mens-basketball/roster'), ('Football', 'https://mgoblue.com/sports/football/roster'), ('Hockey', 'https://mgoblue.com/sports/mens-ice-hockey/roster')]
    d =  counting_in_state_players(get_players_in_state(get_player_towns_states(list_tups)))
    for team in d:
        outFile.write(f"There are {str(d[team])} in state players on the {team} team.\n")
    outFile.close()



def main():
    list_tups = [('Basketball', 'https://mgoblue.com/sports/mens-basketball/roster'), ('Football', 'https://mgoblue.com/sports/football/roster'), ('Hockey', 'https://mgoblue.com/sports/mens-ice-hockey/roster')]
   
    counting_in_state_players(get_players_in_state(get_player_towns_states(list_tups)))

    cur, conn = setUpDatabase('players.db')
    setUpSportsTable(cur, conn)

    setUpPlayersTable(get_player_towns_states(list_tups), cur, conn)



    cur.execute('SELECT * FROM Players')
    lst = cur.fetchall()
    length = len(lst)
    if length == 158:
        print(get_per_in_state(cur, conn))
        write_data_to_file("Players.txt", cur, conn)
    
    conn.close()

    #making pie chart 
    labels = ['In State Players', 'Out of State Players']
    sizes = [32.28, 67.72]
    colors = ['lightblue', 'yellow']
    explode = (0.1, 0)  # explode 1st slice
    plt.pie(sizes, explode = explode, labels=labels, colors=colors,
    autopct='%1.1f%%', startangle=140)
    plt.title("Percentage of UMich Men's Basketball, Football, and Hockey Players \n" + "that are from in state versus out of state")
    plt.axis('equal')
    plt.show()  


    #bar graph for in state players 
    names = ['Basketball', 'Football', 'Hockey']
    values = [7, 35, 9]
    plt.bar(names,values)
    plt.ylabel("Number of Players")
    plt.title("Number of In State Players on the \n" + "Michigan Men's Basketball, Football, and Hockey Teams")
    plt.show()




if __name__ == "__main__":
    main()