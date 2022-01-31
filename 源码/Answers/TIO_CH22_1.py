# TIO_CH22_1.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Answer to Try It Out, Question 1, Chapter 22

# Program to create silly sentences

import random
noun_file = open("nouns.txt", 'r')
nouns = noun_file.readline()
noun_list = nouns.split(',')

adj_file = open("adjectives.txt", 'r')
adjectives = adj_file.readline()
adj_list = adjectives.split(',')

verb_file = open("verbs.txt", 'r')
verbs = verb_file.readline()
verb_list = verbs.split(',')

adverb_file = open("adverbs.txt", 'r')
adverbs = adverb_file.readline()
adverb_list = adverbs.split(',')

def print_sentences():
    noun = random.choice(noun_list)
    adj = random.choice(adj_list)
    verb = random.choice(verb_list)
    adverb = random.choice(adverb_list)
    print("The", adj, noun, verb, adverb + '.', end='')

if __name__=="__main__":
    while True:
        print_sentences()
        input()