import requests
import os
import sqlite3
import json
import http.client
import numpy as np 
import matplotlib.pyplot as plt

def get_hockey_data():
    '''No inputs. Returns a list of tuples in the format (sport, first name, last name, year). 
    Uses the sportradar.us API to retrieve values for each player on Michigan Wolverines Hockey.''' 

    base_url = 'https://api.sportradar.us/ncaamh-{}{}/teams/{}/profile.{}?api_key={}'
    request_url = base_url.format('t', '3', 'cf14c7f3-b5bf-44d6-8742-6ed15568de88', 'json', 't2465xfkx7ueuvgw2qjrmzvm')
    hockey_response = requests.get(request_url)
    
    
    hockey_dict = json.loads(hockey_response.text) #type: dict
    hockey_players = hockey_dict['players']
    #print(hockey_players)
    tup_lst = []
    for d in hockey_players:
        tup_lst.append(('Hockey', d['first_name'], d['last_name'], d['experience']))
    #print(tup_lst)
    return tup_lst

def get_basketball_data():
    '''No inputs. Returns a list of tuples in the format (sport, first name, last name, year). 
    Uses the sportradar.us API to retrieve values for each player on Michigan Wolverines Basketball.'''

    base_url = 'https://api.sportradar.us/ncaamb/{}/{}/{}/teams/{}/profile.{}?api_key={}'
    request_url = base_url.format('trial', 'v7', 'en', 'bdc2561d-f603-4fab-a262-f1d2af462277','json', 'kpgxkbp9xe2x2ap468z6j7hs')
    basketball_response = requests.get(request_url)

    basketball_dict = json.loads(basketball_response.text) #type: dict
    basketball_players = basketball_dict['players']
    #print(hockey_players)
    tup_lst = []
    for d in basketball_players:
        tup_lst.append(('Basketball', d['first_name'], d['last_name'], d['experience']))
    #print(tup_lst)
    return tup_lst


def get_football_data():
    '''No inputs. Returns a list of tuples in the format (sport, first name, last name, year). 
    Uses the sportradar.us API to retrieve values for each player on Michigan Wolverines Football.'''

    base_url = 'https://api.sportradar.us/ncaafb-{}{}/teams/{}/roster.{}?api_key={}'
    request_url = base_url.format('t', '1', 'MICH', 'json', 'a7vnjfg5daky49k66fzh3xnj')
    football_response = requests.get(request_url)
    #print(football_response.text)
    football_dict = json.loads(football_response.text)
    football_players = football_dict['players']
    tup_lst = []
    for d in football_players:
        tup_lst.append(('Football', d['name_first'], d['name_last'], d['experience']))
    #print(tup_lst)
    return tup_lst


def accumulate_data(hockey_lst, bball_lst, football_lst):
    '''Inputs the list of tuples that are returned from get_hockey_data(), get_basketball_data(), 
    and get_football_data(). Aggregates the returned tuples from all three teams into a single list.'''

    final_lst = []
    for tup in hockey_lst:
        final_lst.append(tup)
    for tup in bball_lst:
        final_lst.append(tup)
    for tup in football_lst:
        final_lst.append(tup)
    return final_lst

def setUpDatabase(db_name):
    '''Takes the name of a database, a string, as an input. 
    Returns the cursor and connection to the database.'''

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpYearsTable(tup_lst, cur, conn):
    '''Takes the list of tuples returned from accumulate_data(), the database cursor, 
    and connection as inputs. Returns nothing. Creates the Wolverines_Years database, 
    which holds the information on each player.'''

    cur.execute('CREATE TABLE IF NOT EXISTS Wolverines_Years (sport TEXT, first_name TEXT, last_name TEXT, year TEXT)')
    for x in range(0,25):
        cur.execute('SELECT * FROM Wolverines_Years')
        lst = cur.fetchall()
        length = len(lst)
        if length == 169:
            break
        
        cur.execute('INSERT OR IGNORE INTO Wolverines_Years (sport, first_name, last_name, year) VALUES (?,?,?,?)', (tup_lst[length][0], tup_lst[length][1], tup_lst[length][2], tup_lst[length][3]))
    
    conn.commit()

