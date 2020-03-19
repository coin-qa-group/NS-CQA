# -*- coding: utf-8 -*-
import json
import sys
sys.path.insert(0, '../SymbolicExecutor/')
from symbolics_webqsp import Symbolics_WebQSP

b_print = True
LINE_SIZE = 100000
special_counting_characters = {'-','|','&'}

# action sequence
class Action():
    def __init__(self, action_type, e, r, t):
        self.action_type = action_type
        self.e = e
        self.r = r
        self.t = t

    def to_str(self):
        return "{{\'{0}\':[\'{1}\', \'{2}\', \'{3}\']}}".format(self.action_type, self.e, self.r, self.t)

class Qapair(object):
    def __init__(self, question, answer, sparql):
        self.question = question
        self.answer = answer
        self.sparql = sparql

    def obj_2_json(obj):
        return {
            "question": obj.question,
            "answer": obj.answer,
            "sparql": obj.sparql,
        }

class WebQSP(object):
    def __init__(self, id, question, action_sequence_list, entity, relation, type, entity_mask, relation_mask, type_mask, mask_action_sequence_list, answerlist):
        self.id = id
        self.question = question
        self.action_sequence_list = action_sequence_list
        self.entity = entity
        self.relation = relation
        self.type = type
        self.entity_mask = entity_mask
        self.relation_mask = relation_mask
        self.type_mask = type_mask
        self.mask_action_sequence_list = mask_action_sequence_list
        self.answerlist = answerlist

    def obj_2_json(obj):
        return {
            obj.id: {
                "question": obj.question,
                "action_sequence_list": obj.action_sequence_list,
                "entity": obj.entity,
                "relation": obj.relation,
                "type": obj.type,
                "entity_mask": obj.entity_mask,
                "relation_mask": obj.relation_mask,
                "type_mask": obj.type_mask,
                "mask_action_sequence_list": obj.mask_action_sequence_list,
                "answers": obj.answerlist,
            }
        }

    def get_webqsp_set_item(self, annotationPath, origPath):
        setitem = {}
        annotation_list = list()
        orig_list = list()
        question_dict = {}
        with open(annotationPath, 'r', encoding="UTF-8") as infile:
            count = 0
            while True:
                lines_gen = list(islice(infile, LINE_SIZE))
                if not lines_gen:
                    break
                for line in lines_gen:
                    annotation_list.append(line.strip())
                count = count + 1
                print(count)
        with open(origPath, 'r', encoding="UTF-8") as infile:
            count = 0
            while True:
                lines_gen = list(islice(infile, LINE_SIZE))
                if not lines_gen:
                    break
                for line in lines_gen:
                    orig_list.append(line.strip())
                count = count + 1
                print(count)
        count = 0
        # Each question is corresponding to one action sequence.
        while count < len(annotation_list):
            line_string = str(annotation_list[count]).strip()
            if str(line_string).startswith('['):
                count += 1
            else:
                string_list = str(line_string).split(' ')
                if 'simple_' in str(annotationPath):
                    ID_string = 'simple_' + string_list[0]
                elif 'logical_' in str(annotationPath):
                    ID_string = 'logical_' + string_list[0]
                elif 'quantative_' in str(annotationPath):
                    ID_string = 'quantative_' + string_list[0]
                elif 'count_' in str(annotationPath) and 'compcount_' not in str(annotationPath):
                    ID_string = 'count_' + string_list[0]
                elif 'bool_' in str(annotationPath):
                    ID_string = 'bool_' + string_list[0]
                elif 'comp_' in str(annotationPath):
                    ID_string = 'comp_' + string_list[0]
                elif 'compcount_' in str(annotationPath):
                    ID_string = 'compcount_' + string_list[0]
                elif 'compcountappro_' in str(annotationPath):
                    ID_string = 'compcountappro_' + string_list[0]
                elif 'compappro_' in str(annotationPath):
                    ID_string = 'compappro_' + string_list[0]
                question_string = ' '.join(string_list[1:])
                actionSequenceList = list()
                count += 1
                while count < len(annotation_list) and str(annotation_list[count]).strip().startswith('['):
                    actionSequence = eval(str(annotation_list[count]).strip())
                    actionSequenceList.append(actionSequence)
                    count += 1
                question_info = {}
                # Original annotation information.
                question_info.setdefault('question', question_string)
                question_info.setdefault('action_sequence_list', actionSequenceList)
                question_dict.setdefault(ID_string, question_info)

        count = 0
        while count < len(orig_list):
            if 'simple_' in str(origPath):
                ID_string = 'simple_' + str(orig_list[count]).strip()
            elif 'logical_' in str(origPath):
                ID_string = 'logical_' + str(orig_list[count]).strip()
            elif 'quantative_' in str(origPath):
                ID_string = 'quantative_' + str(orig_list[count]).strip()
            elif 'count_' in str(origPath) and 'compcount_' not in str(origPath):
                ID_string = 'count_' + str(orig_list[count]).strip()
            elif 'bool_' in str(origPath):
                ID_string = 'bool_' + str(orig_list[count]).strip()
            elif 'comp_' in str(origPath):
                ID_string = 'comp_' + str(orig_list[count]).strip()
            elif 'compcount_' in str(origPath):
                ID_string = 'compcount_' + str(orig_list[count]).strip()
            elif 'compcountappro_' in str(origPath):
                ID_string = 'compcountappro_' + str(orig_list[count]).strip()
            elif 'compappro_' in str(annotationPath):
                ID_string = 'compappro_' + str(orig_list[count]).strip()
            if ID_string in question_dict:
                question_info_new = question_dict.get(ID_string)
                entity_list = list()
                relation_list = list()
                type_list = list()
                if count + 2 < len(orig_list) and str(orig_list[count + 2]).startswith('context_entities'):
                    entity_string = str(orig_list[count + 2]).strip()
                    entity_string = entity_string.replace('context_entities:', '').strip()
                    if len(entity_string) > 0:
                        entity_list = entity_string.split(',')
                if count + 3 < len(orig_list) and str(orig_list[count + 3]).startswith('context_relations'):
                    relation_string = str(orig_list[count + 3]).strip()
                    relation_string = relation_string.replace('context_relations:', '').strip()
                    if len(relation_string) > 0:
                        relation_list = relation_string.split(',')
                if count + 4 < len(orig_list) and str(orig_list[count + 4]).startswith('context_types'):
                    type_string = str(orig_list[count + 4]).strip()
                    type_string = type_string.replace('context_types:', '').strip()
                    if len(type_string) > 0:
                        type_list = type_string.split(',')
                question_info_new.setdefault('entity', entity_list)
                question_info_new.setdefault('relation', relation_list)
                question_info_new.setdefault('type', type_list)
                entity_maskID = {}
                if len(entity_list) != 0:
                    for i, entity in enumerate(entity_list):
                        entity_maskID.setdefault(entity, 'ENTITY' + str(i + 1))
                question_info_new.setdefault('entity_mask', entity_maskID)
                relation_maskID = {}
                if len(relation_list) != 0:
                    relation_index = 0
                    for relation in relation_list:
                        relation = relation.replace('-', '')
                        if relation not in relation_maskID:
                            relation_index += 1
                            relation_maskID.setdefault(relation, 'RELATION' + str(relation_index))
                question_info_new.setdefault('relation_mask', relation_maskID)
                type_maskID = {}
                if len(type_list) != 0:
                    for i, type in enumerate(type_list):
                        type_maskID.setdefault(type, 'TYPE' + str(i + 1))
                question_info_new.setdefault('type_mask', type_maskID)
                actions = question_info_new.get('action_sequence_list')
                MASK_actions = list()
                if len(actions) > 0:
                    for action in actions:
                        MASK_action = list()
                        for dict in action:
                            MASK_dict = {}
                            for temp_key, temp_value in dict.items():
                                MASK_key = temp_key
                                MASK_value = list()
                                for token in temp_value:
                                    if '-' in token and token != '-':
                                        token_new = token.replace('-', '')
                                        if token_new in relation_maskID:
                                            MASK_value.append('-' + str(relation_maskID.get(token_new)))
                                    else:
                                        if token in entity_maskID:
                                            MASK_value.append(entity_maskID.get(token))
                                        elif token in relation_maskID:
                                            MASK_value.append(relation_maskID.get(token))
                                        elif token in type_maskID:
                                            MASK_value.append(type_maskID.get(token))
                                        elif token in special_counting_characters:
                                            MASK_value.append(token)
                                MASK_dict.setdefault(MASK_key, MASK_value)
                            MASK_action.append(MASK_dict)
                        MASK_actions.append(MASK_action)
                question_info_new.setdefault('mask_action_sequence_list', MASK_actions)
                question_dict.setdefault(ID_string, question_info_new)
            count += 5
        return question_dict
        return setitem

