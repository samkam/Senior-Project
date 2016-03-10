from sklearn.datasets import fetch_20newsgroups
categories = ['alt.atheism','soc.religion.christian', 'comp.graphics','sci.med']

twenty_train = fetch_20newsgroups(subset="train",categories=categories, shuffle=True, random_state=42)
print("target names")
print(twenty_train.target_names)
print()
print("")
print("first three lines of 0th article?")
print("\n".join(twenty_train.data[0].split("\n")[:3]))
print("target names [0]:")
print(twenty_train.target_names[twenty_train.target[0]])

#tokenizing text
from sklearn.feature_extraction.text import CountVectorizer
count_vect = CountVectorizer()
print(type(twenty_train.data))
X_train_counts = count_vect.fit_transform(twenty_train.data)
print("x_train_counts.shape: "+str(X_train_counts.shape))
try:
    print("attempting to print column 0")
    print(X_train_counts.getcol(0))
    print(count_vect.vocabulary)
    print(count_vect.vocabulary_.get("theta"))
except Exception:
    print("didn't work")
from sklearn.feature_extraction.text import TfidfTransformer
tfidf_transformer = TfidfTransformer().fit(X_train_counts)
X_train_tfidf = tfidf_transformer.transform(X_train_counts)
print("\n printing param names")
print(tfidf_transformer._get_param_names())

# classifier
print("twenty_train.target: ")
print(twenty_train.target[:10])
from sklearn.naive_bayes import MultinomialNB
clf = MultinomialNB().fit(X_train_tfidf, twenty_train.target)

#classify test documents.
docs_new = ["God is love", "OpenGL on the GPU is fast", "god I hate computers and GPU"]
X_new_counts = count_vect.transform(docs_new)
X_new_tfidf = tfidf_transformer.transform(X_new_counts)

predicted = clf.predict(X_new_tfidf)

for doc, category in zip(docs_new, predicted):
    print("%r => %s" %(doc, twenty_train.target_names[category]))

