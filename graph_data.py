import os, json
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

def process_sentiments(data):
    obj = {"pleasant": [], "unpleasant": [], "neutral": [], "amt": 1}
    for segment in data:
        obj[segment[0].lower()].append(segment[1])
    
    return obj

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
    json_files = ['data1.json', 'data2.json']
    random_names = ['Charlotte', 'Lucas', 'Ava', 'Oliver', 'Amelia', 'Henry']
    dataMetaData = [{"name": "Opening"},{"name": "Agreement"},{"name": "Displeasure"},{"name": "Appointment"},{"name": "Query"},{"name": "Elucidation"}]
    scoring = [{"name": "Pleasant Welcome"},{"name": "Rate of Speech"},{"name": "Creation of Urgency"},{"name": "Process Explanation"},{"name": "Reflective Listening"},{"name": "Process Documentation Explanation"}]
    sentiment_arr = []
    call_count_arr = []
    
    for filename in json_files:
        with open(filename) as json_file:
            agent_data = json.load(json_file)
            scoring_module = agent_data['json']['scoring_module']
            call_metadata = agent_data['json']['call_metadata']
            sentiment_data = agent_data['json']['sentiment']
            name_record = scoring_module["Names"]["remark"]

            agent_name = return_agent_name(name_record, random_names)

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
            sentiment = process_sentiments(sentiment_data)
            for item in sentiment_arr:
                if(item['name'] == agent_name):
                    item["pleasant"] += sentiment["pleasant"]
                    item["unpleasant"] += sentiment["unpleasant"]
                    item["neutral"] += sentiment["neutral"]
                    agent_name_found = True
            
            if not agent_name_found:
                sentiment["name"] = agent_name
                sentiment_arr.append(sentiment)

            agent_name_found = False
            for item in call_count_arr:
                if(item['name'] == agent_name):
                    item['Number of Calls'] += 1
                    agent_name_found = True
            
            if not agent_name_found:
                call_count_arr.append({"name": agent_name, 'Number of Calls': 1})
    
    dataMetaData = final_process(dataMetaData)
    scoring = final_process(scoring)
    sentiment_arr = final_process(sentiment_arr)

    print("metadata", dataMetaData)
    print("\n")
    print("------------------------------------------")

    print("scoring",scoring)
    print("\n")
    print("------------------------------------------")
    print(sentiment_arr)
    print("\n")
    print("------------------------------------------")
    print(call_count_arr)


