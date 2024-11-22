import csv
import difflib
import language_tool_python
import math
import marking
import modelling
import ocr
import re
import string
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.corpus import words
from nltk.corpus import wordnet
from rake_nltk import Rake

test1 = ocr.teacher_answer_scan()
test2 = ocr.student_answer_scan() 
 
strr = ""
for i in range(len(test2)):
    g=[]
    o=test2[i].split(" ")
    for k in range(0,len(o)):
        o[k]=(o[k].lower()).strip(",")
        o[k]=(o[k].lower()).strip("?")
        o[k]=(o[k].lower()).strip("/")
        if(o[k] in modelling.model):
            continue
        else:
            g.append(o[k])
    for s in range(len(g)):
        if(g[s] in o):
            o.remove(g[s])
    for w in range(len(o)):
        strr+=o[w]+" "
    if(i<len(test2)-1):
        strr+="."


strr=strr.lstrip(" ")
strr=strr.rstrip(" ")
print(strr.split("."))
test2=strr.split('.')
print("Student's answer split into different sentences: ",test2)



index=[]
for i in range(len(test2)):
    p=modelling.preprocess(test2[i])
    if(len(p)==0):
        index.append(i)
test2temp = test2.copy()
for z in range(len(index)):
    ke=index[z]
    test2temp.remove(test2[ke])
test2 = test2temp.copy()    
print(index)
print(test2)
index1=[]
for i in range(len(test2)-1):
    a=test2[i].split(" ")
    for j in range(i+1,len(test2)):
        b=test2[j].split(" ")
        sm=difflib.SequenceMatcher(None,a,b)
        if(sm.ratio()>0.75):
            index1.append(j)


index2=[]
len(test2)
for y in range(len(test2)-1):
    for z in range(y+1,len(test2)):
        print(y,z)
        m = modelling.heat_map_matrix_between_two_sentences(test2[y],test2[z])
        if(m > 0.99):
            index2.append(z)


ss2=""
print(index1,index2)
for i in range(len(test2)):
    if i not in index1:
        if i not in index2:
            ss2+=test2[i]+"."


ss1=test1
print("TEACHER'S ANSWER:\n",ss1)
print("STUDENT'S ANSWER:\n",ss2)
m = modelling.heat_map_matrix_between_two_sentences(ss1,ss2)
m = m*10
arr = []
m = round(m,2)
print("Score of Student's answer based on Context Similarity:",m)
arr.append(m)



#length of students answer
res = sum([i.strip(string.punctuation).isalpha() and i.strip(string.digits).isalpha() for i in test1.split()])
print("Length of Student's answer:-",res)



#checking grammatical errors
tool = language_tool_python.LanguageTool('en-US')
matches = tool.check(strr)
print("Approximate number of errors:",len(matches))
print("Score of the answer based on number of errors:",(10-round((len(matches)/res)*10,2)))
arr.append(10-round((len(matches)/res)*10,2))



dict={1:30,2:60,3:90,4:120,5:150}
#checking length of answer
print("Enter the maximum marks:")
marks=int(input())
print(res)
if(res<dict[marks]):
    x=round(10-(dict[marks]-res)/(10*marks),2)
elif(res>dict[marks]):
    x=10
print("Score of the answer based on length of the answer:",x)
arr.append(x)



keywords=[]
count9=0
r=Rake()
r.extract_keywords_from_text(test1)
t=r.get_ranked_phrases()
print(t)
for i in range(len(t)):
    kw=[]
    kw=t[i].split(" ")
    keywords.extend(kw)
keywords = modelling.remove(keywords)
kl=[]
for k in range(len(keywords)):
    if(keywords[k].isalpha() and len(keywords[k])>2):
        continue
    else:
        kl.append(keywords[k])
for m in range(len(kl)):
    keywords.remove(kl[m])
print(keywords)
for j in range(len(keywords)):
    if(keywords[j] in test2.lower()):
        count9+=1
    elif(keywords[j] not in test2.lower()):
        synonyms=[]
        for syn in wordnet.synsets(keywords[j]):
            for l in syn.lemmas():
                synonyms.append(l.name())
        synonyms=remove(synonyms)
        print("WORD:",keywords[j],"\n",synonyms,"\n")
        for n in range(len(synonyms)):
            if(synonyms[n] in test2.lower()):
                count9+=1
                break
print("Number of keywords found: ",count9)
print("Total number of keywords: ",len(keywords))
print("Score of student's answer  based on keywords:",round(count9/len(keywords)*10,2))



print("Enter the marks awarded by the teacher:")
mark=input()
h=round((float(mark)/marks),2)
arr.append(h)
print("Scores that will be added to the dataset:",arr)



#writing the scores to a csv file
with open("dataset##.csv", 'a') as csvfile:
    csvwriter = csv.writer(csvfile,lineterminator='\n')
    csvwriter.writerow(arr)
print("The observations has been added to the dataset.")

marking.marker(arr)
#final marks provided