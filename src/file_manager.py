import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from nltk.tokenize import word_tokenize
from pathlib import Path

data_folder = Path("../data")
file_to_open = data_folder / "merged_dataframe.csv"
initial_load = pd.read_csv(file_to_open,sep="|")
cities = initial_load.CITY.unique().tolist()

def all_regions(data,city):
    city_data = data[data["CITY"] == city] 
    region_list = city_data.REGION.unique().tolist()
    return region_list

# Pre processing
initial_load.dropna(inplace=True)

def filtered_data(city,region=None,cusine=None):
    city_data = initial_load[initial_load["CITY"] == city] 
    if(region != None):
        city_data = initial_load[initial_load["REGION"] == region] 
    city_data = city_data[city_data['RATING'] !="NEW"]
    city_data = city_data[city_data['RATING'] !="-"]
    city_data["RATING"] = city_data["RATING"].astype("float")
    city_data["VOTES"] = city_data["VOTES"].astype("float")
    return city_data

# Simple recommender calculated weight function
def weighted_rating(x, m, C):
    v = x['VOTES']
    R = x['RATING']
    # Calculating the score
    return (v/(v+m) * R) + (m/(m+v) * C)

# Simple recommender
def simple_recommender(fil_data):
    cols = ["NAME","CUSINE_CATEGORY","REGION","RATING","VOTES"]
    fil_data = fil_data[cols]
    # print(fil_data.head())
    C = fil_data["RATING"].mean() # mean
    m = fil_data['VOTES'].quantile(0.85) # minimum votes required # 85 percentile
    q_restaurant = fil_data.copy().loc[fil_data['VOTES'] >= m]
    q_restaurant['score'] = q_restaurant.apply(weighted_rating,args=[m,C], axis=1)
    q_restaurant_sorted = q_restaurant.sort_values('score',ascending=False)
    return q_restaurant_sorted


# Content based recommender
data_sample=[]
def cont_recommender(fil_data,location,title):   
    
    global data_sample       
    global cosine_sim
    global sim_scores
    global tfidf_matrix
    global corpus_index
    global feature
    global rest_indices
    global idx
    
    # When location comes from function ,our new data consist only location dataset
    data_sample = fil_data.loc[fil_data['REGION'] == location]  
    
    # index will be reset for cosine similarty index because Cosine similarty index has to be same value with result of tf-idf vectorize
    data_sample.reset_index(level=0, inplace=True) 
    
    #Feature Extraction
    data_sample['Split']="X"
    for i in range(0,data_sample.index[-1]):
        split_data=re.split(r'[,]', data_sample['CUSINE_CATEGORY'][i])
        for k,l in enumerate(split_data):
            split_data[k]=(split_data[k].replace(" ", ""))
        split_data=' '.join(split_data[:])
        data_sample['Split'].iloc[i]=split_data
        
    #TF-IDF vectorizer
    #Extracting Stopword
    tfidf = TfidfVectorizer(stop_words='english')
#Replace NaN for empty string
    data_sample['Split'] = data_sample['Split'].fillna('')
#Applying TF-IDF Vectorizer
    tfidf_matrix = tfidf.fit_transform(data_sample['Split'])
    tfidf_matrix.shape
    
    # Using for see Cosine Similarty scores
    feature= tfidf.get_feature_names()
#Cosine Similarity
    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix) 
    
    # Column names are using for index
    corpus_index=[n for n in data_sample['Split']]
       
    #Construct a reverse map of indices    
    indices = pd.Series(data_sample.index, index=data_sample['NAME']).drop_duplicates() 
    
    #index of the restaurant matchs the cuisines
    idx = indices[title]
#Aggregate rating added with cosine score in sim_score list.
    sim_scores=[]
    for i,j in enumerate(cosine_sim[idx]):
        k=data_sample['RATING'].iloc[i]
        if j != 0 :
            sim_scores.append((i,j,k))
            
    #Sort the restaurant names based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: (x[1],x[2]) , reverse=True)
# 10 similar cuisines
    sim_scores = sim_scores[0:10]
    rest_indices = [i[0] for i in sim_scores] 
  
    data_x =data_sample[['NAME','CUSINE_CATEGORY','RATING']].iloc[rest_indices]
    
    data_x['Cosine Similarity']=0
    for i,j in enumerate(sim_scores):
        data_x['Cosine Similarity'].iloc[i]=round(sim_scores[i][1],2)
   
    return data_x


data = filtered_data("Delhi NCR")

# Simple Call
# qualified = simple_recommender(data)
# print(qualified.head())

# Cont Call
# cont_qualified = cont_recommender(data,'Indirapuram','The Daily Bread')
# print(cont_qualified)

# @filtered_data(city,region)
def get_cusine_counts(data):
    vec = CountVectorizer(tokenizer=lambda x: [i.strip() for i in x.split(',')], lowercase=False)
    counts = vec.fit_transform(data['CUSINE_CATEGORY']) # actual count, output will be a sparse matrix
    computed_cat_count = dict(zip(vec.get_feature_names(), counts.sum(axis=0).tolist()[0]))
    c_df = pd.DataFrame(list(computed_cat_count.items()), columns=['Cusine', 'Count'])
    return c_df

# print(get_cusine_counts(data).head(10))