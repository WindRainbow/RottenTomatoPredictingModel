### Import everything ###
import re
import time
import pandas as pd
import pandas_profiling
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import calendar
import timestring
from textblob import TextBlob
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn import linear_model
from sklearn import *
import sklearn
from multiprocessing import Pool, cpu_count
import gc; gc.enable()
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from time import gmtime, strftime


### SCENARIO 1 ###  (We have one big dataset to split)
def f(df_polarity_desc):
    if df_polarity_desc['sentiment'] > 0:
        val = "2"
    elif df_polarity_desc['sentiment'] == 0:
        val = "1"
    else:
        val = "0"
    return val
def SCENE1(FD):
    df=pd.read_csv(FD, sep ='\t')
    df=pd.DataFrame(data = df)
    #Time Processing
    df['Release_Date'] = ''
    df['Release_Month'] = ''
    df['Release_Day'] = ''
    df['Weekend_Release'] = ''
    df['Holiday_Release'] = ''
    df['Release_Type'] = ''
    #df['Difference'] = ''
    holidays = ['1-1', 
                #Memorial Day
                '5-25', '5-26', '5-27', '5-28', '5-29', '5-30', '5-31', 
                #Independence Day
                '7-4', 
                # Labor Day
                '9-1', '9-2', '9-3', '9-4', '9-5', '9-6', '9-7', 
                #Thanksgiving Day
                '11-22', '11-23', '11-24', '11-25', '11-26', '11-27', '11-28', 
                #Christmas Day
                '12-25']
    for i in range(0, len(df.index) - 1):
        try:
            df['Release_Date'][i] = timestring.Date(df['In Theaters'][i])
            df['Release_Month'][i] = timestring.Date(df['In Theaters'][i]).month
            df['Release_Day'][i]= calendar.day_name[timestring.Date(df['In Theaters'][i]).weekday]
            if str(df['Release_Day'][i]) == 'Friday' or str(df['Release_Day'][i]) == 'Saturday' or str(df['Release_Day'][i]) == 'Sunday':
                df['Weekend_Release'][i] = 1
            else:
                df['Weekend_Release'][i] = 0
            if str(timestring.Date(df['In Theaters'][i]).month) + '-' + str(timestring.Date(df['In Theaters'][i]).day) in holidays:
                df['Holiday_Release'][i] = 1
            else:
                df['Holiday_Release'][i] = 0
            temp = re.sub('[^a-zA-Z]',' ',df['In Theaters'][i])
            temp = re.sub(' +',' ',temp).strip()
            df['Release_Type'][i] = str(temp[4:])
        except:
            df['Weekend_Release'][i] = 0
            df['Holiday_Release'][i] = 0
            df['Release_Type'][i] = 'wide'
    #Synopsis Processing
    bloblist_desc = list()
    df_review_str = df['synopsis'].astype(str)
    for row in df_review_str:
        blob = TextBlob(row)
        bloblist_desc.append((row,blob.sentiment.polarity, blob.sentiment.subjectivity))
        df_polarity_desc = pd.DataFrame(bloblist_desc, columns = ['summary','sentiment','polarity'])
    df['synopsis_sc'] = df_polarity_desc.apply(f, axis=1)
    #Clean the rest data
    df['audience_score'] = df['audience_score'].replace('None', np.nan)
    df['audience_score'] = df['audience_score'].str.strip("%")
    df['audience_score'] = df['audience_score'].astype(float)
    df['critic_score'] = df['critic_score'].replace('None', np.nan)
    df['critic_score'] = df['critic_score'].str.strip("%")
    df['critic_score'] = df['critic_score'].astype(float)
    del df['actor_links']
    del df['Box Office']
    df['Runtime']=df['Runtime'].replace('None', np.nan)
    df['Runtime']=df['Runtime'].str.strip("minutes")
    df['Runtime']=df['Runtime'].astype(float)
    df['Holiday_Release']=df['Holiday_Release'].replace('', np.nan)
    df['Holiday_Release']=df['Holiday_Release'].fillna(2.0)
    df['Holiday_Release']=df['Holiday_Release'].astype(float)
    df['Weekend_Release']=df['Holiday_Release'].replace('', np.nan)
    df['Weekend_Release']=df['Holiday_Release'].fillna(2.0)
    df['Weekend_Release']=df['Holiday_Release'].astype(float)
    #df['synopsis_sc']=df['synopsis_sc'].astype(int)
    #df['Release_Month']=df['Release_Month'].replace('', np.nan)
    #df['Release_Month']=df['Release_Month'].fillna(2.0)
    #df['Release_Month']=df['Release_Month'].astype(float)
    #get dummies to category variable
    dummies_Studio=pd.get_dummies(df['Studio'],prefix ='Studio')
    dummies_Wtitten=pd.get_dummies(df['Written By'],prefix ='Written By')
    dummies_Directed=pd.get_dummies(df['Directed By'],prefix='Directed By') 
    dummies_rating=pd.get_dummies(df['Rating'],prefix='Rating')
    dummies_genre=pd.get_dummies(df['Genre'],prefix='Genre')
    dummies_release_type = pd.get_dummies(df['Release_Type'],prefix='Release_Type')
    df=pd.concat([df,dummies_Studio,dummies_Wtitten,dummies_rating,dummies_genre,dummies_release_type],axis=1)
    del df['actor_names']
    del df['synopsis']
    del df['In Theaters']
    del df['Genre']
    del df['Studio']
    del df['Directed By']
    del df['Rating']
    del df['Written By']
    del df['Release_Date']
    del df['Release_Day']
    del df['Release_Month']
    del df['Release_Type']
    #Create dependent variable
    df['difference'] = df['critic_score']-df['audience_score']
    #Split the train/test data
    df = df.fillna(0)
    cols = [c for c in df.columns if c not in ['movie_id','difference']]
    test_size = 0.4; seed = 123
    features = df[cols]
    labels = df['difference'].values
    df_train, df_test, label_train, label_test = cross_validation.train_test_split(df, labels, test_size=test_size, 
    random_state=seed)
    data_train = df_train[cols]
    data_test = df_test[cols]
    #Train Model
    clf = MLPClassifier(random_state=49)                                          
    clf.fit(data_train,label_train)
    pred=clf.predict(data_test)
    #Evaluation
    #MSE Score
    mse = mean_squared_error(label_test, pred)
    #R2
    r2 = r2_score(label_test, pred) 
    return mse, r2

