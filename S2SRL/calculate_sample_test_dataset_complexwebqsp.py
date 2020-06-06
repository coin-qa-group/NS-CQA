'''Get all questions, annotated actions, entities, relations, types together in JSON format.
'''

import json
from symbolics_webqsp_novar import Symbolics_WebQSP_novar
# from transform_util import transformBooleanToString, list2dict
import logging

data_dir = './data/complexWeb/'
prediction_dir = './data/complexwebqsp/complexwebqsp_test_result/'

def dedupe(items):
    seen = set()
    for item in items:
        if item not in seen:
            yield item
            seen.add(item)

def list2dict(list):
    final_list = []
    temp_list = []
    new_list = []
    action_list = []
    left_count, right_count, action_count = 0, 0, 0
    for a in list:
        if a.startswith("A"):
            action_count+=1
            action_list.append(a)
        if (a == "("):
            new_list = []
            left_count+=1
            continue
        if (a == ")"):
            right_count+=1
            if ("-" in new_list and new_list[-1] != "-"):
                new_list[new_list.index("-") + 1] = "-" + new_list[new_list.index("-") + 1]
                new_list.remove("-")
            if (new_list == []):
                new_list = ["", "", ""]
            if (len(new_list) == 1):
                new_list = [new_list[0], "", ""]
            if ("&" in new_list):
                new_list = ["&", "", ""]
            if ("-" in new_list):
                new_list = ["-", "", ""]
            if ("|" in new_list):
                new_list = ["|", "", ""]
            temp_list.append(new_list)
            # To handle the error when action sequence is like 'A1 (Q1,P1,Q2) A2 Q3,P2,Q4)'.
            new_list = []
            continue
        if not a.startswith("A"):
            if a.startswith("E"):  a = "Q17"
            if a.startswith("T"):  a = "Q17"
            new_list.append(a)

    # To handle the error when action sequence is like 'A1 Q1,P1,Q2) A2(Q3,P2,Q4', 'A1(Q1,P1,Q2 A2(Q3,P2,Q4)'.
    number_list = [left_count, right_count, len(action_list), len(temp_list)]
    set_temp = set(number_list)
    # The value of multiple numbers is same.
    if len(set_temp) == 1:
        for action, parameter_temp in zip(action_list, temp_list):
            final_list.append({action: parameter_temp})
    # print("final_list", final_list)
    return final_list