def setUpSportsTable(tup_lst, cur, conn):
    '''Takes the list of tuples that matches a sport to an id number, the database cursor, and connection as inputs. 
    Returns nothing. Creates the Sports database, which matches the sport title to an id # (1, 2, 3).'''

    cur.execute('CREATE TABLE IF NOT EXISTS Sports (sport_title TEXT, sport_id INTEGER)')
    for tup in tup_lst:
        cur.execute('INSERT INTO Sports (sport_title, sport_id) VALUES (?,?)', (tup[0], tup[1]))
    
    conn.commit()

def setUpIDsYearsTable(cur, conn):
    '''Method name is a misnomer. Selects data for each sport and joins the “Wolverines_Years” table 
    with the “Sports” table on the sport title. Calculates the grade distribution for each team.'''

    cur.execute('SELECT Wolverines_Years.first_name, Wolverines_Years.last_name, Wolverines_Years.year FROM Wolverines_Years JOIN Sports ON Wolverines_Years.sport=Sports.sport_title WHERE Wolverines_Years.sport=?', ('Hockey',))
    hockey_selected = cur.fetchall()
    #print(hockey_selected)
    total_hockey = len(hockey_selected)
    hockey_fr = 0
    hockey_so = 0
    hockey_jr = 0
    hockey_sr = 0
    hockey_gr = 0
    for item in hockey_selected:
        if item[2] == 'FR':
            hockey_fr += 1
        if item[2] == 'SO':
            hockey_so += 1
        if item[2] == 'JR':
            hockey_jr += 1
        if item[2] == 'SR':
            hockey_sr += 1
        if item[2] == 'GR':
            hockey_gr += 1
    percent_fr = hockey_fr / total_hockey
    percent_so = hockey_so / total_hockey
    percent_jr = hockey_jr / total_hockey
    percent_sr = hockey_sr / total_hockey
    percent_gr = hockey_gr / total_hockey
    # print(percent_fr)
    # print(percent_so)
    # print(percent_jr)
    # print(percent_sr)
    # print(percent_gr)
    

    cur.execute('SELECT Wolverines_Years.first_name, Wolverines_Years.last_name, Wolverines_Years.year FROM Wolverines_Years JOIN Sports ON Wolverines_Years.sport=Sports.sport_title WHERE Wolverines_Years.sport=?', ('Basketball',))
    bball_selected = cur.fetchall()
    #print(bball_selected)
    total_bball = len(bball_selected)
    bball_fr = 0
    bball_so = 0
    bball_jr = 0
    bball_sr = 0
    bball_gr = 0
    for item in bball_selected:
        if item[2] == 'FR':
            bball_fr += 1
        if item[2] == 'SO':
            bball_so += 1
        if item[2] == 'JR':
            bball_jr += 1
        if item[2] == 'SR':
            bball_sr += 1
        if item[2] == 'GR':
            bball_gr += 1
    percent_bball_fr = bball_fr / total_bball
    percent_bball_so = bball_so / total_bball
    percent_bball_jr = bball_jr / total_bball
    percent_bball_sr = bball_sr / total_bball
    percent_bball_gr = bball_gr / total_bball
    # print(percent_bball_fr)
    # print(percent_bball_so)
    # print(percent_bball_jr)
    # print(percent_bball_sr)
    # print(percent_bball_gr)
    

    cur.execute('SELECT Wolverines_Years.first_name, Wolverines_Years.last_name, Wolverines_Years.year FROM Wolverines_Years JOIN Sports ON Wolverines_Years.sport=Sports.sport_title WHERE Wolverines_Years.sport=?', ('Football',))
    football_selected = cur.fetchall()
    #print(bball_selected)
    total_football = len(football_selected)
    football_fr = 0
    football_so = 0
    football_jr = 0
    football_sr = 0
    football_gr = 0
    for item in football_selected:
        if item[2] == 'FR':
            football_fr += 1
        if item[2] == 'SO':
            football_so += 1
        if item[2] == 'JR':
            football_jr += 1
        if item[2] == 'SR':
            football_sr += 1
        if item[2] == 'GR':
            football_gr += 1
    percent_football_fr = football_fr / total_football
    percent_football_so = football_so / total_football
    percent_football_jr = football_jr / total_football
    percent_football_sr = football_sr / total_football
    percent_football_gr = football_gr / total_football
    # print(percent_football_fr)
    # print(percent_football_so)
    # print(percent_football_jr)
    # print(percent_football_sr)
    # print(percent_football_gr)

    return ("The percent of freshmen on the hockey team is " + str(percent_fr) + ".\n"+
    "The percent of sophomores on the hockey team is " + str(percent_so) + ".\n"+
    "The percent of juniors on the hockey team is " + str(percent_jr) + ".\n"+
    "The percent of seniors on the hockey team is " + str(percent_sr) + ".\n"+
    "The percent of graduates on the hockey team is " + str(percent_gr) + ".\n" + 
    "The percent of freshmen on the basketball team is " + str(percent_bball_fr) + ".\n"+
    "The percent of sophomores on the basketball team is " + str(percent_bball_so) + ".\n"+
    "The percent of juniors on the basketball team is " + str(percent_bball_jr) + ".\n"+
    "The percent of seniors on the basketball team is " + str(percent_bball_sr) + ".\n"+
    "The percent of graduates on the basketball team is " + str(percent_bball_gr) + ".\n" + 
    "The percent of freshmen on the football team is " + str(percent_football_fr) + ".\n"+
    "The percent of sophomores on the football team is " + str(percent_football_so) + ".\n"+
    "The percent of juniors on the football team is " + str(percent_football_jr) + ".\n"+
    "The percent of seniors on the football team is " + str(percent_football_sr) + ".\n"+
    "The percent of graduates on the football team is " + str(percent_football_gr) + ".\n")


