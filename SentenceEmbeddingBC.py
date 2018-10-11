# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import jieba.posseg
import jieba.analyse
import math
from collections import defaultdict, Counter
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score





def BuildDictionary(df, feature, key):
    pos = ['n', 'nz', 'v', 'vd', 'vn', 'l', 'a', 'd', 'nrt', 'r', 'nr']
    Articles = {}
    for index, row in df.set_index(key).iterrows():
        words = []
        try:
            for word, flag in jieba.posseg.cut(row[feature]):
                if flag in pos:
                    words.append(word)
        except AttributeError:
            pass
        if words:
            Articles[index] = words
    Terms = set([y for key, value in Articles.items() for y in value])
    # Dict = dict(zip(SetWords, np.arange(len(SetWords))))
    return Terms, Articles


def IDF(Terms, Articles):
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
    traindata = pd.DataFrame(V.T)
    traindata['cid'] = list(OccurenceMatrix.columns)
    k = S.size
    Uk = U[:, :k]
    Sk = np.diag(S)
    translate = np.linalg.inv(Sk) @ np.transpose(Uk)

    return traindata, OccurenceMatrix.index, translate, Sk


def main():
    Reviews = pd.read_csv('ReviewsLabel.csv')
    TrainTerms, TrainArticles = BuildDictionary(Reviews, 'content','cid')
    idf = IDF(TrainTerms, TrainArticles)
    tfidf = TFIDF(idf, TrainArticles)
    traindata, index, translate, Sk = LSA(tfidf)
    testdata = Reviews.iloc[200:225]
    TestTerms, TestArticles = BuildDictionary(testdata, 'content','cid')
    testtfidf = TFIDF(idf, TestArticles)
    # Fill nan with zero
    for key, value in testtfidf.items():
        for x in index:
            try:
                value[x] = value[x]
                pass
            except KeyError:
                value[x] = 0

    D = pd.DataFrame(testtfidf).values.T
    Dj = []
    for dj in D:
        Dj.append(translate @ dj)

    trainlabel = Reviews[['cid', 'customer']].fillna(0)
    trainlabel['customer'] = trainlabel['customer'].apply(int)
    X = traindata.merge(trainlabel, on='cid').drop('cid', axis=1).values[:, :-1].astype('float')
    y = traindata.merge(trainlabel, on='cid').drop('cid', axis=1).values[:, -1]
    clf = DecisionTreeClassifier(random_state=0)
    clf.fit(X, y)
    pred = clf.predict(Dj)


if __name__ == '__main__':
    main()