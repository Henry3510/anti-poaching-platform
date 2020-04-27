from stanfordcorenlp import StanfordCoreNLP
import logging

full_text = ''
data = []


def getName(data, keyword):
    name = None
    nameDict = {}

    for line in data:
        keyword_location = line.find(keyword)
        if keyword_location == -1:
            continue

        checkRange = line[keyword_location:len(
            line)].replace('）', '')  # just in case

        # try to match names from previous results
        '''for possibleName in nameList:
            # print(checkRange[len(pattern):len(name)+len(pattern)])
            if checkRange[len(pattern):len(possibleName)+len(pattern)] == possibleName:
                return'''

        nerResult = nlp.ner(checkRange)
        if nerResult[1][1] == 'PERSON':  # nerResult[0] is keyword

            name = nerResult[1][0]

            if not nameDict.__contains__(name):
                nameDict[name] = 1

            else:
                nameDict[name] += 1

    return nameDict


def getInfo(data, name):
    info = {'name': name, 'gender': None, 'birth': None, 'race': None,
            'education_level': None, 'is_valid_person': True}

    gender = ['男', '女']
    splited_text = []

    for line in data:
        if name not in line:
            continue

        nerResult = nlp.ner(line)

        if 'DATE' in str(nerResult):

            for i in nerResult:
                if i[1] == 'DEMONYM' or i[1] == 'NATIONALITY':  # find race info
                    if '族' in i[0]:
                        info['race'] = i[0]
                        break

            splited_text = line.split('。')[0].split('，')

            gender_found = False
            birth_found = False
            education_level_found = False
            for i in splited_text:
                if gender_found and birth_found and education_level_found:
                    break

                if i in gender:
                    info['gender'] = i
                    gender_found = True

                if '生' in i and not birth_found:
                    nerResult = nlp.ner(i)
                    birth = ''
                    for j in nerResult:
                        if j[1] == 'DATE':
                            birth += j[0]

                    if birth:
                        info['birth'] = birth
                        birth_found = True

                if '文化' in i or '文盲' in i and not education_level_found:
                    info['education_level'] = i
                    education_level_found = True

            break

    from collections import Counter

    if Counter(info.values())[None] == len(info) - 2:
        info['is_valid_person'] = False

    return info


def getNameAllOccurrences(text, names):
    name_list = list(names.keys())
    name_occurrences = {}
    for name in name_list:
        name_occurrences[name] = text.count(name)

    return name_occurrences


def getLocation(data):
    place = '公诉机关'
    isDetected = True

    for line in data:
        if place not in line:
            continue

        nerResult = nlp.ner(line)
        location = ''

        for item in nerResult:
            if item[1] == 'ORGANIZATION':
                location += item[0]

        if not location:
            isDetected = False

            from string import punctuation
            punc = '，。、【 】 “”：；（）《》‘’「」？！()、%^>℃：.”“^-——=&#@￥' + punctuation

            location = line[line.find(
                place) + len(place):len(line)].strip(punc)

        return (location, line, isDetected)

    return (None, None, isDetected)


def getSentence(data):
    sentence = []
    data_reversed = list(reversed(data))
    number = 0

    for number in range(0, len(data_reversed)):
        if data_reversed[number][len(data_reversed[number])-5:] == '判决如下：':
            break

    for i in range(number-1, 0-1, -1):
        text = data_reversed[i]
        nerResult = nlp.ner(text)
        if nerResult[0][1] != 'NUMBER' and text[0] != '（' and text[0:2] != '被告人':
            break
        sentence.append(data_reversed[i])

    return sentence


def getSpeciesInfo(text):

    appeared_species = {}

    from ast import literal_eval

    with open('result.txt', 'r') as file:
        data = literal_eval(file.read())

    for species in data.keys():
        if species in text:
            appeared_species[species] = data[species]

    return appeared_species


def main(file, keyword, get_location=False, get_info=False, get_name_all_occurrences=False, get_sentence=False, get_species_info=False, vaild_person_only=False):
    global full_text

    with open(file, 'r') as doc:
        for line in doc.readlines():
            if line.strip():
                full_text += line
                data.append(line.strip())

    names = getName(data, keyword)
    print('NAMES MATCH KEYWORD \"' + keyword + '\": ' + str(names))

    if get_location:
        location = getLocation(data)
        if not location[2]:
            print('CAN\'T DETECT LOCATION, THE RESULT IS: ', location)

        else:
            print('LOCATION: ', location[0])

    if get_name_all_occurrences:
        print('ALL OCCURRENCES: ', getNameAllOccurrences(full_text, names))

    if get_info:
        for name in names:
            person_info = getInfo(data, name)
            if person_info['is_valid_person']:
                print(person_info)
            else:
                if not vaild_person_only:
                    print('MAY NOT BE A VALID PERSON: ', person_info)

    if get_sentence:
        sentence = getSentence(data)
        print('SENTENCE:')
        for i in sentence:
            print(i)

    if get_species_info:
        species_info = getSpeciesInfo(full_text)
        print(species_info)


if __name__ == '__main__':

    try:
        import urllib.request
        urllib.request.urlopen('http://127.0.0.1:9000')

    except urllib.error.URLError:
        print('INITIALIZING STANFORD CORENLP...')

        try:
            from psutil import AccessDenied
            from sys import exit
            nlp = StanfordCoreNLP('../../stanford-corenlp-full-2020-04-20/',
                                  lang='zh', logging_level=logging.INFO, port=9000)
        except AccessDenied:
            print('ACCESS DENIED, PLEASE RUN AS ROOT')
            exit()

    print('USING EXISTING SERVER ON http://127.0.0.1:9000')
    nlp = StanfordCoreNLP('http://localhost', lang='zh', port=9000)

    main('./files/10.txt', '被告人', get_location=True,
         get_info=True, get_sentence=True, get_species_info=True, vaild_person_only=False)
