import sys 
import math 
args = sys.argv 
train = args[1]
output = args[2]

with open(train, "r") as f_in: 
    trainData = f_in.readlines()

def majorityVote(d):
    sum= 0
    for line in d[1:]:
        sum += int(line[-2])
    if sum< (len(d)-1)/2:
        return 0
    return 1 

def error(data):
    trainError= 0 
    prediction= str(majorityVote(data))
    for lines in trainData[1:]:
        if lines[-2]!= prediction:
            trainError+=1
    rate = trainError/(len(data)-1)

    return rate 

def entropy(data):
    sumOne = 0
    for line in data[1:]:
        sumOne += int(line[-2])
    pOne= sumOne/(len(data)-1)
    pZero= 1-pOne
    entropy= -(pOne*math.log2(pOne)) - pZero*math.log2(pZero)
    return entropy 

with open(output, "w") as f_out:
    errorRate= error(trainData)
    entropyd= entropy(trainData)
    f_out.write("entropy: "+ str(entropyd)+ "\n")
    f_out.write("error: "+ str(errorRate)+ "\n")
    

result= -(0.5*math.log2(0.5)) - 0.5*math.log2(0.5)
print(result)

