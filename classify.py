from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
import WebDB
import random
db = WebDB.WebDB("data.db")
tag_names = ["nd_Person", "Adventure", "Alternate_Universe",
             "Anthro", "Comedy","Crossover", "Dark",
             "Drama","Equestria_Girls", "Horror", "Human",
             "Mystery", "Random", "Romance","Sad", "Sci_Fi",
             "Slice_of_Life","Thriller","Tragedy"
             ]
def random_select_sets(numTrain, numTest):
    #fetch all story id's
    story_ids = db.get_all_docIDs()
    print("number of docs:{}".format(len(story_ids)))
    random.shuffle(story_ids)
    #throw or catch exception?
    out = {}
    out["train"] = story_ids[0:numTrain]
    out["test"] = story_ids[numTrain:numTrain+numTest]
    return out
def select_sets_by_tag(numTrain, numTest, tags=["Adventure","Comedy","Romance","Sad","Slice_of_Life"]):
    train = []
    test = []
    fetched = []
    #out = db.get_docs_by_tag("Adventure")
    #print(out)
    for tag in tags:
        ids = db.get_docs_by_tag(tag)
        random.shuffle(ids)
        train.extend(ids[0:numTrain])
        test.extend(ids[numTrain:numTrain+numTest])

    #remove duplicates
    train = list(set(train))
    test = list(set(test))
    for i in test:
        if i in train:
            train.remove(i)
    out = {"train":train,"test":test}
    print("train size: {} test size: {}".format(len(train),len(test)))
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
    '''
    gets list of tags for each doc Id in list
    :param id_list:
    :return:
    '''
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
def id_to_filename(doc_ids):
    out = []
    for id in doc_ids:
        filename = "raw_texts/{}.txt".format(id)
        out.append(filename)
    return out

def main():
    sets = select_sets_by_tag(10,2,tag_names)
    #sets = random_select_sets(30,6)
    train_tags = fetch_tags(sets["train"])
    train_texts = id_to_filename(sets["train"])#txt_to_list(sets["train"])
    #vectorize
    count_vect = CountVectorizer(stop_words='english', encoding="utf-16", input="filename")
    X_train_counts = count_vect.fit_transform(train_texts)

    #tf-idf transformation
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

    #process tags
    mlb = MultiLabelBinarizer()
    processed_train_tags = mlb.fit_transform(train_tags)
    #rint(processed_train_tags)
    #classifier
    #clf = OneVsRestClassifier(MultinomialNB())
    clf = OneVsRestClassifier(LinearSVC())
    clf.fit(X_train_tfidf,processed_train_tags)
    print("classes:{}".format(clf.classes_))
    #process test set

    test_texts = id_to_filename(sets["test"])#txt_to_list(sets["test"])
    X_test_counts = count_vect.transform(test_texts)
    #print("X_test_counts inverse transformed: {}".format(count_vect.inverse_transform(X_test_counts)))
    X_test_tfidf = tfidf_transformer.transform(X_test_counts)

    predicted_tags = clf.predict(X_test_tfidf)
    predicted_tags_readable = mlb.inverse_transform(predicted_tags)
    test_tags_actual = fetch_tags(sets["test"])
    predicted_probs = clf.decision_function(X_test_tfidf)
    #predicted_probs = clf.get_params(X_test_tfidf)
    print("predicted probs")
    for i, id  in enumerate(sets["test"]):
        doc_name = db.get_any_by_doc_ID("title",id)
        doc_desc = db.get_any_by_doc_ID("short_description",id)
        print("\n\nid:{}, title: {}".format(id,doc_name))
        print(doc_desc)
        y = [float("{:.3}".format(j)) for j in predicted_probs[i]]
        #y = predicted_probs[i]
        zipped = list(zip(mlb.classes_,y))
        zipped.sort(key=lambda x: x[1],reverse=True)

        print(zipped)
        print("predicted: {}".format(predicted_tags_readable[i]))
        print("actual: {}".format(test_tags_actual[i]))

        #for count, tag_val in enumerate(predicted_probs[i]):




    #print_actual_v_predicted(sets["test"],predicted_tags_readable)

def print_actual_v_predicted(test_id_set, predicted_tags_readable):
    '''
    prints out actual vs predicted tags, as well as title and description
    :param test_id_set: list of document ids in test set
    :param predicted_tags_readable: list tags per document as plain english
    :return: none
    '''
    test_tags = fetch_tags(test_id_set)
    #print("get params: {}".format(clf.get_params(deep=True)))
    for i,id in enumerate(test_id_set):
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
main()