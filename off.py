import sqlite3
import json
import os

#only have in one file
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_ing_table(cur, conn):
    cur.execute("DROP TABLE IF EXISTS Ingredients")
    cur.execute("CREATE TABLE Ingredients (ing_id INTEGER, ingredient TEXT)")

    query = "INSERT INTO Ingredients (ing_id, ingredient) VALUES (?, ?)"
    values = (0, "Flour")
    cur.execute(query, values)
    query = "INSERT INTO Ingredients (ing_id, ingredient) VALUES (?, ?)"
    values = (1, "Milk")
    cur.execute(query, values)
    query = "INSERT INTO Ingredients (ing_id, ingredient) VALUES (?, ?)"
    values = (2, "Butter")
    cur.execute(query, values)
    conn.commit()

def set_up_country_table(cur, conn):
    cur.execute("DROP TABLE IF EXISTS Countries")
    cur.execute("CREATE TABLE Countries (country_id INTEGER, country TEXT)")

    query = "INSERT INTO Countries (country_id, country) VALUES (?, ?)"
    values = (0, "France")
    cur.execute(query, values)
    query = "INSERT INTO Countries (country_id, country) VALUES (?, ?)"
    values = (1, "United States")
    cur.execute(query, values)
    query = "INSERT INTO Countries (country_id, country) VALUES (?, ?)"
    values = (2, "Spain")
    cur.execute(query, values)
    query = "INSERT INTO Countries (country_id, country) VALUES (?, ?)"
    values = (3, "Germany")
    cur.execute(query, values)
    query = "INSERT INTO Countries (country_id, country) VALUES (?, ?)"
    values = (4, "United Kingdom")
    cur.execute(query, values)
 
    conn.commit()

def get_brand_data(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Brands (brand_id, brand)")
    cur.execute("CREATE TABLE IF NOT EXISTS Brand_scores_and_countries (brand_id, nut_score, country_id)")
def main():

    #only have in one file
    db_name = "foodquest.db"
    cur, conn = setUpDatabase(db_name)
    # set_up_ing_table(cur,conn)
    # set_up_country_table(cur, conn)
    get_brand_data(cur, conn)

if __name__ == "__main__":
    main()
    #unittest.main(verbosity = 2)