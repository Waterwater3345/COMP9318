import helper
import random
from sklearn import tree
import pickle

def train(data, classifier_file):
    train_data = pre_process(data)
    clf = {}
    for i in train_data:
        temp_train = [j[:-1] for j in train_data[i]]
        temp_result = [j[-1] for j in train_data[i]]
        clf[i] = tree.DecisionTreeClassifier()
        clf[i].fit(temp_train, temp_result)
    file = open(classifier_file)
    pickle.dump(clf, file)


def test(data, classifier_file):
    test_data = pre_process(data)
    for i in test_data:
        temp_train = [j[:-1] for j in test_data[i]]



def pre_process(line):
    dict = {}
    dictionary = ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW',
                  'P', 'B', 'CH', 'D', 'DH', 'F', 'G', 'HH', 'JH', 'K', 'L', 'M', 'N', 'NG', 'R', 'S',
                  'SH', 'T', 'TH', 'V', 'W', 'Y', 'Z', 'ZH']
    #pre None = 39 next none = 40
    for i, word in enumerate(dictionary):
        dict[word] = i

    train_data = {}
    for i in line:
        data = i.split(':')[1].split(" ")
        position = 0
        temp_list = []
        for i, phon in enumerate(data):
            if phon[-1] in '012':
                temp_result = 0
                if phon[-1] == '1':
                    temp_result = 1
                phon = phon[:-1]
                if i == 0:
                    pre = 39
                else:
                    if data[i - 1][-1] in '012':
                        pre = dict[data[i-1][:-1]]
                    else:
                        pre = dict[data[i-1]]
                if i == len(data) - 1:
                    next = 40
                else:
                    if data[i+1][-1] in '012':
                        next = dict[data[i+1][:-1]]
                    else:
                        next = dict[data[i+1]]

                temp_list.append([dict[phon], position, pre, next, temp_result])
                position += 1

        if len(temp_list) not in train_data:
            train_data[len(temp_list)] = []
        train_data[len(temp_list)] += temp_list
    return train_data

def get_data(line):
    dict = {}
    dictionary = ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW',
                  'P', 'B', 'CH', 'D', 'DH', 'F', 'G', 'HH', 'JH', 'K', 'L', 'M', 'N', 'NG', 'R', 'S',
                  'SH', 'T', 'TH', 'V', 'W', 'Y', 'Z', 'ZH']
    for i, word in enumerate(dictionary):
        dict[word] = i

    train_data = []
    for i in line:
        data = i.split(':')[1].split(" ")
        temp_list = []
        position= 0
        for i, phon in enumerate(data):
            if phon[-1] in '012':
                temp_result = 0
                if phon[-1] == '1':
                    temp_result = 1
                phon = phon[:-1]
                if i == 0:
                    pre = 39
                else:
                    if data[i - 1][-1] in '012':
                        pre = dict[data[i-1][:-1]]
                    else:
                        pre = dict[data[i-1]]
                if i == len(data) - 1:
                    next = 40
                else:
                    if data[i+1][-1] in '012':
                        next = dict[data[i+1][:-1]]
                    else:
                        next = dict[data[i+1]]

                temp_list.append([dict[phon], position, pre, next, temp_result])
                position += 1
        train_data.append(temp_list)
    return train_data


def divide(data, seprate = 1):
    train = {}
    test  = {}
    for i in data:
        train[i] = []
        test[i] = []
    for i in data:
        for j in data[i]:
            if(random.randint(0,10) >= seprate):
                train[i].append(j)
            else:
                test[i].append(j)

    return train, test

raw_data = helper.read_data("./asset/training_data.txt")
for i in raw_data:
    print(i)
exit(1)
true = 0
false = 0

for a in test_data:
    for i in test_data[a]:
        predict = []
        for word in i:
            predict.append( clf[a].predict_proba([word[:-1]])[0][-1])
        pred = predict.index(max(predict))

        if i[pred][-1] != 1:
            # print(predict)
            # print(i)
            false += 1
        else:
            true +=1
    print(a, true/(true + false), true+false)

    print(len(train[a]), len(test_data[a]))
   # print(clf[4].tree_.__getstate__())
# a = []
# b = []
# for i in range(true):
#     a.append(1)
#     b.append(1)
# for i in range(false):
#     a.append(0)
#     b.append(1)
# from sklearn.metrics import f1_score
# print(f1_score(a, b, average="macro"))
#    clf[i].predict_proba(test[i][-1][:-1])
