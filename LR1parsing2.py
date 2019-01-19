# with user-defined error recovery
from pprint import pprint
from random import randint
from threading import Thread,Lock
mutex = Lock()
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
def closure(I,G,Nt):
    J = [p for p in I]
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
                        b = list(beta+a)[0]
                        if p[0] == handle[k+1]:
                            new_p = (p[0],'.'+p[1],b)
                            if new_p not in J1: J1.append(new_p)
        flag = True
        for x in J1:
            if x not in J:
                flag = False
                J.append(x)
        if flag: break
    return J
def goto(I,G,X,Nt):
    W = []
    for x in I:
        handle = list(x[1])
        k = handle.index('.')
        if k != len(handle)-1:
            if handle[k+1] == X:
                S1 = ''.join([handle[i] for i in range(k)])
                S2 = ''.join([handle[i] for i in range(k+2,len(handle))])
                W.append((x[0],S1+X+'.'+S2,x[2]))
    return closure(W,G,Nt)
def items(G,T,Nt):
    C = [ closure([(G[0][0],'.'+G[0][1],'$')],G,Nt) ]
    action = {}
    goto_k = {}
    reduction_states = {}
    while True:
        C1 = [ I for I in C ]
        for I in C1:
            for X in T:
                goto_list = goto(I,G,X,Nt)
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
                goto_list = goto(I,G,X,Nt)
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
    return C,action,goto_k,reduction_states,accept_state
def driver():
    fileHandle = open('grammarinput3.txt')
    G,T,Nt = import_grammar(fileHandle)
    print T,Nt
    C,action_list,goto_list,reduction_states,accept_state = items(G,T,Nt)
    print 'Canonical states'
    for i in range(len(C)): print i,C[i]
    print 'Action list'
    pprint(action_list)
    print 'Goto list'
    pprint(goto_list)
    print 'Reduction states'
    pprint(reduction_states)
    print 'Accept state',accept_state
    stack = [0]
    symbol_stack=['$']
    input_str = raw_input('Enter some string ')+'$'
    i,top = 0,0
    # LR(1) AUTOMATON PARSING 
    def automatonThread(symbol_stack,stack,input_str,i,top):
        global mutex
        mutex.acquire()
        print 'STATE','INPUT','SYMBOL_STACK','ACTION'
        while True:
            print 'Input string',input_str
            s = stack[top]
            try:
                print s,input_str[i] if i != len(input_str) else 'Finish',symbol_stack,
                if s == accept_state:
                    print 'accept'
                    mutex.release()
                    break
                elif len(reduction_states[s]) != 0 and input_str[i] in reduction_states[s]:
                    A,beta = reduction_states[s][input_str[i]]
                    print 'reduce',A,'->',beta
                    for j in range(len(beta)):
                        del stack[top]
                        del symbol_stack[top]
                    t = stack[top]
                    stack.insert(top,goto_list[t][A])
                    symbol_stack.insert(top,A)
                else:
                    a = input_str[i]
                    stack.insert(top,action_list[s][a])
                    symbol_stack.insert(top,a)
                    print 'shift',action_list[s][a]
                    i = i + 1
            except:
                print '\nSyntax error detected'
                print 'Expected any of the following'
                errors = []
                if s in action_list:
                    for prod in action_list[s]: errors.append(prod)
                elif s in reduction_states:
                    for prod in reduction_states[s]: errors.append(prod)
                for j in range(len(errors)): print j+1,')',errors[j] if errors[j] != '$' else 'End of line'
                threadList = [None for j in range(len(errors))]
                print 'Got',input_str[i],'at position',i
                mutex.release()
                for k in range(len(errors)):
                    r = errors[k]
                    e = input_str[i]
                    buffer_str = ''.join(input_str[j] for j in range(i))+r+''.join(input_str[j] for j in range(i+1,len(input_str)))
                    if i == len(buffer_str) - 1 and e == '$': buffer_str = buffer_str + '$'
                    print 'Current adjusted input',buffer_str
                    threadList[k] = Thread(target=automatonThread,args=(symbol_stack,stack,buffer_str,i,top,))
                for k in range(len(errors)): threadList[k].start()
                for k in range(len(errors)): threadList[k].join()
                break
    automatonThread(symbol_stack,stack,input_str,i,top)