# parse sparql in dataset to action sequence
def processSparql(sparql_str, id="empty"):
        sparql_list = []
        untreated_list = sparql_str.split("\n")
        answer_keys = []
        index = -1
        for untreated_str in untreated_list:
            index += 1
            action_type = "A1"
            s = ""
            r = ""
            t = ""

            # remove note
            note_index = untreated_str.find("#")
            if note_index != -1:
                untreated_str = untreated_str[0:note_index]
            # remove /t
            untreated_str = untreated_str.replace("\t", "")
            untreated_str = untreated_str.strip()
            if untreated_str == '':
                continue

            if "UNION" == untreated_str:
                if b_print:
                    print("has union", id)

            if untreated_str.startswith("SELECT"):  # find answer key
                for item in untreated_str.split(" "):
                    if "?" in item:
                        answer_keys.append(item.replace(" ", ""))
            elif untreated_str.startswith("PREFIX") or "langMatches" in untreated_str:
                # ignore
                pass
            elif untreated_str.startswith("FILTER (?x != ns:"):
                # filter not equal
                action_type = "A5"
                s = "?x"
                # s = "ANSWER"
                t = untreated_str.replace("FILTER (?x != ns:", "").replace(")", "").replace(" ", "")
                action_item = Action(action_type, s, r, t)
                if isValidAction(action_item):
                    sparql_list.append(action_item)
            elif "ORDER BY" in untreated_str:
                action_type = "A8" if "ORDER BY DESC" in untreated_str else "A7"
                start_index = untreated_str.find("?")
                if start_index != -1:
                    end_index = untreated_str.find(")", start_index) if action_type == "A8" else len(untreated_str)
                    if end_index != -1:
                        var_name = untreated_str[start_index:end_index-1]
                        if index < len(untreated_list):
                            if untreated_list[index+1].startswith("LIMIT "):
                                limit_n = int(untreated_list[index+1].replace("LIMIT ", ""))
                                for to_find_var in untreated_list:
                                    if var_name in to_find_var:
                                        var_list = to_find_var.strip().split(" ")
                                        relative_var = var_list[0]
                                        relative_r = var_list[1].replace("ns:", "")
                                        action_item = Action(action_type, relative_var, relative_r, limit_n)
                                        if isValidAction(action_item):
                                            sparql_list.append(action_item)
            elif untreated_str.count("?") == 2 and ("FILTER" not in untreated_str or "EXISTS" not in untreated_str):
                action_type = "A4"  # joint
                triple_list = untreated_str.split(" ")
                if len(triple_list) == 4:
                    s = triple_list[0].replace("ns:", "")
                    r = triple_list[1].replace("ns:", "")
                    t = triple_list[2].replace("ns:", "")
                    if s != "" and r != "" and t != "":
                        action_item = Action(action_type, s, r, t)
                        if isValidAction(action_item):
                            sparql_list.append(action_item)
            elif untreated_str.count("?") == 1 and untreated_str.startswith("ns:"):
                # base action: select
                action_type = "A1"
                triple_list = untreated_str.split(" ")
                if len(triple_list) == 4:
                    s = triple_list[0].replace("ns:", "")
                    r = triple_list[1].replace("ns:", "")
                    t = triple_list[2].replace("ns:", "")
                    if s != "" and r != "" and t != "":
                        action_item = Action(action_type, s, r, t)
                        if isValidAction(action_item):
                            sparql_list.append(action_item)
            elif untreated_str.count("?") == 1 and untreated_str.startswith("?"):
                # ?x ns:a ns:b
                # if have e,  A3 : filter variable: find sub set fits the bill
                # if don't have e, A1_3 :find e
                action_type = "A3"
                triple_list = untreated_str.split(" ")
                if True:
                    s = triple_list[0].replace("ns:", "")
                    r = triple_list[1].replace("ns:", "")
                    t = triple_list[2].replace("ns:", "")
                    if s != "" and r != "" and t != "":
                        # for action in sparql_list:
                        #     if action.e == s or action.t == s:  # already has variable
                        #         action_type = "A4"
                        # special for webqsp: swap s and t ,A3->A1 "6" means single action_seq
                        # print(len(untreated_list), "length of untreated_list")
                        # if len(untreated_list) == 6:
                        #     action_type = "A1"
                        #     temp = s
                        #     s = t
                        #     t = temp
                        action_item = Action(action_type, s, r, t)
                        if isValidAction(action_item):
                            sparql_list.append(action_item)
                # print(action_item)


        # reorder list
        reorder_sparql_list = reorder(sparql_list, answer_keys)
        # reorder_sparql_list = sparql_list
        # for astr in reorder_sparql_list:
        #     print(astr.to_str())

        old_sqarql_list = []
        for item in reorder_sparql_list:
            seqset = {}
            seqlist = []
            seqlist.append(item.e)
            seqlist.append(item.r)
            seqlist.append(item.t)
            seqset[item.action_type] = seqlist
            old_sqarql_list.append(seqset)
        return old_sqarql_list

