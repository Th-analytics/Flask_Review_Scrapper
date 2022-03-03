import json
import os
import pandas as pd
from urllib.request import urlopen as ureq
from bs4 import BeautifulSoup as bs
import getpass
import pymongo
from flask import render_template


class Scrap:
    temp = ''
    bs_data = ''
    url = 'https://www.flipkart.com'
    product = ''
    nop = int()  # Number of Product
    database = None
    table = None
    search_url = ''
    p_url_list = []
    iter_value = None
    data_main = []
    df = None

    def __init__(self):
        pass

    """
    def takeInput(self):
        try:
            self.product = input('Enter Product Name').replace(' ', '')
            self.nop = int(input("Enter Number of Products "))
        except Exception as e:
            print(f'Error in TakeInput {e}')
    """
    def search(self, s_data):
        try:
            s_url = self.url + f'/search?q={s_data}'
            self.search_url = s_url
        except Exception as e:
            print(f"Error in Search {e}")
            print(f"URL: {s_url}")
            return False
        else:
            s_data = self.getRequest(s_url)
            return self.beautify(s_data)

    def getRequest(self, http_link):

        """
        Take https_link
        Return: http_data
        Call Beautify () after this to get html parsed
        """
        try:
            https = ureq(http_link)
            while True:
                try:
                    http_data = https.read()
                except http.client.IncompleteRead as icread:
                    print(f"Url: {http_link}")
                    continue
                else:
                    https.close()
                    break
            return http_data
        except Exception as e:
            print("Error in getRequest {e}")

    def beautify(self, b_data):
        """
        Take html code as input

        return the Beautified Html code
        """

        try:
            data = bs(b_data, 'html.parser')
            data = bs(data.prettify())
        except Exception as e:
            print(f'Error in beautify {e}')
            return False
        else:
            return data

    def connectToDb(self, dbname):
        print('Connecting to DataBase')
        try:
            cloud_url = f"mongodb+srv://adi_21:21101424@cluster1.beiuo.mongodb.net/{dbname}?retryWrites=true&w=majority"
            client = pymongo.MongoClient(cloud_url)
        except Exception as e:
            print(f"Error in connection To Data Base {e}")
            return False
        else:
            print('Connection Sucessfull !')
        try:
            self.database = client[dbname]
        except Exception as e:
            print(f"Error: No Collection with name {dbname} found (: \n{e}")

    def getdata(self):
        # print('In get data from data base')
        try:
            self.table = self.database[self.product]
        except Exception as e:
            print(f'Error in getdata Tabel \n{e}')
        try:
            collections = self.database.list_collection_names()
            if self.product in collections:
                db_data = self.table.find().limit(self.nop)
            else:
                return None
        except Exception as e:
            print(f"Error in getData\n{e}")
            return False
        else:
            print(db_data)
            return db_data

    def saveDownload(self,data_r):
        self.df = pd.DataFrame(data_r)
        self.df.to_csv('static/scrapper_data.csv')


    def display(self):
        print("In display")
        reviews = [i for i in self.data_main]
        return render_template('results.html', rows= [reviews, self.product ])

    def extractProductURL2(self, no_of_product2):
        '''
        Function called when box class id is _4ddWXP
        Returns the Product UrL
        '''
        # print('In extractProductURL2()')
        productOnPage = int(self.bs_data.find('span', {'class': '_10Ermr'}).text.strip().split()[3]) - int(
            self.bs_data.find('span', {'class': '_10Ermr'}).text.strip().split()[1]) + 1

        # stores all the product box that have class:_4ddWXP
        productBox = self.bs_data.findAll('div', {'class': '_4ddWXP'})

        # to store the product url
        p_url = []

        # loop to iterate through all the product boxes in productBox variable
        for i in productBox:
            try:
                p_url.append(self.url + i.a['href'])
                # print(self.url+ i.a['href'])
            except Exception as e:
                print(f'Error in extractProductURL2\n Error:{e}')
                return False
            finally:
                # print('In finally',len(p_url),no_of_product2)
                if len(p_url) == no_of_product2:
                    # print('In finally',len(p_url))
                    return p_url


    def extractProductURL(self, no_of_product):
        '''
        Function to check for the type of product box in the flipkart page
        if it finds div class with class ='_1AtVbE col-12-12'
        than it will call extractProductURL1(bs_html) method other wise
        it will call extractProductURL2(bs_html) to extract the infromation
        using other class id.

        Returns Function

        Algo:
        ->Find div with 'class':'_1AtVbE col-12-12'
            -> Slice the list
        ->extract,search and verify wether div class is '_4ddWXP'
            -> if true call extractProductURL2(bs_html1) with html data of that product page
        -> Else call extractProductURL1(bs_html1) to execute extraction using other div class
        ->if above conditions through error
            -> Call extractProductURL2(bs_html1)
        -> if no error

        '''
        # print('In extractProductURL()')

        try:
            s = self.bs_data.findAll('div', {'class': '_1AtVbE col-12-12'})[3:]
            if s[0].div.div.div.attrs['class'][0] == '_4ddWXP':
                return self.extractProductURL2(no_of_product)
            else:
                return self.extractProductURL1(no_of_product)
        except Exception as e:
            print('raised Exception in extractProductURL(bs_html1)')
            # print(f'Error in extractProductURL(bs_html1)\nError Code: {e}')
            return self.extractProductURL1(no_of_product)
        # else:
        # return extractProductURL1(bs_html1)

    def extractProductURL1(self, no_of_product1):
        '''
        Function called when box class id is _1AtVbE col-12-12
        Returns the Product UrL
        '''
        # print('In extractProductURL1()')
        productOnPage = int(self.bs_data.find('span', {'class': '_10Ermr'}).text.strip().split()[3]) - int(
            self.bs_data.find('span', {'class': '_10Ermr'}).text.strip().split()[1]) + 1
        # Stores the total number of product that's on the page
        productBox = self.bs_data.findAll('div', {'class': '_1AtVbE col-12-12'})[3:]


        # stores the Product URl
        p_url = []
        counter = 0
        # loop to iterate through all the product boxes in productBox variable
        for i in productBox:
            try:
                # print(counter, (self.url+ i.a['href']))
                p_url.append(self.url + i.a['href'])
                # print(self.url+ i.a['href'])

            except Exception as e:
                print(f'Error in extractProductURL1\n Error:{e}')
                del p_url
                return False
            finally:
                # print('In finally',len(p_url),no_of_product1)
                counter += 1
                if len(p_url) == no_of_product1:
                    return p_url

    def getValue(self):
        iter_list = []
        p_on_page = int(self.bs_data.find('span', {'class': '_10Ermr'}).text.strip().split()[3]) - int(
            self.bs_data.find('span', {'class': '_10Ermr'}).text.strip().split()[1]) + 1
        iteration = (self.nop - p_on_page) / p_on_page
        re = self.nop % p_on_page
        # print("In get Value",iteration,re)
        req_count = int(iteration)
        if type(iteration) == float:
            for i in range(0, req_count):
                iter_list.append(p_on_page)
            iter_list.append(re)
        elif type(iteration) == int:
            for i in range(0, req_count):
                iter_list.append(p_on_page)
        return iter(iter_list)

    def scrapy(self, s_data, p_req, current_p=1):
        scrapy_data = self.extractProductURL(p_req)
        for i in scrapy_data:
            self.p_url_list.append(i)
        # print(f"len(self.p_url_list) = {len(self.p_url_list)} and self.nop = {self.nop}")
        if len(self.p_url_list) < self.nop:
            current_p += 1
            n_p_link = self.search_url + f"&page={current_p}"
            html_scrapy = self.getRequest(n_p_link)
            bs_scrapy = self.beautify(html_scrapy)
            value = next(self.iter_value)
            # print(f"Curent page = {current_p} and Value ={value}")
            del scrapy_data
            return self.scrapy(bs_scrapy, value, current_p)
        else:
            del scrapy_data
            # return self.p_url_list

    def reviewPageLink(self, p_page):
        """
        Receives the product page html and
        return the link of the review page
        if review page does not exist the return false
        """
        # print("\n\n\n",p_page,end='\n\n\n\n')
        try:
            if p_page.find('div', {'class': 'col JOpGWq'}):
                # print(p_page.find('div',{'class':'col JOpGWq'}))
                # for i in ty:

                """
                print('\n\nreviewPageLink True', self.url + p_page.find('div', {'class': 'col JOpGWq'}).a['href'],
                      "\n\n")
                """
                link = self.url + p_page.find('div', {'class': 'col JOpGWq'}).a['href']
                # truncate = link.find('&aid')
                # link = link[:truncate]
                #truncate.clear()
                return link
            else:
                #print('Calling Review Scrapper 2')
                return False
        except:
            #print('eFalse')
            return 1

    def reviewExtractor(self, r_page):
        """
        This method is used to extract reviews of products
        if there is a seperate review page

        Algo:
        find div with 'class':'t-ZTKy'
        -> Iterate through each div
            -> Extract text associated with each individual review div
            -> Append into r list
        -> return r list
        """

        # print(r_page)
        r = []
        reviews = r_page.findAll('div', {'class': 't-ZTKy'})
        # print("reviews:",reviews)
        for i in reviews:
            r_v = i.div.div.text.replace('\n', '').strip().replace('...', '')
            # print(f'Reviews: {r_v}')
            r.append(r_v)
        return r

    def reviewExtractor2(self, r_page):

        """
        Called to extract the reviews on that same page where product is shown

        Algo:
        find div with 'class':'_16PBlm'
        -> Iterate through each div
            -> find div with 'class':'t-ZTKy'
            -> Extract text reviews
                ->if error occurs i.e no text data or div is there
                ->review variable r_v = empty
                -> if text data is there no error occured
                    -> append review in list
            -> Append into r list
        -> return r list
        """
        r = []
        reviewBox = r_page.findAll('div', {'class': '_16PBlm'})
        # print("reviews:",reviews)
        for i in reviewBox:
            rView = i.find('div', {'class': 't-ZTKy'})
            try:
                r_v = rView.div.div.text.replace('\n', '').strip().replace('...', '')
            except:
                r_v = ''
            else:
                # print(f'Reviews: {r_v}')
                r.append(r_v)
        return r

    def getReviews(self):
        data_review = {}

        """
        Use to get reviews,product Name, product Price and Product Rating
        Take no argument

        """
        # loop to itterate through each product link and extract the information.
        for i in range(0, len(self.p_url_list)):
            # print(f'{i} Begins')

            # productpage stores the Html of product url webpage for further processing.
            productPage = self.beautify(self.getRequest(self.p_url_list[i]))  # TODO for loop for pages[i]
            try:
                # Name of the Product
                pName = productPage.find('span', {'class': 'B_NuCI'}).text.replace('\n', '').strip()  # Name of Product
            except:
                pName = 'No Name'

            try:
                # Rating of the product
                pRating = productPage.find('div', {'class': '_3_L3jD'}).div.div.text.replace('\n',
                                                                                             '').strip()  # Rating of Product
            except:
                pRating = 'No Rating'
            # print(pName,pRating)

            # To get review of the product
            # calling reviewpageLink with productPage as input
            # to get wether review Page exist or not if true then if
            # will run, otherwise else will run
            check = self.reviewPageLink(productPage)
            if check not in [False, 1]:
                # print('In review Page')

                # calling review Page Link with product page html as iput to get the link
                # of review page
                self.temp = productPage
                rpl = self.reviewPageLink(productPage)

                # passing review page link to getRequest to get the html data of the review page
                reviewPage = self.beautify(self.getRequest(rpl))
                # print(f'RPL: {rpl}')
                # calling reviewExtractor with html data of reviewPage
                # to Extract information/ reviews of the product on that page
                reviews = self.reviewExtractor(reviewPage)

                # if no reviews are there than calling another review extractor to extract
                # reviews on that page without calling review page seperately
                if len(reviews) == 0:
                    reviews = self.reviewExtractor2(productPage)

            elif check == 1:
                reviews = self.reviewExtractor2(productPage)
            # if no reviews are there than else will run

            else:
                reviews = 'No Reviews'
            try:
                pPrice = productPage.find('div', {'class': '_30jeq3 _16Jk6d'}).text.replace('\n', '').strip()
            except:
                pPrice = 'No pricing'

            """
            print('-' * 200)
            print(
                f"\nProduct Name: {pName}\nProduct Rating: {pRating}\nProduct Price:{pPrice}\n\nReviews\n{reviews}\n\n")
            """
            data_review['Product Name'] = pName
            data_review['Product Rating'] = pRating
            data_review['Product Price'] = pPrice
            data_review['Reviews'] = reviews
            self.data_main.append(
                {'Product Name': pName, 'Product Price': pPrice, 'Product Rating': pRating, 'Reviews': reviews})
            self.table.insert_one(
                {'Product Name': pName, 'Product Price': pPrice, 'Product Rating': pRating, 'Reviews': reviews})

    def initiateReviewScrapper(self):
        product_on_page_0 = int(self.bs_data.find('span', {'class': '_10Ermr'}).text.strip().split()[3]) - int(
            self.bs_data.find('span', {'class': '_10Ermr'}).text.strip().split()[1]) + 1
        # print(f"Scrap.nop:{self.nop} product_on_page_0:{product_on_page_0}")
        if self.nop <= product_on_page_0:
            product_req = self.nop
        else:
            product_req = product_on_page_0
        self.iter_value = self.getValue()
        self.scrapy(s_data=self.bs_data, p_req=product_req)
        self.getReviews()

    def scraperMain(self):
        """if os.path.exists("static/scrapper_data.csv"):
            os.remove("static/scrapper_data.csv")
        else:
            pass"""
        #self.takeInput()
        self.bs_data = self.search(self.product)
        # db_admin = input('Enter Database User Name')
        # db_password = getpass.getpass('Enter Password')
        database_name = 'reviews'  # input("Enter the Database Name")
        self.connectToDb(database_name)
        data = self.getdata()
        if data == None:
            self.initiateReviewScrapper()
        else:
            if self.table.count_documents({}) < self.nop:
                self.initiateReviewScrapper()
            else:
                for data_items in data:
                    self.data_main.append(data_items)
        copy_data_main = self.data_main.copy()
        self.saveDownload(copy_data_main)
        self.p_url_list.clear()
        self.data_main.clear()
        self.product = ''
        self.nop = int()