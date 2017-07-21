# Linear-Sensitivity-Hashing-

To compare a corpus of texts to find the most similar we could try many approaches; one is to create k-shinles from the words, hash them to numbers and compare directly these sets of shingles to calculate Jaccard similarity (https://en.wikipedia.org/wiki/Jaccard_index). Another approach when we deal with big datasets is to use linear sensitivity hashing (LSH) and try to find documents that hash in the same value and consider them similar. 

LSH is implemented using minhashes over the shingles set and then cutting the minihashes to bands of r integer and try to hash this r integer into a new bucket. When two documents hash into the same bucket into any of the bands we can consider that this results from actual similarity. The probability of two documents that have s similarity to at least hash into one same bucket is ![equat](https://latex.codecogs.com/gif.latex?1%20-%20%281%20-s%5Er%29) where b are the bands and r the integers per band. For more about the LSH you can look Mining of Massive Datasets by Jure Leskovec, Anand Rajaraman, Jeff Ullman chapter 3.4 (http://www.mmds.org/)

This implementation was tested in Reuters-21578 dataset which is standart machine learning dataset. The documents are a collection of 22 files each containing about 1000 documents in SGML format. The dataset can be downloaded from  https://archive.ics.uci.edu/ml/datasets/Reuters-21578+Text+Categorization+Collection. 

To run the file simply extract the dataset files in folder named data in the same directory where the two runables are and then run

python LSH_preprocessing.py [k] 

where k is the k-shingles used. This script parses the documents, transforms them, creates the k-shingles and stores the result in a json file named shinglesMap.json in order to be used in the next script. If no k is passed the default k which is 3 will be used.
For the nexr script type 
