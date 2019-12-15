from os import path
from wordcloud import WordCloud
import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import json
import os
import webbrowser  


def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def grab_wordcloud_data(cur, conn):
    
    cur.execute('''SELECT Recipes.recipenames, Ingredients.ingredient FROM Recipes_and_Ingredients
    JOIN Ingredients ON Recipes_and_Ingredients.ingredient_id = Ingredients.ingredient_id 
    JOIN Recipes ON Recipes.recipe_id = Recipes_and_Ingredients.recipe_id ORDER BY Recipes.recipe_id''')
    output_table = cur.fetchall()
    ingredient_string = ""
    for output in output_table:
        if ' ' in output[1]:
            ingredient_string = ingredient_string + " " + output[1].replace(' ', '_')
    print(ingredient_string)
    return ingredient_string

def word_cloud(word_string):

    # Read the whole text.
    text = word_string 

    # Generate a word cloud image
    wordcloud = WordCloud().generate(text)

    # Display the generated image:
    # the matplotlib way:

    # lower max_font_size
    wordcloud = WordCloud(background_color="white", max_font_size=40).generate(text)
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()


def grab_pie_data(cur, conn):
    country_list = []
    cur.execute('''SELECT Brand_countries_sold.country_id, Countries.country FROM Brand_countries_sold
    JOIN Countries ON Brand_countries_sold.country_id = Countries.country_id 
    ORDER BY Countries.country_id''')
    output_table = cur.fetchall()
    for output in output_table:
        country_list.append(output)

    return country_list
    

def pie_graph(country_list):
    country_dict = {}
    country_pie_list = []
    
    
    for country in country_list:
        if country[1] in country_dict:
            country_dict[country[1]] = country_dict[country[1]] + 1
        else:
            country_dict[country[1]] = 1

    sorted_totals = sorted(country_dict.values(), reverse = True)[0:10]
    for n in sorted_totals:
        for country in country_dict:
            if country_dict[country] == n:
                country_pie_list.append(country)
    
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
    wedges, texts = ax.pie(sorted_totals, wedgeprops=dict(width=0.5), startangle=-40)

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(str(country_pie_list[i]) + " (" + str(sorted_totals[i]) + ")", xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y), horizontalalignment=horizontalalignment, **kw)

    ax.set_title("Top 10 Countries where Brands are Sold")
    plt.show()
    
    return country_pie_list

def grab_staticmap_data(cur, conn, country_list):
    coord_list = []
    cur.execute('''SELECT Countries.country, Lat_lng.latitude, Lat_lng.longitude FROM Countries
    JOIN Lat_lng ON Countries.country_id = Lat_lng.country_id ORDER BY Countries.country_id''')
    output_table = cur.fetchall()
    for output in output_table:
        if output[0] in country_list:
            coord_list.append((output[1], output[2]))
    

    return coord_list
    

def staticmap(coord_list):
    coord_string_list = []
    key = '5BPqkMyJdoFaGeY6MfwAbOk73xXK5Kq9'
    base_url = 'https://www.mapquestapi.com/staticmap/v5/map?locations=' 
    coord_string = ""
    for coord in coord_list:
        coord_string_list.append(str(coord[0]) + "," + str(coord[1]) + "||")
    for coord in coord_string_list:
        coord_string = coord_string + coord
    url = base_url + coord_string + '&size=@2x&key=' + key
    webbrowser.open(url, new=0, autoraise=True)

