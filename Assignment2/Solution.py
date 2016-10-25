import os,pickle,sys,time
from nltk.stem.porter import *
from nltk.stem.wordnet import WordNetLemmatizer

#converts a number to it's binary string
def binaryString(n):
    return str(bin(n))[2:]

#returns the gamma codes of the numbers in binary format
def gammaCode(n):
    unary=binaryString(n)
    compressed=''
    i=1
    while(i<len(unary)):
        compressed+='1'
        i+=1

    compressed+='0'+unary[1:]
    return bin(int(compressed,2))

#returns the delta codes of the numbers in binary format
def deltaCode(n):
    unary=binaryString(n)
    length=len(unary)
    lenUnary=binaryString(length)
    compressed=''
    i=1
    while(i<len(lenUnary)):
        compressed+='1'
        i+=1
    compressed+='0'+lenUnary[1:]
    compressed+=compressed+unary[1:]
    return bin(int(compressed,2))


def blockCompression(termDict,docDict,termFileName,docFileName,k):
    try:
        termFile=open('./'+termFileName,'w')
        docFile=open('./'+docFileName,'w')
        count=0
        wordList=[]
        for word in termDict:
            #if the block size is still less than k, append the word to the wordlist
            if count<k:
                wordList.append(word)
                count+=1
            df=len([i for i in termDict[word] if termDict[word][i]>0])
            docFile.write(gammaCode(df)) #write the gamma code of the document frequency
            prev=0
            for doc in termDict[word]:
                gap=gammaCode(doc-prev)
                tf=gammaCode(termDict[word][doc])
                doclen=gammaCode(sum(docDict[doc].values()))
                max_tf=gammaCode(max(docDict[doc].values()))
                prev=doc
                docFile.write(gap) #writing the gamma code of the gap
                docFile.write(tf)#writing the tf in the doc
                docFile.write(doclen) #writing the length of the doc
                docFile.write(max_tf) #writing the maximum term frequency in the doc
            else:#reset the block
                count=0
                termFile.write(str(len(wordList))+''.join(wordList)) #write the block to the termfile
                wordList=[]

        #if block is not null and it's size<=k append it to the termFile
        if wordList!=[]:
            termFile.write(len(wordList)+''.join(wordList))
        termFile.close()
        docFile.close()
    except IOError:
        print 'Cannot open the files'

def frontCodingCompression(termDict,docDict,termFileName,docFileName):
    try:
        termFile=open('./'+termFileName,'w')
        docFile=open('./'+docFileName,'w')
        minlen=min([len(word) for word in termDict])
        sortedList=sorted([word for word in termDict])
        prefixlen=0
        flag=True
        prev=0
        fronCodeString=''
        while prefixlen<minlen and flag:
            currChar=sortedList[0][prefixlen]
            for word in sortedList:
                if word[prefixlen]!=currChar:
                    flag=False
            prefixlen+=1

        #if there's a common prefix string among all the words in the dictionary
        if prefixlen>=1:
            fronCodeString+=str(len(sortedList[0]))+sortedList[0][:prefixlen]+'*'+sortedList[0][prefixlen:]
            for word in sortedList[1:]:
                fronCodeString+=str(len(word)-prefixlen)+'|'+word[prefixlen:]
        else:
            for word in sortedList:
                fronCodeString+=str(len(word))+word
        termFile.write(fronCodeString)
        for word in sortedList:
            for doc in termDict[word]:
                gap=gammaCode(doc-prev)
                tf=gammaCode(termDict[word][doc])
                doclen=gammaCode(sum(docDict[doc].values()))
                max_tf=gammaCode(max(docDict[doc].values()))
                prev=doc
                docFile.write(gap) #writing the gamma code of the gap
                docFile.write(tf)#writing the tf in the doc
                docFile.write(doclen) #writing the length of the doc
                docFile.write(max_tf) #writing the maximum term frequency in the doc
        termFile.close()
        docFile.close()
    except IOError:
        print 'Cannot open the files'

def readStopWords(stopwordsFilePath):
    #read the stopwords
    stopwords=[]
    with open(stopwordsFilePath,'r') as f:
        for line in f:
            for word in line.split():
               stopwords.append(word)
    return stopwords


#takes the file path and the stopwords as
#arguments and outputs the stems and the lemmas
def parseFile(filePath,stopwords):
    array=[]
    lmtzr=WordNetLemmatizer()
    stemmer = PorterStemmer()
    lemmas=[]
    stems=[]
    with open(filePath, "r") as ins:
        for line in ins:
            line=transformText(line)
            words=line.split(' ')
            for word in words:
                if word not in stopwords and word.strip()!='':
                    lemmas.append(lmtzr.lemmatize(word))
                    stems.append(stemmer.stem(word))
    return lemmas,stems





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


#return the stem dictionary,lemma dictionary and the doc dictionary
def createDict(folderPath,stopwords):
    stemDict=dict()
    lemmaDict=dict()
    docDict=dict()
    for filename in os.listdir(folderPath):
        filepath=os.path.join(folderPath,filename)
        fileNumber=int(filename[9:])
        lemmas,stems=parseFile(filepath,stopwords)
        docDict[fileNumber]=dict()

        #creating lemma dictionary
        for lemma in lemmas:
            if lemma in lemmaDict:
                if fileNumber in lemmaDict[lemma]:
                    lemmaDict[lemma][fileNumber]+=1
                else:
                    lemmaDict[lemma][fileNumber]=1
            else:
                lemmaDict[lemma]=dict()
                lemmaDict[lemma][fileNumber]=1

        #creating stem dictionary
        for stem in stems:
            if stem in stemDict:
                if fileNumber in stemDict[stem]:
                    stemDict[stem][fileNumber]+=1
                else:
                    stemDict[stem][fileNumber]=1
            else:
                stemDict[stem]=dict()
                stemDict[stem][fileNumber]=1

        #create the document dictionary
        for stem in lemmas:
            if stem in docDict[fileNumber]:
                docDict[fileNumber][stem]+=1
            else:
                docDict[fileNumber][stem]=1

    return lemmaDict,stemDict,docDict


