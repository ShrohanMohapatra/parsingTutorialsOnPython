from pprint import pprint
from sys import exit
def add(listA,x):
    if x not in listA: listA.append(x)
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
        for NonT in Nt: firstA[NonT] = [i for i in tempA[NonT]]
    return firstA
def closure(I,G,T,Nt):
    J = [p for p in I]
    first_set_list = first_set(G,T,Nt)
    while True:
        J1 = [x for x in J]
        for x in J1:
            handle = list(x[1])
            a = x[2]
            k = handle.index('.')
            if k+1!=len(handle):
                if handle[k+1] in Nt:
                    for p in G:
                        beta = ''.join(handle[m] for m in range(k+2,len(handle)))
                        b1 = list(beta+a)[0]
                        if p[0] == handle[k+1]:
                            if b1 in T:
                                new_p = (p[0],'.'+p[1],b1)
                                if new_p not in J1: J1.append(new_p)
                            elif b1 in Nt:
                                for b in first_set_list[b1]:
                                    new_p = (p[0],'.'+p[1],b if b!='' else '$')
                                    if new_p not in J1: J1.append(new_p)
        flag = True
        for x in J1:
            if x not in J:
                flag = False
                J.append(x)
        if flag: break
    return J
def goto(I,G,X,T,Nt):
    W = []
    for x in I:
        handle = list(x[1])
        k = handle.index('.')
        if k != len(handle)-1:
            if handle[k+1] == X:
                S1 = ''.join([handle[i] for i in range(k)])
                S2 = ''.join([handle[i] for i in range(k+2,len(handle))])
                W.append((x[0],S1+X+'.'+S2,x[2]))
    return closure(W,G,T,Nt)
def items(G,T,Nt):
    C = [ closure([(G[0][0],'.'+G[0][1],'$')],G,T,Nt) ]
    action = {}
    goto_k = {}
    reduction_states = {}
    while True:
        C1 = [ I for I in C ]
        for I in C1:
            for X in T:
                goto_list = goto(I,G,X,T,Nt)
                if len(goto_list)!=0 and goto_list not in C1:
                    C1.append(goto_list)
                    if C1.index(I) not in action: action[C1.index(I)] = {}
                    if X not in action[C1.index(I)]:
                        action[C1.index(I)][X] = C1.index(goto_list)
                elif goto_list in C1:
                    if C1.index(I) not in action: action[C1.index(I)] = {}
                    if X not in action[C1.index(I)]:
                        action[C1.index(I)][X] = C1.index(goto_list)
        for I in C1:
            for X in Nt:
                goto_list = goto(I,G,X,T,Nt)
                if len(goto_list)!=0 and goto_list not in C1:
                    C1.append(goto_list)
                    if C1.index(I) not in goto_k: goto_k[C1.index(I)] = {}
                    if X not in goto_k[C1.index(I)]:
                        goto_k[C1.index(I)][X] = C1.index(goto_list)
                elif goto_list in C1:
                    if C1.index(I) not in goto_k: goto_k[C1.index(I)] = {}
                    if X not in goto_k[C1.index(I)]:
                        goto_k[C1.index(I)][X] = C1.index(goto_list)
        flag = True
        for x in C1:
            if x not in C:
                flag = False
                C.append(x)
        if flag: break
    for state in range(len(C)):
        reduction_states[state] = {}
        for production in C[state]:
            if production[1][len(production[1])-1] == '.':
                rhs = list(production[1])
                del rhs[-1]
                rhsStr = ''.join(i for i in rhs)
                Pp = (production[0],rhsStr)
                reduction_states[state][production[2]] = Pp
    accept_state = 0
    for x in reduction_states:
        if '$' in reduction_states[x]:
            if reduction_states[x]['$'] == G[0]:
                accept_state = x
                break
    return action,goto_k,reduction_states,accept_state
def driver():
    fileHandle = open('grammar14.txt')
    G,T,Nt = import_grammar(fileHandle)
    print T,Nt
    action_list,goto_list,reduction_states,accept_state = items(G,T,Nt)
    print 'Action list'
    pprint(action_list)
    print 'Goto list'
    pprint(goto_list)
    print 'Reduction states'
    pprint(reduction_states)
    print 'Accept state',accept_state
    stack = [0]
    input_str = raw_input('Enter some string ')+'$'
    i,top = 0,0
    # LR(1) AUTOMATON PARSING 
    while True:
        s = stack[top]
        try:
            print s,stack,input_str[i] if i != len(input_str) else 'Finish',
            if s == accept_state and input_str[i]=='$':
                print 'accept'
                break
            elif len(reduction_states[s]) != 0 and input_str[i] in reduction_states[s]:
                A,beta = reduction_states[s][input_str[i]]
                print 'reduce',A,'->',beta
                for j in range(len(beta)): del stack[top]
                t = stack[top]
                stack.insert(top,goto_list[t][A])
            else:
                a = input_str[i]
                stack.insert(top,action_list[s][a])
                print 'shift',action_list[s][a]
                i = i + 1
        except:
            print 'Syntax error'
            break
driver()