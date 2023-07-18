import json
import numpy as np
slot_keys = ["time","climate","activity","interest_1","interest_2","budget","housing"]
slot_values = ["1. Quarter","Warm and sunny","Relaxing on the beach","History","Nature","Lower","Camping"]
slot_dict = dict(zip(slot_keys, slot_values))

map_time = {
    "1. Quarter": ["Jan", "Feb", "Mär"],
    "2. Quarter": ["Apr", "Mai", "Jun"],
    "3. Quarter": ["Jul", "Aug", "Sep"],
    "4. Quarter": ["Okt", "Nov", "Dez"]
}
map_climate = {
    "Warm and sunny": "warm",
    "Cold Weather": "kalt"
}
map_activity = {
    "Relaxing on the beach": "Strandurlaub",
    "Exploring a city": "Städtereise",
    "Experiencing adventures": "Rundreise",
    "Experiencing culture": "Kultur"
}
map_interest = {
    'History': 'Geschichte',
    'Nature': 'Natur',
    'Culture': 'Kultur',
    'Great food': 'Kulinarik',
    'Party': 'Party',
    'Wellness': 'Wellness',
    'Adventure': 'Abenteuer'
}
map_budget = {
    'Lower': 'Günstiger als Deutschland',
    'Equal': 'Durchschnitt Deutschland',
    'Higher': 'Teurer als Deutschland',
}
map_housing = {
    'Camping': 'Camping',
    'Hotel/Hostel/Vacation house': 'Ferienhaus/Hotel/Hostel',
}
map_months = {
    "Jan": "Januar",
    "Feb": "Februar",
    "Mär": "März",
    "Apr": "April",
    "Mai": "Mai",
    "Jun": "Juni",
    "Jul": "Juli",
    "Aug": "August",
    "Sep": "September",
    "Okt": "Oktober",
    "Nov": "November",
    "Dez": "Dezember"
}
with open('dataset\dataset_destination.json') as f:
    data = json.load(f) 
length=len(data['Reiseziel'])

def random_sampling(mapper):
    leng =len(mapper)
    indicies = list(mapper.keys())
    rand= np.random.randint(0,leng)
    return indicies[rand]

def bootstraping(n,categories):
    bootstrap= []
    for i in range(n):
        bootstrap.append([random_sampling(category) for category in categories])
    return bootstrap

def easy_count(key,input,mapper,length=length):
    '''checks for each destination if the activity is available and returns a list of 1 and 0'''
    return [1 if mapper[input] in data[key][str(dest)] else 0 for dest in range(length)]
def weighted_count(key, input,mapper,weight=0.5,length=length):
    '''function to weight the differing interests priorities. Otherwise same count as easy_count'''
    # Interest 1
    int_1 = [1 if mapper[input[0]] in data[key][str(dest)] else 0 for dest in range(length)]
    # Interest 2
    int_2 = [round(weight,1) if mapper[input[1]] in data[key][str(dest)] else 0 for dest in range(length)]
    return np.array(int_1) + np.array(int_2)
def evaluate_climate(key, input, mapper_a,mapper_b,length=length):
    ''''''
    # get climate score
    # iterate months of quarter
    climate = []
    rain = []
    for month in mapper_a[input[0]]:
        # get bool array with climate hit for each month
        climate.append([1 if mapper_b[input[1]] in data[key][str(dest)][month]['Klima'] else 0 for dest in range(length)])
        # get rain score for each month
        rain.append([data[key][str(dest)][month]['Regenwahrscheinlichkeit']for dest in range(length)])
    climate_sum = np.round(np.array(np.array(climate[0])+np.array(climate[1])+np.array(climate[2]))/3,1)
    rain_sum = np.round(np.array(np.array(rain[0])+np.array(rain[1])+np.array(rain[2]))/3,1)
    # Reverse Rain score - little rain is good
    rain_sum = np.absolute(1 - rain_sum)
    return climate_sum, rain_sum

def evaluate_time(key, input, mapper_a,mapper_b,length=length):
    # for each month in chosen quarter
    time= []
    for month in mapper_a[input]:
        # check if travel is recommended for that month
        time.append([1 if mapper_b[month] in data[key][str(dest)] else 0 for dest in range(length)])
    return np.round(np.array(np.array(time[0])+np.array(time[1])+np.array(time[2]))/3,1)


def compute_total(slot_dict):
    activity = np.array(easy_count(key="Reiseart",input=slot_dict['activity'],mapper=map_activity))
    budget = np.array(easy_count(key="Preisniveau",input=slot_dict['budget'],mapper=map_budget))
    housing = np.array(easy_count(key="Unterkunft",input=slot_dict['housing'],mapper=map_housing))
    interest = np.round(np.array(weighted_count(key="Interessen",input=[slot_dict['interest_1'],slot_dict['interest_2']],mapper=map_interest))/1.5,1)
    climate, rain = evaluate_climate('Klima und Regenwahrscheinlichkeit',[slot_dict['time'],slot_dict['climate']],mapper_a=map_time,mapper_b=map_climate)
    time = np.array(evaluate_time("Beste Monate zum Reisen", slot_dict['time'],mapper_a=map_time, mapper_b=map_months))
    #assert len(activity) == len(budget) == len(housing) == len(interest) == len(climate) == len(rain) == len(time), "Length of score lists not equal"
    #return np.round(np.array(activity + budget + housing + interest + np.array(climate) + np.array(rain) + time)/7,4)
    return np.round(np.array(activity+ budget + housing + interest + np.array(climate)+ np.array(rain) + time)/6,4)


def get_top5(score_list):
    sorted = np.flip(np.argsort(score_list))
    destinations = [data["Reiseziel"][str(dest)]for dest in sorted[:5]]
    scores = score_list[sorted[:5]]
    return destinations,scores


categories = [map_time,map_climate,map_activity,map_interest,map_interest,map_budget,map_housing]
categories = [map_time,map_climate,map_activity,map_interest,map_interest,map_budget,map_housing]
slot_keys = ["time","climate","activity","interest_1","interest_2","budget","housing"]
boots= bootstraping(500,categories)
means = []
varis = []
for i in range(len(boots)):
    slot_dict = dict(zip(slot_keys, boots[i]))
    comp = compute_total(slot_dict)
    means.append(np.mean(comp)*100)
    varis.append(np.var(comp)*100)
print('Mean Scores for Iterations: ',means[:5],'Variance of means: ', np.var(means))
print('Variances for Iterations: ',varis[:5], 'Mean of variances: ', np.mean(varis))
# Score upscaled to 0-100
# What do we expect: With more categories: higher variance between iterations (variance of means), higher variance within iteration (mean of variances)
#dest,scores = get_top5(compute_total(slot_dict))

#print("This is my recommendation: \n " + f'- 1. {dest[0]} - Score: {scores[0]} \n' + f'- 2. {dest[1]} - Score: {scores[1]} \n' + f'- 3. {dest[2]} - Score: {scores[2]} \n' + f'- 4. {dest[3]} - Score: {scores[3]} \n' + f'- 5. {dest[4]} - Score: {scores[4]} \n')