start_time = time.clock()
print('Pragram SCENE1 started at: ' + str(strftime("%Y-%m-%d_%H-%M-%S")))
print(SCENE1(input("\nWhere is the dataset?\n")))
#"C:/Users/calvi/Documents/GitHub/RottenTomatoPredictingModel/The_Model/test.txt"
print("Program took: " + "--- %s seconds ---" % (time.clock() - start_time))



### SCENARIO 2 ###  (We have train and test sets separately)
def f(df_polarity_desc):
    if df_polarity_desc['sentiment'] > 0:
        val = "2"
    elif df_polarity_desc['sentiment'] == 0:
        val = "1"
    else:
        val = "0"
    return val
def MakeDF(FP):
    #Read Data
    df=pd.read_csv(FP, sep='\t')
    df=pd.DataFrame(data=df)
    #Time Processing
    df['Release_Date'] = ''
    df['Release_Month'] = ''
    df['Release_Day'] = ''
    df['Weekend_Release'] = ''
    df['Holiday_Release'] = ''
    df['Release_Type'] = ''
    #df['Difference'] = ''
    holidays = ['1-1', 
                #Memorial Day
                '5-25', '5-26', '5-27', '5-28', '5-29', '5-30', '5-31', 
                #Independence Day
                '7-4', 
                # Labor Day
                '9-1', '9-2', '9-3', '9-4', '9-5', '9-6', '9-7', 
                #Thanksgiving Day
                '11-22', '11-23', '11-24', '11-25', '11-26', '11-27', '11-28', 
                #Christmas Day
                '12-25']
    for i in range(0, len(df.index) - 1):
        try:
            df['Release_Date'][i] = timestring.Date(df['In Theaters'][i])
            df['Release_Month'][i] = timestring.Date(df['In Theaters'][i]).month
            df['Release_Day'][i]= calendar.day_name[timestring.Date(df['In Theaters'][i]).weekday]
            if str(df['Release_Day'][i]) == 'Friday' or str(df['Release_Day'][i]) == 'Saturday' or str(df['Release_Day'][i]) == 'Sunday':
                df['Weekend_Release'][i] = 1
            else:
                df['Weekend_Release'][i] = 0
            if str(timestring.Date(df['In Theaters'][i]).month) + '-' + str(timestring.Date(df['In Theaters'][i]).day) in holidays:
                df['Holiday_Release'][i] = 1
            else:
                df['Holiday_Release'][i] = 0
            temp = re.sub('[^a-zA-Z]',' ',df['In Theaters'][i])
            temp = re.sub(' +',' ',temp).strip()
            df['Release_Type'][i] = str(temp[4:])
        except:
            df['Weekend_Release'][i] = 0
            df['Holiday_Release'][i] = 0
            df['Release_Type'][i] = 'wide'
    #Synopsis Processing
    bloblist_desc = list()
    df_review_str = df['synopsis'].astype(str)
    for row in df_review_str:
        blob = TextBlob(row)
        bloblist_desc.append((row,blob.sentiment.polarity, blob.sentiment.subjectivity))
        df_polarity_desc = pd.DataFrame(bloblist_desc, columns = ['summary','sentiment','polarity'])
    df['synopsis_sc'] = df_polarity_desc.apply(f, axis=1)
    #Clean the rest data
    df['audience_score'] = df['audience_score'].replace('None', np.nan)
    df['audience_score'] = df['audience_score'].str.strip("%")
    df['audience_score'] = df['audience_score'].astype(float)
    df['critic_score'] = df['critic_score'].replace('None', np.nan)
    df['critic_score'] = df['critic_score'].str.strip("%")
    df['critic_score'] = df['critic_score'].astype(float)
    df['difference'] = df['critic_score'] - df['audience_score']
    del df['actor_links']
    del df['Box Office']
    df['Runtime']=df['Runtime'].replace('None', np.nan)
    df['Runtime']=df['Runtime'].str.strip("minutes")
    df['Runtime']=df['Runtime'].astype(float)
    df['Holiday_Release']=df['Holiday_Release'].replace('', np.nan)
    df['Holiday_Release']=df['Holiday_Release'].fillna(2.0)
    df['Holiday_Release']=df['Holiday_Release'].astype(float)
    df['Weekend_Release']=df['Holiday_Release'].replace('', np.nan)
    df['Weekend_Release']=df['Holiday_Release'].fillna(2.0)
    df['Weekend_Release']=df['Holiday_Release'].astype(float)
    #df['synopsis_sc']=df['synopsis_sc'].astype(int)
    #df['Release_Month']=df['Release_Month'].replace('', np.nan)
    #df['Release_Month']=df['Release_Month'].fillna(2.0)
    #df['Release_Month']=df['Release_Month'].astype(float)
    #get dummies to category variable
    dummies_Studio=pd.get_dummies(df['Studio'],prefix ='Studio')
    dummies_Wtitten=pd.get_dummies(df['Written By'],prefix ='Written By')
    dummies_Directed=pd.get_dummies(df['Directed By'],prefix='Directed By') 
    dummies_rating=pd.get_dummies(df['Rating'],prefix='Rating')
    dummies_genre=pd.get_dummies(df['Genre'],prefix='Genre')
    dummies_release_type = pd.get_dummies(df['Release_Type'],prefix='Release_Type')
    df=pd.concat([df,dummies_Studio,dummies_Wtitten,dummies_rating,dummies_genre,dummies_release_type],axis=1)
    del df['actor_names']
    del df['synopsis']
    del df['In Theaters']
    del df['Genre']
    del df['Studio']
    del df['Directed By']
    del df['Rating']
    del df['Written By']
    del df['Release_Date']
    del df['Release_Day']
    del df['Release_Month']
    del df['Release_Type']
    return df
