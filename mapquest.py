from geopy import distance
import requests
import json
import os
import csv
import sqlite3

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


def get_countries(filename):
    country_list = []
    country_list_clean = []
    country_list_final = []
    full_path = os.path.join(os.path.dirname(__file__), filename)
    f = open(full_path, 'r')
    data = f.read()
    f.close()
    
    for n in data.split(','):
        m = n.replace('\cb3 ', '').replace('\cb1', '')
        m = m.replace('}', '')
        country_list.append(''.join(m.split('\\')))
        
    for n in country_list:
        country_list_clean.append(n.strip('\n'))

    for n in country_list_clean:
        split_string = n.split('\n')
        for m in split_string:
            country_list_final.append(m.rstrip())
    
    return country_list_final



def get_mapquest(country_list, cur, conn, start):
    #coord_list = []
    key = '5BPqkMyJdoFaGeY6MfwAbOk73xXK5Kq9'
    base_url = 'https://www.mapquestapi.com/geocoding/v1/address?key='

    
    for n in range(start, start + 20):
        if n >= 239:
            break
        url = base_url + key + '&inFormat=kvp&outFormat=json&location=' + country_list[n] + '&thumbMaps=false'
        cur.execute("INSERT INTO Countries (country_id,country) VALUES (?,?)",(n,country_list[n]))
        
        try:
            r = requests.get(url)
            dict = json.loads(r.text)      
        except:
            print("Error when reading from url")
            dict = {}

    
        latitude = dict["results"][0]['locations'][0]['displayLatLng']['lat']
        longitude = dict["results"][0]['locations'][0]['displayLatLng']['lng']
        
        cur.execute("INSERT INTO Lat_lng (country_id, latitude, longitude) VALUES (?,?,?)",(n,latitude,longitude))
        
        #coords = (latitude, longitude)
        #coord_list.append(coords)

    
    conn.commit()
    
        
   

def get_distance(cur, conn, start):
    url = 'https://www.mapquestapi.com/geocoding/v1/address?key=5BPqkMyJdoFaGeY6MfwAbOk73xXK5Kq9&inFormat=kvp&outFormat=json&location=AnnArbor&thumbMaps=false'
    # cur.execute("DROP TABLE IF EXISTS Distances")
    
    try:
        r = requests.get(url)
        dict = json.loads(r.text)      
    except:
        print("Error when reading from url")
        dict = {}
    
    aa_latitude = dict["results"][0]['locations'][0]['displayLatLng']['lat']
    aa_longitude = dict["results"][0]['locations'][0]['displayLatLng']['lng']
    aa_coords = (aa_latitude, aa_longitude)
    
    
    coord_list = []
    cur.execute("SELECT latitude, longitude FROM Lat_lng WHERE country_id BETWEEN ? AND ?", (start, start + 19))
    for row in cur:
        latitude = row[0]
        longitude = row[1]
        coord_list.append((latitude, longitude))
    print(len(coord_list))
    
    
    if start >= 239:
        print("No more countries to input")
        return
    for n in range(len(coord_list)):
        if start >= 239:
            print("No more countries to input")
            return
        distance_from_aa = distance.distance(aa_coords, coord_list[n]).kilometers
        cur.execute("INSERT INTO Distances (country_id,distance) VALUES (?,?)",(start,distance_from_aa))
        start += 1
    '''for n in range(len(coord_list)):
        distance_from_aa = distance.distance(aa_coords, coord_list[n]).kilometers
        cur.execute("INSERT INTO Distances (country_id,distance) VALUES (?,?)",(n,distance_from_aa))'''


    conn.commit()



def main():
    db_name = "foodquest.db"
    cur, conn = setUpDatabase(db_name)
    country_list = get_countries('countries.csv')
    cur.execute("CREATE TABLE IF NOT EXISTS Countries (country_id INTEGER, country TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS Lat_lng (country_id INTEGER, latitude REAL, longitude REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS Distances (country_id INTEGER, distance REAL)")

    cur.execute('SELECT * FROM Countries WHERE country_id= (SELECT MAX(country_id) FROM Countries)')
    start = cur.fetchone()
    if start:
        start = start[0] + 1
    else:
        start = 0

    get_mapquest(country_list, cur, conn, start) 
    get_distance(cur, conn, start)



if __name__ == "__main__":
    main()
    
    

    
