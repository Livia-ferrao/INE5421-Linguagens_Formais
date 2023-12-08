from copy import deepcopy

#Regex validation
def is_valid_regex(regex):
    return valid_brackets(regex) and valid_operations(regex)


def valid_brackets(regex):
    opened_brackets = 0
    for c in regex:
        if c == '(':
            opened_brackets += 1
        if c == ')':
            opened_brackets -= 1
        if opened_brackets < 0:
            return False
    if opened_brackets == 0:
        return True
    return False


def valid_operations(regex):
    for i, c in enumerate(regex):
        if c == '*':
            if i == 0:
                return False
            if regex[i - 1] in '(|':
                return False
        if c == '|':
            if i == 0 or i == len(regex) - 1:
                return False
            if regex[i - 1] in '(|':
                return False
            if regex[i + 1] in ')|':
                return False
    return True

class RegexNode:

    @staticmethod
    def trim_brackets(regex):
        while regex[0] == '(' and regex[-1] == ')' and is_valid_regex(regex[1:-1]):
            regex = regex[1:-1]
        return regex
    
    @staticmethod
    def is_concat(c):
        return c == '(' or RegexNode.is_letter(c)

    @staticmethod
    def is_letter(c):
        return c in alphabet

    def __init__(self, regex):
        self.nullable = None
        self.firstpos = []
        self.lastpos = []
        self.item = None
        self.position = None
        self.children = []

        #Check if it is leaf
        if len(regex) == 1 and self.is_letter(regex):
            #Leaf
            self.item = regex
            self.nullable = False
            #Lambda checking
            if self.item == '&':
                self.nullable = True
            else:
                self.nullable = False
            return
        
        #It is an internal node
        #Finding the leftmost operators in all three
        kleene = -1
        or_operator = -1
        concatenation = -1
        i = 0

        #Getting the rest of terms    
        while i < len(regex):
            if regex[i] == '(':
                #Composed block
                bracketing_level = 1
                #Skipping the entire term
                i+=1
                while bracketing_level != 0 and i < len(regex):
                    if regex[i] == '(':
                        bracketing_level += 1
                    if regex[i] == ')':
                        bracketing_level -= 1
                    i+=1
            else:
                #Going to the next char
                i+=1

            #Found a concatenation in previous iteration
            #And also it was the last element check if breaking
            if i == len(regex):
                break

            #Testing if concatenation
            # print(regex[i])
            if self.is_concat(regex[i]):
                if concatenation == -1:
                    concatenation = i
                continue
            #Testing for kleene
            if regex[i] == '*':
                if kleene == -1:
                    kleene = i
                continue
            #Testing for or operator
            if regex[i] == '|':
                if or_operator == -1:
                    or_operator = i
        
        #Setting the current operation by priority
        if or_operator != -1:
            #Found an or operation
            self.item = '|'
            self.children.append(RegexNode(self.trim_brackets(regex[:or_operator])))
            self.children.append(RegexNode(self.trim_brackets(regex[(or_operator+1):])))
        elif concatenation != -1:
            #Found a concatenation
            self.item = '.'
            self.children.append(RegexNode(self.trim_brackets(regex[:concatenation])))
            self.children.append(RegexNode(self.trim_brackets(regex[concatenation:])))
        elif kleene != -1:
            #Found a kleene
            self.item = '*'
            self.children.append(RegexNode(self.trim_brackets(regex[:kleene])))

    def calc_functions(self, pos, followpos):
        if self.is_letter(self.item):
            #Its &
            if self.item == '&':
                self.firstpos = []
                self.lastpos = []
                self.position = None
                return pos
            #Is a leaf
            self.firstpos = [pos]
            self.lastpos = [pos]
            self.position = pos
            #Add the position in the followpos list
            followpos.append([self.item,[]])
            return pos+1
        #Is an internal node
        for child in self.children:
            pos = child.calc_functions(pos, followpos)
        #Calculate current functions

        if self.item == '.':
            #Is concatenation
            #Firstpos
            if self.children[0].nullable:
                self.firstpos = sorted(list(set(self.children[0].firstpos + self.children[1].firstpos)))
            else:
                self.firstpos = deepcopy(self.children[0].firstpos)
            #Lastpos
            if self.children[1].nullable:
                self.lastpos = sorted(list(set(self.children[0].lastpos + self.children[1].lastpos)))
            else:
                self.lastpos = deepcopy(self.children[1].lastpos)
            #Nullable
            self.nullable = self.children[0].nullable and self.children[1].nullable
            #Followpos
            for i in self.children[0].lastpos:
                for j in self.children[1].firstpos:
                    if j not in followpos[i][1]:
                        followpos[i][1] = sorted(followpos[i][1] + [j])

        elif self.item == '|':
            #Is or operator
            #Firstpos
            self.firstpos = sorted(list(set(self.children[0].firstpos + self.children[1].firstpos)))
            #Lastpos
            self.lastpos = sorted(list(set(self.children[0].lastpos + self.children[1].lastpos)))
            #Nullable
            self.nullable = self.children[0].nullable or self.children[1].nullable

        elif self.item == '*':
            #Is kleene
            #Firstpos
            self.firstpos = deepcopy(self.children[0].firstpos)
            #Lastpos
            self.lastpos = deepcopy(self.children[0].lastpos)
            #Nullable
            self.nullable = True
            #Followpos
            for i in self.children[0].lastpos:
                for j in self.children[0].firstpos:
                    if j not in followpos[i][1]:
                        followpos[i][1] = sorted(followpos[i][1] + [j])

        return pos