driver()
# The output of the program
# ['a', 'b', '$'] ['G', 'S']
# Canonical states
# 0 [('G', '.S', '$'), ('S', '.abS', '$'), ('S', '.baS', '$'), ('S', '.aaSbbS', '$'), ('S', '.bbSaaS', '$'), ('S', '.', '$')]
# 1 [('S', 'a.bS', '$'), ('S', 'a.aSbbS', '$')]
# 2 [('S', 'b.aS', '$'), ('S', 'b.bSaaS', '$')]
# 3 [('S', 'aa.SbbS', '$'), ('S', '.abS', 'b'), ('S', '.baS', 'b'), ('S', '.aaSbbS', 'b'), ('S', '.bbSaaS', 'b'), ('S', '.', 'b')]
# 4 [('S', 'ab.S', '$'), ('S', '.abS', '$'), ('S', '.baS', '$'), ('S', '.aaSbbS', '$'), ('S', '.bbSaaS', '$'), ('S', '.', '$')]
# 5 [('S', 'ba.S', '$'), ('S', '.abS', '$'), ('S', '.baS', '$'), ('S', '.aaSbbS', '$'), ('S', '.bbSaaS', '$'), ('S', '.', '$')]
# 6 [('S', 'bb.SaaS', '$'), ('S', '.abS', 'a'), ('S', '.baS', 'a'), ('S', '.aaSbbS', 'a'), ('S', '.bbSaaS', 'a'), ('S', '.', 'a')]
# 7 [('S', 'a.bS', 'b'), ('S', 'a.aSbbS', 'b')]
# 8 [('S', 'b.aS', 'b'), ('S', 'b.bSaaS', 'b')]
# 9 [('S', 'a.bS', 'a'), ('S', 'a.aSbbS', 'a')]
# 10 [('S', 'b.aS', 'a'), ('S', 'b.bSaaS', 'a')]
# 11 [('S', 'aa.SbbS', 'b'), ('S', '.abS', 'b'), ('S', '.baS', 'b'), ('S', '.aaSbbS', 'b'), ('S', '.bbSaaS', 'b'), ('S', '.', 'b')]
# 12 [('S', 'ab.S', 'b'), ('S', '.abS', 'b'), ('S', '.baS', 'b'), ('S', '.aaSbbS', 'b'), ('S', '.bbSaaS', 'b'), ('S', '.', 'b')]
# 13 [('S', 'ba.S', 'b'), ('S', '.abS', 'b'), ('S', '.baS', 'b'), ('S', '.aaSbbS', 'b'), ('S', '.bbSaaS', 'b'), ('S', '.', 'b')]
# 14 [('S', 'bb.SaaS', 'b'), ('S', '.abS', 'a'), ('S', '.baS', 'a'), ('S', '.aaSbbS', 'a'), ('S', '.bbSaaS', 'a'), ('S', '.', 'a')]
# 15 [('S', 'aa.SbbS', 'a'), ('S', '.abS', 'b'), ('S', '.baS', 'b'), ('S', '.aaSbbS', 'b'), ('S', '.bbSaaS', 'b'), ('S', '.', 'b')]
# 16 [('S', 'ab.S', 'a'), ('S', '.abS', 'a'), ('S', '.baS', 'a'), ('S', '.aaSbbS', 'a'), ('S', '.bbSaaS', 'a'), ('S', '.', 'a')]
# 17 [('S', 'ba.S', 'a'), ('S', '.abS', 'a'), ('S', '.baS', 'a'), ('S', '.aaSbbS', 'a'), ('S', '.bbSaaS', 'a'), ('S', '.', 'a')]
# 18 [('S', 'bb.SaaS', 'a'), ('S', '.abS', 'a'), ('S', '.baS', 'a'), ('S', '.aaSbbS', 'a'), ('S', '.bbSaaS', 'a'), ('S', '.', 'a')]
# 19 [('G', 'S.', '$')]
# 20 [('S', 'aaS.bbS', '$')]
# 21 [('S', 'abS.', '$')]
# 22 [('S', 'baS.', '$')]
# 23 [('S', 'bbS.aaS', '$')]
# 24 [('S', 'aaS.bbS', 'b')]
# 25 [('S', 'abS.', 'b')]
# 26 [('S', 'baS.', 'b')]
# 27 [('S', 'bbS.aaS', 'b')]
# 28 [('S', 'aaS.bbS', 'a')]
# 29 [('S', 'abS.', 'a')]
# 30 [('S', 'baS.', 'a')]
# 31 [('S', 'bbS.aaS', 'a')]
# 32 [('S', 'aaSb.bS', '$')]
# 33 [('S', 'bbSa.aS', '$')]
# 34 [('S', 'aaSb.bS', 'b')]
# 35 [('S', 'bbSa.aS', 'b')]
# 36 [('S', 'aaSb.bS', 'a')]
# 37 [('S', 'bbSa.aS', 'a')]
# 38 [('S', 'aaSbb.S', '$'), ('S', '.abS', '$'), ('S', '.baS', '$'), ('S', '.aaSbbS', '$'), ('S', '.bbSaaS', '$'), ('S', '.', '$')]
# 39 [('S', 'bbSaa.S', '$'), ('S', '.abS', '$'), ('S', '.baS', '$'), ('S', '.aaSbbS', '$'), ('S', '.bbSaaS', '$'), ('S', '.', '$')]
# 40 [('S', 'aaSbb.S', 'b'), ('S', '.abS', 'b'), ('S', '.baS', 'b'), ('S', '.aaSbbS', 'b'), ('S', '.bbSaaS', 'b'), ('S', '.', 'b')]
# 41 [('S', 'bbSaa.S', 'b'), ('S', '.abS', 'b'), ('S', '.baS', 'b'), ('S', '.aaSbbS', 'b'), ('S', '.bbSaaS', 'b'), ('S', '.', 'b')]
# 42 [('S', 'aaSbb.S', 'a'), ('S', '.abS', 'a'), ('S', '.baS', 'a'), ('S', '.aaSbbS', 'a'), ('S', '.bbSaaS', 'a'), ('S', '.', 'a')]
# 43 [('S', 'bbSaa.S', 'a'), ('S', '.abS', 'a'), ('S', '.baS', 'a'), ('S', '.aaSbbS', 'a'), ('S', '.bbSaaS', 'a'), ('S', '.', 'a')]
# 44 [('S', 'aaSbbS.', '$')]
# 45 [('S', 'bbSaaS.', '$')]
# 46 [('S', 'aaSbbS.', 'b')]
# 47 [('S', 'bbSaaS.', 'b')]
# 48 [('S', 'aaSbbS.', 'a')]
# 49 [('S', 'bbSaaS.', 'a')]
# Action list
# {0: {'a': 1, 'b': 2},
#  1: {'a': 3, 'b': 4},
#  2: {'a': 5, 'b': 6},
#  3: {'a': 7, 'b': 8},
#  4: {'a': 1, 'b': 2},
#  5: {'a': 1, 'b': 2},
#  6: {'a': 9, 'b': 10},
#  7: {'a': 11, 'b': 12},
#  8: {'a': 13, 'b': 14},
#  9: {'a': 15, 'b': 16},
#  10: {'a': 17, 'b': 18},
#  11: {'a': 7, 'b': 8},
#  12: {'a': 7, 'b': 8},
#  13: {'a': 7, 'b': 8},
#  14: {'a': 9, 'b': 10},
#  15: {'a': 7, 'b': 8},
#  16: {'a': 9, 'b': 10},
#  17: {'a': 9, 'b': 10},
#  18: {'a': 9, 'b': 10},
#  20: {'b': 32},
#  23: {'a': 33},
#  24: {'b': 34},
#  27: {'a': 35},
#  28: {'b': 36},
#  31: {'a': 37},
#  32: {'b': 38},
#  33: {'a': 39},
#  34: {'b': 40},
#  35: {'a': 41},
#  36: {'b': 42},
#  37: {'a': 43},
#  38: {'a': 1, 'b': 2},
#  39: {'a': 1, 'b': 2},
#  40: {'a': 7, 'b': 8},
#  41: {'a': 7, 'b': 8},
#  42: {'a': 9, 'b': 10},
#  43: {'a': 9, 'b': 10}}
# Goto list
# {0: {'S': 19},
#  3: {'S': 20},
#  4: {'S': 21},
#  5: {'S': 22},
#  6: {'S': 23},
#  11: {'S': 24},
#  12: {'S': 25},
#  13: {'S': 26},
#  14: {'S': 27},
#  15: {'S': 28},
#  16: {'S': 29},
#  17: {'S': 30},
#  18: {'S': 31},
#  38: {'S': 44},
#  39: {'S': 45},
#  40: {'S': 46},
#  41: {'S': 47},
#  42: {'S': 48},
#  43: {'S': 49}}
# Reduction states
# {0: {'$': ('S', '')},
#  1: {},
#  2: {},
#  3: {'b': ('S', '')},
#  4: {'$': ('S', '')},
#  5: {'$': ('S', '')},
#  6: {'a': ('S', '')},
#  7: {},
#  8: {},
#  9: {},
#  10: {},
#  11: {'b': ('S', '')},
#  12: {'b': ('S', '')},
#  13: {'b': ('S', '')},
#  14: {'a': ('S', '')},
#  15: {'b': ('S', '')},
#  16: {'a': ('S', '')},
#  17: {'a': ('S', '')},
#  18: {'a': ('S', '')},
#  19: {'$': ('G', 'S')},
#  20: {},
#  21: {'$': ('S', 'abS')},
#  22: {'$': ('S', 'baS')},
#  23: {},
#  24: {},
#  25: {'b': ('S', 'abS')},
#  26: {'b': ('S', 'baS')},
#  27: {},
#  28: {},
#  29: {'a': ('S', 'abS')},
#  30: {'a': ('S', 'baS')},
#  31: {},
#  32: {},
#  33: {},
#  34: {},
#  35: {},
#  36: {},
#  37: {},
#  38: {'$': ('S', '')},
#  39: {'$': ('S', '')},
#  40: {'b': ('S', '')},
#  41: {'b': ('S', '')},
#  42: {'a': ('S', '')},
#  43: {'a': ('S', '')},
#  44: {'$': ('S', 'aaSbbS')},
#  45: {'$': ('S', 'bbSaaS')},
#  46: {'b': ('S', 'aaSbbS')},
#  47: {'b': ('S', 'bbSaaS')},
#  48: {'a': ('S', 'aaSbbS')},
#  49: {'a': ('S', 'bbSaaS')}}
# Accept state 19
# Enter some string aaaabbaaaabb
# STATE INPUT SYMBOL_STACK ACTION
# Input string aaaabbaaaabb$
# 0 a ['$'] shift 1
# Input string aaaabbaaaabb$
# 1 a ['a', '$'] shift 3
# Input string aaaabbaaaabb$
# 3 a ['a', 'a', '$'] shift 7
# Input string aaaabbaaaabb$
# 7 a ['a', 'a', 'a', '$'] shift 11
# Input string aaaabbaaaabb$
# 11 b ['a', 'a', 'a', 'a', '$'] reduce S -> 
# Input string aaaabbaaaabb$
# 24 b ['S', 'a', 'a', 'a', 'a', '$'] shift 34
# Input string aaaabbaaaabb$
# 34 b ['b', 'S', 'a', 'a', 'a', 'a', '$'] shift 40
# Input string aaaabbaaaabb$
# 40 a ['b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] shift 7
# Input string aaaabbaaaabb$
# 7 a ['a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] shift 11
# Input string aaaabbaaaabb$
# 11 a ['a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] shift 7
# Input string aaaabbaaaabb$
# 7 a ['a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] shift 11
# Input string aaaabbaaaabb$
# 11 b ['a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] reduce S -> 
# Input string aaaabbaaaabb$
# 24 b ['S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] shift 34
# Input string aaaabbaaaabb$
# 34 b ['b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] shift 40
# Input string aaaabbaaaabb$
# 40 $ ['b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] 
# Syntax error detected
# Expected any of the following
# 1 ) a
# 2 ) b
# Got $ at position 12
# Current adjusted input aaaabbaaaabba$
# Current adjusted input aaaabbaaaabbb$
# STATE INPUT SYMBOL_STACK ACTION
# Input string aaaabbaaaabba$
# 40 a ['b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] shift 7
# Input string aaaabbaaaabba$
# 7 $ ['a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] 
# Syntax error detected
# Expected any of the following
# 1 ) a
# 2 ) b
# Got $ at position 13
# Current adjusted input aaaabbaaaabbaa$
#  Current adjusted input aaaabbaaaabbab$
# STATE INPUT SYMBOL_STACK ACTION
# Input string aaaabbaaaabbb$
# 7 b ['a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] shift 12
# Input string aaaabbaaaabbb$
# 12 $ ['b', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] 
# Syntax error detected
# Expected any of the following
# 1 ) a
# 2 ) b
# Got $ at position 13
# Current adjusted input aaaabbaaaabbba$
#  STATE INPUT SYMBOL_STACK Current adjusted input aaaabbaaaabbbb$
# ACTION
# Input string aaaabbaaaabbaa$
# 12 a ['b', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] shift 7
# Input string aaaabbaaaabbaa$
# 7 $ ['a', 'b', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] 
# Syntax error detected
# Expected any of the following
# 1 ) a
# 2 ) b
# Got $ at position 14
# Current adjusted input aaaabbaaaabbaaa$
#  Current adjusted input aaaabbaaaabbaab$
# STATE INPUT SYMBOL_STACK ACTION
# Input string aaaabbaaaabbab$
# 7 b ['a', 'b', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] shift 12
# Input string aaaabbaaaabbab$
# 12 $ ['b', 'a', 'b', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] 
# Syntax error detected
# Expected any of the following
# 1 ) a
# 2 ) b
# Got $ at position 14
# Current adjusted input aaaabbaaaabbaba$
#  Current adjusted input aaaabbaaaabbabb$
# STATE INPUT SYMBOL_STACK ACTION
# Input string aaaabbaaaabbba$
# 12 a ['b', 'a', 'b', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] shift 7
# Input string aaaabbaaaabbba$
# 7 $ ['a', 'b', 'a', 'b', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] 
# Syntax error detected
# Expected any of the following
# 1 ) a
# 2 ) b
# Got $ at position 14
# Current adjusted input aaaabbaaaabbbaa$
#  STATE INPUT SYMBOL_STACK ACTIONCurrent adjusted input aaaabbaaaabbbab$

