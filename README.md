# RecoTrax Music Reccomendation Engine

![Project Image](https://i.imgur.com/OnzkYRM.png)

## [Click here to open RecoTrax App](https://recotrax.herokuapp.com/)

> Site may take some time to load. Please be patient :)

---

### Table of Contents

- [Description](#des436cription)
- [How To Use](#how-to-use)
- [Working of project](#how-it-works)
- [Detailed Workflow with Code](#how-it-works)
- [References](#references)
- [Author Info](#author-info)

---

## Description

Recotrax is a content based reccomendation system made with python. 

It uses the spotify dataset to screen through tens of thousands of songs and provide you with the songs you like. Its reccommendations will be based on the songs and music artists you select. 

### Technologies Used

- Python
- Flask
- Heroku
- Ajax

### Python Libraries Used

* Basic (Numpy, pandas, json, sys)
* pyarrow (make light-weight feather file)
* sklearn 
    - TfidfVectorizer
    - cosine_similarity
    - MinMaxScaler
* flask

[Back To The Top](#read-me-template)

---

## How To Use

### What to download?

No installation or download required. It is a web app supported on any generally used web browser

### What to do?

> Pictures are given in accordance to desktop users. Mobile users could easily follow along with the same steps.

When the site loads, you''ll see a page like this.

![Project Image](https://i.imgur.com/22ngBXe.jpg)

You will be served with a random list of 16 very popular songs

If you like any song simply click on it.

![Project Image](https://i.imgur.com/Esg8ezs.jpeg)

Your selected song will come up on the upper bar and you will be provided more songs which are similar to your selected song.

The parameters used for finding similarity between songs is discussed well in [How it works] section.

![Project Image](https://i.imgur.com/2lrQufa.jpg)

More the number of songs you select, better will be the final prediction.

When you have selected enough songs, click the button on the bottom right corner.

![Project Image](https://i.imgur.com/yPol8rG.jpg)

The final result will give you the music artists you should listen to.

The result artists is divided into 2 categories. 

- You have listened to few of their songs. You should check out more of their works
- Artists you have never listened to, whom you should definitely check out

![Project Image](https://i.imgur.com/zXwSrg6.jpg)
![Project Image](https://i.imgur.com/lbI1dSh.jpg)

Song reccomendations are right on your screen. Any song which is reccommended to you and you didn't click are the ones which carry a similar trait to one or multiple songs you've chosen.

---

## Working of Project

### Feature Engineering

After basic feature engineering like removing duplicates and one hot encoding of a few columns of the spotify dataset, we build a complete feature set of all songs with each song having encoded values for genre, popularity and year of release.

TFIDF is used for encoding the genre. You can read about it in [References]. Using a table is created of shape (170653, 3071).

After a few manipulations with genre combinations and filtering out the rows with very low popularity, the shape of feature set is brought down to (688, 163). 

Now, we put the spotify dataset and the feature set into a feather file (CSV file has high load time and memory consumption, thus not used)

If you want to check the feature engineering part. Check the `1Featured.ipynb` file in this repo.

We are good to go to the reccommendation part.

### Creating Reccommendations

We use 3 functions to carry out the entire creating reccommendation process

#### First, we need to convert the selected songs into a dataset. 

#### Here, `id_list` refers to the ids of songs chosen by user. `spotify_df` is the entire spotify dataset.
```python
def createPlaylist(id_list, spotify_df):

    idDF = pd.DataFrame({'id':[],'name':[],'artists':[],'url':[],'date_added':[]})
    for id in id_list:
        artistName = spotify_df[spotify_df['id'] == id]['artists_upd_v1'].iloc[0]
        songName = spotify_df[spotify_df['id'] == id]['name'].values[0]
        imageId = spotify_df[spotify_df['id'] == id]['url'].values[0]
        newRow = {'id':id,'name':songName,'artists':artistName,'url':imageId,
        'date_added':pd.to_datetime('2021-04-27 08:09:52+00:00')}
        idDF = idDF.append(newRow,ignore_index=True)

    return idDF
```
---
#### Next, we create a cosine similarity vector with the help of the playlist dataset `playlist_df`. Weight factor is kept `1.09`.

```python
def generate_playlist_feature(complete_feature_set, playlist_df, weight_factor):

    complete_feature_set_playlist = complete_feature_set[complete_feature_set['id'].isin(playlist_df['id'].values)]#.drop('id', axis = 1).mean(axis =0)
    complete_feature_set_playlist = complete_feature_set_playlist.merge(playlist_df[['id','date_added']], on = 'id', how = 'inner')
    complete_feature_set_nonplaylist = complete_feature_set[~complete_feature_set['id'].isin(playlist_df['id'].values)]#.drop('id', axis = 1)
    
    playlist_feature_set = complete_feature_set_playlist.sort_values('date_added',ascending=False)

    most_recent_date = playlist_feature_set.iloc[0,-1]
    
    for ix, row in playlist_feature_set.iterrows():
        playlist_feature_set.loc[ix,'months_from_recent'] = int((most_recent_date.to_pydatetime() - row.iloc[-1].to_pydatetime()).days / 30)
        
    playlist_feature_set['weight'] = playlist_feature_set['months_from_recent'].apply(lambda x: weight_factor ** (-x))
    
    playlist_feature_set_weighted = playlist_feature_set.copy()
    #print(playlist_feature_set_weighted.iloc[:,:-4].columns)
    playlist_feature_set_weighted.update(playlist_feature_set_weighted.iloc[:,:-4].mul(playlist_feature_set_weighted.weight,0))
    playlist_feature_set_weighted_final = playlist_feature_set_weighted.iloc[:, :-4]
    #playlist_feature_set_weighted_final['id'] = playlist_feature_set['id']
    
    return playlist_feature_set_weighted_final.sum(axis = 0), complete_feature_set_nonplaylist

```
---
#### Now, the real deal is this function which uses the cosine similarity vector to find recommendations and returns the top 10 recommendations.

#### Also, I made a small function `remove_same_tracks()` which removes tracks which are already recommended in the past.

```python
def remove_same_tracks(recos, chosen):
    l = []
    for i in range(50):
        if recos.iloc[i]['id'] in chosen:
            l.append(recos.iloc[i].name)

    recos.drop(l, inplace=True)
    return recos


def generate_playlist_recos(spotify_df, features, feature_set, chosen):

    recos = spotify_df[spotify_df['id'].isin(feature_set['id'].values)]
    recos['sim'] = cosine_similarity(feature_set.drop('id', axis = 1).values, features.values.reshape(1, -1))[:,0]
    recos_top = recos.sort_values('sim',ascending = False).head(50)

    recos_top = remove_same_tracks(recos_top, chosen)
    recos_top = recos_top.drop_duplicates("artists").head(10)
    recos_top['artists'] = recos_top['artists'].apply(ast.literal_eval)
    recos_top['url'] = recos_top['id'].apply(lambda x: spotify_df[spotify_df['id'] == x]['url'].values[0])

    recos_top = recos_top[['id','name','artists','url']]
    
    return recos_top
```

### Building the Flask app

I wouldn't be showing the redundant portion which is same for building any flask app.

If you want to check the full flask app code, check `test.py` file in my github repo.

#### First, the feature engineered dataframe (spotify dataset and complete feature set dataset) is loaded

```python
app = Flask(__name__)
spotify_df = pd.read_feather('spotify_df_low.feather')
complete_feature_set = pd.read_feather('cfs_final.feather')
default_date = pd.to_datetime('2021-04-27 08:09:52+00:00')
recos = pd.DataFrame()
```
---
#### When any song card is clicked, it is routed to the `/show` page

```python
@app.route('/show',methods=['POST'])
def show():
	global recos
	id_list = []
	id_list.append(request.form['id'])
	chosen = request.form['chosen'].split(",")

	selected = createPlaylist(id_list,spotify_df,2)
	feature_vector, feature_set = generate_playlist_feature(complete_feature_set, selected, 1.09)
	new_recos = generate_playlist_recos(spotify_df, feature_vector, feature_set, chosen)

	# top song added to new_recos
	recos = new_recos

	id_list = list(recos['id'])
	names = list(recos['name'])
	artists = list(recos['artists'])
	url_list = list(recos['url'])
	
	name_list = ""
	for i in names:
		name_list += i+"$@"
	artist_list = ""
	for i in artists:
		artist_list += ",".join(i)+"$@"


	return jsonify({'id':id_list,'name':name_list,'artist':artist_list,'url':url_list})
```
---
#### When a song is clicked, we dont want the page to reload. Not only will that destroy the user experience, but it will take exponentially more time if we had to render every image and the entire data of page every time user clicks a song card.

#### The solution is switching to _Ajax_ which will submit our data without reloading page.

```js
$("#main").on('submit', function(event){
	$.ajax({
		url: "/show",
		type: "post",
		data: {
			// These are params sent to show route
			id: $("#id").val(),
			chosen: String(chosen_ids)
		}
	})
	.done(function(data){
		id_list = String(data.id).split(',')
		name_list = String(data.name).split('$@')
		artist_list = String(data.artist).split('$@')
		url_list = String(data.url).split(',')
		n = id_list.length
		for(i=0;i<n;i++){
			cardString = `
				<div class="card">
					<span style="display:none;">`+id_list[i]+`</span>
					<img src=`+url_list[i]+`>
					<h3>`+name_list[i]+`</h3>
					<h4>
					`+artist_list[i].split(',').join('<br>')+`
					</h4>
				</div>
			`
			$("#cards").append(cardString)
		}
		chosen_ids = (chosen_ids + "," + id_list).split(",")
	})
	event.preventDefault();
});
```
---
#### Here, `data` is the json object sent by flask. All the individual data is first extracted from the object.

#### `cardString` creates an html string for the song card where all the information we got is binded and appended onto the html page.

If you want to check the full js code of ajax, check `static/script.js` file in my github repo.

---


## References

This project is inspired from the code of [**Madhav Thaker**](https://github.com/madhavthaker/spotify-recommendation-system). His [Youtube Channel](https://www.youtube.com/channel/UC0-S_HnWTDFaXgTbYSL46Ug) is also extremely educational.

Big Thanks to his high quality code. Please take your time to check his repo or videos if you want.

[Click here](https://medium.com/analytics-vidhya/understanding-tf-idf-in-nlp-4a28eebdee6a) to know about TFIDF and why is it appropriate to use it 

[Click here](https://www.geeksforgeeks.org/cosine-similarity/) to know about cosine similarity

[Click here](https://www.youtube.com/watch?v=mrExsjcvF4o&t=882s) to know how to deploy flask app to heroku

---

## Author Info

I am a third year student pursuing B-Tech Degree.

I am a competitive coder and a Data Science enthusiast with a few application based projects.

I recently wrote a blog on [Why Data Science is bad for your health](https://www.analyticsvidhya.com/blog/2021/03/data-science-is-not-good-for-health-a-unique-look-at-data-science/). Give it a read if you like.

You can connect with me at [Linkedin](https://www.linkedin.com/in/soumyadeep-auddy-270a89141/)