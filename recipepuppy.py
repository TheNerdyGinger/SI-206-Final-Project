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

def dictionary(ingredients, recipe):
    recipedict = {}
    data = get_data(ingredients, recipe)
    for i in data['results']:
        key = i['title']
        values = i['ingredients']
        recipedict[key] = values
    return recipedict    

def create_database(ingredients, recipe):
    data = dictionary(ingredients, recipe)
    recipenames = data.keys()
    ingredients = data.values()
    ingredientlist = []
    recipelist = []
    conn = sqlite3.connect("Recipes.sqlite")
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS Recipes(recipe_id INTEGER, recipename TEXT)')

    cur.execute('SELECT * FROM Recipes WHERE recipe_id = (SELECT MAX(recipe_id) FROM Recipes)')
    start = cur.fetchone()
    if start:
        start = start[0] + 1
    else:
        start = 0
    for i in recipenames:
        istrip = i.strip('\n ')
        if istrip not in recipelist:
            recipelist.append(i)
            cur.execute('INSERT INTO Recipes(recipe_id,recipename)VALUES(?,?)', (start, istrip))
            start += 1
    
    cur.execute('SELECT * FROM Ingredients WHERE ingredient_id = (SELECT MAX(ingredient_id) FROM Ingredients)')
    start2 = cur.fetchone()
    if start2:
        start2 = start2[0] + 1
    else:
        start2 = 0
    cur.execute('CREATE TABLE IF NOT EXISTS Ingredients(ingredient_id INTEGER, ingredient TEXT)')
    
    single_ing = []
    for i in ingredients:
        ingredient_single = i.split(',')
        for y in ingredient_single:
            if y not in single_ing:
                single_ing.append(y)
    
    print(single_ing)

    conn.commit()

print(create_database('eggs','omelet'))