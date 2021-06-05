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
import random
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
	initial_ids = ['50kpGaPAhYJ3sGmk6vplg0','6DCZcSspjsKoFjzjrWoCdn','2XU0oxnq2qxCpomAAuJY8K','7BKLCZ1jbUBVqRi2FVlTVw','7qiZfU4dY1lWllzX7mPBI3','0pqnGHJpmpxLKifKRmU6WP','0e7ipj03S05BNilyu5bRzt','0VjIjW4GlUZAMYd2vXMi3b','2Fxmhks0bxGSBdJ92vM42m','0TK2YIli7K1leLovkQiNik','7KXjTSCq5nL1LoYtL7XAwS','698ItKASDavgwZ3WjaWjtz','0nbXyq5TXYPCO7pr3N8S4I','2b8fOow8UzyDFAE27YhOZM','6lanRgr6wXibZr8KgzXxBl','5vGLcdRuSbUhD8ScwsGSdA','2nLtzopw4rPReszdYBJU6h','2JzZzZUQj3Qff7wapcbKjc','32OlwWuMpZ6b0aN2RZOeMS','09CtPGIpYB4BrO8qb1RGsF','2iuZJX9X9P0GKaE93xcPjk','4sPmO7WMQUAf45kwMOtONw','1p80LdxRV74UKvL8gnD7ky','27tNWlhdAryQY04Gb2ZhUI','1Lim1Py7xBgbAkAys3AGAG','0JmiBCpWc1IAc0et7Xm7FL','2Cd9iWfcOpGDHLz6tVA3G4','15JINEqzVMv3SvJTAXAKED','0nrRP2bk19rLc0orkWPQk2','2ekn2ttSfGqwhhate0LSR0','6nTiIhLmQ3FWhvrGafw2zj','4kflIGfjdZJW4ot2ioixTB','6RtPijgfPKROxEzTHNRiDp','4pAl7FkDMNBsjykPXo91B3','1i1fxkWeaMmKEB4T7zqbzK','23L5CiUhw2jV1OIMwthR3S','7gvd8xj4QgPqbQSsn5pV7d','5kRPPEWFJIMox5qIkQkiz5','1dGr1c8CrMLDpV6mPbImSI','3ebXMykcMXOcLeJ9xZ17XH','4w8niZpiMy6qz1mntFA5uM','0F7FA14euOIX8KcbEturGH','6habFhsOp2NvshLv26DqMb','4uqh9bualXNHXXwO2wPorc','7yBbV2k2S2uhaQc24NF2xt','44AyOl4qVkzS48vBsbNXaC','7iN1s7xHE4ifF5povM6A48','20fBuVybkHgjF6vNhSMROD','6naxalmIoLFWR0siv8dnQQ','5xEM5hIgJ1jjgcEBfpkt2F','2TfSHkHiFO4gRztVIkggkE','2gZUPNdnz5Y45eiGxpHGSc','4tCtwWceOPWzenK2HAIJSb','6HZILIRieu8S0iqY8kIKhj','4IhKLu7Vk3j2TLmnFPl6To','04ZTP5KsCypmtCmQg5tH9R','6mFkJmJqdDVQ1REhVfGgd1','4JiEyzf0Md7KEFFGWDDdCr','4eHbdreAnSOrDDsFfc4Fpm','3ZffCQKLFLUvYM59XKLbVm','1gv4xPanImH17bKZ9rOveR','4JehYebiI9JE8sR8MisGVb','37sINbJZcFdHFAsVNsPq1i','6KBYefIoo7KydImq1uUQlL','2bjUEg4jBtKBlPdNrTAppI','11LmqTE2naFULdEP94AUBa','5ghIJDpPoe3CfHMGu71E6T','1N1ZpYUJc9fwrqk53FGgWv','4h7qcXBtaOJnmrapxoWxGf','1MtUq6Wp1eQ8PC6BbPCj8P','4ipnJyDU3Lq15qBAYNqlqK','3PYx9Wte3jwb48V0wArMOy','4Ub8UsjWuewQrPhuepfVpd','3S4px9f4lceWdKf0gWciFu','6JyuJFedEvPmdWQW0PkbGJ','5UsLjwBaTHBX4ektWIr4XX','6Rb0ptOEjBjPPQUlQtQGbL','6gj08XDlv9Duc2fPOxUmVD']
	initial_ids = random.sample(initial_ids,16)
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




