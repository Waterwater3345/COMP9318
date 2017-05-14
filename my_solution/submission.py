import helper
from sklearn import tree
from sklearn.svm import SVC
import pickle
import nltk

class word:
    def __init__(self, str):
        self.name, self.phonem = str.split(':')
        self.syllables = []
        for i in self.phonem.split(" "):
            self.syllables.append(syllbale(i))
        self.len = 0
        self.result = 0
        temp = 0
        for i in self.syllables:
            if i.is_vowel:
                self.len += 1
                if i.stress == 1:
                    self.result = temp + 1
                temp += 1
        self.pho_len = len(self.syllables)

    def __repr__(self):
        string = self.name + ":" + str(self.pho_len) +":"
        for i in self.syllables:
            string += i.name + " "
            if i.is_vowel:
                string += str(i.stress) + " "
        return string + ":"+str(self.result)+"/"+str(self.len)


class syllbale:
    def __init__(self, str):
        self.is_vowel = False
        self.stress = None
        self.name = str
        if str[-1] in '012':
            self.is_vowel = True
            self.stress = int(str[-1])
            self.name = str[:-1]


def train(data, classifier_file):
    train_data, index_file = pre_process(data)
    clf = {}
    for i in [2, 3, 4]:
        temp_train = [j[:-1] for j in train_data[i]]
        temp_result = [j[-1] for j in train_data[i]]
        # if i in [3,4]:
        #     clf[i] = SVC(probability = True)
        # else:
        class_weight = {}
        class_weight[0] = 1
        class_weight[1] = 9
        clf[i] = tree.DecisionTreeClassifier(class_weight=class_weight, max_depth=14)
        clf[i].fit(temp_train, temp_result)
    file = open(classifier_file, 'wb')
    pickle.dump((clf, index_file), file)


def test(data, classifier_file):
    file = open(classifier_file, 'rb')
    clf, index_file = pickle.load(file)
    test_data = get_data(data, index_file)
    result = []
    for word in test_data:
        index = len(word)
        predict = []
        for syllable in word:
            predict.append(clf[index].predict_proba([syllable])[0][-1])
        # if len(predict) == 4:
        #     predict[3] *= 30
        #     predict[2] *= 4
        # if len(predict) == 3:
        #     predict[2] *= 5
        pred = predict.index(max(predict))
        result.append(pred + 1)
    return result


def add_dict(index, dict):
    if index not in dict:
        dict[index] = 1
    else:
        dict[index] += 1


def clear_phon(phone):
    if phone[-1] in '012':
        return phone[:-1]
    return phone


def pre_process(line):
    # dict = {}
    # dictionary = ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW',
    #               'P', 'B', 'CH', 'D', 'DH', 'F', 'G', 'HH', 'JH', 'K', 'L', 'M', 'N', 'NG', 'R', 'S',
    #               'SH', 'T', 'TH', 'V', 'W', 'Y', 'Z', 'ZH']
    # # pre None = 39 next none = 40
    # # tags = {'NN':1, 'NNP':2, 'NNS':3, 'JJ':4, 'RB':5, 'IN':6, 'DT':7, 'JJR':8, 'VB':9}
    # for i, word in enumerate(dictionary):
    #     dict[word] = i

    train_data = {}
    stress_occ = {}
    total_occ = {}
    pre_occ = {}
    next_occ = {}
    for i in line:
        phons = i.split(':')[1].split(" ")
        pre = 'PRE'
        add_dict('PRE', total_occ)
        add_dict('NEXT', total_occ)
        for index, j in enumerate(phons):
            if j[-1] in '012':
                if j[-1] == '1':
                    add_dict(j[:-1], stress_occ)
                    add_dict(pre, pre_occ)
                    if index == len(phons) - 1:
                        add_dict('NEXT', next_occ)
                    else:
                        add_dict(clear_phon(phons[index + 1]), next_occ)
                j = j[:-1]
            add_dict(j, total_occ)
            pre = j

    # feature calibration
    for i in stress_occ:
        stress_occ[i] = stress_occ[i] / total_occ[i]
    #    print(i,end=' ')
    #print()
    for i in pre_occ:
        pre_occ[i] = pre_occ[i] / total_occ[i]
    #    print(i,end=' ')
   # print()

    for i in next_occ:
        next_occ[i] = next_occ[i] / total_occ[i]
    #   print(i,end=' ')


    for i in line:
        # a = nltk.pos_tag([i.split(':')[0]])[0][-1]
        # tag = tags.get(a, 0)
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
                    pre = 'PRE'
                else:
                    pre = clear_phon(data[i - 1])

                if i == len(data) - 1:
                    next = 'NEXT'
                else:
                    next = clear_phon(data[i + 1])
                    #               Phoneme name   No of vowel  pre Phoneme   next Phoneme      result
                if pre not in pre_occ:
                    pre_occ[pre] = 0
                if next not in next_occ:
                    next_occ[next] = 0
                if phon not in stress_occ:
                    stress_occ[phon] = 0
                temp_list.append([stress_occ[phon], position, pre_occ[pre], next_occ[next], temp_result])
                position += 1

        if len(temp_list) not in train_data:
            train_data[len(temp_list)] = []
        train_data[len(temp_list)] += temp_list
    index_list = [stress_occ, pre_occ, next_occ]
    return train_data, index_list


def get_data(line, index_list):
    # dict = {}
    # dictionary = ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW',
    #               'P', 'B', 'CH', 'D', 'DH', 'F', 'G', 'HH', 'JH', 'K', 'L', 'M', 'N', 'NG', 'R', 'S',
    #               'SH', 'T', 'TH', 'V', 'W', 'Y', 'Z', 'ZH']
    # # tag_list = {'NN': 1, 'NNP': 2, 'NNS': 3, 'JJ': 4, 'RB': 5, 'IN': 6, 'DT': 7, 'JJR': 8, 'VB': 9}
    # for i, word in enumerate(dictionary):
    #     dict[word] = i

    train_data = []
    stress_occ = index_list[0]
    pre_occ = index_list[1]
    next_occ = index_list[2]
    for i in line:
        # a = nltk.pos_tag([i.split(':')[0]])[0][-1]
        # tag = tag_list.get(a, 0)

        data = i.split(':')[1].split(" ")
        temp_list = []
        position = 0

        total = 0
        for i, phon in enumerate(data):
            if phon in ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW']:
                total += 1
        for i, phon in enumerate(data):
            if phon in ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW']:
                if i == 0:
                    pre = pre_occ['PRE']
                else:
                    pre = pre_occ[data[i - 1]]
                if i == len(data) - 1:
                    next = next_occ['NEXT']
                else:
                    next = next_occ[data[i + 1]]

                temp_list.append([stress_occ[phon], position, pre, next])
                position += 1
        train_data.append(temp_list)
    return train_data
