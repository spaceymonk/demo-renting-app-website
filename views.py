# THIS FILE IS FOR ROUTING WEBSITE

from flask import Flask, render_template, request, redirect
import database

def home_page():
    if (request.method == "GET"):
        # first fetch the data from the database
        products = database.fetch_AllProducts()
        # display it
        return render_template("home.html", total_item=len(products), products=products, logged=False, filtered=False)
    else:
        print(request.form)
        products = database.fetch_FilteredProducts(request.form)
        return render_template("home.html", total_item=len(products), products=products, logged=False, filtered=True)