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
    #alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '\n', ]
    country_list = []
    country_list_clean = []
    country_list_final = []
    full_path = os.path.join(os.path.dirname(__file__), filename)
    f = open(full_path, 'r')
    data = f.read()
    f.close()
    
    for n in data.split(','):
        m = n.replace('\cb3 ', '').replace('\cb1', '')
        country_list.append(''.join(m.split('\\')))
        
    for n in country_list:
        country_list_clean.append(n.strip('\n'))

    for n in country_list_clean:
        split_string = n.split('\n')
        for m in split_string:
            country_list_final.append(m.rstrip())
    
    return country_list_final



def get_mapquest(country_list, cur, conn):
    coord_list = []
    key = '5BPqkMyJdoFaGeY6MfwAbOk73xXK5Kq9'
    base_url = 'https://www.mapquestapi.com/geocoding/v1/address?key='

    cur.execute("DROP TABLE IF EXISTS Countries")
    cur.execute("DROP TABLE IF EXISTS Lat_lng")
    cur.execute("CREATE TABLE Countries (country_id INTEGER, country TEXT)")
    cur.execute("CREATE TABLE Lat_lng (country_id INTEGER, latitude REAL, longitude REAL)")
    
    for n in range(0, 20):
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
        
        cur.execute("INSERT INTO Lat_lng (country_id,latitude, longitude) VALUES (?,?,?)",(n,latitude, longitude))
        
        coords = (latitude, longitude)
        coord_list.append(coords)

    
    conn.commit()
    return coord_list

        
   

def get_distance(coord_list, cur, conn):
    url = 'https://www.mapquestapi.com/geocoding/v1/address?key=5BPqkMyJdoFaGeY6MfwAbOk73xXK5Kq9&inFormat=kvp&outFormat=json&location=AnnArbor&thumbMaps=false'
    cur.execute("DROP TABLE IF EXISTS Distances")
    cur.execute("CREATE TABLE Distances (country_id INTEGER, distance REAL)")
    
    
    try:
        r = requests.get(url)
        dict = json.loads(r.text)      
    except:
        print("Error when reading from url")
        dict = {}

    latitude = dict["results"][0]['locations'][0]['displayLatLng']['lat']
    longitude = dict["results"][0]['locations'][0]['displayLatLng']['lng']
    aa_coords = (latitude, longitude)
    
    #print(aa_coords)
    
    for n in range(len(coord_list)):
        distance_from_aa = distance.distance(aa_coords, coord_list[n]).kilometers
        cur.execute("INSERT INTO Distances (country_id,distance) VALUES (?,?)",(n,distance_from_aa))
        #print(distance_from_aa)

    conn.commit()
    return distance_from_aa


def main():
    db_name = "foodquest.db"
    cur, conn = setUpDatabase(db_name)
    country_list = get_countries('countries.csv')
    coordinate_list = get_mapquest(country_list, cur, conn) 
    get_distance(coordinate_list, cur, conn)



if __name__ == "__main__":
    main()
    
    
    
    ''' 
    get_countries - From a csv file of countries, returns list of those countries. Having trouble creating the list, removing extra data and spaces. 
                    Potential problem with countries with multiple words, not sure if mapquest api will accept format

    get_mapquest - Takes list of countries and returns coordines for those countries. Returns multiple coordinates, not sure which one to use.
                    Appending coordinates to list and using list[0] seems to work well

    get_distance - Takes in coorindate list from get_mapquest and uses geopy to calculate distance from AA. Works as expected

    Do not create databases/visualizations until all functions work as expected

    '''
