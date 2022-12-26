import os, json, math
import string
import random
import requests


def process_call_metadata(data):
    scoring_data = {segment["name"].lower(): [] for segment in dataMetaData}

    for segment in data:
        labels_covered = set()
        for labels in segment['labels']:
            if (segment['speaker']=="Agent") and (labels.lower() in scoring_data.keys()) and (labels.lower() not in labels_covered):
                scoring_data[labels.lower()].append(segment['score'])
            labels_covered.add(labels.lower())
    return scoring_data

def process_call_scoring(data):
    scoring_data = {segment["name"].lower(): [] for segment in scoring}
    for segment_key in data.keys():
        if 'scores_sum' not in data[segment_key].keys():
            score = 0
            continue
        score = data[segment_key]['scores_sum']
        if score == '-':
            score = 0
        scoring_data[segment_key.lower()] = score
    return scoring_data

def process_sentiments(sentiment_data, agent_name):
    if agent_name not in call_sentiments.keys():
        call_sentiments[agent_name] = {}
        call_sentiments[agent_name]['ag_pleasant'] = 0
        call_sentiments[agent_name]['ag_unpleasant'] = 0
        call_sentiments[agent_name]['ag_neutral'] = 0

        call_sentiments[agent_name]['cust_pleasant'] = 0
        call_sentiments[agent_name]['cust_unpleasant'] = 0
        call_sentiments[agent_name]['cust_neutral'] = 0
        
    ag_pleasant, ag_unpleasant, ag_neutral = 0,0,0
    cust_pleasant, cust_unpleasant, cust_neutral = 0,0,0
    
    for idx,sent in enumerate(sentiment_data):
        if(speakers[idx] == "Agent"):
            if sent[0] == "Pleasant":
                ag_pleasant += 1
            if sent[0] == "Unpleasant":
                ag_unpleasant += 1
            if sent[0] == "Neutral":
                ag_neutral += 1
        else:
            if sent[0] == "Pleasant":
                cust_pleasant += 1
            if sent[0] == "Unpleasant":
                cust_unpleasant += 1
            if sent[0] == "Neutral":
                cust_neutral += 1

    print(ag_pleasant, ag_unpleasant, ag_neutral)
    print(cust_pleasant, cust_unpleasant, cust_neutral)
    print("\n")

    call_sentiments[agent_name]['ag_pleasant'] += ag_pleasant*normalizing_factor/(duration/60)
    call_sentiments[agent_name]['ag_unpleasant'] += ag_unpleasant*normalizing_factor/(duration/60)
    call_sentiments[agent_name]['ag_neutral'] += ag_neutral*normalizing_factor/(duration/60)

    call_sentiments[agent_name]['cust_pleasant'] += cust_pleasant*normalizing_factor/(duration/60)
    call_sentiments[agent_name]['cust_unpleasant'] += cust_unpleasant*normalizing_factor/(duration/60)
    call_sentiments[agent_name]['cust_neutral'] += cust_neutral*normalizing_factor/(duration/60)

def process_call_intent(call_intent_data, agent_name):
    if agent_name not in call_intents.keys():
        call_intents[agent_name] = {}
    
    for intent in call_intent_data:
        if intent not in call_intents[agent_name].keys():
            call_intents[agent_name][intent] = 0
        
        call_intents[agent_name][intent] += 1

def process_call_intent_count(call_intent_data):
    for intent in call_intent_data:
        if intent not in call_intents_count.keys():
            call_intents_count[intent] = 0
        call_intents_count[intent] += 1



def final_process(arr_obj):
    for item in arr_obj:
        for key in item.keys():
            if isinstance(item[key], list):
                item[key] = sum(item[key]) / (len(item[key]) or 1)

    return arr_obj

def return_agent_name(name_record, random_names):
    agent_name = name_record.split(",")[0].split(":")[1].strip()
    if agent_name == "NA":
        agent_name = random.choices(random_names)[0]
    
    return agent_name