# parse sparql for value type answer
def processSparql_value(sparql_str, id="empty"):
        sparql_list = []
        untreated_list = sparql_str.split("\n")
        answer_keys = []
        value_len = len(untreated_list)
        if value_len == 8:
            value_str = untreated_list[5]
            value_str_list = value_str.split(" ")
            if len(value_str_list) == 4 and value_str_list[2] == '?x' and value_str_list[3] == '.':
                s = value_str_list[0]
                r = value_str_list[1]
                return [s, r]
        return []

def isValidAction(action_item):
    e = action_item.e
    t = action_item.t
    str_t = str(action_item.t)
    return (e.startswith("m.") or e.startswith("?"))\
           and (str_t.startswith("m.") or str_t.startswith("?") or str_t == "" or isinstance(t, int))

def reorder(sparql_list, answer_keys):
    count = 0
    final_len = len(sparql_list)
    reorder_sparql_list = []

    last_variable = ""
    # while len(sparql_list) != 0:
    for key in answer_keys:
        # has_last_select = False
        add_next_variable(sparql_list, key, reorder_sparql_list)
        # print(reorder_sparql_list)
            # contains key
            # 提取包含key并排序
            # for action_item in sparql_list:
            #     # last select action of answer key
            #     if action_item.t == key:
            #         reorder_sparql_list.append(action_item)
            #         sparql_list.remove(action_item)
            #         break
            #
            #         if action_item.e.startswith('?'):
            #             last_variable = action_item.e
            #         has_last_select = True
            #     if has_last_select:
            #         seq = action_item.to_str()
            #         print (seq)
            #         if len(sparql_list) == 1:
            #             reorder_sparql_list.append(action_item)
            #             sparql_list.remove(action_item)
            #             break
            #         if "?x" in seq:
            #             if seq.count("?") == 1:
            #                 reorder_sparql_list.append(action_item)
            #             elif seq.count("?") == 2:
            #                 reorder_sparql_list.append(action_item)
            #                 # define next variable
            #                 next_variable = action_item.e if (action_item.t == "?x") else action_item.t
            #             sparql_list.remove(action_item)
            #             break
            #         elif next_variable != "" and next_variable in seq:
            #             if seq.count("?") == 1:
            #                 reorder_sparql_list.append(action_item)
            #             elif seq.count("?") == 2:
            #                 reorder_sparql_list.append(action_item)
            #                 # define next variable
            #                 next_variable = action_item.e if (action_item.t == next_variable) else action_item.t
            #             sparql_list.remove(action_item)
            #             break
    reorder_sparql_list.reverse()
    return reorder_sparql_list

