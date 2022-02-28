#!/usr/bin/env python
# coding: utf-8


# import pandas as pd
from flask import Flask,render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup as BS
from urllib.request import urlopen as uReq

import pymongo


from flask_cors import cross_origin

from reviewScrapper import Scrap
app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def homepage():
    if request.method == 'POST':
        searched_product_name = request.form['content'].replace(' ', '')
        number_of_product = int(request.form['expected_review'])
        obj.product = searched_product_name
        obj.nop = number_of_product
        obj.scraperMain()
        return redirect(url_for('feedback'))

    else:
        return render_template('index.html')



@app.route('/feedback', methods=['GET'])
@cross_origin()
def feedback():
    reviews = [i for i in obj.data_main]
    #print(reviews)
    return render_template('results.html', rows= [reviews,obj.product ])
    #return render_template('results.html', reviews= db_data)

if __name__ == '__main__':
    obj = Scrap()
    app.run(port=8000, debug=True)