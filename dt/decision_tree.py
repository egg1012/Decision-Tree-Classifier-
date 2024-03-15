#import argparse
import sys 
import math

args = sys.argv
train = args[1]
test = args[2]
maxDepth= int(args[3])
trainOut = args[4]
testOut = args[5]
metricsOut= args[6]
printing= args[7]

with open(train, "r") as f_in: 
    trainData = f_in.readlines()

with open(test, "r") as f_in: 
    testData = f_in.readlines()

def partition(data, val, attribute, instances):
    result= []
    for i in instances:
        if int(data[i][2*attribute])== val:
            result.append(i)
    return result         

def entropy(data, i):
    sumOne = 0
    for val in i:
        sumOne += int(float(data[val][-2]))
    pOne= sumOne/int(len(i))
    pZero= 1-pOne
    if pZero==0 or pOne==0:
        return 0 
    x = - (pOne* math.log2(pOne) +pZero* math.log2(pZero))
    return x

def majorityVote(d, i):
    sum= 0
    for val in i:
        sum += int(d[val][-2])

    if sum>= (int(len(i))/2):
        return 1
    return 0

def mutualInfo(data, a1, a2, instances):
    #a1, a2 are the column indices of the things we are interested in. 
    # they range from [0, len(lines))
    pOnepZero= 0 
    pOnepOne= 0 
    pZeropOne= 0 
    pZeropZero= 0
    a1One= 0 
    a2One= 0
    a1Zero= 0 
    a2Zero= 0 
    for val in instances:
        if int(data[val][2*a1])==1:
            a1One+=1
            if int(data[val][a2])==0:
                a2Zero+=1
                pOnepZero+=1
            else:
                a2One+=1
                pOnepOne+=1
        elif int(data[val][2*a1])==0:
            a1Zero+=1
            if int(data[val][a2])==1:
                a2One+=1
                pZeropOne+=1
            else:
                a2Zero+=1
                pZeropZero+=1
    one= 0 

    if pOnepOne!= 0 and a1One != 0 and a2One != 0:
        one=(pOnepOne/int(len(instances)))*math.log2((pOnepOne/int(len(instances)))/((a1One*a2One)/int(len(instances))**2))
    two= 0 
    if pOnepZero!= 0 and a1One != 0 and a2Zero != 0:
        two = (pOnepZero/int(len(instances)))*math.log2((pOnepZero/int(len(instances)))/((a1One*a2Zero)/int(len(instances))**2))
    three= 0 
    if pZeropZero!= 0 and a1Zero != 0 and a2Zero != 0:
        three =(pZeropZero/int(len(instances)))*math.log2((pZeropZero/int(len(instances)))/((a1Zero*a2Zero)/int(len(instances))**2))
    four= 0 
    if pZeropOne!= 0 and a1Zero != 0 and a2One != 0:
        four =(pZeropOne/int(len(instances)))*math.log2((pZeropOne/int(len(instances)))/((a1Zero*a2One)/int(len(instances))**2))
    res= one+two+three+four
    return res 

class Node:
    def __init__(self, attrList, instances, currDepth, isLeaf):
        self.daddy= None 
        self.attrList= attrList # a list of remaining attributes 
        self.instances= instances # a list of remaining instances LIST LIST LIST 
        self.isLeaf= isLeaf
        self.left = None
        self.right = None
        self.attr = None # the attribute, an integer. 
        self.majority = None # the thing to return when evaluating tree 
        self.currDepth= currDepth#current depth

  
def makeTree(node, data, maxDepth):
    if maxDepth == 0:
        return None
    if (node.currDepth==maxDepth):
        node.isLeaf=True 
        node.majority= majorityVote(data, node.instances)
        return 
    else:
        bestMutualInfo= 0 
        bestAttribute= 0 
        for i in node.attrList:
            tmpMI= mutualInfo(data,i, -2, node.instances)
            if tmpMI>bestMutualInfo:
                bestMutualInfo= tmpMI 
                bestAttribute= i 
        if bestMutualInfo==0:
            node.isLeaf= True 
            node.majority= majorityVote(data, node.instances)
            return 
        else:
            node.attr= bestAttribute
            left= Node(node.attrList, partition(data, 0, node.attr, node.instances), node.currDepth+1, False)
            right= Node(node.attrList, partition(data, 1, node.attr, node.instances), node.currDepth+1, False)

            left.daddy=node 
            right.daddy=node 

            node.left = left
            node.right= right
            makeTree(left, data, maxDepth)
            makeTree(right, data, maxDepth)