def eval_Action():
    with open(data_dir+"Annotation_test.json", 'r') as load_f, open(prediction_dir+"pt_predict.actions", 'r') as predict_actions\
        , open(data_dir+"PT_test.question", 'r') as RL_test:
        load_dict = json.load(load_f)
        num = 0
        total_precision = 0
        total_recall = 0
        total_jaccard = 0
        total_f1 = 0
        total_right_count = 0
        total_answer_count = 0
        total_response_count = 0
        bool_right_count = 0
        count_right_count = 0
        for x, y in zip(predict_actions, RL_test):
            action = x.strip().split(":")[1]
            id = y.strip().split(" ")[0]
            if True:
                num += 1
                entity_mask = load_dict[id]["entity_mask"] if load_dict[id]["entity_mask"] != None else {}
                relation_mask = load_dict[id]["relation_mask"] if load_dict[id]["relation_mask"] != None else {}
                type_mask = load_dict[id]["type_mask"] if load_dict[id]["type_mask"] != None else {}
                response_entities = load_dict[id]["response_entities"]
                # orig_response = load_dict[id]["orig_response"].strip() if load_dict[id]["orig_response"] != None else ""
                # Update(add) elements in dict.
                entity_mask.update(relation_mask)
                # entity_mask.update(type_mask)
                new_action = list()
                # Default separator of split() method is any whitespace.
                for act in action.split():
                    for k, v in entity_mask.items():
                        if act == v:
                            act = k
                            break
                        else:
                            for k, v in type_mask.items():
                                if act == v:
                                    act = k
                                    break
                    new_action.append(act)
                '''print("{0}: {1}->{2}".format(num, id, action))'''
                logging.info("%d: %s -> %s", num, id, action)
                # print(" ".join(new_action))
                symbolic_seq = list2dict(new_action)
                del_element = ['#UNK', '']
                # print(symbolic_seq)
                for item in symbolic_seq:
                    temp_list = list(dedupe(list(item.values())[0]))
                    for element in temp_list:
                        if element in del_element:
                            temp_list.remove(element)
                    item[list(item.keys())[0]] = temp_list
                # print(symbolic_seq)
                symbolic_exe = Symbolics_WebQSP_novar(symbolic_seq)
                answer = symbolic_exe.executor()
                # print(answer)
                # print(response_entities)
                # if answer != {}:
                #     # print(answer.values())
                #     if list(answer.values())[0] != [] and list(answer.values())[0] != set():
                #         # print(id)
                #         # print(symbolic_seq)
                #         # print(response_entities)
                #         print(answer)
                #         print(response_entities)
                #         print(id)
                #         print(symbolic_seq)
                #         print('*'*80)
                # if answer == {} or list(answer.values())[0] == [] or list(answer.values())[0] == set():
                #     print(answer)
                #     print(response_entities)
                #     print(id)
                #     print(symbolic_seq)
                #     print('*'*80)
                # if num == 50:
                #     break
                answer_list = []
                if answer != {}:
                    if list(answer.values())[0] != [] and list(answer.values())[0] != set():
                        answer_list = list(answer.values())[0]
                right_count = 0
                for e in response_entities:
                    if e in answer_list:
                        right_count += 1
                total_right_count += right_count
                total_answer_count += len(answer)
                total_response_count += len(response_entities)

                # precision
                precision = right_count / float(len(answer)) if len(answer_list) != 0 else 0
                total_precision += precision

                # recall
                recall = (right_count / float(len(response_entities))) if len(response_entities) != 0 else 0
                total_recall += recall

                # jaccard
                intersec = set(response_entities).intersection(set(answer_list))
                union = set([])
                union.update(response_entities)
                union.update(answer_list)
                jaccard = float(len(intersec)) / float(len(answer_list)) if len(answer_list) != 0 else 0
                total_jaccard += jaccard

                # f1
                f1 = float(len(intersec))/float(len(response_entities)) if len(response_entities) != 0 else 0
                total_f1 += f1
                if num%500 ==0:
                    print(total_f1/num)
        #
        #         '''print("orig:", len(response_entities), "answer:", len(answer), "right:", right_count)
        #         print("Precision:", precision),
        #         print("Recall:", recall)
        #         print("Recall:", jaccard)
        #         print('===============================')'''
        #         logging.info("orig:%d, answer:%d, right:%d", len(response_entities), len(answer), right_count)
        #         logging.info("Precision:%f", precision)
        #         logging.info("Recall:%f", recall)
        #         logging.info("Jaccard:%f", jaccard)
        #         logging.info("F1:%f", f1)
        #         logging.info("============================")
        # #
        # # # print answer
        # # mean_pre = total_precision / num
        # # mean_recall = total_recall / num
        # # mean_jaccard = total_jaccard / num
        mean_f1 = total_f1 / num
        print(mean_f1)
        # mean_pre2 = float(total_right_count) / total_answer_count
        # mean_recall2 = float(total_right_count) / total_response_count
        # string_mean_pre = "state::mean_pre::mean_recall -> %s::%f::%f" %(state, mean_pre, mean_recall)
        # string_mean_pre2 = "state::mean_pre2::mean_recall2 -> %s::%f::%f" %(state, mean_pre2, mean_recall2)
        # print(string_mean_pre)
        # print(string_mean_pre2)
        # print("++++++++++++++")
        # logging.info("state::mean_pre::mean_recall -> %s::%f::%f", state, mean_pre, mean_recall)
        # logging.info("state::mean_pre2::mean_recall2 -> %s::%f::%f", state, mean_pre2, mean_recall2)
        # logging.info("++++++++++++++")
        # linelist.append(string_mean_pre + '\r\n')
        # linelist.append(string_mean_pre2 + '\r\n')
        # linelist.append('++++++++++++++\n\n')
        # return linelist

if __name__ == "__main__":
    eval_Action()