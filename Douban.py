# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from selenium import webdriver
from urllib import request
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
from collections import defaultdict
import pickle
import MySQLdb
from datetime import date
import re
import time


def Login(url, username, password):
    driver = webdriver.Chrome(executable_path=
                              r'/Users/mchen/Documents/18FallCourses/Independent Study/Codes/Data/chromedriver')
    driver.get(url)
    driver.find_element_by_id('email').send_keys(username)
    driver.find_element_by_id('password').send_keys(password)
    try:
        driver.find_element_by_id('captcha_field').send_keys(input('Verify Code:'))
        driver.find_element_by_id('captcha_field').submit()
    except:
        driver.find_element_by_id('password').submit()
    req = requests.Session()
    cookies = driver.get_cookies()
    for cookie in cookies:
        req.cookies.set(cookie['name'], cookie['value'])
    headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}
    req.headers = headers

    return req, driver


def MakeSoup(req, url):
    soup = BeautifulSoup(req.get(url).content, 'html.parser', from_encoding='utf-8')
    return soup


def ReplacePounctuation(pattern, sentence):
    for i in pattern:
        sentence = sentence.replace(i, ' ')
    return sentence


# userclass.user_intro().intro.replace('’', ' ')


class ReviewContent():
    def __init__(self, tag):
        self.tag = tag
        self.ReviewID = tag.input['value']
        self.UserName = tag.a['title']
        self.UserUrl = tag.a['href']
        self.Votes = tag.find('span', class_='votes').text
        self.RateStars = tag.find('span', class_='rating')['class'][0][-2]
        self.Reviews = tag.find_all('span', class_='short')[0].text
        self.Times = tag.find('span', class_='comment-time')['title']


class UserProfile():
    def __init__(self, req, url):
        self.req = req
        self.url = url
        self.soup = MakeSoup(req, url)

    def basic_info(self):
        try:
            self.username = self.soup.find('div', class_='info').h1.text.split('\n')[1].split(' ')[-1]
            self.userid = self.soup.find('div', class_='user-info').find('div', class_='pl').text.split(' ')[0]
            return self
        except AttributeError:
            pass


    def user_intro(self):
        pattern = '‘’！——+|、·。/？；：“”「」【】=-》《～@#¥%……&*（），:;\'.,\%'
        self.intro = ReplacePounctuation(pattern, self.soup.find('div', class_='user-intro').find('span').text)
        return self

    def friends(self):
        try:
            self.followers = re.findall(r'\d+', self.soup.find('p', class_='rev-link').text)[0]
            self.follows = re.findall(r'\d+', self.soup.find('div', {'id': 'friend'}).a.text)[
                0]  # find numbers in string
        except IndexError:
            self.followers = '0'
            self.follows = '0'
        return self

    def movies(self):
        try:
            self.watched = re.findall(r'\d+',
                                      self.soup.find('div', {'id': 'movie'}).find('span', class_='pl').find_all('a')[
                                          -1].text)[0]
        except IndexError:
            self.watched = '0'
        return self


def requestsql(sql):
    db = MySQLdb.connect(host='localhost', user='root', passwd='12345droeeN', db='testdb', charset='utf8')
    cursor = db.cursor()

    '''sql = "INSERT IGNORE INTO testdb.Douban_Movie_Reviews(cid, user_name, movie_code, \
           votes, rate_stars, date, content, add_time) \
           VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
          (cid, username, moviecode, votes, ratestars, Date, content, addtime)'''

    try:
        # execute sql
        cursor.execute(sql)
        # submit to database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()

    db.close()


if __name__ == '__main__':

    loginurl = 'https://www.douban.com/accounts/login?source=main'
    username = '1175331160@qq.com'
    password = '138droeen'
    req, driver = Login(loginurl, username, password)

    url = 'https://movie.douban.com/subject/26387939/comments?start=0&limit=20&sort=new_score&status=P'
    a = 0
    soup = MakeSoup(req, url)

    ReviewsNumber = int(soup.find('li', class_='is-active').contents[1].text[3:-1])
    for i in range(int(ReviewsNumber / 20)):
        moviecode = '26387939' #'4920389' '3742360''26363254''26336252''27133303''27113517''27622447'
        url = 'https://movie.douban.com/subject/' + \
              moviecode + '/comments?start=' + str(a) + '&limit=20&sort=new_score&status=P'
        soup = MakeSoup(req, url)
        if len(soup.find_all('div', class_='comment-item')) <= 1:
            break
        else:
            # ReviewDict = {}
            for item in soup.find_all('div', class_='comment-item'):
                try:
                    reviewclass = ReviewContent(item)
                    userclass = UserProfile(req, reviewclass.UserUrl)
                    # ReviewDict[reviewclass.ReviewID] = reviewclass

                    reviewsql = "INSERT IGNORE INTO testdb.Douban_Movie_Reviews(cid, user_name, movie_code, " \
                                "votes, rate_stars, date, content, add_time) " \
                                "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                                (reviewclass.ReviewID, reviewclass.UserName, moviecode, reviewclass.Votes,
                                 reviewclass.RateStars, reviewclass.Times, reviewclass.Reviews, str(datetime.now()))
                    requestsql(reviewsql)

                    usersql = "INSERT IGNORE INTO testdb.Douban_Users (user_id, user_name, intro, followers, follow, watched_movies) " \
                              "VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % \
                              (userclass.basic_info().userid, userclass.basic_info().username,
                               userclass.user_intro().intro, userclass.friends().followers,
                               userclass.friends().follows, userclass.movies().watched)

                    requestsql(usersql)
                    #time.sleep(np.random.uniform(1, 2))


                except (TypeError, AttributeError):
                    pass

            a = a + 20
            print(a + 20)

# soup.find_all('div', class_='comment-item')[0].find_all('span', class_='short')[0].text reviews
# .a['href'] user url
# .a['title'] user name
# .find('span',class_='votes').text  votes number
# .find('span', class_='rating')['class'][0][-2] rate stars
# .find('span', class_ = 'comment-time')['title']  times
# next page: soup, url = MakeSoup('https://movie.douban.com/subject/4920389/comments?start=1000&limit=20&sort=new_score&status=P')