def train(data, maxDepth):
    if maxDepth == 0:
        return majorityVote(data[1:], [i for i in range(len(data)-1)])
    root= Node([x for x in range(0, int(len(data[2])/2)-1)], [x for x in range(1, int(len(data)))], 0, False)
    makeTree(root, data, maxDepth)
    return root

## evaluates for a single instance in the test Data
def eval(trainData, testData, instance, maxDepth):
    thing= train(trainData, maxDepth)
    if type(thing) == int:
        return thing
    case = testData[int(instance)]
    while thing.isLeaf ==False:
        attribute= thing.attr
        if int(case[attribute*2])==1:
            thing=thing.right 
        else:
            thing=thing.left 
    return thing.majority 

def testError(trainData, testData, maxDepth):
    error=0
    for i in range(len(testData)):
        res= eval(trainData, testData, i, maxDepth)
        if res!= int(testData[i][-2]):
            error+=1
    rate= error/int(len(testData))
    return rate 
##### PRINTINGGGGG 
def bracketText(data, instances):
    numOnes= 0 
    for val in instances:
        numOnes+= int(data[val][-2])
    numZeroes= int(len(instances))-numOnes
    res = f"[{numZeroes} 0/{numOnes} 1]"
    return res 

result = []

def printTree(node, labels, num, data, str):
    if node == None:
        return
    if node.isLeaf==True:
        result.append(f"{str*(node.currDepth)}{labels[node.daddy.attr]} = {num}: {bracketText(data, node.instances)}")
        return 
    else:
        if node.left!= None:
            result.append(f"{str*(node.currDepth)}{labels[node.daddy.attr]} = {num}: {bracketText(data, node.instances)}")
            printTree(node.left, labels,0 , data, str)
        if node.right!= None:
            printTree(node.right, labels,1, data, str)

def print_tree(data, maxDepth):
    node= train(trainData, maxDepth)
    if type(node) != Node:
        return 
    labels= data[0].split()
    labels.pop()
    str="| "
    result.append(bracketText(data, node.instances))
    printTree(node.left, labels, 0, data, str)
    printTree(node.right, labels, 1, data, str)

print_tree(trainData, maxDepth)

#WRITING STUFF 
with open(trainOut, "w") as f_out:
    for i in range(1, len(trainData)):
        f_out.write(str(eval(trainData, trainData, i, maxDepth))+'\n')

with open(testOut, "w") as f_out:
    for i in range(1, len(testData)):
        f_out.write(str(eval(trainData, testData, i, maxDepth))+'\n')

with open(metricsOut, "w") as f_out:
    f_out.write('error(train): '+ str(testError(trainData[1:], trainData[1:], maxDepth))+ '\n')
    f_out.write('error(test): '+ str(testError(trainData[1:], testData[1:], maxDepth))+ '\n')

with open(printing, "w") as f_out:
    for val in result:
        f_out.write(val + '\n')


'''
if __name__ == '__main__':


    # This takes care of command line argument parsing for you!
    # To access a specific argument, simply access args.<argument name>.
    # For example, to get the train_input path, you can use `args.train_input`.
    parser = argparse.ArgumentParser()
    parser.add_argument("train_input", type=str, help='path to training input .tsv file')
    parser.add_argument("test_input", type=str, help='path to the test input .tsv file')
    parser.add_argument("max_depth", type=int, 
                        help='maximum depth to which the tree should be built')
    parser.add_argument("train_out", type=str, 
                        help='path to output .txt file to which the feature extractions on the training data should be written')
    parser.add_argument("test_out", type=str, 
                        help='path to output .txt file to which the feature extractions on the test data should be written')
    parser.add_argument("metrics_out", type=str, 
                        help='path of the output .txt file to which metrics such as train and test error should be written')
    parser.add_argument("print_out", type=str,
                        help='path of the output .txt file to which the printed tree should be written')
    args = parser.parse_args()
    
    #Here's an example of how to use argparse
    print_out = args.print_out

    #Here is a recommended way to print the tree to a file
    # with open(print_out, "w") as file:
    #     print_tree(dTree, file)
'''
print(math.log10(46/5))