def getFileSize(filename):
    return os.path.getsize("./"+filename)

def docWithlargestMaxTF(docDict):
    id=0
    maxval=0
    for doc in docDict:
        temp=max(docDict[doc].values())
        if temp>maxval:
            maxval=temp
            id=doc
    id=str(id)
    id='cranfield'+'0'*(4-len(id))+str(id)
    return id,str(maxval)

def docWithLargestDocLen(docDict):
    id=0
    maxval=0
    for doc in docDict:
        temp=sum(docDict[doc].values())
        if temp>maxval:
            maxval=temp
            id=doc
    id=str(id)
    id='cranfield'+'0'*(4-len(id))+str(id)
    return id,str(maxval)


def termWithLargestDF(stemDict):
    maxval=0
    maxstem=''
    for stem in stemDict:
        temp=len([i for i in stemDict[stem] if stemDict[stem][i]>0])
        if temp>maxval:
            maxval=temp
            maxstem=stem
    return maxstem,str(maxval)

def termsWithLowestDF(stemDict):
    for stem in stemDict:
        temp=len([i for i in stemDict[stem] if stemDict[stem][i]>0])
        if temp==1:
            yield stem,'1'

def writeDictToFile(filename,d):
    with open('./'+filename, 'wb') as handle:
      pickle.dump(d, handle)


def printAttributesWords(wordList,stemDict):
    print 'Word'+' '+'DF'+' '+'TF'+' '+'Size'
    for word in wordList:
        word=word.lower()
        stemmer = PorterStemmer()
        temp=stemmer.stem(word)
        df=len([i for i in stemDict[temp] if stemDict[temp][i]>0])
        tf=sum(stemDict[temp])
        print word+' '+str(df)+' '+str(tf)+' '+str(sys.getsizeof(stemDict[temp]))+' bytes'

def getTFMaxTFDoclen(word,stemDict,docDict):
    print word
    word=word.lower()
    stemmer = PorterStemmer()
    stem=stemmer.stem(word)
    i=0
    docids=sorted(stemDict[word])
    print 'Doc TF DocLen Max_TF'
    for doc in docids:
        print str(doc)+' ',
        print stemDict[stem][doc],
        print ' '+str(sum(docDict[doc].values())),
        print ' '+str(max(docDict[doc].values()))
        i+=1
        if i==3:
            break
if __name__=='__main__':
    # stopwords=readStopWords('/home/aditya/Desktop/Aditya/IR/Assignments/Assignment2/stopwords')
    stopwords=readStopWords('/people/cs/s/sanda/cs6322/resourcesIR/stopwords')
    start_time=time.time()
    # lemmaDict,stemDict,docDict=createDict('/home/aditya/Desktop/Aditya/IR/Assignments/Assignment1/Cranfield',
    #            stopwords)
    lemmaDict,stemDict,docDict=createDict('/people/cs/s/sanda/cs6322/Cranfield',
               stopwords)
    stop_time=time.time()
    print 'Time take to make Index_version1.uncompress :'+str(stop_time-start_time)
    print 'Size of the Index_version1.uncompress file :'+str(getFileSize('Index_version1.uncompress'))
    print 'Time take to make Index_version2.uncompress :'+str(stop_time-start_time)
    print 'Size of the Index_version2.uncompress file :'+str(getFileSize('Index_version2.uncompress'))
    writeDictToFile('Index_version1.uncompress',lemmaDict)
    writeDictToFile('Index_version2.uncompress',stemDict)
    start_time=time.time()
    blockCompression(lemmaDict,docDict,'Index_version1.compressed','Index_version1.compressedDictionary',8)
    stop_time=time.time()
    print 'Time taken to make Index_version1.compressed :'+str(stop_time-start_time)
    print 'Size of the Index_version1.compressed file :'+str(getFileSize('Index_version1.compressed'))
    start_time=time.time()
    frontCodingCompression(stemDict,docDict,'Index_version2.compressed','Index_version2.compressedDictionary')
    stop_time=time.time()
    print 'Time taken to make Index_version2.compressed :'+str(stop_time-start_time)
    print 'Size of the Index_version2.compressed file :'+str(getFileSize('Index_version2.compressed'))
    print 'Stem with largest DF:'+str(termWithLargestDF(stemDict))
    print 'Stem(s) with lowest DF'
    print 'Stem\tDF'
    for i,j in termsWithLowestDF(stemDict):
        print i,j
    print 'Doc with largest max TF:'+str(docWithlargestMaxTF(docDict))
    print 'Doc with largest doclen:'+str(docWithLargestDocLen(docDict))
    termArray=["Reynolds", "NASA", "Prandtl", "flow", "pressure", "boundary", "shock" ]
    printAttributesWords(termArray,stemDict)
    print "Nasa's posting list:"
    getTFMaxTFDoclen('NASA',stemDict,docDict)