class RegexTree:
    def __init__(self, regex):
        self.root = RegexNode(regex)
        self.followpos = []
        self.functions()
    
    def functions(self):
        self.root.calc_functions(0, self.followpos)   
    
    def toDfa(self):

        def contains_hashtag(q):
            for i in q:
                if self.followpos[i][0] == '#':
                    return True
            return False

        M = [] #Marked states
        Q = [] #States list in the followpos form ( array of positions ) 
        # V = alphabet - {'#'} #Automata alphabet
        V = [char for char in alphabet if char != '#']
        d = [] #Delta function
        F = [] #FInal states list in the form of indexes (int)

        q0 = self.root.firstpos
        Q.append(q0)
        if contains_hashtag(q0):
            F.append(q0)

        transitions = []
        
        while len(Q) - len(M) > 0:
            #There exists one unmarked
            #We take one of those
            q = [i for i in Q if i not in M][0]
            #We mark it
            M.append(q)
            #For each letter in the automata's alphabet
            for a in V:
                # Compute destination state ( d(q,a) = U )
                U = []
                #Compute U
                #foreach position in state
                for i in q:
                    #if i has label a
                    if self.followpos[i][0] == a:
                        #We add the position to U's composition
                        U = U + self.followpos[i][1]
                U = sorted(list(set(U)))
                #Checking if this is a valid state
                if len(U) == 0:
                    #No positions, skipping, it won't produce any new states ( also won't be final )
                    continue
                if U not in Q:
                    Q.append(U)
                    if contains_hashtag(U):
                        F.append(U)
                #Transitions
                transitions.append([q, a, U])
        
        new_transitions = []
        for item in transitions:
            new_inner_list = []
            for i in item:
                new_inner_list2 = []
                for j in i:
                    if isinstance(j, int):
                        new_inner_list2.append(j+1)
                    else:
                        new_inner_list2.append(j)
                new_inner_list.append(new_inner_list2)
            new_transitions.append(new_inner_list)
        d = new_transitions
        
        final = []
        for item in F:
            new_final = []
            for i in item:
                new_final.append(i+1)
            final.append(new_final)
        F = final

        init = []
        for i in q0:
            init.append(i+1)
        q0 = init

        return Dfa(Q,V,d,q0,F)

        
class Dfa:

    def __init__(self,Q,V,d,q0,F):
        self.Q = Q
        self.V = V
        self.d = d
        self.q0 = q0
        self.F = F

def preprocess(regex):
    regex = clean_kleene(regex)
    regex = regex.replace(' ','')
    regex = '(' + regex + ')' + '#'
    while '()' in regex:
        regex = regex.replace('()','')
    return regex

def clean_kleene(regex):
    for i in range(0, len(regex) - 1):
        while i < len(regex) - 1 and regex[i + 1] == regex[i] and regex[i] == '*':
            regex = regex[:i] + regex[i + 1:]
    return regex

def gen_alphabet(regex):
    alphabet = [char for char in regex if char.isalpha()]
    alphabet = list(dict.fromkeys(alphabet))
    alphabet.append('#')
    if '&' in regex:
        alphabet.append('&')
    alphabet.sort()
    return alphabet

def transform_to_string(input_list):
    result_str = ""
    for inner_list in input_list:
        inner_str = "{" + ",".join(map(str, inner_list[0])) + "}," + inner_list[1][0] + ",{" + ",".join(map(str, inner_list[2])) + "};"
        result_str += inner_str
    result = result_str[:-1]
    return result

def transform_to_string_final(input_list):
    result_str = "{{{}}}".format("},{".join(map(lambda x: ",".join(map(str, x)), input_list)))
    result_str = "{" + result_str + "}"
    return result_str

def transform_to_string_init(input_list):
    formatted_str = "{{{}}}".format(",".join(map(str, input_list)))
    return formatted_str

def print_output(dfa, alphabet):
    final = transform_to_string_final(dfa.F)
    transitions = transform_to_string(dfa.d)
    init = transform_to_string_init(dfa.q0)
    num_states = str(len(dfa.Q))
    alphabet = '{' + ','.join(filter(lambda x: x != '#' and x!='&', alphabet)) + '}'
    string = num_states +  ";" + init + ";" + final +  ";" +  alphabet + ";" + transitions
    print(string)

#Settings
alphabet = None

#Main
#Main
# regex = '(&|b)(ab)*(&|a)'
# regex = 'a(a*(bb*a)*)*|b(b*(aa*b)*)*'
# regex = 'a(a|b)*a'
# regex = 'aa*(bb*aa*b)*'
# regex = '(&|b)(ab)*(&|a)'
# regex = 'a((&|ba)|(ab)*)*b'
regex = input()

#Preprocess regex and generate the alphabet 
p_regex = preprocess(regex)
alphabet = gen_alphabet(p_regex)

#Construct
tree = RegexTree(p_regex)
dfa = tree.toDfa()

#Result
print_output(dfa, alphabet)
