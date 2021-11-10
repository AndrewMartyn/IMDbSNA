from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import re
import argparse

# command line args
parser = argparse.ArgumentParser()
parser.add_argument('--no-export', dest='export', default=True, action='store_false')
parser.add_argument('--nodes_o', help='Optional command line argument to change the nodes output file name', default='nodes.csv')
parser.add_argument('--edges_o', help='Optional command line argument to change the edges output file name', default='edges.csv')
parser.add_argument('--n', help='Optional command line argument to change the number of movies to include ranging from 0-250', default=250)
args = parser.parse_args()

# setup beautifulsoup
url = 'http://www.imdb.com/chart/top'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

# grab movies, crew, and ratings data
movies = soup.select('td.titleColumn')
crew = [a.attrs.get('title') for a in soup.select('td.titleColumn a')]
ratings = [b.attrs.get('data-value') for b in soup.select('td.posterColumn span[name=ir]')] 

# create dataframe
nodes_df = pd.DataFrame(columns=['Id', 'Name', 'Year', 'Director', 'Actors', 'Rating'])

# parse data and populate nodes_df
for index in range(0, int(args.n)):
    movie_string = movies[index].get_text()
    movie = (' '.join(movie_string.split()).replace('.', ''))
    movie_title = movie[len(str(index))+1:-7]
    year = re.search('\((.*?)\)', movie_string).group(1)
    place = movie[:len(str(index))-(len(movie))]
    director, actors_string = crew[index].split(' (dir.), ')
    actors_list = actors_string.split(', ')
    
    # append data to df
    nodes_df = nodes_df.append({'Id': place,
                                'Name': movie_title,
                                'Year': year,
                                'Director': director,
                                'Actors': actors_list,
                                'Rating': ratings[index]}, ignore_index=True)

# export nodes
if(args.export):            
    nodes_df.to_csv(args.nodes_o, index=False)
    print("Stored nodes as " + '\'' + args.nodes_o + '\'')


# create dataframe
edges_df = pd.DataFrame(columns=['Source', 'Target', 'Type', 'hasCommonActor', 'hasCommonDirector', 'hasCommonReleaseYear'])
for i in range(0,len(nodes_df)):
    for j in range(i+1,len(nodes_df)):    
        hasCommonActor = bool(set(nodes_df.values[i][4]).intersection(nodes_df.values[j][4]))
        hasCommonDirector = (nodes_df.values[i][3] == nodes_df.values[j][3])
        hasCommonReleaseYear = (nodes_df.values[i][2] == nodes_df.values[j][2])
        
        if(not hasCommonActor and not hasCommonDirector and not hasCommonReleaseYear):
            continue
        
        edges_df = edges_df.append({'Source': i+1,
                                    'Target': j+1,
                                    'Type': 'Undirected',
                                    'hasCommonActor': hasCommonActor,
                                    'hasCommonDirector': hasCommonDirector,
                                    'hasCommonReleaseYear': hasCommonReleaseYear}, ignore_index=True)

# export nodes
if(args.export):            
    edges_df.to_csv(args.edges_o, index=False)
    print("Stored edges as " + '\'' + args.edges_o + '\'')