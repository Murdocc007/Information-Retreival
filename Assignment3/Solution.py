from __future__ import division
import os
from math import log10, sqrt
from nltk.stem.porter import *
from nltk.stem.wordnet import WordNetLemmatizer

def readStopWords(stopwordsFilePath):
    #read the stopwords
    stopwords=[]
    with open(stopwordsFilePath,'r') as f:
        for line in f:
            for word in line.split():
               stopwords.append(word)
    return stopwords


#transform a crude line to a refined one
def transformText(line):
    #remove sgml tags
    tag=re.compile("\\<.*?>")
    line = tag.sub(" ",line)


    #remove digits
    tag=re.compile("[\\d+]")
    line = tag.sub("",line)

    #remove special characters
    tag=re.compile("[+^:,?;=%#&~`$!@*_)/(}{\\.]")
    line = tag.sub("",line)

    #remove possesives
    tag=re.compile("\\'s")
    line = tag.sub("",line)

    #replace the "'" with space
    tag=re.compile("\\'")
    line = tag.sub(" ",line)

    #replace the "-" with space
    tag=re.compile("-")
    line = tag.sub(" ",line)

    #replace multiple spaces with a single space
    tag=re.compile("\\s+")
    line = tag.sub(" ",line)

    #convert the line to lowercase
    line=line.lower()

    return line

#takes the file path and the stopwords as
#arguments and outputs the stems and the lemmas
def parseFile(filePath,stopwords):
    lmtzr=WordNetLemmatizer()
    lemmas=[]
    with open(filePath, "r") as ins:
        for line in ins:
            line=transformText(line)
            words=line.split(' ')
            for word in words:
                if word not in stopwords and word.strip()!='':
                    lemmas.append(lmtzr.lemmatize(word))
    return lemmas


def tokenize(doc,stopwords):
    temp=[]
    lmtzr=WordNetLemmatizer()
    for string in doc:
        if string.strip().lower() not in stopwords:
            if lmtzr.lemmatize(string.strip().lower())!='':
                temp.append(lmtzr.lemmatize(string.strip().lower()))
    return temp

#creating a dictionary for the query
def createDictionary(docs):
    d=dict()
    n=len(docs)
    for i in range(len(docs)):
        for word in docs[i]:
            if word in d:
                if i+1 in d[word]:
                    d[word][i+1]+=1
                else:
                    d[word][i+1]=1
            else:
                d[word]=dict()
                for k in range(n):
                    d[word][k+1]=0
                d[word][i+1]=1
    return d


#return the lemma dictionary and the count
def createDict(folderPath,stopwords):
    lemmaDict=dict()
    numberOfDocs=0
    docslen=[]

    for filename in os.listdir(folderPath):
        filepath=os.path.join(folderPath,filename)
        fileNumber=int(filename[9:])
        lemmas=parseFile(filepath,stopwords)
        numberOfDocs+=1
        #creating lemma dictionary
        count=0
        for lemma in lemmas:
            if lemma in lemmaDict:
                if fileNumber in lemmaDict[lemma]:
                    lemmaDict[lemma][fileNumber]+=1
                else:
                    lemmaDict[lemma][fileNumber]=1
            else:
                lemmaDict[lemma]=dict()
                lemmaDict[lemma][fileNumber]=1
            count+=1
        docslen.append(count)
    return lemmaDict,numberOfDocs,docslen


def processString(doc):
    doc=doc.replace("'s",'')
    doc=re.sub('[^A-Za-z]+',' ',doc)
    doc=doc.split(' ')
    return doc

def vectorQuery(queryNumber,stopwords,query,d,avgQueryLength,collectionSize,weightingScheme=1):

    tokens=[]

    tokens.append(tokenize(processString(query),stopwords))
    queryDict=createDictionary(tokens)

    keys_a = set(queryDict.keys())
    keys_b = set(d.keys())
    keys=keys_a | keys_b
    cosine_dict_query=dict()

    normalization_denom=0
    max_tf=max(queryDict[temp][i] for temp in queryDict for i in queryDict[temp].keys() )
    for word in keys_a:
        cosine_dict_query[word]=dict()
        cosine_dict_query[word]['tf_raw']=query.count(word)
        cosine_dict_query[word]['df']=len([val for val in d[word].values()]) if word in d else 0
        cosine_dict_query[word]['idf']=log10(collectionSize/cosine_dict_query[word]['df']) if cosine_dict_query[word]['df']!=0 else 0
        if weightingScheme==1:
            cosine_dict_query[word]['wt']=(0.4 + 0.6 * log10(cosine_dict_query[word]['tf_raw'] + 0.5) / log10(max_tf + 1.0)) * (cosine_dict_query[word]['idf']/ log10(collectionSize)) if max_tf!=0  and collectionSize>1 else 0
        else:
            cosine_dict_query[word]['wt']=(0.4 + 0.6 * (cosine_dict_query[word]['tf_raw'] / (cosine_dict_query[word]['tf_raw'] + 0.5 + 1.5 * (len(query) / avgQueryLength))) * cosine_dict_query[word]['idf'])
        normalization_denom+=cosine_dict_query[word]['wt']**2

    f=open('./queryVector/'+str(queryNumber)+'_W'+str(weightingScheme),'wb')
    f.write('{:25}'.format('Word')),
    f.write('{:25}'.format('tf')),
    f.write('{:25}'.format('df')),
    f.write('{:25}'.format('idf')),
    f.write('{:25}'.format('wt')),
    f.write('{:25}'.format('nlized')+"\n")

    for word in keys_a:
        f.write('{:15}'.format(word)),
        f.write('{:15}'.format(cosine_dict_query[word]['tf_raw'])),
        f.write('{:15}'.format(cosine_dict_query[word]['df'])),
        f.write('{:15}'.format(cosine_dict_query[word]['idf'])),
        f.write('{:15}'.format(cosine_dict_query[word]['wt'])),
        cosine_dict_query[word]['nlized']=cosine_dict_query[word]['wt']/sqrt(normalization_denom)
        f.write('{:15}'.format(cosine_dict_query[word]['wt']/sqrt(normalization_denom))+"\n")


