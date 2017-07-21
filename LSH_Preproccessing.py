# -*- coding: utf-8 -*-
"""
Created by Michail Nikolaos

Preprocessing of the Reuters corpus for LSH technique

Find all the *.sgm files in data file located in current execution path 
and creates a single json document with the k-shingles of each document. 
The k-shingles are concatanated and hashed in order to be numbers.

shingleLength parameter changes the number of k conscutive words used for
each shingle
"""

from bs4 import BeautifulSoup
import binascii
import re
import glob
import os
import json
import sys
from tqdm import tqdm

print('Creating k-shingles from data files')

#Parameters
if (len(sys.argv) > 1):
    shingleLength = int(sys.argv[1])  
    print('Shingles Length used is '+str(shingleLength))
else : 
    print('Default shingle Length used (3-shingles)')
    shingleLength = 3      

textIDs,texts = [],[]

datapath = os.getcwd()+os.path.sep+'data'; #Get current execution path

filenames = glob.glob(os.path.join(datapath, '*.sgm'))

print('Parsing data files...')

for filename in tqdm(filenames):
    
    file = open(filename, 'r')
    data= file.read()
    
    soup = BeautifulSoup(data,'html.parser')    
    reutersTags = soup.find_all('reuters')
    
    for frag in reutersTags:        
        body = frag.find('body')        
        
        if body is not None:
            bodylength = len(BeautifulSoup.get_text(body).split())        
            if (bodylength > shingleLength):
                texts.append(BeautifulSoup.get_text(body))
                textIDs.append(frag.get('newid'))

print('Converting to lowercase and removing special characters...')
 
textsLower = [ x.lower() for x in texts]; #Convrt to lower and remove special characters

rx = re.compile('([\n\.\",\'])')
textsNoSpecial = [ rx.sub("",x) for x in textsLower]; 
                 
textMap = dict(zip(textIDs, textsNoSpecial)) 

textDict = {key: value.split() for (key,value) in textMap.items()}
 
textDictHased = {}
textDictUnHased = {}

print('Creating and hashing shingles...\n')

for (key,value) in textDict.items():
    docShingleList = [value[i:i+shingleLength] for i in range(len(value) - shingleLength + 1)]
    joinedDocShingles = [ "".join(shingle) for shingle in docShingleList] #Concatanate Shingles into one word
    hashedDocShingles = [ (binascii.crc32(bytes(jShingle,'utf-8')) & 0xffffffff) for jShingle in joinedDocShingles] #Hash joined shinles in 32 bit 
    textDictHased[key] = hashedDocShingles 
               
exec_path = os.getcwd();
with open(exec_path+os.path.sep+'shinglesMap.json', 'w') as f:
        json.dump(textDictHased, f)
      
print(len(textDictHased),' documnets were read, transformed and cut into',shingleLength,'shingles')
print('Saved '+str(shingleLength)+'-shingles of texts in shinglesMap.json succefully')
        
