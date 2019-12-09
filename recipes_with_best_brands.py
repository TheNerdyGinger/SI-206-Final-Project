import sqlite3
import json
import os

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


def create_sample_recipe_table(cur, conn): #for testing. remove when we have real data
    cur.execute('CREATE TABLE IF NOT EXISTS Recipes(recipe_id INTEGER, recipename TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS Recipes_and_ingredients(recipe_id INTEGER, ingredient_id INTEGER)')

    query = "INSERT INTO Recipes(recipe_id, recipename) VALUES (?,?)"
    values = (0, "omlet")
    cur.execute(query,values)
    
    query = "INSERT INTO Recipes(recipe_id, recipename) VALUES (?,?)"
    values = (1, "Pizza")
    cur.execute(query,values)

    query = "INSERT INTO Recipes(recipe_id, recipename) VALUES (?,?)"
    values = (2, "burger")
    cur.execute(query,values)

    query = "INSERT INTO Recipes_and_ingredients(recipe_id, ingredient_id) VALUES (?,?)"
    values = (0, 0)
    cur.execute(query,values)
    query = "INSERT INTO Recipes_and_ingredients(recipe_id, ingredient_id) VALUES (?,?)"
    values = (0, 1)
    cur.execute(query,values)

    query = "INSERT INTO Recipes_and_ingredients(recipe_id, ingredient_id) VALUES (?,?)"
    values = (1, 1)
    cur.execute(query,values)

    query = "INSERT INTO Recipes_and_ingredients(recipe_id, ingredient_id) VALUES (?,?)"
    values = (2, 2)
    cur.execute(query,values)
    query = "INSERT INTO Recipes_and_ingredients(recipe_id, ingredient_id) VALUES (?,?)"
    values = (2, 0)
    cur.execute(query,values)

    conn.commit()
def main():
    db_name = "foodquest.db"
    cur, conn = setUpDatabase(db_name)

   #create_sample_recipe_table(cur, conn) #for testing. remove when we have real data
    #cur.execute("DROP TABLE IF EXISTS Recipes_and_best_brands")
    cur.execute("CREATE TABLE IF NOT EXISTS Recipes_and_best_brands (recipe_id INTEGER, brand_id INTEGER)")

    cur.execute("SELECT * FROM Recipes_and_best_brands WHERE recipe_id = (SELECT MAX(recipe_id) FROM Recipes_and_best_brands)")
    start = cur.fetchone()
    if start:
        start= start[0]+1
    else:
        start = 0

    cur.execute("SELECT ingredient_id FROM Recipes_and_ingredients WHERE recipe_id = ?", (start,))
    ings = cur.fetchall()
    
    for i in ings:
        cur.execute("SELECT brand_id FROM Best_brands WHERE ingredient_id = ?", (i[0],))
        b = cur.fetchone()
        
        query = "INSERT INTO Recipes_and_best_brands(recipe_id, brand_id) VALUES (?,?)"
        values = (start, b[0])
        cur.execute(query,values)

    conn.commit()
if __name__ == "__main__":
    main()