def add_next_variable(sparql_list, variable_key, reorder_sparql_list):
    for action_item in sparql_list:
        # filter_not_equal is always the last action
        if action_item.action_type == "A5":
            reorder_sparql_list.append(action_item)
            sparql_list.remove(action_item)
            break

    if variable_key == "":
        return

    variable_sql_list = []
    for sql in sparql_list:
        if variable_key == sql.e or variable_key == sql.t:
            variable_sql_list.append(sql)

    if len(variable_sql_list) == 0:
        return
    if len(variable_sql_list) == 1:
        cur_action = variable_sql_list[0]
        if cur_action == "?x" and "?" not in cur_action.t and cur_action.action_type == "A3":
            cur_action.action_type = "A1"
            e = cur_action.e
            t = cur_action.t
            cur_action.e = t
            cur_action.t = e
            reorder_sparql_list.append(sql)
            sparql_list.remove(sql)
            variable_sql_list.remove(sql)
            return

    next_variable = ""

    for sql in variable_sql_list:
        if sql.action_type == "A8" or sql.action_type == "A7":
            reorder_sparql_list.append(sql)
            sparql_list.remove(sql)
            variable_sql_list.remove(sql)

    for sql in variable_sql_list:
        if sql.action_type == "A9":
            reorder_sparql_list.append(sql)
            sparql_list.remove(sql)
            variable_sql_list.remove(sql)

    for sql in variable_sql_list:
        if sql.action_type == "A3":
            reorder_sparql_list.append(sql)
            sparql_list.remove(sql)
            variable_sql_list.remove(sql)

    for sql in variable_sql_list:
        if sql.action_type == "A4":
            # next_variable
            next_variable = sql.e
            reorder_sparql_list.append(sql)
            sparql_list.remove(sql)
            variable_sql_list.remove(sql)

    for sql in variable_sql_list:
        if sql.action_type == "A2":
            reorder_sparql_list.append(sql)
            sparql_list.remove(sql)
            variable_sql_list.remove(sql)

    for sql in variable_sql_list:
        if sql.action_type == "A1":
            reorder_sparql_list.append(sql)
            sparql_list.remove(sql)
            variable_sql_list.remove(sql)

    return add_next_variable(sparql_list, next_variable, reorder_sparql_list)

