# Essential libraries
import os
import pandas as pd
import numpy as np

# Regular expression import
import re

# Unicode library
import unicodedata

# Natural Language Toolkit (NLTK) library/modules
import nltk
from nltk.tokenize.toktok import ToktokTokenizer
from nltk.corpus import stopwords

# Ensure necessary NLTK resources are downloaded
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('omw-1.4')

def basic_clean(string):
    """
    This function takes in a string and
    returns the string normalized and cleaned of
    numbers, punctuation, and converts to lowercase.
    """
    # Normalize the unicode string
    string = unicodedata.normalize('NFKD', string)\
             .encode('ascii', 'ignore')\
             .decode('utf-8', 'ignore')
    
    # Remove punctuation and numbers
    string = re.sub(r'[^\w\s]', '', string)  # Remove punctuation
    string = re.sub(r'\d+', '', string)  # Remove numbers
    
    # Convert to lowercase
    string = string.lower()
    
    return string

def tokenize(string):
    """
    This function takes in a string and
    returns a tokenized string.
    """
    # Create tokenizer.
    tokenizer = ToktokTokenizer()

    # Use tokenizer
    string = tokenizer.tokenize(string, return_str=True)

    return string

def stem(string):
    """
    This function takes in a string and
    returns a string with words stemmed.
    """
    # Create porter stemmer.
    ps = nltk.porter.PorterStemmer()

    # Use the stemmer to stem each word in the list of words we created by using split.
    stems = [ps.stem(word) for word in string.split()]

    # Join our lists of words into a string again and assign to a variable.
    string = ' '.join(stems)

    return string

def lemmatize(string):
    """
    This function takes in a string and
    returns a string with words lemmatized.
    """
    # Create the lemmatizer.
    wnl = nltk.stem.WordNetLemmatizer()

    # Use the lemmatizer on each word in the list of words we created by using split.
    lemmas = [wnl.lemmatize(word) for word in string.split()]

    # Join our list of words into a string again and assign to a variable.
    string = ' '.join(lemmas)

    return string

def remove_stopwords(string, extra_words=[], exclude_words=[]):
    """
    This function takes in a string, optional extra_words and exclude_words parameters
    with default empty lists and returns a string.
    """
    # Create stopword_list.
    stopword_list = stopwords.words('english')

    # Remove 'exclude_words' from stopword_list to keep these in my text.
    stopword_list = set(stopword_list) - set(exclude_words)

    # Add in 'extra_words' to stopword_list.
    stopword_list = stopword_list.union(set(extra_words))

    # Split words in string.
    words = string.split()

    # Create a list of words from my string with stopwords removed and assign to variable.
    filtered_words = [word for word in words if word not in stopword_list]

    # Join words in the list back into strings and assign to a variable.
    string_without_stopwords = ' '.join(filtered_words)

    return string_without_stopwords

def clean(text):
    """
    This function combines the above steps and adds extra stop words to clean text.
    """
    return remove_stopwords(lemmatize(basic_clean(text)))

