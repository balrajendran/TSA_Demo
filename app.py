#Description : This is a sentiment analysis program that parses the tweets fetched from Twitter Using Python

#Import the libraries
from flask import Flask, render_template, request, redirect, url_for
import os
import shutil
import tweepy
from textblob import TextBlob
from wordcloud import WordCloud
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import json
from pandas.io.json import json_normalize
plt.style.use('fivethirtyeight')

# %matplotlib inline

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        global search_words

        #Create authentication Object
        authenticate = tweepy.OAuthHandler('OkFRQDJyYH6u7CylN1LUMpdEe','KJO6ycr1PQ0h575BRe2rEQt9bLtqGdADW67hg7ReKEACRzb9mt')
        #Set the access token and access token secret
        authenticate.set_access_token('1334438233069895681-krIJc2LigPqDLgozO5f7Ky6L7UF9ZT','wMCwn3TGGmgtSfYQ9LgpJUS2rnRZ0fwoVGUZQopvSLYOG')
        
        #create the API object while passing in the auth information
        api = tweepy.API(authenticate, wait_on_rate_limit = True)
        
        # Define the search term and the date_since date as variables
        search_words = request.form['searchText']
        date_since = "2020-11-16"
        new_search = search_words + " -filter:retweets"

        # Collect tweets - Twitter API Call
        tweets = list(tweepy.Cursor(api.search, q=new_search, lang="en", since=date_since).items(50))

        # Call the function and unload each _json into tweets
        tweets_list = [jsonify_tweepy(tweet) for tweet in tweets]

        # Convert followers_list to a pandas dataframe
        df = json_normalize(tweets_list)
        df = df.filter(['text'])
        df.columns=['Tweets']

        # df = pd.DataFrame()
        # # append columns to an empty DataFrame 
        # df['Tweets'] = ['Believe it or not, each year there are about 80,000 wildfires in the UnitedStates . Most of these are very small',
        #                 'botanists assess how much wildfires damaged California’s plants',
        #                 'Researchers Find Hot And Dry Wildfires On The Rise - Wyoming Public Media  Heatwave Wildfires',
        #                 'Close to Home: How wild animals cope with wildfire - Santa Rosa Press Democrat  Heatwave Wildfires',
        #                 'Grand County Craft Breweries Provide Wildfire Relief with Collaboration Brew',
        #                 'Make It Better Media Group/ is matching donations to the CDP California Wildfires Fund up to $25K th',
        #                 'Good night, sweet prince, and flights of angels sing thee to thy rest (The 2020 Oregon Wildfires 15)',
        #                 'Another Australian wildfire ignites—in one of its most unique ecosystems - National Geographic  Heatwave Wildfires',
        #                 'Excited to work w/ the new Wildfire Caucus, because when it comes to addressing wildfires &amp;',
        #                 'Free slideshow. Why Prepare Now? Because It\'s Too Late After A Disaster Strikes    via']

        # Clean the tweets
        df['Tweets'] = df['Tweets'].apply(cleanTxt)

        # Create two new columns 'Subjectivity' & 'Polarity'
        df['Subjectivity'] = df['Tweets'].apply(getSubjectivity)
        df['Polarity'] = df['Tweets'].apply(getPolarity)
        print(df['Subjectivity'][0])

        df['Analysis'] = df['Polarity'].apply(getAnalysis)

        # word cloud visualization
        allWords = ' '.join([twts for twts in df['Tweets']])
        wordCloud = WordCloud(width=500, height=300, random_state=21, max_font_size=110).generate(allWords)
        wordCloud.to_file('C:/Users/Balra/Desktop/TSA_Demo/img/wordCloud.png')

        # Plotting
        plt.figure(figsize=(8,6))
        for i in range(0, df.shape[0]):
            plt.scatter(df["Polarity"][i], df["Subjectivity"][i], color='Blue')
            # plt.scatter(x,y,color)
        plt.title('Sentiment Analysis') 
        plt.xlabel('Polarity')
        plt.ylabel('Subjectivity')
        pltFig = plt.gcf()
        pltFig.savefig('C:/Users/Balra/Desktop/TSA_Demo/img/plot.png')
        pltFig.clear()
        plt.close(pltFig)

        # Plotting and visualizing the counts
        plt.title('Sentiment Analysis')
        plt.xlabel('Sentiment')
        plt.ylabel('Counts')
        df['Analysis'].value_counts().plot(kind = 'bar')
        pltFig = plt.gcf()
        pltFig.savefig('C:/Users/Balra/Desktop/TSA_Demo/img/plotBar.png')
        pltFig.clear()
        plt.close(pltFig)
    

        df['Analysis'].value_counts().plot(kind='pie', autopct='%1.0f%%', colors=["yellow", "green", "red"])
        pltFig = plt.gcf()
        pltFig.savefig('C:/Users/Balra/Desktop/TSA_Demo/img/plotPie.png')
        pltFig.clear()
        return redirect(url_for('analysis'))
    return render_template("search.html")

# function to convert _json to JSON
def jsonify_tweepy(tweepy_object):
    json_str = json.dumps(tweepy_object._json)
    return json.loads(json_str)

# Create a function to clean the tweets
def cleanTxt(text):
    text = re.sub('@[A-Za-z0–9]+', '', text) #Removing @mentions
    text = re.sub('#', '', text) # Removing '#' hash tag
    text = re.sub('RT[\s]+', '', text) # Removing RT
    text = re.sub('https?:\/\/\S+', '', text) # Removing hyperlink
    return text

# Create a function to get the subjectivity
def getSubjectivity(text):
    return TextBlob(text).sentiment.subjectivity

# Create a function to get the polarity
def getPolarity(text):
    return  TextBlob(text).sentiment.polarity

# Create a function to compute negative (-1), neutral (0) and positive (+1) analysis
def getAnalysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'

@app.route('/analysis')
def analysis():
    print(search_words)
    return render_template('analysis.html', input=search_words)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)