w_1 = 0.2
def calc_01_reward(answer, true_answer):
    true_reward = 0.0
    try:
        if len(true_answer) == 0:
            if len(answer) == 0:
                return 1.0
            else:
                return w_1
        else:
            right_count = 0
            for e in answer:
                if e in true_answer:
                    right_count += 1
            return float(right_count) / float(len(true_answer))
    except:
        return true_reward

w_1 = 0.2
def calc_01_reward_type(res_answer, true_answer, type = "f1"):
    true_reward = 0.0
    res_answer = set(res_answer)
    true_answer = set(true_answer)
    intersec = set(res_answer).intersection(set(true_answer))
    if len(true_answer) == 0:
        return 0.0
    if type == "jaccard":
        union = set([])
        union.update(res_answer)
        union.update(true_answer)
        true_reward = float(len(intersec)) / float(len(union))
    elif type == "recall":
        true_reward = float(len(intersec)) / float(len(true_answer))
    elif type == "f1":
        if len(res_answer) == 0:
            prec = 0.0
        else:
            prec = float(len(intersec)) / float(len(res_answer))
        rec = float(len(intersec)) / float(len(true_answer))
        if prec == 0 and rec == 0:
            true_reward = 0.0
        else:
            true_reward = (2.0 * prec * rec) / (prec + rec)
    return true_reward


