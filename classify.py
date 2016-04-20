from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
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

def select_by_trait(numTrain, numTest, trait_name="likes",tags=tag_names):
    '''
    select story ids for test and training by given trait (not random)
    :param numTrain: number of training documents per tag
    :param numTest: number of testing documents per tag
    :param trait_name: trait to judge by (favorites, likes, dislikes, comments)
    :param tags:
    :return:
    '''
    limit = (numTrain +numTest)* len(tags)
    story_ids = db.get_all_docIDs()#get_docIDs_by_top_trait(trait_name)
    if limit > len(story_ids):
        raise NameError("attempting to use set bigger than corpus")
    # mother of all SQL statements
    #the above is not even remotely true
    subquery_string = """SELECT docfimficID FROM (
        SELECT docfimficID,likes
        FROM DocumentToTags
        INNER JOIN Documents
        on Documents.fimficID = DocumentToTags.docfimficID
        Where {tag} = 1
        Order By {trait} desc
        limit {numDocs})
    """
    z = [subquery_string.format(tag=i,trait=trait_name,numDocs=numTest+numTrain) for i in tags]
    sql = "\n UNION \n".join(z)
    res = db.execute(sql)
    reslist = res.fetchall()
    if reslist == []:
        NameError("no results :((((( something went horribly wrong")
    else:
        reslist = [i[0] for i in reslist]
        train = []
        test = []
        for i, tag in enumerate(tags):
            offset = (numTest+numTrain)*i
            train.extend(reslist[offset:offset+numTrain])
            test.extend(reslist[offset+numTrain: offset+numTrain+numTest])
        print("training set size:{} test set size {}".format(len(train),len(test)))
        out = {"train":train,"test":test}
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
    #sets = select_by_trait(10,2,tags=["Comedy","Human","Sad","Dark"])
    sets = select_sets_by_tag(20,4,tag_names)
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
    class_list = mlb.classes_
    report = metrics.classification_report(mlb.transform(test_tags_actual),predicted_tags,target_names=class_list)
    print(report)
    #retrieve top 30% for each class
    top_percentage = 30
    threshold_index = int( len(sets["test"]) *(top_percentage/100.0) )
    threshold_vals_dic = {}
    threshold_vals = []
    num_classes = len(class_list)
    for i in range(num_classes):
        z = [ predicted_probs[j,i] for j in range(len(sets["test"]))]
        z.sort(reverse=True)
        threshold_vals_dic[class_list[i]]= z[threshold_index]
        threshold_vals.append(z[threshold_index])
    print(threshold_vals_dic)


    print_predictions(sets["test"],predicted_tags_readable,class_list, class_probablities=predicted_probs,threshold_vals=threshold_vals)


def print_predictions(test_id_set, predicted_tags_readable, class_list, class_probablities=None, threshold_vals=None):
    '''
    prints out actual vs predicted tags, as well as title and description
    :param test_id_set: list of document ids in test set
    :param predicted_tags_readable: list tags per document as plain english
    :param: class_probabilities: list of probabilities for each class of every document. 2d
    :return: none
    '''
    test_tags = fetch_tags(test_id_set)
    #print("get params: {}".format(clf.get_params(deep=True)))
    for i,id in enumerate(test_id_set):
        print("\n")
        print("id: {}".format(id))
        doc_name = db.get_any_by_doc_ID("title",id)
        doc_desc = db.get_any_by_doc_ID("short_description",id)
        tags_by_threshold = []
        if class_probablities != None:
            if threshold_vals != None:
                tags_by_threshold = [class_list[j]  for j in range(len(class_list)) if class_probablities[i,j]> threshold_vals[j]]
            y = [float("{:.3}".format(j)) for j in class_probablities[i]]
            #y = predicted_probs[i]
            zipped = list(zip(class_list,y))
            zipped.sort(key=lambda x: x[1],reverse=True)
        print(zipped)
        print("title: {}".format(doc_name))
        print("description: {}".format(doc_desc))
        print("tags predicted by threshold of top 30%: {}".format(str(tags_by_threshold)))
        print("predicted: {}".format(predicted_tags_readable[i]))
        print("actual: {}".format(test_tags[i]))
    #get labels
    #tags = db.lookup_tags_by_doc_ID(story_ids[0])
    #print(tags)
main()