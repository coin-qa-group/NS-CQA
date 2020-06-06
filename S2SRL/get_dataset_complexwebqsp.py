# -*- coding: utf-8 -*-
import json
import string
import sys
data_dir='./data/complexWeb/'

def get_seq2seq_train_Complexwebqsp():
    Complex_TrainQ = open(data_dir + 'PT_train.question', 'w', encoding="UTF-8")
    Complex_TrainA = open(data_dir + 'PT_train.action', 'w', encoding="UTF-8")
    action_file = open(data_dir+"action_result.txt", 'r', encoding="UTF-8")
    action_dict = {}
    for item in action_file:
        action_dict[item.split('\t')[0]] = item.split('\t')[1]
    with open(data_dir+'ComplexWebQuestions_train.json', 'r', encoding="UTF-8") as train_file:
        train_json_file = json.load(train_file)
        for question in train_json_file:
            if question['ID'] in action_dict.keys():
                entities_set = []
                entities_dict = dict()
                relations_set = []
                relations_dict = dict()
                type_set = []
                types_dict = dict()
                json_action = eval(action_dict[question['ID']])
                for item in json_action:
                    print(item)
                    if '?' not in list(item.values())[0][0]:
                        entities_set.append(list(item.values())[0][0])
                    if '?' not in list(item.values())[0][2]:
                        type_set.append(list(item.values())[0][2])
                    if list(item.values())[0][1] != '':
                        relations_set.append(list(item.values())[0][1])
                e_index = 1
                r_index = 1
                t_index = 1
                for e in entities_set:
                    entities_dict[e] = "ENTITY{0}".format(e_index)
                    e_index += 1
                for r in relations_set:
                    relations_dict[r] = "RELATION{0}".format(r_index)
                    r_index += 1
                for t in type_set:
                    types_dict[t] = "TYPE{0}".format(t_index)
                    t_index += 1
                str_action = question['ID']
                for item in json_action:
                    str_action += ' '
                    str_action += str(list(item.keys())[0])
                    str_action += ' ( '
                    if list(item.values())[0][0] in entities_dict.keys():
                        str_action += entities_dict[list(item.values())[0][0]]
                        str_action += ' '
                    if list(item.values())[0][1] in relations_dict.keys():
                        str_action += relations_dict[list(item.values())[0][1]]
                        str_action += ' '
                    if list(item.values())[0][2] in types_dict.keys():
                        str_action += types_dict[list(item.values())[0][2]]
                        str_action += ' '
                    str_action += ')'

                str_question = question['ID']
                str_question += ' <E> '
                for e in entities_dict.values():
                    str_question += e
                    str_question += ' '
                str_question += '</E> <R> '
                for r in relations_dict.values():
                    str_question += r
                    str_question += ' '
                str_question += '</R> <T> '
                for t in types_dict.values():
                    str_question += t
                    str_question += ' '
                str_question += '</T> '
                str_txt = question['machine_question'].lower().translate(str.maketrans('', '', string.punctuation))
                str_question += str_txt
                Complex_TrainQ.write(str_question+'\n')
                Complex_TrainA.write(str_action+'\n')


