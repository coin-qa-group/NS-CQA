import string
from nltk.translate import bleu_score
from nltk.tokenize import TweetTokenizer
from SymbolicExecutor.symbolics import Symbolics
from SymbolicExecutor.transform_util import list2dict, transformBooleanToString

W_1 = 0.2
W_2 = 0.8
epsilon = 0.1

def calc_bleu_many(cand_seq, ref_sequences):
    sf = bleu_score.SmoothingFunction()
    return bleu_score.sentence_bleu(ref_sequences, cand_seq,
                                    smoothing_function=sf.method1,
                                    weights=(0.5, 0.5))

def calc_True_Reward(action_sequence, qa_info):
    entity_mask = qa_info['entity_mask'] if 'entity_mask' in qa_info.keys() else {}
    relation_mask = qa_info["relation_mask"] if 'relation_mask' in qa_info.keys() else {}
    type_mask = qa_info['type_mask'] if 'type_mask' in qa_info.keys() else {}
    # Update(add) elements in dict.
    masking_elements = {**entity_mask, **relation_mask, **type_mask}
    new_action = list()
    # Default separator of split() method is any whitespace.
    for act in action_sequence:
        for k, v in masking_elements.items():
            if act == v:
                act = k
                break
        new_action.append(act)
    symbolic_seq = list2dict(new_action)
    # print (symbolic_seq)
    symbolic_exe = Symbolics(symbolic_seq)
    answer = symbolic_exe.executor()
    return calc_adaptative_reward(answer, qa_info)

def calc_01_reward(answer, qa_info):
    true_reward = 0.0
    response_entities = qa_info['response_entities'] if 'response_entities' in qa_info.keys() else []
    orig_response = qa_info['orig_response'].strip() if 'orig_response' in qa_info.keys() else ""
    qid = qa_info['qid'].strip() if 'qid' in qa_info.keys() else ""
    if qid.startswith("Quantitative Reasoning (Count) (All)_") or qid.startswith("Comparative Reasoning (Count) (All)_"):
        if not isinstance(answer, int):
            return 0.0
        if orig_response.isdigit():
            true_answer = int(orig_response)
        else:
            import re
            orig_response_temp = re.findall(r"\d+\.?\d*", orig_response)
            true_answer = sum([int(i) for i in orig_response_temp])
        if answer == true_answer:
            true_reward = 1.0
        return true_reward

    # For boolean, the returned answer is a list.
    elif qid.startswith("Verification (Boolean) (All)_"):
        # To judge the returned answers are in dict format or boolean format.
        if (type(answer) == dict):
            temp = []
            if '|BOOL_RESULT|' in answer:
                temp.extend(answer['|BOOL_RESULT|'])
                predicted_answer_string = transformBooleanToString(temp)
                if predicted_answer_string != '' and predicted_answer_string == orig_response:
                    true_reward = 1.0
        else:
            predicted_answer = ""
            if answer == True:
                predicted_answer = "YES"
            if answer == False:
                predicted_answer = "NO"
            if predicted_answer == orig_response:
                true_reward = 1.0
        return true_reward

    elif qid.startswith("Simple Question (Direct)_") or qid.startswith("Logical Reasoning (All)_") or qid.startswith("Quantitative Reasoning (All)_") or qid.startswith("Comparative Reasoning (All)_"):
        # To judge the returned answers are in dict format or boolean format.
        if type(answer) == dict:
            temp = []
            for key, value in answer.items():
                if key != '|BOOL_RESULT|' and value:
                    temp.extend(list(value))
            predicted_answer = temp

        elif type(answer) == type([]) or type(answer) == type(set([])):
            predicted_answer = sorted((list(answer)))
        elif type(answer) == int:
            predicted_answer = [answer]
        else:
            predicted_answer = [answer]
        # Solve the problem when response entities is [] and original response is 'None'.
        if orig_response == 'None':
            if len(predicted_answer) == 0:
                return 1.0
            else:
                return 0.0
        else:
            if len(response_entities) == 0:
                return W_1
            else:
                if len(predicted_answer) == 0:
                    return 0.0
                else:
                    right_count = 0
                    for e in response_entities:
                        if (e in predicted_answer):
                            right_count += 1
                    return float(right_count)/float(len(response_entities))

