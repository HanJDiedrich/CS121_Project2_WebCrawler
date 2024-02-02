def sortFreq(freqMap): #parameter: dictionary
    #Convert to a list of tuples
    unordered = []
    for key, value in freqMap.items():
        temp = (key, value)
        unordered.append(temp) 
    
    
    #sorted by frequency (tuples)
    ordered = selectionSort(unordered)
    
    #sort alphabetically for ties
    maxFreq = ordered[0][1]
    #big list
    orderedWords = []
    for i in range(maxFreq, 0, -1):
        #locate all words with i frequency:
        words = []
        for j in ordered:
            if j[1] == i:
                words.append(j[0])
        #sort alphabetically
        words.sort()       
        for k in words:
            #create tuple (word, freq)
            temp = (k, i)
            #add our sorted words to the big list
            orderedWords.append(temp)
    
    return orderedWords

def selectionSort(arr):
        n = len(arr)
        for i in range(n):
            min_index = i
            for j in range(i+1,n):
                if arr[min_index][1] < arr[j][1]: #descending order
                    min_index = j
            temp = arr[i]
            arr[i] = arr[min_index]
            arr[min_index] = temp
        return arr
    
mList = {'jennifer': 2, 'employmentresearch': 1, 'designsystems': 1, 'programmingembedded': 1, '3062learn': 1, 'zhenpinw': 1, 'zhenping': 1, 'wu': 13, 'xhx': 1, 'xiaohui': 1, 'xie': 3, 'biologymedical': 1, '4058learn': 1, 'yamingy': 1, 'yaming': 1, 'yu': 10, '2228learn': 1, 'zhaoxia': 2, '2214': 1, 'shz': 1, 'shuang': 1, 'zhao': 10, '4214learn': 1, 'zhengkai': 1, 'kai': 5, 'zheng': 8, '6095learn': 1, 'hziv': 1, 'hadar': 4, 'ziv': 4, '5062learn': 1, 'locate': 1, 'finance': 1, 'personnel': 3, 'sciencestaff': 1, 'informaticsstaff': 1, 'statisticsstaff': 1, 'sahar': 1, 'abdizadeh': 1, 'madina': 1, 'abdrakhmanova': 1, 'christie': 1, 'anne': 1, 'abel': 1, 'hillary': 1, 'abraham': 2, 'rohan': 1, 'achar': 1, 'ishita': 1, 'acharya': 1, 'arkadeep': 1, 'adhikari': 1, 'ramtin': 2, 'afshar': 2, 'lehar': 1, 'agarwal': 3, 'nitin': 1, 'tarun': 1, 'laleh': 1, 'aghababaie': 1, 'beni': 1, 'forest': 1, 'agostinelli': 1, 'julius': 1, 'aguma': 2, 'avinash': 2, 'nath': 1, 'aita': 1, 'fatema': 1, 'akbar': 1, 'fatimah': 1, 'abdulrahman': 2, 'alamoudi': 1, 'dalal': 1, 'naser': 1, 'alharthi': 1, 'nailah': 1, 'saleh': 2, 'alhassoun': 1, 'emmanouil': 1, 'alimpertis': 1, 'wail': 1, 'yousef': 1, 'alkowaileet': 1, 'abdulhamid': 1, 'allsaudi': 1, 'sumaya': 1, 'almanee': 1, 'sofanah': 1, 'alrobayan': 1, 'abdulaziz': 1, 'nasser': 1, 'alshayban': 1, 'anas': 1, 'tarik': 1, 'alsoliman': 1, 'sadeem': 1, 'alsudais': 1, 'anil': 1, 'altinay': 1, 'maral': 1, 'amir': 2, 'craig': 2, 'gordon': 1, 'anderson': 2, 'maria': 2, 'jose': 4, 'coto': 1, 'marshall': 1, 'hina': 3, 'arora': 2, 'shivam': 3, 'reza': 3, 'asadi': 2, 'chinmayee': 1, 'milind': 2, 'athalye': 1, 'bhanu': 1, 'kiran': 1, 'atturu': 1, 'bache': 1, 'graham': 1, 'bachelder': 1, 'shreyas': 1, 'badiger': 1, 'mahadev': 1, 'hoon': 1, 'bae': 1, 'qiushi': 1, 'sabur': 1, 'hassan': 1, 'baidya': 1, 'kanika': 1, 'baijal': 1, 'evita': 1, 'zoi': 1, 'bakopoulou': 1, 'ashwin': 1, 'balachandran': 1, 'smitha': 1, 'balagurunatan': 1, 'armin': 1, 'balalaie': 1, 'baldwin': 3, 'sahil': 1, 'bansal': 1, 'akshay': 1, 'sudhir': 1, 'bapat': 1, 'caio': 1, 'batista': 1, 'melo': 1, 'damon': 1, 'bayer': 1, 'benedict': 3, 'brandon': 1, 'berman': 1, 'olivia': 4, 'marie': 4, 'bernstein': 4, 'juan': 2, 'besa': 2, 'vial': 1, 'mukul': 1, 'bhardwaj': 1, 'abhijeet': 1, 'suresh': 1, 'bhute': 1, 'dharshan': 1, 'birur': 1, 'jayaprabhu': 1, 'chad': 1, 'bloxham': 1, 'boyd': 3, 'tatiana': 1, 'bradley': 2, 'kathryn': 1, 'barrett': 1, 'brewster': 1, 'jeffrey': 7, 'bryan': 5 }
#print(mList)
sortedWords = {}
for word, freq in sorted(mList.items(), key=lambda x: -x[1]):
    sortedWords[word] = freq

top50 = []
topCount = 0
for key, value in sortedWords.items():
    #print(f"{key}: {value}")
    top50.append(key)
    topCount += 1
    if topCount == 50:
        break
print(top50)