def get_seq2seq_true_train_Complexwebqsp():
    Complex_TrainQ = open(data_dir + 'PT_train.question', 'w', encoding="UTF-8")
    Complex_TrainA = open(data_dir + 'PT_train.action', 'w', encoding="UTF-8")
    Annotation_Entity_Relation_Type = open(data_dir + 'Annotation_train.json', 'w', encoding='utf-8')
    Annotation_Entity_Relation_Type.write('{'+'\n')
    count_dict = 0
    action_file = open(data_dir+"action_result.txt", 'r', encoding="UTF-8")
    action_dict = {}
    for item in action_file:
        action_dict[item.split('\t')[0]] = item.split('\t')[1]
    with open(data_dir+'ComplexWebQuestions_train.json', 'r', encoding="UTF-8") as train_file:
        train_json_file = json.load(train_file)
        for question in train_json_file:
            if question['ID'] in action_dict.keys():
                count_dict += 1
                entities_set = []
                entities_dict = dict()
                relations_set = []
                relations_dict = dict()
                type_set = []
                types_dict = dict()
                json_action = eval(action_dict[question['ID']])
                for item in json_action:
                    if '?' not in list(item.values())[0][0]:
                        entities_set.append(list(item.values())[0][0])
                    if '?' not in list(item.values())[0][2]:
                        type_set.append(list(item.values())[0][2])
                    if list(item.values())[0][1] != '':
                        relations_set.append(list(item.values())[0][1])
                e_index = 1
                r_index = 1
                t_index = 1
                for e in entities_set:
                    entities_dict[e] = "ENTITY{0}".format(e_index)
                    e_index += 1
                for r in relations_set:
                    relations_dict[r] = "RELATION{0}".format(r_index)
                    r_index += 1
                for t in type_set:
                    types_dict[t] = "TYPE{0}".format(t_index)
                    t_index += 1
                str_action = question['ID']
                for item in json_action:
                    str_action += ' '
                    str_action += str(list(item.keys())[0])
                    str_action += ' ( '
                    if list(item.values())[0][0] in entities_dict.keys():
                        str_action += entities_dict[list(item.values())[0][0]]
                        str_action += ' '
                    if list(item.values())[0][1] in relations_dict.keys():
                        str_action += relations_dict[list(item.values())[0][1]]
                        str_action += ' '
                    if list(item.values())[0][2] in types_dict.keys():
                        str_action += types_dict[list(item.values())[0][2]]
                        str_action += ' '
                    str_action += ')'

                str_question = question['ID']+" "
                input_question = '<E> '
                for e in entities_dict.values():
                    input_question += e
                    input_question += ' '
                input_question += '</E> <R> '
                for r in relations_dict.values():
                    input_question += r
                    input_question += ' '
                str_question += '</R> <T> '
                for t in types_dict.values():
                    input_question += t
                    input_question += ' '
                input_question += '</T> '
                str_txt = question['machine_question'].lower().translate(str.maketrans('', '', string.punctuation))
                input_question += str_txt
                str_question += input_question
                #获取问题答案列表
                answer_list = []
                for answer in question['answers']:
                    answer_list.append(answer['answer_id'])
                answer_str = ', '.join(answer_list)
                Annotation_temp = {
                    'entity_mask':entities_dict,
                    'relation_mask':relations_dict,
                    'type_mask':types_dict,
                    'response_entities':answer_list,
                    'orig_response':answer_str,
                    'response_bools':[],
                    'input':input_question,
                    'question':str_txt,
                    'compositionality_type':question['compositionality_type'],
                    'int_mask':{}
                }
                Annotation_Entity_Relation_Type.write("\""+question['ID']+"\""+':'+'\n')
                if count_dict != 19677:
                    Annotation_Entity_Relation_Type.write(json.dumps(Annotation_temp, indent=1)+',')
                else:
                    Annotation_Entity_Relation_Type.write(json.dumps(Annotation_temp, indent=1))
                Complex_TrainQ.write(str_question+'\n')
                Complex_TrainA.write(str_action+'\n')
        Annotation_Entity_Relation_Type.write('}')


