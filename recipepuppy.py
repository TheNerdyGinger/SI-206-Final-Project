import json
import requests
import sqlite3



def get_data(ingredients, recipe):
    url = 'http://www.recipepuppy.com/api/?i={}&q={}&p=3'
    request_url = url.format(ingredients, recipe)
    r = requests.get(request_url)
    data = r.text
    data2 = json.loads(data)
    return data2





def read_file(filename):
    with open(filename) as f:
        lines = f.readlines()
    return lines





def create_tuples(filename):
    recipelist = []
    recipe = read_file('recipes.txt')
    for i in recipe:
        x = i.split(',')
        recipe = x[1]
        ingredients = x[0]
        data = get_data(ingredients, recipe)
        results = data['results']
        recipe_name = results[0]['title']
        ingredient_names = results[0]['ingredients']
        if (recipe_name, ingredient_names) not in recipelist:
            recipelist.append((recipe_name, ingredient_names))

    return recipelist



def create_database(filename):
    conn = sqlite3.connect("Recipes.sqlite")
    cur = conn.cursor()
    data = create_tuples(filename)

    cur.execute('CREATE TABLE IF NOT EXISTS Recipes(recipe_id INTEGER, recipenames TEXT)')

    # ADD NEXT ENTRY TO DATABASE-------------------------------------------------------------------

    cur.execute('SELECT * FROM Recipes WHERE recipe_id = (SELECT MAX(recipe_id) FROM Recipes)')
    start = cur.fetchone()
    if start:
        start = start[0] + 1
    else:
        start = 0
    recipename = data[start][0]
    cur.execute('INSERT INTO Recipes (recipe_id, recipenames) VALUES (?,?)', (start, recipename))
    
    
    #INGREDIENTS---------------------------------------------------------------------------------


    cur.execute('CREATE TABLE IF NOT EXISTS Ingredients (ingredient_id INTEGER, ingredient TEXT)')
    cur.execute('SELECT * FROM Ingredients WHERE ingredient_id = (SELECT MAX(ingredient_id) FROM Ingredients)')
    start2 = cur.fetchone()
    if start2:
        start2 = start2[0] + 1
    else:
        start2 = 0

    ingredients = data[start][1]
    ing = [i for i in ingredients.split(', ')]
    cur.execute('CREATE TABLE IF NOT EXISTS Recipes_and_Ingredients (recipe_id INTEGER, ingredient_id INTEGER)')
    for i in ing:
        cur.execute('SELECT ingredient_id FROM Ingredients WHERE ingredient = ?', (i, ))
        repeats = cur.fetchall()
        if not repeats:
            cur.execute('INSERT INTO Ingredients (ingredient_id, ingredient) VALUES(?,?)', (start2, i))
            cur.execute('INSERT INTO Recipes_and_Ingredients (recipe_id, ingredient_id) VALUES(?,?)', (start, start2))
        else:
            cur.execute('INSERT INTO Recipes_and_Ingredients (recipe_id, ingredient_id) VALUES(?,?)', (start, repeats[0][0]))
        
        start2 += 1
    

    conn.commit()

print(create_database('recipes.txt'))