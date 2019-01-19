from pprint import pprint
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
    T.append('#')
    return G,T,Nt
def closure(I,G,Nt):
    J = [p for p in I]
    while True:
        J1 = [x for x in J]
        for x in J1:
            handle = list(x[1])
            k = handle.index('.')
            if k+1!=len(handle):
                if handle[k+1] in Nt:
                    for p in G:
                        if p[0] == handle[k+1]:
                            new_p = (p[0],'.'+p[1])
                            if new_p not in J1: J1.append(new_p)
        flag = True
        for x in J1:
            if x not in J:
                flag = False
                J.append(x)
        if flag: break
    return J
def goto(I,X,Nt):
    W = []
    for x in I:
        handle = list(x[1])
        k = handle.index('.')
        if k != len(handle)-1:
            if handle[k+1] == X:
                S1 = ''.join([handle[i] for i in range(k)])
                S2 = ''.join([handle[i] for i in range(k+2,len(handle))])
                W.append((x[0],S1+X+'.'+S2))
    return closure(W,G,Nt)
def items(G,T,Nt):
    C = [ closure([(G[0][0],'.'+G[0][1])],G,Nt) ]
    action = {}
    goto_k = {}
    reduction_states = {}
    while True:
        C1 = [ I for I in C ]
        for I in C1:
            for X in T:
                goto_list = goto(I,X,Nt)
                if len(goto_list)!=0 and goto_list not in C1:
                    C1.append(goto_list)
                    if C1.index(I) not in action: action[C1.index(I)] = {}
                    if X not in action[C1.index(I)]: action[C1.index(I)][X] = C1.index(goto_list)
                elif goto_list in C1:
                    if C1.index(I) not in action: action[C1.index(I)] = {}
                    if X not in action[C1.index(I)]: action[C1.index(I)][X] = C1.index(goto_list)
        for I in C1:
            for X in Nt:
                goto_list = goto(I,X,Nt)
                if len(goto_list)!=0 and goto_list not in C1:
                    C1.append(goto_list)
                    if C1.index(I) not in goto_k: goto_k[C1.index(I)] = {}
                    if X not in goto_k[C1.index(I)]: goto_k[C1.index(I)][X] = C1.index(goto_list)
                elif goto_list in C1:
                    if C1.index(I) not in goto_k: goto_k[C1.index(I)] = {}
                    if X not in goto_k[C1.index(I)]: goto_k[C1.index(I)][X] = C1.index(goto_list)
        flag = True
        for x in C1:
            if x not in C:
                flag = False
                C.append(x)
        if flag: break
    for P in G:
        Pp = (P[0],P[1]+'.')
        for state in range(len(C)):
            if Pp in C[state]: reduction_states[state] = P
    accept_state = 0
    for x in reduction_states:
        if reduction_states[x] == G[0]: accept_state = x
    return C,action,goto_k,reduction_states,accept_state
txt = raw_input('Enter the name of the file. ')+'.txt'
fileHandle = open(txt)
G,T,Nt = import_grammar(fileHandle)
print T,Nt
C,action_list,goto_list,reduction_states,accept_state = items(G,T,Nt)
print 'Action list'
pprint(action_list)
print 'Goto list'
pprint(goto_list)
print 'Reduction states'
pprint(reduction_states)
print 'Accept state',accept_state
stack = [0]
input_str = raw_input('Enter some string ')+'#'
i,top = 0,0
# LR(0) AUTOMATON PARSING 
while True:
    s = stack[top]
    try:
        print s,stack,input_str[i] if i != len(input_str) else 'Finish',
        if s == accept_state:
            print 'accept'
            break
        elif s in reduction_states:
            A,beta = reduction_states[s]
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