from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB
import WebDB
import random
tag_names = ["nd_Person", "Adventure", "Alternate_Universe",
             "Anthro", "Comedy","Crossover", "Dark",
             "Drama","Equestria_Girls", "Horror", "Human",
             "Mystery", "Random", "Romance","Sad", "Sci_Fi",
             "Slice_of_Life","Thriller","Tragedy"
             ]
def random_select_sets(numTrain, numTest):
    #fetch all story id's
    story_ids = db.get_all_docIDs()
    random.shuffle(story_ids)
    #throw or catch exception?
    out = {}
    out["train"] = story_ids[0:numTrain]
    out["test"] = story_ids[numTrain:numTrain+numTest]
    return out
def txt_to_list(doc_ids):
    out = []
    for id in doc_ids:
        filename = "raw_texts/{}.txt".format(id)
        with open(filename, encoding="utf-16") as f:
            s = f.read()
            out.append(s)
    return out
def fetch_tags(id_list):
    #memory inefficient?
    out = []
    for id in id_list:
        tag_list = db.lookup_tags_by_doc_ID(id)[2:]
        temp = []
        for i,tag in enumerate(tag_list):
            if tag ==1:
                temp.append(tag_names[i])
        out.append(temp)
    return out


db = WebDB.WebDB("data.db")
sets = random_select_sets(30,5)
train_tags = fetch_tags(sets["train"])
train_texts = txt_to_list(sets["train"])

#vectorize
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(train_texts)

#tf-idf transformation
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

#process tags
mlb = MultiLabelBinarizer()
processed_train_tags = mlb.fit_transform(train_tags)
print(processed_train_tags)
#classifier
clf = OneVsRestClassifier(MultinomialNB())
clf.fit(X_train_tfidf,processed_train_tags)
print("classes:{}".format(clf.classes_))

#process test set

test_texts = txt_to_list(sets["test"])
X_test_counts = count_vect.transform(test_texts)
print("X_test_counts.shape: {}".format(X_test_counts.shape))
X_test_tfidf = tfidf_transformer.transform(X_test_counts)

predicted_tags = clf.predict(X_test_tfidf)
predicted_tags_readable = mlb.inverse_transform(predicted_tags)
test_tags = fetch_tags(sets["test"])

#print results

print("get params: {}".format(clf.get_params(deep=True)))
for i,id in enumerate(sets["test"]):
    print("\n")
    print("id: {}".format(id))
    doc_name = db.get_any_by_doc_ID("title",id)
    doc_desc = db.get_any_by_doc_ID("short_description",id)
    print("title: {}".format(doc_name))
    print("description: {}".format(doc_desc))
    print("predicted: {}".format(predicted_tags_readable[i]))
    print("actual: {}".format(test_tags[i]))

#get labels
#tags = db.lookup_tags_by_doc_ID(story_ids[0])
#print(tags)
