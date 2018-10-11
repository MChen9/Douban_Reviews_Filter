# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import jieba.posseg
import jieba.analyse
import math
from collections import defaultdict, Counter
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
from sklearn import svm

jieba.enable_parallel(8)


def DetermineUser(Users):
    tags = ['合作', '专栏', '淘宝', '影评人', '公众', '号', '公众号', '电邮', '商务', '微信', '豆瓣', '影评', '短评', '账号', '营销', '字幕']
    UserDict = {}
    for index, row in Users.iterrows():
        if any(x in row['intro'] for x in tags) or row['followers'] > 3000 or row['watched_movies'] > 2000:
            UserDict[row['user_name']] = 0
        else:
            UserDict[row['user_name']] = 1
    return UserDict


def DetermineReview(ReviewsTrain, UserDict):
    ReviewsLabel = {}
    for index, row in ReviewsTrain.iterrows():
        try:
            ReviewsLabel[row['cid']] = UserDict[row['user_name']]
        except KeyError:
            pass
    return ReviewsLabel


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


def TFIDF(IDF, Articles):
    Frequency = {}
    for cid, article in Articles.items():
        Frequency[cid] = Counter(article)

    TfIdf = {}
    for cid, freqs in Frequency.items():
        tfidf = {}
        for key, freq in freqs.items():
            tfidf[key] = IDF[key] * freq
        TfIdf[cid] = tfidf
    return TfIdf


def LSA(TfIdf):
    OccurenceMatrix = pd.DataFrame(TfIdf).fillna(0)
    U, S, V = np.linalg.svd(OccurenceMatrix.values)
    k = S.size
    Uk = U[:, :k]
    Sk = np.diag(S)
    translate = np.linalg.inv(Sk) @ np.transpose(Uk)

    return V.T, list(OccurenceMatrix.columns), translate, Sk


def main():
    reviews = pd.read_csv('ReviewsData_update.csv')
    Users = pd.read_csv('userdata_update.csv')
    ReviewsTrain = reviews.iloc[:int(reviews.shape[0] * 0.8), :]
    Users = Users[Users.isna()['intro'] == False]
    Users['intro'] = Users['intro'].apply(lambda x: [y for y in jieba.cut(x)])
    UserDict = DetermineUser(Users)
    ReviewsLabel = DetermineReview(ReviewsTrain, UserDict)
    ReviewsTrain = ReviewsTrain[ReviewsTrain['cid'].isin(list(ReviewsLabel.keys()))]
    pos = ['n', 'nz', 'v', 'vd', 'vn', 'l', 'a', 'd', 'nrt', 'r', 'nr']
    ReviewsTrain['content'] = ReviewsTrain['content'].apply(lambda x: [y for y, f in jieba.posseg.cut(x) if f in pos])
    Articles = dict(zip(ReviewsTrain['cid'], ReviewsTrain['content']))
    idf = IDF(Articles)
    TfIdf = TFIDF(idf, Articles)
    data, index, translate, Sk = LSA(TfIdf)

    label = []
    for x in index:
        label.append(ReviewsLabel[x])

    traindata, testdata = data[:int(len(data) * .9)], data[int(len(data) * .9):]
    trainlabel, testlabel = label[:int(len(data) * .9)], label[int(len(data) * .9):]
    clf = [DecisionTreeClassifier(random_state=0), svm.SVC()]
    for model in clf:
        model.fit(traindata, trainlabel)
        pred = model.predict(testdata)

        n = 0
        for i in range(len(pred)):
            if pred[i] == testlabel[i]:
                n = n + 1
        print(n / len(pred))


if __name__ == '__main__':
    main()
