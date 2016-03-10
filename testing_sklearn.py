stories = [
"what a tragedy! I died and now i am sad",
"funny, this is a comedy jokes and comedy and all things hilarious.",
"lasers! this is science and fiction, robots, future.",
"this is about funny jokes about science and robots",
"this is a story that is both sad and funny and comedic and died"
]
tags = []
tags.append( {"comedy":False, "tragedy":True, "scifi":False})
tags.append({"comedy":True, "tragedy":False, "scifi":False})
tags.append({"comedy":False, "tragedy":False, "scifi":True})
tags.append({"comedy":True, "tragedy":False, "scifi":True})
tags.append({"comedy":True, "tragedy":True, "scifi":False})

def preprocess_tags(tags):
    out = []
    for item in tags:
        temp = []
        for value in item.keys():
            if item[value] == True:
                temp.append(value)
        out.append(temp)
    return out
from sklearn.feature_extraction.text import CountVectorizer
count_vect = CountVectorizer()
train_counts = count_vect.fit_transform(stories)

from sklearn.feature_extraction.text import TfidfTransformer
tfidf_transformer = TfidfTransformer().fit(train_counts)
X_train_tfidf = tfidf_transformer.transform(train_counts)

#format tags
from sklearn.preprocessing import MultiLabelBinarizer

mlb = MultiLabelBinarizer()
tag_list = preprocess_tags(tags)
processed_tags = mlb.fit_transform(tag_list)
print(processed_tags)
#train the classifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB
clf = OneVsRestClassifier(MultinomialNB())#MultinomialNB()
clf.fit(X_train_tfidf,processed_tags)

test_docs = ["funny funny joke", "died sad joke tragedy funny", "lasers and robots"]
X_test_counts = count_vect.transform(test_docs)
print("X_test_counts.shape")
print(X_test_counts.shape)
X_test_tfidf = tfidf_transformer.transform(X_test_counts)

predicted = clf.predict(X_test_tfidf)
print(predicted)
print(mlb.inverse_transform(predicted))