def process_webqsp_RL():
    # Load WebQuestions Semantic Parses
    WebQSPList = []
    WebQSPList_Correct = []
    to_handle_list = []
    to_test_by_hand_list = []
    WebQSPList_Incorrect = []
    no_gold_answer = []
    AnswerType_Value_idlist = []
    to_add_list = []
    result_list = []
    no_x_list = []
    json_errorlist = []
    true_count = 0
    errorlist = []

    with open("WebQSPList_Correct.json", "r", encoding='UTF-8') as correct_list:
        WebQSPList_Correct = json.load(correct_list)
    with open("WebQSP.train.json", "r", encoding='UTF-8') as webQaTrain:
        load_dictTrain = json.load(webQaTrain)
    with open("WebQSP.test.json", "r", encoding='UTF-8') as webQaTest:
        load_dictTest = json.load(webQaTest)
    with open("to_handle.json", "r", encoding='UTF-8') as to_handle_file:
        to_handle_list = json.load(to_handle_file)
    with open("to_test_by_hand.json", "r", encoding='UTF-8') as to_test_by_hand_file:
        to_test_by_hand_list = json.load(to_test_by_hand_file)

    train_questions = load_dictTrain["Questions"]
    test_questions = load_dictTest["Questions"]
    all_questions = train_questions + test_questions
    small_questions = train_questions[0:9] + test_questions[0:9]

    process_questions = all_questions
    # total rewards
    total_reward = 0
    test_count = 0
    total_reward_jaccard = 0
    total_reward_precision = 0
    total_reward_recall = 0

    all_count = 0
    for parse_q in process_questions:
        question = parse_q["ProcessedQuestion"]
        for q in parse_q["Parses"]:
            id = q["ParseId"]
            # if id in WebQSPList_Correct or id in to_handle_list:
            # if id not in to_test_by_hand_list:
            #     continue
            if b_print:
                print(id)
            all_count += 1
            sparql = q["Sparql"]
            reward = 0.0
            answerList = q["Answers"]
            if len(answerList) == 0:
                print(id, "no gold answer")
                no_gold_answer.append(id)
            else:
                Answers = []
                for an in answerList:
                    Answers.append(an['AnswerArgument'])
                answer_type = answerList[0]['AnswerType']
                if answer_type == "Value":
                    AnswerType_Value_idlist.append(id)
                    sr_list = processSparql_value(sparql)
                    if len(sr_list) == 2:
                        for an in Answers:
                            to_add_list.append(str(sr_list[0] + '**' + sr_list[1] + '**' + an))
                else:
                    # assert answer_type == "Entity"
                    # continue
                    # if id == "WebQTrn-193.P0" or id == "WebQTrn-194.P0":  # test one
                    if True:  # test all
                        # test seq
                        true_answer = Answers
                        test_sparql = sparql
                        seq = processSparql(test_sparql, id)
                        if b_print:
                            print(seq)
                        symbolic_exe = Symbolics_WebQSP(seq)
                        answer = symbolic_exe.executor()
                        if b_print:
                            print("answer: ", answer)
                            print("true_answer: ", true_answer)
                        try:
                            key = "?x"
                            if key in answer:
                                res_answer = answer[key]
                                reward = calc_01_reward_type(res_answer, true_answer, "f1")
                                if b_print:
                                    print(id, reward)
                                result_list.append({id: [seq, reward]})
                                if reward != 1.0:
                                    result_list.append({id: list(res_answer)})
                                    result_list.append({id: list(true_answer)})

                                reward_jaccard = calc_01_reward_type(res_answer, true_answer, "jaccard")
                                reward_recall = calc_01_reward_type(res_answer, true_answer, "recall")
                                reward_precision = calc_01_reward_type(res_answer, true_answer, "precision")
                                test_count += 1
                                if reward == 1.0:
                                    # if get right answer, generate action sequence
                                    true_count += 1
                                    entity = set()
                                    relation = set()
                                    type = set()
                                    e_index = 1
                                    r_index = 1
                                    t_index = 1
                                    for srt in seq:
                                        for k, v in srt.items():
                                            if v[0] != "":
                                                entity.add(v[0])
                                            if v[1] != "":
                                                relation.add(v[1])
                                            if v[2] != "":
                                                type.add(v[2])
                                    entity = list(entity)
                                    relation = list(relation)
                                    type = list(type)
                                    entity_mask = dict()
                                    relation_mask = dict()
                                    type_mask = dict()
                                    for e in entity:
                                        dict_entity = {e: "ENTITY{0}".format(e_index)}
                                        entity_mask.update(dict_entity)
                                        e_index += 1
                                    for r in relation:
                                        dict_relation = {r: "RELATION{0}".format(r_index)}
                                        relation_mask.update(dict_relation)
                                        r_index += 1
                                    for t in type:
                                        dict_type = {t: "TYPE{0}".format(t_index)}
                                        type_mask.update(dict_type)
                                        t_index += 1
                                    mask_action_sequence_list = []

                                    for srt in seq:
                                        mask_set = {}
                                        masklist = []
                                        a_mask = ""
                                        e_mask = ""
                                        r_mask = ""
                                        t_mask = ""
                                        for k, v in srt.items():
                                            a_mask = k
                                            e_mask_key = v[0]
                                            r_mask_key = v[1]
                                            t_mask_key = v[2]
                                            e_mask = entity_mask[e_mask_key] if e_mask_key != "" else ""
                                            r_mask = relation_mask[r_mask_key] if r_mask_key != "" else ""
                                            t_mask = type_mask[t_mask_key] if t_mask_key != "" else ""
                                        if a_mask != "":
                                            masklist.append(e_mask)
                                            masklist.append(r_mask)
                                            masklist.append(t_mask)
                                            mask_set = {a_mask: masklist}
                                            mask_action_sequence_list.append(mask_set)
                                    if id != "" and question != "" and seq != "":
                                        correct_item = WebQSP(id, question, seq, entity, relation, type, entity_mask,
                                                              relation_mask, type_mask, mask_action_sequence_list,
                                                              answerList)
                                    # print(question)
                                    # print(answer)
                                    WebQSPList_Correct.append(id)
                                else:
                                    if b_print:
                                        print('incorrect!', reward)
                                        print("answer", answer)
                                        print("seq", seq)
                                        print("true_answer", true_answer)
                                        print("id", id)
                                        print(" ")
                                    WebQSPList_Incorrect.append(id)
                                    errorlist.append(id)
                                    json_errorlist.append(q)

                                total_reward += reward
                                total_reward_jaccard += reward_jaccard
                                total_reward_recall += reward_recall
                                total_reward_precision += reward_precision
                            else:
                                no_x_list.append(id)
                        except Exception as exception:
                            print(exception)
                            pass

    print('all_count', all_count)
    questions_count = len(process_questions)
    mean_reward_jaccard = total_reward_jaccard / questions_count
    mean_reward_recall = total_reward_recall / questions_count
    mean_reward_precision = total_reward_precision / questions_count
    mean_reward = total_reward / questions_count
    print("mean_reward_jaccard: ", mean_reward_jaccard)
    print("mean_reward_recall: ", mean_reward_recall)
    print("mean_reward_precision: ", mean_reward_precision)
    print("mean_reward_f1: ", mean_reward)
    print("{0} pairs correct".format(true_count))
    print(errorlist)

    # not x
    jsondata = json.dumps(no_x_list, indent=1)
    fileObject = open('no_x_list.json', 'w')
    fileObject.write(jsondata)
    fileObject.close()

    # result_list
    jsondata = json.dumps(result_list, indent=1)
    fileObject = open('result_list.json', 'w')
    fileObject.write(jsondata)
    fileObject.close()

    # no_gold_answer
    jsondata = json.dumps(no_gold_answer, indent=1)
    fileObject = open('no_gold_answer.json', 'w')
    fileObject.write(jsondata)
    fileObject.close()

    # AnswerType_Value_idlist
    jsondata = json.dumps(AnswerType_Value_idlist, indent=1)
    fileObject = open('AnswerType_Value_idlist.json', 'w')
    fileObject.write(jsondata)
    fileObject.close()

    # to_add_list
    jsondata = json.dumps(to_add_list, indent=1)
    fileObject = open('to_add_list.json', 'w')
    fileObject.write(jsondata)
    fileObject.close()

    # jsondata = json.dumps(WebQSPList_Correct, indent=1, default=WebQSP.obj_2_json)
    jsondata = json.dumps(WebQSPList_Correct, indent=1)
    fileObject = open('WebQSPList_Correct1.json', 'w')
    fileObject.write(jsondata)
    fileObject.close()


