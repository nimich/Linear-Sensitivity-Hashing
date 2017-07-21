# -*- coding: utf-8 -*-
"""
Created by Michail Nikolaos

This script finds the k-nearest neightboors with LSH from a list of minhashes
and compares the results with actual Jaccard similarity of the sets.
The minhashes are calculated from the shingles in shinglesMap.json
located in execution path and created from LSH_Preproccessing.py

The algorithm parameters are 
-kNeigh Number of neighhboors 
-bands Number of bands for Minhashes
-r Integers per band
-jaccardThres Threshold for two sets to be similar by Jaccard similarity.
If no threshold is implemented then we will have many false postives from
Jaccard method
"""

import numpy as np
import operator 
import random
import time
import os
import json
import sys
from tqdm import tqdm
from collections import defaultdict


#For command line execution
if (len(sys.argv) > 5):
    targetDocID = str(sys.argv[1])
    kNeigh = int(sys.argv[2])    
    bands = int(sys.argv[3])
    r = int(sys.argv[4]) 
    jaccardThres = int(sys.argv[5])/100    
else :    
    targetDocID = '10864'
    kNeigh = 10
    bands = 10
    r = 4
    jaccardThres = 0.2        
    
print('LSH run for document ',targetDocID,' finding',kNeigh,' nearest neighbors with ',
      bands,' bands of ', r ,' integers')

numHashes = bands*r;     

def findMinHash(myList,a,b,c): 
    hashedList = [ (a*x + b)%c for x in myList]
    return min(hashedList)

def compute_jaccard_index(set_1, set_2):
    n = len(set_1.intersection(set_2))
    return n / float(len(set_1) + len(set_2) - n) #The union's cardinality 
            #is the sets cardinality minus the intersection's cardinality  

path = os.getcwd();

with open(path+os.path.sep+'shinglesMap.json', 'r') as f:
    try:
        shingleMap = json.load(f)
    except ValueError:
        shingleMap = {}
        
f.close()

#hashed in 0 2^32
#hash functions will be in the family  of h(x) = (a*x+b)mod c where c is the big prime
maxShingleID = 2**32-1   
  
##Smallest prime after 2^24-1 
bigPrime = 16777259 

print('\n---------------------------------------------------------')
print('Creating Minihash Signatures')
print('---------------------------------------------------------\n')

print('Calculating',numHashes,'MinHashes for',len(shingleMap),'documents')
signatures = defaultdict(list)

for hashIndex in tqdm(range(0,numHashes)): 
        
    a = random.randint(0, maxShingleID)
    b = random.randint(0, maxShingleID)
    
    for doc,docShingles in shingleMap.items():
        minHash = findMinHash(docShingles,a,b,bigPrime)
        signatures[doc].append(minHash)
    

collisionMap = defaultdict(int)



if (targetDocID not in signatures):
    print('Wrong Document id\nDocument id',targetDocID,'is not in the signatures map\n')
    sys.exit()

start_time = time.time()

targetBuckets = dict()

#Find all buckets for target document and save them in a dictionary
for band in range(bands): 
    targetBuckets[band] = sum((np.multiply(signatures[targetDocID][band*r:(band+1)*r],np.arange(1,r+1)))) % bigPrime

for doc in signatures.keys():

    for band in range(bands):    
        
        bucketID = sum((np.multiply(signatures[doc][band*r:(band+1)*r],np.arange(1,r+1)))) % bigPrime
             
        #if we found another document that hashes in the same bucket we have a collisionn and a candidate key
        if targetBuckets[band] == bucketID:
            collisionMap[doc] += 1

neightMap = { k:v for k,v in collisionMap.items() if k != targetDocID}

neigthboorsSorted = sorted(neightMap.items(), key=operator.itemgetter(1),reverse=True)

topKNN_LSH = neigthboorsSorted[0:kNeigh]

LSH_exec_time = time.time() - start_time

print('\n---------------------------------------------------------')
print('Results fot Document:',targetDocID,)

print('\n---------------------------------------------------------')
print('Locality Sensitive Hashing with MiniHashes')

print('LSH Neightboors for',bands,'bands of ',r,' integers are:\n'  )

for n in topKNN_LSH:
    print('-> Document:',n[0],' collision occured in ',n[1], " of the ",bands,' bands (',round(n[1]/bands,2),')')    

print('\nTotal Time for LSH is:',  LSH_exec_time ," seconds")

start_time = time.time()

jacSimMap = {}

for doc,docShingles in shingleMap.items():
        jacSim = compute_jaccard_index(set(shingleMap[targetDocID]),set(shingleMap[doc]))
        if jacSim > jaccardThres and doc != targetDocID:
            jacSimMap[doc] = jacSim
        
jacNeigthboorsSorted = sorted(jacSimMap.items(), key=operator.itemgetter(1),reverse=True)

topKNN_JAC = jacNeigthboorsSorted[0:kNeigh]

print('\n---------------------------------------------------------')
print('Actual Neightboors based on Jaccard Similairy of shingles are:\n')

for n in topKNN_JAC:
    print('-> Document:',n[0],' simularity ',round(n[1],2))
    
print('\nTotal Time for Jaccard similarity calculation is:',  time.time() - start_time ," seconds")    


if ((len(topKNN_JAC) != 0) & (len(topKNN_LSH) != 0)):
    topKNN_JAC_docs = set([x[0] for x in topKNN_JAC])
    topKNN_LSH_docs = set([x[0] for x in topKNN_LSH])    
    
if len(topKNN_JAC_docs) != 0: #We have ar least one true Neightboor
      TrueNeightboors = len (topKNN_JAC_docs)
      
      TruePositives =  len(set.intersection(topKNN_LSH_docs,topKNN_JAC_docs))
            
      FalsePositives = len(set.difference(topKNN_LSH_docs,topKNN_JAC_docs))
      
      FalseNegatives = len(set.difference(topKNN_JAC_docs,topKNN_LSH_docs))
      
      PercFoundNeigt = TruePositives / TrueNeightboors
 
      print('\n---------------------------------------------------------')     
      print("Accuracy ",PercFoundNeigt ,'\nTrue Neightboors are  ',TrueNeightboors,              
            '\nFound Neightboors from LSH are ',TruePositives,
            '\nNot Found Neightboors from LSH are ',FalseNegatives,
            '\nFalse Neightboors from LSH are ',FalsePositives)      

