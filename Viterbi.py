#!/usr/bin/python3
from math import log
import re
wordtag = {}
ngram = {}

with open("ner_rare2.counts") as f:
    for line in f:
        line = line.strip()
        try:
            splitted_line = line.split(' ')
            count = splitted_line[0]
            _type = splitted_line[1]
            if _type == 'WORDTAG':
                tag = splitted_line[2]
                word = splitted_line[3]
                if word not in wordtag:
                    wordtag[word] = {}
                wordtag[word][tag] = int(count)
            else:
                tag = tuple(splitted_line[2:])
                ngram[tag] = int(count)
        except:
            print(line)

def emission_proba(x, y):
    return log(wordtag[x][y]/ngram[(y,)])

def trigram_proba(yi_2, yi_1, yi):
    if (yi_2, yi_1, yi) in ngram and (yi_2, yi_1) in ngram:
        return log(0.000000001 + ngram[(yi_2, yi_1, yi)]/ngram[(yi_2, yi_1)])
    else:
        return log(0.000000001)

def categorize_lowfreq(word):
    if not re.search(r'\w',word):
        return '<PUNC>'
    elif re.match(r'[A-Z]\.[A-Z]',word):
        return '<ABBREV>'
    elif re.match(r'[A-Z][A-Z]',word):
        return '<ALLCAPS>'
    elif re.match(r'[A-Z][a-z]',word):
        return '<INITCAP>'
    elif re.match(r'[a-z][a-z]',word):
        return '<LOWERCASE>'
    elif re.search(r'\d',word):
        return '<NUM>'
    else:
        return '<OTHER>'
    
def viterbi(sent):
    
    
    """Return the best path, given an HMM model and a sequence of observations"""
    # A - initialise stuff
    V = {}
    V[0,'*','*'] = 1
    path = {}
    path['*','*'] = []
    # run

    def possible_tags(k):
        if k < 1:
            return set(['*'])
        else:
            if sent[k-1] in wordtag:
                return wordtag[sent[k-1]].keys()
            else:
                return wordtag[categorize_lowfreq(sent[k-1])].keys()
    
    # C- Do the iterations for viterbi and psi for time>0 until T
    for k in range(1, len(sent)+1):# loop through time
        temp_path = {}
        word = sent[k-1] 
        ## handling unknown words in test set using low freq words in training set
        word_to_use = word
        if word not in wordtag:
            word_to_use = categorize_lowfreq(sent[k-1])

        for u in possible_tags(k-1): # loop through the states @(t-1)
            for v in possible_tags(k):
                V[k,u,v], prev_w = max([(V[k-1,w,u] + trigram_proba(w,u,v) + emission_proba(word_to_use,v),w) 
                                       for w in possible_tags(k-2)])
                temp_path[u,v] = path[prev_w,u] + [v]
        path = temp_path

    # D - Back-tracking
    prob,umax,vmax = max([(V[len(sent),u,v] + trigram_proba(u,v,'STOP'),u,v) 
                          for u in possible_tags(len(sent)-1) for v in possible_tags(len(sent))])
    
    V_max = []
    
    full_path = ["*","*"]+path[umax,vmax]+["STOP"]
    for i in range(1, len(full_path)-2):
        V_max.append(V[i, full_path[i], full_path[i+1]])
        
    return path[umax,vmax], V_max

count = 0

def run_viterbi(sent):
    tags, proba = viterbi(sent)
    for s, t, p in zip(sent, tags, proba):
        wf.write('{} {} {} \n'.format(s, t, p))
    wf.write('\n')

with open("ner_dev.dat",'r', encoding='utf-8') as f:
    with open("6.txt", 'w') as wf:
        sent = []
        for line in f:
            line = line.strip()
            if line != "":
                sent.append(line.strip())
            else:
                run_viterbi(sent)
                sent = []
        if len(sent) > 0:
            run_viterbi(sent)
            sent = []