def SCENE2(TRAIN,TEST):
    ### For Train Set ###
    data_train = MakeDF(TRAIN)
    data_train = data_train.fillna(0)
    cols_train = [c for c in data_train.columns if c not in ['movie_id','difference']]
    data_train = data_train[cols_train]
    labels_train = data_train['difference'].values
    ### For Test Set ###
    data_test = MakeDF(TEST)
    data_test = data_test.fillna(0)
    cols_test = [c for c in data_test.columns if c not in ['movie_id','difference']]
    data_test = data_test[cols_test]
    labels_test = data_test['difference'].values
    ### Train Model ###
    clf = MLPClassifier(random_state=49)
    #if we use pro dataset we don't need to fit                                         
    clf.fit(data_train, labels_train)
    pred = clf.predict(data_test)
    #Evaluation
    #MSE Score
    mse = mean_squared_error(labels_test, pred)  
    #R2
    r2 = r2_score(labels_test, pred)
    return mse, r2
"""
start_time = time.clock()
print('Pragram SCENE2 started at: ' + str(strftime("%Y-%m-%d_%H-%M-%S")))
print(SCENE2(input("\nWhere is your train?\n"), input("\nWhere is your test?\n")))
#"C:/Users/calvi/Documents/GitHub/RottenTomatoPredictingModel/The_Model/test.txt"
print("Program took: " + "--- %s seconds ---" % (time.clock() - start_time))
"""

### SCENARIO 3 ###  (We only have the test set)