def grab_barchart_data(cur, conn):
    cur.execute('''SELECT Ingredients.ingredient_id, Ingredients.ingredient, Brands_and_scores.nut_score FROM Brands_and_scores
    JOIN Ingredients ON Brands_and_scores.ingredient_id = Ingredients.ingredient_id ORDER BY Ingredients.ingredient_id''')
    ingredient_list_dup = []
    ingredient_list = []
    ingredient_tot = 0
    output_table = cur.fetchall()
    for output in output_table:
        ingredient_list_dup.append(output[1])
    for n in ingredient_list_dup:
        if n not in ingredient_list:
            ingredient_list.append(n)
    
    ingredient_score = {}
    ingredient_dict = {}
    ingredient_score_dict = {}
    for output in output_table:
        for ingredient in ingredient_list:
            if output[1] == ingredient:
                ingredient_tot = output[2]
                if ingredient in ingredient_dict:
                    ingredient_dict[ingredient] = ingredient_dict[ingredient] + 1
                elif ingredient not in ingredient_dict:
                    ingredient_dict[ingredient] = 1
                if ingredient in ingredient_score:
                    ingredient_score[ingredient] = ingredient_score[ingredient] + ingredient_tot
                elif ingredient not in ingredient_score:
                    ingredient_score[ingredient] = 0
    
    for ingredient in ingredient_dict:
        average_ingredient_score = ingredient_score[ingredient] / ingredient_dict[ingredient]
        ingredient_score_dict[ingredient] = average_ingredient_score

    cur.execute('''SELECT Recipes.recipe_id, Recipes.recipenames, Ingredients.ingredient FROM Recipes
    JOIN Recipes_and_Ingredients ON Recipes.recipe_id = Recipes_and_Ingredients.recipe_id 
    JOIN Ingredients ON Ingredients.ingredient_id = Recipes_and_Ingredients.ingredient_id ORDER BY Recipes.recipe_id''')
    output_table = cur.fetchall()
    
    recipe_list_dup = []
    recipe_list = []
    
    for output in output_table:
        recipe_list_dup.append(output[1])
    for n in recipe_list_dup:
        if n not in recipe_list:
            recipe_list.append(n)
    
    recipe_score = {}
    recipe_dict = {}
    recipe_score_dict = {}
    recipe_tot = 0
    for output in output_table:
        for recipe in recipe_list:
            recipe = recipe.strip('\n')
            if output[1] == recipe:
                recipe_tot = ingredient_score_dict[output[2]]
                if recipe in recipe_dict:
                    recipe_dict[recipe] = recipe_dict[recipe] + 1
                elif recipe not in recipe_dict:
                    recipe_dict[recipe] = 1
                if recipe in recipe_score:
                    recipe_score[recipe] = recipe_dict[recipe] + recipe_tot
                elif recipe not in recipe_score:
                    recipe_score[recipe] = 0
    
    for recipe in recipe_dict:
        average_recipe_score = recipe_score[recipe] / recipe_dict[recipe]
        recipe_score_dict[recipe] = average_recipe_score
    
    
    return ingredient_score_dict, recipe_score_dict
            
    

def barchart(ingredient_score_dict, recipe_score_dict):
    xlist_ingredient = []
    ylist_ingredient = []
    tuple_list_ingredient = []
    xlist_recipe = []
    ylist_recipe = []
    tuple_list_recipe = []
    
    fig = plt.figure(figsize=(10,10))
    fig2 = plt.figure(figsize=(10,10))
    ax1 = fig.add_subplot(121)
    ax2 = fig2.add_subplot(121)
    for ingredient in ingredient_score_dict:
        ingredient_tuple = (ingredient, ingredient_score_dict[ingredient])
        tuple_list_ingredient.append(ingredient_tuple)
        xlist_ingredient.append(ingredient)
        ylist_ingredient.append(ingredient_score_dict[ingredient])
    
    for recipe in recipe_score_dict:
        recipe_tuple = (recipe,recipe_score_dict[recipe])
        tuple_list_recipe.append(recipe_tuple)
        xlist_recipe.append(recipe)
        ylist_recipe.append(recipe_score_dict[recipe])

    ax1.bar(xlist_ingredient, ylist_ingredient, align = 'center', color = 'red')
    ax1.set(xlabel='Ingredient', ylabel='Average Nutritional Score', title='Average Nutritional Score by Ingredient')
    ax1.tick_params(axis="x", labelsize=5)
    plt.setp(ax1.get_xticklabels(),rotation=90, horizontalalignment='right')
    plt.tight_layout()
    plt.tight_layout()
    fig.savefig("ingredient_graph.png")

    ax2.bar(xlist_recipe, ylist_recipe, color = 'green')
    ax2.set(xlabel='Recipe', ylabel='Average Nutritional Score', title='Average Nutritional Score by Recipe')
    #ax2.set_yticks(ax2.get_yticks())
    plt.xticks(rotation = 90)
    plt.tight_layout()
    plt.tight_layout()
    fig2.savefig("recipe_graph.png")
    plt.show()
  
   

def main():
    cur, conn = setUpDatabase('foodquest.db')
    #ingredient_string = grab_wordcloud_data(cur, conn)
    #word_cloud(ingredient_string)
    #country_list = grab_pie_data(cur, conn)
    #country_list2 = pie_graph(country_list)
    #coord_list = grab_staticmap_data(cur, conn, country_list2)
    #staticmap(coord_list)
    ingredient_score_dict, recipe_score_dict = grab_barchart_data(cur, conn)
    barchart(ingredient_score_dict, recipe_score_dict)

if __name__ == "__main__":
    main()