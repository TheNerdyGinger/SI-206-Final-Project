from geopy import distance
import requests
import json
import os
import csv


def get_countries(filename):
    country_list = []
    full_path = os.path.join(os.path.dirname(__file__), filename)
    f = open(full_path, 'r')
    data = f.read()
    f.close()
    
    for n in data.split(','):
        m = n.replace('\cb3 ', '').replace('\cb1 ', '')
        country_list.append(''.join(m.split('\\')))
        
    for n in country_list:
        m = n.split('\n')
        


def get_mapquest(url):
    coord_list = []
    key = '5BPqkMyJdoFaGeY6MfwAbOk73xXK5Kq9'
    
    try:
        r = requests.get(url)
        dict = json.loads(r.text)         
    except:
        print("Error when reading from url")
        dict = {}

    for n in dict['results'][0]['locations']:
        latitude = n['latLng']['lat']
        longitude = n['latLng']['lng']
        coords = (latitude, longitude)
        coord_list.append(coords)

    return coord_list
    #return coords

def get_distance(coord_list):
    aa_cords = get_mapquest('https://www.mapquestapi.com/geocoding/v1/address?key=5BPqkMyJdoFaGeY6MfwAbOk73xXK5Kq9&inFormat=kvp&outFormat=json&location=Ann_Arbor&thumbMaps=false')
    print(aa_cords[0])
    print(coord_list[0])
    distance_from_aa = distance.distance(aa_cords[0], coord_list[0]).miles
    return distance_from_aa

    #for n in coord_list:
        #print(n)




if __name__ == '__main__':
    get_countries('countries.csv')
    coordinate_list = get_mapquest('https://www.mapquestapi.com/geocoding/v1/address?key=5BPqkMyJdoFaGeY6MfwAbOk73xXK5Kq9&inFormat=kvp&outFormat=json&location=France&thumbMaps=false') 
    get_distance(coordinate_list)

    ''' 
    get_countries - From a csv file of countries, returns list of those countries. Having trouble creating the list, removing extra data and spaces. 
                    Potential problem with countries with multiple words, not sure if mapquest api will accept format

    get_mapquest - Takes list of countries and returns coordines for those countries. Returns multiple coordinates, not sure which one to use.
                    Appending coordinates to list and using list[0] seems to work well

    get_distance - Takes in coorindate list from get_mapquest and uses geopy to calculate distance from AA. Works as expected

    Do not create databases/visualizations until all functions work as expected

    '''