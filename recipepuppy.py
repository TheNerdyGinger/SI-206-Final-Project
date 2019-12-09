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
    conn = sqlite3.connect("Recipes.sqlite")
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS Recipes')
    cur.execute('CREATE TABLE Recipes(recipe_id INTEGER, recipename TEXT)')
    cur.execute('INSERT INTO Recipes(recipeid)VALUES(0)')
    for i in recipenames:
        cur.execute('INSERT INTO Recipes(recipename)VALUES(?)', (i))
    
    cur.execute('DROP TABLE IF EXISTS Ingredients')
    cur.execute('CREATE TABLE Ingredients(ingredient_id INTEGER, ingredient TEXT)')

        

print(create_database('eggs', 'omelet'))