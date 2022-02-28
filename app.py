#!/usr/bin/env python
# coding: utf-8


# import pandas as pd
from flask import Flask,render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup as BS
from urllib.request import urlopen as uReq
import threading
import pymongo


from flask_cors import cross_origin

from reviewScrapper import Scrap
app = Flask(__name__)
class threadClass:

    def __init__(self,):

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def run(self):
        global free_status
        free_status = False
        free_status = True
@app.route('/', methods=['POST', 'GET'])
def homepage():
    obj = Scrap()
    if request.method == 'POST':
        global free_status
        ## To maintain the internal server issue on heroku
        if free_status != True:
            return "This website is executing some process. Kindly try after some time..."
        else:
            free_status = True
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
    obj = Scrap()
    reviews = [i for i in obj.data_main]
    #print(reviews)
    return render_template('results.html', rows= [reviews,obj.product ])
    #return render_template('results.html', reviews= db_data)

if __name__ == '__main__':

    app.run(port=8000, debug=True)