if __name__ == "__main__":
    json_files = ["83f7628ba8cf4ea28c832978b84bc013.mp3",
        "2c63e672acb744ccbdc9316c33c25e87.mp3",
        "6b027c1079f04865983cc9a333eed11f.mp3",
        "f1407b84e62e470899b63a50033ac076.mp3",
        "3b90532408ba4bdf988041c6ec0028c0.mp3",
        "af34a695a7724592ad64e1aee9906939.mp3",
        "bdf4063d3735470cb5c938573589ab7d.mp3",
        "735485f476f448579a7acad9e71b6130.mp3",
        "0a61e735d06445159a12619e1ab45a6e.mp3",
        "07aa5819454d4836840b903888a069b3.mp3",
        ]
    
    file_type = "hi"
    random_en_names = ['Charlotte', 'Lucas', 'Ava', 'Oliver', 'Amelia', 'Henry','Charlotte', 'Lucas', 'Ava', 'Oliver']
    random_hindi_names = ['हिमांशु', 'संजीव', 'राजकुमार', 'प्रियंका', 'मनीष', 'सुनीता']
    dataMetaData = [{"name": "Opening"},{"name": "Agreement"},{"name": "Displeasure"},{"name": "Appointment"},{"name": "Query"},{"name": "Elucidation"}]
    scoring = [{"name": "Pleasant Welcome"},{"name": "Rate of Speech"},{"name": "Creation of Urgency"},{"name": "Process Explanation"},{"name": "Reflective Listening"},{"name": "Process Documentation Explanation"}]
    call_sentiments = {}
    call_sentiments_arr = []

    call_intents = {}
    call_intents_arr = []

    # call_intents_count = {}
    # call_intents_count_arr = []

    call_count_arr = []
    
    for i, filename in enumerate(json_files):
        headers = {
            'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjcyODA5ODE2LCJqdGkiOiJjNmQ4N2NkMzkwN2Q0OTZmOTE1NWYzOTM3NjdiMWU2ZiIsInVzZXJfaWQiOjIsInVzZXJuYW1lIjoic3VwZXJhZG1pbiIsInJvbGVfaWQiOjEsInJvbGUiOiJhZG1pbiIsIm9yZ2FuaXphdGlvbiI6ImNvdXR1cmUiLCJ2ZXJzaW9uIjoxfQ.2QTNmQQqrSJMj4Zqx_vFAgzTHvzKJ9ACd2VRJLVy3U8',
        }

        payload={}
        url = f"https://sandbox.cai-tech-prod.com/caci_backend/api/data/json/{filename}/"
        response = requests.get(url, headers=headers)
        # print(response.json())

        agent_data = response.json()
        normalizing_factor = 2
        duration = agent_data['json']['duration']
        scoring_module = agent_data['json']['scoring_module']
        speakers = agent_data["json"]["speakers"]
        call_metadata = agent_data['json']['call_metadata']
        sentiment_data = agent_data['json']['sentiment']
        call_intent = agent_data['json']['call_intent']
        
        name_record = scoring_module["Names"]["remark"]
        
        
        if(file_type == "en"):
            agent_name = random_en_names[i]
        else:
            agent_name = random_hindi_names[i]
        # agent_name = return_agent_name(name_record, random_names)
        print(agent_name)
        metadata_score = process_call_metadata(call_metadata)
        for segment in dataMetaData:
            if agent_name not in segment.keys():
                segment[agent_name] = []
            segment[agent_name] += metadata_score[segment['name'].lower()]

        
        scores = process_call_scoring(scoring_module)
        for segment in scoring:
            if agent_name not in segment.keys():
                segment[agent_name] = []
            segment[agent_name].append(scores[segment['name'].lower()])


        agent_name_found = False
        
        process_sentiments(sentiment_data, agent_name)
        process_call_intent(call_intent, agent_name)
        # process_call_intent_count(call_intent)

        agent_name_found = False
        for item in call_count_arr:
            if(item['name'] == agent_name):
                item['Number of Calls'] += 1
                agent_name_found = True
        
        if not agent_name_found:
            call_count_arr.append({"name": agent_name, 'Number of Calls': 1})
    
    dataMetaData = final_process(dataMetaData)
    scoring = final_process(scoring)
    # sentiment_arr = final_process(sentiment_arr)

    for key in call_sentiments.keys():
        obj = {}
        obj["Name"] = key
        obj["Agent Pleasant"] = round(call_sentiments[key]['ag_pleasant'])
        obj["Agent Unpleasant"] = round(call_sentiments[key]['ag_unpleasant'])
        obj["Agent Neutral"] = round(call_sentiments[key]['ag_neutral'])
        obj["Customer Pleasant"] = round(call_sentiments[key]['cust_pleasant'])
        obj["Customer Unpleasant"] = round(call_sentiments[key]['cust_unpleasant'])
        obj["Customer Neutral"] = round(call_sentiments[key]['cust_neutral'])
        call_sentiments_arr.append(obj)

    for key in call_intents.keys():
        obj = {}
        obj["Name"] = key
        for intent in call_intents[key].keys():
            obj[intent] = call_intents[key][intent]
        call_intents_arr.append(obj)

    # for key in call_intents_count.keys():
    #     obj = {}
    #     obj["Name"] = key
    #     for intent in call_intents[key].keys():
    #         obj[intent] = call_intents[key][intent]
    #     call_intents_arr.append(obj)

    # print("metadata", dataMetaData)
    # print("\n")
    # print("------------------------------------------")

    # print("scoring",scoring)
    # print("\n")
    # print("------------------------------------------")
    print(call_sentiments_arr)
    print("\n")
    print("------------------------------------------")
    # print(call_count_arr)