def vectorDocs(d,doc_id,collectionSize,docLen,avgDocLen,weightingScheme=1):
    keys=set(d.keys())
    cosine_dict_doc=dict()
    normalization_denom=0
    max_tf=max([d[word][doc_id] if doc_id in d[word].keys() else 0 for word in d.keys()])
    for word in keys:
        if doc_id in d[word].keys():
            cosine_dict_doc[word]=dict()
            cosine_dict_doc[word]['tf_raw']=d[word][doc_id] if word in d and doc_id in d[word] else 0
            cosine_dict_doc[word]['df']=len([val for val in d[word].values()]) if word in d else 0
            cosine_dict_doc[word]['idf']=log10(collectionSize / cosine_dict_doc[word]['df']) if cosine_dict_doc[word]['df']!=0 else 0
            if weightingScheme==1:
                cosine_dict_doc[word]['wt']=(0.4 + 0.6 * log10 (cosine_dict_doc[word]['tf_raw'] + 0.5) / log10(max_tf + 1.0)) * (cosine_dict_doc[word]['idf']/ log10(collectionSize)) if max_tf!=0 and collectionSize>1 else 0
            else:
                cosine_dict_doc[word]['wt']=(0.4 + 0.6 * (cosine_dict_doc[word]['tf_raw'] / (cosine_dict_doc[word]['tf_raw'] + 0.5 + 1.5 * (docLen / avgDocLen))) * cosine_dict_doc[word]['idf']/ log10(collectionSize))
            normalization_denom+=cosine_dict_doc[word]['wt']**2

    f=open('./DocVectors/'+str(doc_id)+'_vector'+str(weightingScheme),'wb')
    f.write('{:25}'.format('Word')),
    f.write('{:25}'.format('tf')),
    f.write('{:25}'.format('wt')),
    f.write('{:25}'.format('nlized')+"\n")

    for word in keys:
        if doc_id in d[word].keys():
            cosine_dict_doc[word]['nlized']=cosine_dict_doc[word]['wt']/sqrt(normalization_denom)
            f.write('{:25}'.format(word)),
            f.write('{:15}'.format(cosine_dict_doc[word]['tf_raw'])),
            f.write('{:15}'.format(cosine_dict_doc[word]['wt'])),
            f.write('{:15}'.format(cosine_dict_doc[word]['wt']/sqrt(normalization_denom))+"\n")
    f.close()