# Input string aaaabbaaaabbbb$
# 7 b ['a', 'b', 'a', 'b', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] shift 12
# Input string aaaabbaaaabbbb$
# 12 $ ['b', 'a', 'b', 'a', 'b', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] 
# Syntax error detected
# Expected any of the following
# 1 ) a
# 2 ) b
# Got $ at position 14
# Current adjusted input aaaabbaaaabbbba$
#  STATE INPUT Current adjusted input aaaabbaaaabbbbb$
# SYMBOL_STACK ACTION
# Input string aaaabbaaaabbaaa$
# 12 a ['b', 'a', 'b', 'a', 'b', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] shift 7
# Input string aaaabbaaaabbaaa$
# 7 $ ['a', 'b', 'a', 'b', 'a', 'b', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] 
# Syntax error detected
# Expected any of the following
# 1 ) a
# 2 ) b
# Got $ at position 15
# Current adjusted input aaaabbaaaabbaaaa$
#  STATE INPUT SYMBOL_STACK ACTION
# Current adjusted input aaaabbaaaabbaaab$
# Input string aaaabbaaaabbaab$
# 7 b ['a', 'b', 'a', 'b', 'a', 'b', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] shift 12
# Input string aaaabbaaaabbaab$
# 12 $ ['b', 'a', 'b', 'a', 'b', 'a', 'b', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', 'b', 'b', 'S', 'a', 'a', 'a', 'a', '$'] 
# Syntax error detected
# Expected any of the following
# 1 ) a
# 2 ) b
# Got $ at position 15
# Current adjusted input aaaabbaaaabbaaba$
#  Current adjusted input aaaabbaaaabbaabb$
# ..... (further output compressed)