# Get training data for sequence2sequence.
def getTrainingDatasetForPytorch_seq2seq_webqsp():
    fwTrainQ = open('../../data/webqsp_data/mask/PT_train.question', 'w', encoding="UTF-8")
    fwTrainA = open('../../data/webqsp_data/mask/PT_train.action', 'w', encoding="UTF-8")
    fwTestQ = open('../../data/webqsp_data/mask/PT_test.question', 'w', encoding="UTF-8")
    fwTestA = open('../../data/webqsp_data/mask/PT_test.action', 'w', encoding="UTF-8")
    fwQuestionDic = open('../../data/webqsp_data/mask/dic_py.question', 'w', encoding="UTF-8")
    fwActionDic = open('../../data/webqsp_data/mask/dic_py.action', 'w', encoding="UTF-8")
    questionSet = set()
    actionSet = set()
    with open("../../data/webqsp_data/WEBQSP_ANNOTATIONS_full.json", 'r', encoding="UTF-8") as load_f:
        count = 1
        train_action_string_list, test_action_string_list, train_question_string_list, test_question_string_list = list(), list(), list(), list()
        dict_list = list()
        load_dict = json.load(load_f)
        for key, value in load_dict.items():
            try:
                actions = eval(str(value['mask_action_sequence_list']))
            except SyntaxError:
                pass
            if len(actions) > 0:
                count += 1
                action_string = ''
                action = actions[0]
                for dict in action:
                    for temp_key, temp_value in dict.items():
                        action_string += temp_key + ' ( '
                        for token in temp_value:
                            if '-' in token:
                                token = '- ' + token.replace('-','')
                            action_string += str(token) + ' '
                        action_string += ') '
                question_string = '<E> '
                entities = value['entity_mask']
                if len(entities) > 0:
                    for entity_key, entity_value in entities.items():
                        if str(entity_value) != '':
                            question_string += str(entity_value) + ' '
                question_string += '</E> <R> '
                relations = value['relation_mask']
                if len(relations) > 0:
                    for relation_key, relation_value in relations.items():
                        if str(relation_value) !='':
                            question_string += str(relation_value) + ' '
                question_string += '</R> <T> '
                types = value['type_mask']
                if len(types) > 0:
                    for type_key, type_value in types.items():
                        if str(type_value) !='':
                            question_string += str(type_value) + ' '
                question_string += '</T> '
                question_token = str(value['question']).lower().replace('?', '')
                question_token = question_token.replace(',', ' ')
                question_token = question_token.replace(':', ' ')
                question_token = question_token.replace('(', ' ')
                question_token = question_token.replace(')', ' ')
                question_token = question_token.replace('"', ' ')
                question_token = question_token.strip()
                question_string += question_token
                question_string = question_string.strip() + '\n'

                action_string = action_string.strip() + '\n'
                action_tokens = action_string.strip().split(' ')
                action_tokens_set = set(action_tokens)
                actionSet = actionSet.union(action_tokens_set)

                question_tokens = question_string.strip().split(' ')
                question_tokens_set = set(question_tokens)
                questionSet = questionSet.union(question_tokens_set)

                dict_temp = {}
                dict_temp.setdefault('q', str(key) + ' ' + question_string)
                dict_temp.setdefault('a', str(key) + ' ' + action_string)
                dict_list.append(dict_temp)

    # train_size = int(len(dict_list) * 0.95)
    train_size = int(len(dict_list))
    for i, item in enumerate(dict_list):
        if item.get('a').startswith('WebQTrn'):
            train_action_string_list.append(item.get('a'))
            train_question_string_list.append(item.get('q'))
        else:
            test_action_string_list.append(item.get('a'))
            test_question_string_list.append(item.get('q'))
    fwTrainQ.writelines(train_question_string_list)
    fwTrainA.writelines(train_action_string_list)
    fwTestQ.writelines(test_question_string_list)
    fwTestA.writelines(test_action_string_list)
    fwTrainQ.close()
    fwTrainA.close()
    fwTestQ.close()
    fwTestA.close()

    questionList = list()
    for item in questionSet:
        temp = str(item) + '\n'
        if temp != '\n':
            questionList.append(temp)
    actionList = list()
    for item in actionSet:
        temp = str(item) + '\n'
        if temp != '\n':
            actionList.append(temp)
    fwQuestionDic.writelines(questionList)
    fwActionDic.writelines(actionList)
    print("Getting webqsp seq2seq process Dataset is done!")

if __name__ == "__main__":
    print("start process webqsp dataset")
    process_webqsp_RL()
    # getTrainingDatasetForPytorch_seq2seq_webqsp()
