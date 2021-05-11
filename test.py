import pandas as pd
import numpy as np
import json
import re 
import sys
import itertools
import pyarrow
import ast
from flask import Flask,render_template,request,Markup,jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
# from spotipy.oauth2 import SpotifyOAuth
# import spotipy.util as util
import warnings
warnings.filterwarnings("ignore")

from allFunctions import *

# FLASK PART


app = Flask(__name__)
spotify_df = pd.read_feather('spotify_df_low.feather')
complete_feature_set = pd.read_feather('cfs_final.feather')
default_date = pd.to_datetime('2021-04-27 08:09:52+00:00')
recos = pd.DataFrame()

@app.route('/')
@app.route('/home')
def home():
	global recos
	initial_ids = ['50kpGaPAhYJ3sGmk6vplg0','6DCZcSspjsKoFjzjrWoCdn','2XU0oxnq2qxCpomAAuJY8K','7BKLCZ1jbUBVqRi2FVlTVw','7qiZfU4dY1lWllzX7mPBI3','0pqnGHJpmpxLKifKRmU6WP','0e7ipj03S05BNilyu5bRzt','0VjIjW4GlUZAMYd2vXMi3b','2Fxmhks0bxGSBdJ92vM42m','0TK2YIli7K1leLovkQiNik','7KXjTSCq5nL1LoYtL7XAwS','698ItKASDavgwZ3WjaWjtz','0nbXyq5TXYPCO7pr3N8S4I','2b8fOow8UzyDFAE27YhOZM','6lanRgr6wXibZr8KgzXxBl','5vGLcdRuSbUhD8ScwsGSdA','2nLtzopw4rPReszdYBJU6h']
	recos = createPlaylist(initial_ids,spotify_df,1)
	return render_template('test.html', recos=recos)

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


if(__name__ == '__main__'):
	app.run(debug = True)