def get_seq2seq_true_test_Complexwebqsp():
    Complex_TrainQ = open(data_dir + 'PT_test.question', 'w', encoding="UTF-8")
    Complex_TrainA = open(data_dir + 'PT_test.action', 'w', encoding="UTF-8")
    Annotation_Entity_Relation_Type = open(data_dir + 'Annotation_test.json', 'w', encoding='utf-8')
    Annotation_Entity_Relation_Type.write('{'+'\n')
    count_dict = 0
    action_file = open(data_dir+"action_result.txt", 'r', encoding="UTF-8")
    action_dict = {}
    for item in action_file:
        action_dict[item.split('\t')[0]] = item.split('\t')[1]
    with open(data_dir+'ComplexWebQuestions_dev.json', 'r', encoding="UTF-8") as train_file:
        train_json_file = json.load(train_file)
        for question in train_json_file:
            if question['ID'] in action_dict.keys():
                count_dict += 1
                entities_set = []
                entities_dict = dict()
                relations_set = []
                relations_dict = dict()
                type_set = []
                types_dict = dict()
                json_action = eval(action_dict[question['ID']])
                for item in json_action:
                    print(item)
                    if '?' not in list(item.values())[0][0]:
                        entities_set.append(list(item.values())[0][0])
                    if '?' not in list(item.values())[0][2]:
                        type_set.append(list(item.values())[0][2])
                    if list(item.values())[0][1] != '':
                        relations_set.append(list(item.values())[0][1])
                e_index = 1
                r_index = 1
                t_index = 1
                for e in entities_set:
                    entities_dict[e] = "ENTITY{0}".format(e_index)
                    e_index += 1
                for r in relations_set:
                    relations_dict[r] = "RELATION{0}".format(r_index)
                    r_index += 1
                for t in type_set:
                    types_dict[t] = "TYPE{0}".format(t_index)
                    t_index += 1
                str_action = question['ID']
                for item in json_action:
                    str_action += ' '
                    str_action += str(list(item.keys())[0])
                    str_action += ' ( '
                    if list(item.values())[0][0] in entities_dict.keys():
                        str_action += entities_dict[list(item.values())[0][0]]
                        str_action += ' '
                    if list(item.values())[0][1] in relations_dict.keys():
                        str_action += relations_dict[list(item.values())[0][1]]
                        str_action += ' '
                    if list(item.values())[0][2] in types_dict.keys():
                        str_action += types_dict[list(item.values())[0][2]]
                        str_action += ' '
                    str_action += ')'

                str_question = question['ID']+" "
                input_question = '<E> '
                for e in entities_dict.values():
                    input_question += e
                    input_question += ' '
                input_question += '</E> <R> '
                for r in relations_dict.values():
                    input_question += r
                    input_question += ' '
                str_question += '</R> <T> '
                for t in types_dict.values():
                    input_question += t
                    input_question += ' '
                input_question += '</T> '
                str_txt = question['machine_question'].lower().translate(str.maketrans('', '', string.punctuation))
                input_question += str_txt
                str_question += input_question
                #获取问题答案列表
                answer_list = []
                for answer in question['answers']:
                    answer_list.append(answer['answer_id'])
                answer_str = ', '.join(answer_list)
                Annotation_temp = {
                    'entity_mask':entities_dict,
                    'relation_mask':relations_dict,
                    'type_mask':types_dict,
                    'response_entities':answer_list,
                    'orig_response':answer_str,
                    'response_bools':[],
                    'input':input_question,
                    'question':str_txt
                }
                Annotation_Entity_Relation_Type.write("\""+question['ID']+"\""+':'+'\n')
                if count_dict != 2457:
                    Annotation_Entity_Relation_Type.write(json.dumps(Annotation_temp, indent=1)+',')
                else:
                    Annotation_Entity_Relation_Type.write(json.dumps(Annotation_temp, indent=1))
                Complex_TrainQ.write(str_question+'\n')
                Complex_TrainA.write(str_action+'\n')
        Annotation_Entity_Relation_Type.write('}')


def get_all_words():
    complex_file = open(data_dir+'ComplexWebQuestions_train.json','r',encoding='utf-8')
    dev_complex_file = open(data_dir+'ComplexWebQuestions_dev.json','r',encoding='utf-8')
    test_complex_file = open(data_dir+'ComplexWebQuestions_test.json','r',encoding='utf-8')
    share_complex_file = open(data_dir+'share.complexwebqsp.question','w',encoding='utf-8')
    json_file = json.load(complex_file)
    dev_json_file = json.load(dev_complex_file)
    test_json_file = json.load(test_complex_file)
    words = set()
    for item in json_file:
        str_txt = item['machine_question'].lower().translate(str.maketrans('', '', string.punctuation))
        for item2 in str_txt.split(' '):
            if item2 != '':
                words.add(item2)
    for item in dev_json_file:
        str_txt = item['machine_question'].lower().translate(str.maketrans('', '', string.punctuation))
        for item2 in str_txt.split(' '):
            if item2 != '':
                words.add(item2)
    for item in test_json_file:
        str_txt = item['machine_question'].lower().translate(str.maketrans('', '', string.punctuation))
        for item2 in str_txt.split(' '):
            if item2 != '':
                words.add(item2)
    action_list = {'A1', 'A3', 'A4', 'A5', '(', ')', 'ENTITY1', 'ENTITY2', 'ENTITY3', 'RELATION1', 'RELATION2',
                   'RELATION3', 'RELATION4', 'RELATION5', 'RELATION6', 'RELATION7', 'RELATION8',
                   'TYPE1', 'TYPE2', 'TYPE3', 'TYPE4', '<E>', '</E>', '<R>', '</R>', '<T>', '</T>'}
    words |= action_list
    for word in words:
        share_complex_file.write(word+'\n')

if __name__ == "__main__":
    # get_seq2seq_test_Complexwebqsp()
    # get_seq2seq_train_Complexwebqsp()
    # get_seq2seq_true_test_Complexwebqsp()
    get_seq2seq_true_train_Complexwebqsp()
    # get_all_words()