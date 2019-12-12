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

def get_shortest_distance(tup, cur, distances):
    cur.execute("SELECT country_id FROM Brand_countries_sold WHERE brand_id = ?", (tup[0],))
    countries_to_check = cur.fetchall()
    min_distance = distances[countries_to_check[0][0]]
    for c in countries_to_check:
        if distances[c[0]]< min_distance:
            min_distance = distances[c[0]]
    return min_distance

def insert_combined_score(start, brands_and_scores, cur, conn):
    for b in brands_and_scores:
        query = "INSERT INTO Combined_score (ingredient_id, brand_id, score) VALUES (?, ?, ?)"
        values = (start, b[0], b[1])
        cur.execute(query, values)
    conn.commit()

def insert_best_brand(start, brand, cur, conn):
    query = "INSERT INTO Best_brands(ingredient_id, brand_id) VALUES (?, ?)"
    values = (start, brand)
    cur.execute(query, values)
    conn.commit()

def combine(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Combined_score (ingredient_id, brand_id INTEGER, score REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS Best_brands (ingredient_id INTEGER, brand_id INTEGER)")
    # cur.execute("CREATE TABLE IF NOT EXISTS Recipes_and_best_brands (ingredient_id INTEGER, brand_id INTEGER)")

    #determine start point
    cur.execute("SELECT * FROM Combined_score WHERE ingredient_id = (SELECT MAX(ingredient_id) FROM Combined_score)")
    start = cur.fetchone()
    if start:
        start= start[0]+1
    else:
        start = 0

    #check if we've reached end of list
    cur.execute("SELECT ingredient_id FROM Ingredients WHERE ingredient_id = (SELECT MAX(ingredient_id) FROM Ingredients)")
    check= cur.fetchone()
    if(start >check[0]):
        print("No more ingredients to check")
        return

    cur.execute("SELECT brand_id, nut_score FROM Brands_and_scores WHERE ingredient_id = ?", (start,))
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
    while index < len(brands_and_scores) and brands_and_scores[index][1] == max_score:
        min_distance = get_shortest_distance(brands_and_scores[index], cur, distances)
        brands_and_scores[index] =  (brands_and_scores[index][0],  brands_and_scores[index][1], min_distance)
        index+=1
    subtractor = 1 / index #what to subtract from each score based on it's distance

    brands_and_scores[0:index] = sorted(brands_and_scores[0:index], key = itemgetter(2) )
    count = 0
    for b in brands_and_scores[0:index]:
        brands_and_scores[count] = (b[0], round(b[1]- (count * subtractor), 2), b[2])
        count +=1


    insert_combined_score(start, brands_and_scores, cur, conn)
    insert_best_brand(start, brands_and_scores[0][0], cur, conn)

def main():
    #only have in one file
    db_name = "foodquest.db"
    cur, conn = setUpDatabase(db_name)
    
    combine(cur, conn)

if __name__ == "__main__":
    main()
    #unittest.main(verbosity = 2)