def cosineSimilarity(stopwords,query,d,doc_id,collectionSize,docLen,avgDocLen,numberofQueries,avgQueryLength,weightingScheme=1):
    tokens=[]

    tokens.append(tokenize(processString(query),stopwords))
    queryDict=createDictionary(tokens)

    keys_a = set(queryDict.keys())
    keys_b = set(d.keys())
    keys=keys_a | keys_b
    cosine_dict_query=dict()
    cosine_dict_doc=dict()

    normalization_denom=0
    max_tf=max(queryDict[temp][i] for temp in queryDict for i in queryDict[temp].keys() )

    for word in keys:
        cosine_dict_query[word]=dict()
        cosine_dict_query[word]['tf_raw']=query.count(word)
        cosine_dict_query[word]['df']=len([val for val in d[word].keys()]) if word in d else 0
        cosine_dict_query[word]['idf']=log10(collectionSize/cosine_dict_query[word]['df']) if cosine_dict_query[word]['df']!=0 else 0
        if weightingScheme==1:
            cosine_dict_query[word]['wt']=(0.4 + 0.6 * log10(cosine_dict_query[word]['tf_raw'] + 0.5) / log10(max_tf + 1.0)) * (cosine_dict_query[word]['idf']/ log10(collectionSize)) if max_tf!=0  and collectionSize>1 else 0
        else:
            cosine_dict_query[word]['wt']=(0.4 + 0.6 * (cosine_dict_query[word]['tf_raw'] / (cosine_dict_query[word]['tf_raw'] + 0.5 + 1.5 * (len(query) / avgQueryLength))) * cosine_dict_query[word]['idf'])
        normalization_denom+=cosine_dict_query[word]['wt']**2
    for word in keys:
        cosine_dict_query[word]['nlized']=cosine_dict_query[word]['wt']/sqrt(normalization_denom)


    normalization_denom=0
    max_tf=max([d[word][doc_id] if doc_id in d[word].keys() else 0 for word in d.keys()])
    for word in keys:
        cosine_dict_doc[word]=dict()
        cosine_dict_doc[word]['tf_raw']=d[word][doc_id] if word in d and doc_id in d[word].keys() else 0
        cosine_dict_doc[word]['df']=len([val for val in d[word].keys()]) if word in d else 0
        cosine_dict_doc[word]['idf']=log10(collectionSize / cosine_dict_doc[word]['df']) if cosine_dict_doc[word]['df']!=0 else 0
        if weightingScheme==1:
            cosine_dict_doc[word]['wt']=(0.4 + 0.6 * log10 (cosine_dict_doc[word]['tf_raw'] + 0.5) / log10(max_tf + 1.0)) * (cosine_dict_doc[word]['idf']/ log10(collectionSize)) if max_tf!=0 and collectionSize>1 else 0
        else:
            cosine_dict_doc[word]['wt']=(0.4 + 0.6 * (cosine_dict_doc[word]['tf_raw'] / (cosine_dict_doc[word]['tf_raw'] + 0.5 + 1.5 * (docLen / avgDocLen))) * cosine_dict_doc[word]['idf']/ log10(collectionSize))
        normalization_denom+=cosine_dict_doc[word]['wt']**2
    for word in keys:
        cosine_dict_doc[word]['nlized']=cosine_dict_doc[word]['wt']/sqrt(normalization_denom)

    similarity=0
    for word in keys:
        similarity+=cosine_dict_query[word]['nlized']*cosine_dict_doc[word]['nlized']
    # print 'Cosine Similary: ',
    # print similarity
    return similarity


if __name__=='__main__':
    # stopwords=readStopWords('/home/aditya/Desktop/Aditya/IR/Assignments/Assignment2/stopwords')
    stopwords=readStopWords('/people/cs/s/sanda/cs6322/resourcesIR/stopwords')
    # lemmaDict,collectionLength,docslen=createDict('/home/aditya/Desktop/Aditya/IR/Assignments/Assignment1/Cranfield',stopwords)
    lemmaDict,collectionLength,docslen=createDict('/people/cs/s/sanda/cs6322/Cranfield',stopwords)
    query=[]
    temp=0
    with open("./Queries", "r") as ins:
        for line in ins:
            query.append(line)
            temp+=len(line)
    avgQueryLength=temp/len(query)
    numberofQueries=len(query)
    avgDocsLength=sum(docslen)/collectionLength

    for i in range(numberofQueries):
        vectorQuery(i,stopwords,query[i],lemmaDict,avgQueryLength,collectionLength,weightingScheme=1)
    for i in range(numberofQueries):
        vectorQuery(i,stopwords,query[i],lemmaDict,avgQueryLength,collectionLength,weightingScheme=2)

    for i in range(1,collectionLength+1):
        vectorDocs(lemmaDict,i,collectionLength,docslen[i-1],avgDocsLength,weightingScheme=1)

    for i in range(1,collectionLength+1):
        vectorDocs(lemmaDict,i,collectionLength,docslen[i-1],avgDocsLength,weightingScheme=2)

    print 'Cosine similarity with weighting scheme 1'
    #cosine weights 1
    for i in range(len(query)):
        similarity=[]
        for j in range(1,collectionLength+1):
            res=cosineSimilarity(stopwords,query[i],lemmaDict,j,collectionLength,docslen[j-1],sum(docslen)/collectionLength,avgQueryLength,numberofQueries,1)
            similarity.append([res,j])
        similarity=sorted(similarity,key= lambda x:x[0],reverse=True)
        print 'Query '+str(i)
        print similarity[:5]



    #cosine weights 2
    print 'Cosine similarity with weighting scheme 2'
    for i in range(len(query)):
        similarity=[]
        for j in range(1,collectionLength+1):
            res=cosineSimilarity(stopwords,query[i],lemmaDict,j,collectionLength,docslen[i],sum(docslen)/collectionLength,avgQueryLength,numberofQueries,2)
            similarity.append(res)
        similarity=sorted(similarity,key= lambda x:x[0],reverse=True)
        print 'Query '+str(i)
        print similarity[:5]