# TODO: NOT TESTED!
'''
Adaptive reward 是一种partial reward。
首先看问题类型是不是对的，若不对，则整个reward为0；
若对，而答案一个都不对，那么就有W_1的reward；
若type对，答案有一部分也对，再计算不同问题类型的答案正确率（答案是entities的就用F1，答案是boolean的就用准确率，答案是数字的就用s = 1-|T-P|/|T+P+ε|，为R_answer，再乘以权重W_2，这样来计算reward。
即：reward = R_type * (W_1 + W_2 * R_answer), W_1 + W_2 = 1。'''
def calc_adaptative_reward(answer, qa_info):
    response_entities = qa_info['response_entities'] if 'response_entities' in qa_info.keys() else []
    orig_response = qa_info['orig_response'].strip() if 'orig_response' in qa_info.keys() else ""
    qid = qa_info['qid'].strip() if 'qid' in qa_info.keys() else ""
    if qid.startswith("Quantitative Reasoning (Count) (All)_") or qid.startswith("Comparative Reasoning (Count) (All)_"):
        if not isinstance(answer, int):
            return 0.0
        R_type = 1.0
        if orig_response.isdigit():
            true_answer = int(orig_response)
        else:
            import re
            orig_response_temp = re.findall(r"\d+\.?\d*", orig_response)
            true_answer = sum([int(i) for i in orig_response_temp])
        # T: true_answer, P: predicted_answer, similarity s = 1-|T-P|/|T+P+ε|,ε is used to solve the problem when T or P is 0.
        R_answer = 1.0 - abs(float(true_answer - answer)) / abs(float(true_answer + answer + epsilon))
        return (R_type * (W_1 + W_2 * R_answer))

    # For boolean, the returned answer is a list.
    if qid.startswith("Verification (Boolean) (All)_"):
        # To judge the returned answers are in dict format or boolean format.
        if (type(answer) == dict):
            R_type = 1.0
            answer_list = []
            if '|BOOL_RESULT|' in answer:
                answer_list.extend(answer['|BOOL_RESULT|'])
                if len(answer_list) == 0:
                    return (R_type * W_1)
                else:
                    for i, item in enumerate(answer_list):
                        if item == True:
                            answer_list[i] = "YES"
                        elif item == False:
                            answer_list[i] = "NO"
                        else:
                            return 0.0
                    orig_response_list = orig_response.strip().split(' ')
                    true_answer_list = []
                    for token in orig_response_list:
                        if token == 'YES' or token == 'NO':
                            true_answer_list.append(token)
                    if len(true_answer_list) == 0:
                        return (R_type * W_1)
                    else:
                        if len(answer_list) <= len(true_answer_list):
                            correct_count=0.0
                            for i in range(len(answer_list)):
                                if answer_list[i] == true_answer_list[i]:
                                    correct_count+=1
                            R_answer = correct_count / float(len(true_answer_list))
                            return (R_type * (W_1 + W_2 * R_answer))
                        else:
                            # Expand the true_answer_list with duplicating the first element.
                            for i in range(len(answer_list)-len(true_answer_list)):
                                true_answer_list.append(true_answer_list[0])
                            correct_count = 0.0
                            for i in range(len(answer_list)):
                                if answer_list[i] == true_answer_list[i]:
                                    correct_count += 1
                            R_answer = correct_count / float(len(answer_list))
                            return (R_type * (W_1 + W_2 * R_answer))
        else:
            predicted_answer = ""
            if answer == True:
                predicted_answer = "YES"
            if answer == False:
                predicted_answer = "NO"
            if predicted_answer == orig_response.strip():
                return 1.0

    elif qid.startswith("Simple Question (Direct)_") or qid.startswith("Logical Reasoning (All)_") or qid.startswith(
            "Quantitative Reasoning (All)_") or qid.startswith("Comparative Reasoning (All)_"):
        # To judge the returned answers are in dict format or boolean format.
        R_type = 1.0
        if (type(answer) == dict):
            temp = []
            for key, value in answer.items():
                if key != '|BOOL_RESULT|' and value:
                    temp.extend(list(value))
            predicted_answer = temp

        elif type(answer) == type([]) or type(answer) == type(set([])):
            predicted_answer = sorted((list(answer)))
        elif type(answer) == int:
            predicted_answer = [answer]
        else:
            predicted_answer = [answer]
        # Solve the problem when response entities is [] and original response is 'None'.
        if orig_response == 'None':
            if len(predicted_answer) == 0:
                return 1.0
            else:
                return 0.0
        else:
            if len(response_entities) == 0:
                return R_type * W_1
            else:
                if len(predicted_answer) == 0:
                    return R_type * W_1
                else:
                    right_count = 0
                    for e in response_entities:
                        if (e in predicted_answer):
                            right_count += 1
                    # Compute F1 value as reward.
                    precision = float(right_count)/float(len(predicted_answer)) if len(predicted_answer) != 0 else 0
                    recall = float(right_count)/float(len(response_entities)) if len(response_entities) != 0 else 0
                    F1 = 2 * precision * recall / (recall + precision) if (precision!=0 and recall!=0) else 0
                    # TODO： NOT TESTED!
                    return (R_type * (W_1 + W_2 * F1))

def calc_bleu(cand_seq, ref_seq):
    return calc_bleu_many(cand_seq, [ref_seq])

def tokenize(s):
    return TweetTokenizer(preserve_case=False).tokenize(s)

def untokenize(words):
    return "".join([" " + i if not i.startswith("'") and i not in string.punctuation else i for i in words]).strip()
