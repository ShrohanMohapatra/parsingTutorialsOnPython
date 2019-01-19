from pprint import pprint
def add(listA,x):
    if x not in listA: listA.append(x)
def first_set(G,T,Nt):
    firstA = {}
    tempA = {}
    for NonT in Nt: firstA[NonT] = []
    while True:
        for NonT in firstA:
            tempA[NonT] = [i for i in firstA[NonT]]
        for i in range(len(G)):
            if G[i][1] == '': add(tempA[G[i][0]],'')
            elif G[i][1][0] in Nt:
                if '' not in firstA[G[i][1][0]]:
                    for k in firstA[G[i][1][0]]: add(tempA[G[i][0]],k)
                else:
                    listA = [ k for k in firstA[G[i][1][0]] ]
                    r = listA.index('')
                    del listA[r]
                    for k in listA: add(tempA[G[i][0]],k)
                    add(tempA[G[i][0]],'')
            elif G[i][1][0] in T: add(tempA[G[i][0]],G[i][1][0])
        flag = True
        for NonT in Nt: flag = flag and (tempA[NonT] == firstA[NonT])
        if flag: break
        else: print tempA; print firstA; print '---------------'
        for NonT in Nt: firstA[NonT] = [i for i in tempA[NonT]]
    return firstA
def follow_set(G,S,T,Nt):
    followA = {}
    tempA = {}
    for NonT in Nt: followA[NonT] = ['$'] if NonT == S else []
    first_set_list = first_set(G,T,Nt)
    while True:
        for NonT in followA:
            tempA[NonT] = [i for i in followA[NonT]]
        for production in G:
            Aj,rhs = production[0],list(production[1])
            for i in range(len(rhs)):
                Ai = rhs[i]
                if Ai in Nt:
                    if i+1 == len(rhs): w = ''
                    else: w = rhs[i+1]
                    if w == '' or (w in Nt and '' in first_set_list[w]):
                        for k in followA[Aj]: add(tempA[Ai],k)
                    if w in T: add(tempA[Ai],w)
                    if w in Nt:
                        for k in first_set_list[w]: add(tempA[Ai],k) if k!='' else add(tempA[Ai],'$')
            flag = True
        for NonT in Nt: flag = flag and (tempA[NonT] == followA[NonT])
        if flag: break
        else: print tempA; print followA; print '//////////////'
        for NonT in Nt: followA[NonT] = [i for i in tempA[NonT]]
    return followA
def import_grammar(fileHandle):
    G,T,Nt = [],[],[]
    for lines in fileHandle:
        production = lines.split(' -> ')
        if production[0] not in Nt: Nt.append(production[0])
        listStr = list(production[1])
        del listStr[-1]
        production[1] = ''.join(i for i in listStr)
        for char in production[1]:
            if 65<=ord(char) and ord(char)<= 90:
                if char not in Nt: Nt.append(char)
            else:
                if char not in T: T.append(char)
        if production not in G: G.append((production[0],production[1]))
    T.append('$')
    return G,T,Nt
filename = raw_input('Enter the file name ')+'.txt'
fileHandle = open(filename)
G,T,Nt = import_grammar(fileHandle)
pprint(G)
print T,Nt
print 'First set calc'
first_set_list = first_set(G,T,Nt)
print 'Follow set calc'
follow_set_list = follow_set(G,G[0][0],T,Nt)
print 'First'
print first_set_list
print 'Follow'
pprint(follow_set_list)