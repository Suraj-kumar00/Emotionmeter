import re
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 

from flask import Flask, render_template , request

# Remaining code remains unchanged...

app = Flask(__name__)

# Define the folder where Flask should look for templates
# This line tells Flask to look for HTML templates in the 'templates' folder
app.static_folder = 'static'


consumer_key      = ""
consumer_secret   = ""
access_token      = ""
access_token_secret = ""

try: 
    auth = OAuthHandler(consumer_key, consumer_secret)  
    auth.set_access_token(access_token, access_token_secret) 
    api = tweepy.API(auth)
except: 
    print("Error: Authentication Failed")
    api = None  # Set api to None if authentication fails

# Define your functions here
def clean_tweet(tweet): 
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(https?://\S+)", " ", tweet).split())

def get_tweet_sentiment(tweet): 
    analysis = TextBlob(clean_tweet(tweet)) 
    if analysis.sentiment.polarity > 0:
        return "positive"
    elif analysis.sentiment.polarity == 0:
        return "neutral"
    else:
        return "negative"

def get_tweets(api, query, count=5): 
    count = int(count)
    tweets = [] 
    try: 
        fetched_tweets = tweepy.Cursor(api.search_tweets, q=query, lang='en', tweet_mode='extended').items(count)
        for tweet in fetched_tweets: 
            parsed_tweet = {} 
            if 'retweeted_status' in dir(tweet):
                parsed_tweet['text'] = tweet.retweeted_status.full_text
            else:
                parsed_tweet['text'] = tweet.full_text
            parsed_tweet['sentiment'] = get_tweet_sentiment(parsed_tweet['text']) 
            if tweet.retweet_count > 0: 
                if parsed_tweet not in tweets: 
                    tweets.append(parsed_tweet) 
            else: 
                tweets.append(parsed_tweet) 
        return tweets 
    except tweepy.TweepyException as e: 
        print("Error : " + str(e)) 

# Define your routes here

@app.route('/')
def home():
    # Render the 'index.html' template located in the 'templates' folder
    return render_template('index.html')

@app.route("/predict", methods=['POST','GET'])
def pred():
    if request.method=='POST':
        query=request.form['query']
        count=request.form['num']
        if api is not None:  # Check if api is defined
            try:
                fetched_tweets = get_tweets(api, query, count) 
                return render_template('result.html', result=fetched_tweets)
            except Exception as e:
                return "Error: " + str(e)
        else:
            return "Error: API not initialized properly. Please check your API credentials."

@app.route("/predict1", methods=['POST','GET'])
def pred1():
    if request.method=='POST':
        text = request.form['txt']
        blob = TextBlob(text)
        if blob.sentiment.polarity > 0:
            text_sentiment = "positive"
        elif blob.sentiment.polarity == 0:
            text_sentiment = "neutral"
        else:
            text_sentiment = "negative"
        return render_template('result1.html', msg=text, result=text_sentiment)



# This is main function which will run the Flask app
if __name__ == '__main__':
    app.debug=True
    app.run(host='localhost', port=8000)
