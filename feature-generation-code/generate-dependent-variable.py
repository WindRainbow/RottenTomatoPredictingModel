"""
@author: smit-mehta
"""

import pandas as pd


df=pd.read_csv('sample.txt', sep='\t')
df=pd.DataFrame(data=df)

df.head()

df['Difference'] = ''



for i in range(0, len(df.index) - 1):
    try:
        if df['critic_score'][i][:1] == '0':
            critic_score = 0
        else:
            critic_score = int(df['critic_score'][i][:2])
        
        if df['audience_score'][i][:1] == '0':
            audience_score = 0
        else:
            audience_score = int(df['audience_score'][i][:2])
        
            
        df['Difference'][i] = critic_score - audience_score
    except:
        df['Difference'][i] = None


#df.head(10)
