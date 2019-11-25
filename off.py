import sqlite3
import json
import os
import inflect
import requests

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
    query = "INSERT INTO Countries (country_id, country) VALUES (?, ?)"
    values = (5, "Brazil")
    cur.execute(query, values)
    query = "INSERT INTO Countries (country_id, country) VALUES (?, ?)"
    values = (6, "Portugal")
    cur.execute(query, values)
 
    conn.commit()

def format_ingredient_name(ing):
    engine = inflect.engine()
    ing = ing.lower()
    ing = engine.plural(ing)
    ing = ing.replace(" ", "-")
    return ing
    
#Format country names to check if they are in the table. Convert them to their IDS for storage
def format_countries(countries, cur, conn):
    c_ids = []
    for s in countries:
        s = s[3:]
        s = s.capitalize()
        cur.execute("SELECT country_id FROM Countries WHERE country = ?", (s,))
        

        #country not found - maybe change for later
        c = cur.fetchone()
        if c:
            c_ids.append(c[0])
     
    return c_ids



def insert_into_tables(cur, conn, index, product_name, nutriscore, countries, ing_id):
    cur.execute("SELECT * FROM Brands_and_scores ORDER BY brand_id DESC LIMIT 1")
    bookmark = cur.fetchone()
    if bookmark:
        bookmark = bookmark[0]
    else:
        bookmark = 0
    
    #Brands and scores insert
    query = "INSERT INTO Brands_and_scores (brand_id, brand, ing_id, nut_score) VALUES (?, ?, ?, ?)"
    b_id = bookmark+1
    values = (b_id, product_name, ing_id, nutriscore)
    cur.execute(query, values)

    #countries sold insert
    for c_id in countries:
        query = "INSERT INTO Brand_countries_sold (brand_id, country_id) VALUES (?,?)"
        values = (b_id, c_id)
        cur.execute(query, values)
    conn.commit()



def parse_json(data, cur, conn, ing_id):
    count = 0
    index = 0
    
    while count < 10 and index < len(data):
        d = data['products'][index]

        #nutriscore grade
        nutriscore = d.get("nutriscore_grade", -1)
        #if not found, use novagroup
        if nutriscore == -1:
            nutriscore = d.get('nova_group', -1)

            #if nova group not found either, skip this brand
            if (nutriscore == -1):
                index += 1
                continue
        
        #convert abcde nutriscore to an integer
        if type(nutriscore) == str:
            if nutriscore == 'a':
                nutriscore = 5
            elif nutriscore == 'b':
                nutriscore = 4
            elif nutriscore == 'c':
                nutriscore = 3
            elif nutriscore == 'd':
                nutriscore = 2
            else:
                nutriscore = 1

        product_name = d['product_name']
        countries = d['countries_tags']
        countries = format_countries(countries, cur, conn)
        if countries == []:
            index += 1
            continue

        insert_into_tables(cur, conn, count, product_name, nutriscore, countries, ing_id)
        index +=1
        count+=1


def request_url(cur, conn):
    #DROPS DELETE/COMMENT OUT WHEN NOT NEEDED
    # cur.execute("DROP TABLE IF EXISTS Brands_and_scores")
    # cur.execute("DROP TABLE IF EXISTS Brand_countries_sold")

    cur.execute("CREATE TABLE IF NOT EXISTS Brands_and_scores (brand_id, brand, ing_id, nut_score)")
    cur.execute("CREATE TABLE IF NOT EXISTS Brand_countries_sold (brand_id, country_id)")

    bookmark = open("off_bookmark.txt", 'r')
    pos = int(bookmark.read())

    cur.execute("SELECT ingredient FROM Ingredients WHERE ing_id = ?", (pos,))
    ing = cur.fetchone()[0]
    ing = format_ingredient_name(ing)

    try:
        url =  'https://fr-en.openfoodfacts.org/category/{}/1.json'
        request_url = url.format(ing)
        r = requests.get(request_url)
        data = json.loads(r.text)
    except:
        print("Error reading from url")
        # quit()
        data = []
    
    parse_json(data, cur, conn, pos) 

    bookmark.close()
    pos +=1
    bookmark = open("off_bookmark.txt", 'w')
    bookmark.write(str(pos))
    bookmark.close()

def main():

    #only have in one file
    db_name = "foodquest.db"
    cur, conn = setUpDatabase(db_name)
    # set_up_ing_table(cur,conn)
    set_up_country_table(cur, conn)
    request_url(cur, conn)

if __name__ == "__main__":
    main()
    #unittest.main(verbosity = 2)