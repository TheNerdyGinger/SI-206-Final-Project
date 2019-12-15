import sqlite3
import json
import os

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def join_databases(cur, conn, filename):
    #cur.execute("SELECT Restaurants.name, Categories.title FROM Restaurants LEFT JOIN Categories ON Restaurants.category_id = Categories.id")
    cur.execute('''SELECT Recipes.recipenames, Brands_and_scores.brand FROM Recipes_and_best_brands 
    JOIN Brands_and_scores ON Recipes_and_best_brands.brand_id = Brands_and_scores.brand_id 
    JOIN Recipes ON Recipes.recipe_id = Recipes_and_best_brands.recipe_id ORDER BY Recipes.recipe_id''')
    output_table = cur.fetchall()

    outfile = open(filename, 'w')
    outfile.write("Recipes and Healthiest Brands as Ingredients\n\n")
    recipe_name = output_table[0][0]
    recipe_name = recipe_name.strip("\n")
    recipe_name = recipe_name.strip("\r")
    out_string = recipe_name + ':'

    for o in output_table:
        o = (o[0].strip('\n\r'), o[1])
        if not(o[0] == recipe_name):
            out_string = out_string.rstrip(',')
            out_string += '.'
            outfile.write(out_string + '\n\n')
            recipe_name = o[0]
            out_string = recipe_name+":"
        else:
            out_string += " " + o[1] + ','

    outfile.close()
    
def main():
    db_name = "foodquest.db"
    cur, conn = setUpDatabase(db_name)
    join_databases(cur, conn, "recipe_output.txt")

if __name__ == "__main__":
    main()