def write_data_to_file(filename, cur, conn):
    '''Takes in a filename (string), the database cursor, and connection as inputs. 
    Creates a file and writes the calculations from setUpIDsYearsTable() into a file.'''


    path = os.path.dirname(os.path.abspath(__file__)) + os.sep
    outFile = open(path + filename, "w")
    outFile.write(setUpIDsYearsTable(cur, conn))
    outFile.close()


def main():
    '''Takes nothing as an input and returns nothing. Calls the functions setUpDatabase(), setUpYearsTable(),
    setUpSportsTable(), setUpIdsYearsTable(), write_data_to_file() 
    and includes the code for the bar graph visualization.'''

    
    cur, conn = setUpDatabase('Wolverines_Years.db')
    
    setUpYearsTable(accumulate_data(get_hockey_data(), get_basketball_data(), get_football_data()), cur, conn)

    tup_lst = [('Hockey', 1), ('Basketball', 2), ('Football', 3)]
    setUpSportsTable(tup_lst, cur, conn)

    cur.execute('SELECT * FROM Wolverines_Years')
    lst = cur.fetchall()
    length = len(lst)
    if length == 169:
        setUpIDsYearsTable(cur, conn) #the joined table and calculations

        write_data_to_file('Years.txt', cur, conn)

    #visualization
    # set width of bars
    barWidth = 0.25
 
    # set heights of bars
    bars1 = [38.46, 19.23, 30.77, 11.54, 0.0]
    bars2 = [23.53, 5.88, 17.65, 41.18, 11.76]
    bars3 = [25.4, 29.37, 20.63, 16.6, 7.94]
 
# Set position of bar on X axis
    r1 = np.arange(len(bars1))
    r2 = [x + barWidth for x in r1]
    r3 = [x + barWidth for x in r2]
 
# Make the plot
    plt.bar(r1, bars1, color='red', width=barWidth, edgecolor='white', label='Hockey')
    plt.bar(r2, bars2, color='blue', width=barWidth, edgecolor='white', label='Basketball')
    plt.bar(r3, bars3, color='green', width=barWidth, edgecolor='white', label='Football')
 
# Add xticks on the middle of the group bars
    plt.xlabel('Grade', fontweight='bold')
    plt.ylabel('Percent (%) of Team', fontweight='bold')
    plt.title('Class Distribution of Michigan Sports Team', fontweight='bold')
    plt.xticks([r + barWidth for r in range(len(bars1))], ['FR', 'SO', 'JR', 'SR', 'GR'])
 
# Create legend & Show graphic
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()       