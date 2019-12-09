import sqlite3
import json
import os
import inflect
import geopy.distance
import requests
from operator import itemgetter

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

#for testing, remove when we have mapquest data
def get_distances(cur, conn):
    url = "https://www.mapquestapi.com/geocoding/v1/address?key=eG2u4AiKGQtV2YBYLgLkKrQLy54uvW9s&inFormat=kvp&outFormat=json&location=Ann-Arbor&thumbMaps=false"
    r = requests.get(url)
    data = json.loads(r.text)
    lat = data["results"][0]['locations'][0]['displayLatLng']['lat']
    lng = data["results"][0]['locations'][0]['displayLatLng']['lng']
    coords_1 = (lat,lng)

    for i in range(0, 7):
        cur.execute("SELECT country FROM Countries WHERE country_id = ?", (i,))
        c = cur.fetchone()
        url = "https://www.mapquestapi.com/geocoding/v1/address?key=eG2u4AiKGQtV2YBYLgLkKrQLy54uvW9s&inFormat=kvp&outFormat=json&location={}&thumbMaps=false"
        request_url = url.format(c)
        r = requests.get(request_url)
        data = json.loads(r.text)
        lat = data["results"][0]['locations'][0]['displayLatLng']['lat']
        lng = data["results"][0]['locations'][0]['displayLatLng']['lng']

        coords_2 = (lat, lng)
        distance = geopy.distance.distance(coords_1, coords_2).km

        # cur.execute("SELECT * FROM Countries ORDER BY country_id DESC LIMIT 1")
        # bookmark = cur.fetchone()
        # if bookmark:
        #     bookmark = bookmark[0]+1
        # else:
        #     bookmark = 0

        query ="INSERT INTO Distances(country_id, distance) VALUES (?, ?)"
        values = (i, distance)
        cur.execute(query, values)
    conn.commit()

def get_shortest_distance(tup, cur, distances):
    cur.execute("SELECT country_id FROM Brand_countries_sold WHERE brand_id = ?", (tup[1],))
    countries_to_check = cur.fetchall()
    min_distance = distances[countries_to_check[0][0]]
    for c in countries_to_check:
        if distances[c[0]]< min_distance:
            min_distance = distances[c[0]]
    return min_distance


def combine(cur, conn):
    get_distances(cur, conn)
    # cur.execute("DROP TABLE IF EXISTS Combined_score")
    cur.execute("CREATE TABLE IF NOT EXISTS Combined_score (ing_id, brand_id INTEGER, score REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS Best_brands (ing_id INTEGER, brand_id INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS Recipes_and_best_brands (rec_id INTEGER, brand_id INTEGER)")

    #determine start point
    cur.execute("SELECT * FROM Combined_score WHERE ing_id = (SELECT MAX(ing_id) FROM Combined_score)")
    start = cur.fetchone()
    if start:
        start= start[0]+1
    else:
        start = 0


    cur.execute("SELECT brand_id, nut_score FROM Brands_and_scores WHERE ing_id = ?", (start,))
    brands_and_scores = cur.fetchall()

    #get countries sold
    countries = []
    for b in brands_and_scores:
        cur.execute("SELECT country_id FROM Brand_countries_sold WHERE brand_id = ?", (b[0],))
        counts = cur.fetchall()
        for c in counts:
            if not c[0] in countries:
                countries.append(c[0])

    #get distances for each country
    distances = dict()
    for c in countries:
        cur.execute("SELECT distance FROM Distances WHERE country_id = ? LIMIT 1", (c,))
        d = cur.fetchone()
        distances[c] = d[0]

    #sort by highest score
    brands_and_scores = sorted(brands_and_scores, key = lambda x: -x[1])
    
    max_score = brands_and_scores[0][1]

    #determine best countries for each brand with the max score
    index = 0
    while brands_and_scores[index][1] == max_score:
        min_distance = get_shortest_distance(brands_and_scores[index], cur, distances)
        brands_and_scores[index] =  (brands_and_scores[index][0],  brands_and_scores[index][1], min_distance)
        index+=1
    # sorted(student_tuples, key=itemgetter(1,2))
    subtractor = 1 / index #what to subtract from each score based on it's distance
    # shortened_list = sorted(brands_and_scores[0:index], key = lambda x: x[2])
    brands_and_scores[0:index] = sorted(brands_and_scores[0:index], key = itemgetter(2) )
    count = 0
    for b in brands_and_scores[0:index]:
        brands_and_scores[count] = (b[0], round(b[1]- (count * subtractor), 2), b[2])
        count +=1


def main():
    #only have in one file
    db_name = "foodquest.db"
    cur, conn = setUpDatabase(db_name)
    combine(cur, conn)


if __name__ == "__main__":
    main()
    #unittest.main(verbosity = 2)