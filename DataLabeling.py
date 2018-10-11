# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import jieba.posseg
import jieba
import math
from collections import defaultdict, Counter
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score

jieba.enable_parallel(8)


reviews = pd.read_csv('ReviewsData_update.csv')
Users = pd.read_csv('userdata_update.csv')
ReviewsTrain = reviews.iloc[:int(reviews.shape[0]*0.8),:]
Users = Users[Users.isna()['intro']== False]
Users['intro'] = Users['intro'].apply(lambda x: [y for y in jieba.cut(x)])

def DetermineUser(Users):
    tags = ['合作', '专栏', '淘宝', '影评人', '公众', '号', '公众号','电邮','商务','微信','豆瓣','影评','短评','账号','营销','字幕']
    UserDict = {}
    for index, row in Users.iterrows():
        if any(x in row['intro'] for x in tags) or row['followers']> 3000 or row['watched_movies']> 2000:
            UserDict[row['user_name']] = 0
        else:
            UserDict[row['user_name']] = 1
    return UserDict
UserDict = DetermineUser(Users)

def DetermineReview(ReviewsTrain, UserDict):
    ReviewsLabel = {}
    for index, row in ReviewsTrain.iterrows():
        try:
            ReviewsLabel[row['cid']] = UserDict[row['user_name']]
        except KeyError:
            pass
    return ReviewsLabel

ReviewsLabel = DetermineReview(ReviewsTrain, UserDict)
ReviewsTrain = ReviewsTrain[ReviewsTrain['cid'].isin(list(ReviewsLabel.keys()))]
pos = ['n', 'nz', 'v', 'vd', 'vn', 'l', 'a', 'd', 'nrt', 'r', 'nr']
ReviewsTrain['content'] = ReviewsTrain['content'].apply(lambda x: [y for y,f in jieba.posseg.cut(x) if f in pos])
# ReviewsTrain[ReviewsTrain['cid'].isin(list(ReviewsLabel.keys()))]
Articles = dict(zip(ReviewsTrain['cid'],ReviewsTrain['content']))

def IDF(Articles):
    Terms = set([y for key, value in Articles.items() for y in value])
    N = len(Articles)
    IDF = {}
    for term in Terms:
        i = 0
        for cid, article in Articles.items():
            if term in article: i += 1
        IDF[term] = np.log(N / (i + 1))
    return IDF

print(IDF(Articles))

'''def BuildDictionary(df, feature, key):
    pos = ['n', 'nz', 'v', 'vd', 'vn', 'l', 'a', 'd', 'nrt', 'r', 'nr']
    Articles, ReviewsLabel = {}, {}
    for index, row in df.set_index(key).iterrows():
        print(index)
        words = []
        try:
            for word, flag in jieba.posseg.cut(row[feature]):
                if flag in pos:
                    words.append(word)
        except AttributeError:
            pass

        if words:
            Articles[index] = words

    return Articles'''

#user = BuildDictionary(Users,'intro','user_name')



'''tags = ['合作', '专栏', '淘宝', '影评人', '公众', '号', '公众号','电邮','商务','微信','豆瓣','影评','短评','账号','营销','字幕']
UserDict = {}
for index, row in Users.iterrows():
    print(index)
    try:
        seg = [word for word, flag in jieba.posseg.cut(row['intro'])]
    except AttributeError:
        seg = []
    if any(x in seg for x in tags) or row['followers']> 3000 or row['watched_movies']> 2000:
        UserDict[row['user_name']] = 0
    else:
        UserDict[row['user_name']] = 1

ReviewsLabel = {}
for index, row in reviews.iterrows():
    try:
        ReviewsLabel[row['cid']] = UserDict[row['user_name']]
    except KeyError:
        pass'''


pass



'''Users = pd.read_csv('userdata.csv')
ReviewsUsers = Reviews.merge(Users, on='user_name', how='left')'''

def LabelData(ReviewsUsers, Reviews):
    tags = ['合作', '专栏', '淘宝', '影评人', '公众号', '电邮','商务','微信','豆瓣','影评','短评','账号','营销','字幕']

    UserDict = {}
    for row in ReviewsUsers.values:
        try:
            seg = [word for word, flag in jieba.posseg.cut(row[12])]
            if any(x in seg for x in tags) and math.isnan(row[9]):
                UserDict[row[2]] = '0'
            elif not any(x in seg for x in tags) and math.isnan(row[9]):
                UserDict[row[2]] = '1'
        except (TypeError, AttributeError):
            if row[13] <= 2000 and row[-1] <= 500:
                UserDict[row[2]] = '1'
            else:
                UserDict[row[2]] = '0'

    Label = pd.DataFrame.from_dict(UserDict, orient='index')
    ReviewsLabel = Reviews.merge(Label, left_on='user_name', right_index=True)
    ReviewsLabel.drop(columns='customer ', inplace=True)
    ReviewsLabel.rename(columns={0: 'customer'}, inplace=True)
    ReviewsLabel.to_csv('ReviewsLabel.csv')
    pass


'''def MapToDict(Dict, Articles):
    ArticlesVectors = []
    for article in Articles:
        articlevector = []
        for word in article:
            articlevector.append(Dict[word])
        ArticlesVectors.append(articlevector)

    # padding vectors to the same length
    maxlen = max([len(x) for x in Articles])
    for v in ArticlesVectors:
        if len(v) < maxlen:
            i = maxlen - len(v)
            for z in np.zeros((i,), dtype=int):
                v.append(z)

    return ArticlesVectors'''

pass