import pandas as pd
import os
import json

# location of the data source
data_dir = "../cornell movie-dialogs corpus"
movie_title_file = "movie_titles_metadata.txt"
movie_lines_file = "movie_lines.txt"
movie_conversations_file = "movie_conversations.txt"

# get logger
logger = logging.getLogger(__name__)

def parse_titles(filename):
    '''process the movie_title_file'''
    with open(filename, 'r', encoding='latin-1') as f:
        for line in f:
            line = line.strip("\n")
            yield line.split(" +++$+++ ")


def search_id(titles, movie_title):
    '''search for the movie id given a movie_title
    input:
        titles (pd.DataFrame): Title dataframe
        movie_title (str): a movie title 
    '''
    row = titles[titles["title"] == movie_title]
    return row["id"].values[0]


def parse_lines(filename, movie_index):
    '''process the movie_lines_file
    input:
        filename: filename of movie_lines_file
        movie_index (str[]): contains the indexes needed
    ''' 
    with open(filename, 'r', encoding='latin-1') as f:
        for line in f:
            line = line.strip("\n")
            content = line.split(" +++$+++ ")
            if content[2] in movie_index:
                yield content

def process_conversation(movie_conversations, movie_lines):
    '''
    assign conversation number to each line
    input:
        movie_conversations (pd.DataFrame): with column ["movie_id", "utterances", ...]
        movie_lines (pd.DataFrame): with column ["movie_id", "line_id", "text", ...]
    output:
        join_df (pd.DataFrame): with column ["movie_id", "line_id", "text", "conversation_id", ...]
    '''
    # load the utterances as list instead of strings
    movie_conversations['utterances'] = movie_conversations['utterances'].apply(lambda x: json.loads(x.replace("'", '"')))

    # expand the conversation_id
    movie_conversations["conversation_id"] = movie_conversations.index

    # expand the conversation
    utterances_match = movie_conversations.groupby(["movie_id", "conversation_id"])['utterances']\
        .apply(lambda x: x.explode()).reset_index()[["movie_id", "conversation_id", "utterances"]]\
        .rename(columns={"utterances": "line_id"})
    
    # join movie_lines and utterances_match on movie_id and line_id
    join_df = pd.merge(movie_lines, utterances_match,  how='left', 
                  left_on=['movie_id', 'line_id'], right_on = ['movie_id', 'line_id'])
    
    return join_df

def generate_csv(movie_ids, output_filename):
    '''
    generate the csv file for model training given a list of movie ids
    input:
        movie_ids (str[]): the movie ids needed
        output_filename (str): location to store the output file
    output:
        None
    '''
    movie_lines = pd.DataFrame(parse_lines(os.path.join(data_dir, movie_lines_file), 
                                       movie_index=movie_ids), 
                           columns=["line_id", "char_id", "movie_id", "char_name", "text"])

    movie_conversations = pd.DataFrame(parse_lines(os.path.join(data_dir, movie_conversations_file), 
                                               movie_index=movie_ids), 
                           columns=["char1", "char2", "movie_id", "utterances"])
    
    # join the utterances to conversations
    join_df = process_conversation(movie_conversations, movie_lines)

    # remove empty rows
    join_df['length'] = join_df.text.apply(lambda x: len(x))
    join_df = join_df[join_df['length'] != 0]

    # output to csv
    join_df.to_csv(output_filename)


if __name__ == "__main__":

    # load raw data
    try:
        logger.info("load raw data")
        # read the titles file
        titles = pd.DataFrame(parse_titles(os.path.join(data_dir, movie_title_file)), 
                        columns=["id", "title", "year", "rating", "votes", "genres"])
        titles['genres'] = titles['genres'].apply(lambda x: json.loads(x.replace("'", '"')))

        # statistics on movie genres
        genres_match = titles.groupby(["id"])['genres'].apply(lambda x: x.explode())\
            .reset_index()[["id", "genres"]]\
            .rename(columns={"id": "movie_id"})
        # print(genres_match.groupby('genres').count().sort_values(by='movie_id', ascending=False).head(10))
    except Exception as ex:
        logger.error(ex)
        raise


    # generate single-movie dataset
    try:
        logger.info("generate single-movie dataset")
        movie_id = search_id(titles, "annie hall")
        generate_csv([movie_id], "../data/annie_hall.csv")
    except Exception as ex:
        logger.error(ex)
        raise


    # generate single-category dataset
    try:
        logger.info("generate single-category dataset")
        animation_ids = genres_match[genres_match.genres=='animation']
        animation_ids = list(set(animation_ids.movie_id.values))
        generate_csv(animation_ids, "../data/animations.csv")
    except Exception as ex:
        logger.error(ex)
        raise

    # generate full dataset
    try:
        logger.info("generate full dataset")
        all_ids = list(set(titles.id.values))
        generate_csv(all_ids, "../data/all.csv")
    except Exception as ex:
        logger.error(ex)
        raise


    
    

