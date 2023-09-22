def read_input(input_string):
    input_lines = input_string.strip().split(';')
    num_states = int(input_lines[0])
    start_state = input_lines[1]
    final_states = set(input_lines[2].strip('{}').split(','))
    alphabet = (input_lines[3].strip('{}').split(','))
    transitions = input_lines[4:]

    return num_states, start_state, final_states, alphabet, transitions

def epsilon_closure(states, transitions):
    epsilon_closure_set = set(states)
    new_states = set(states)
    while True:
        for transition in transitions:
            source, symbol, target = transition.split(',')
            if source in epsilon_closure_set and symbol == '&':
                new_states.add(target)
        if new_states == epsilon_closure_set:
            break
        epsilon_closure_set = new_states.copy()
    return sorted(epsilon_closure_set)

def get_target_states(states, symbol, transitions):
    target_states = set()
    for state in states:
        for transition in transitions:
            source, trans_symbol, target = transition.split(',')
            if source == state and trans_symbol == symbol:
                target_states.add(target)
    return target_states

def determine_afd(input_string):
    num_states, start_state, final_states, alphabet, transitions = read_input(input_string)

    # Create a dictionary to store the new states and transitions of the DFA
    dfa_transitions = []

    # Initialize the epsilon-closure of the start state if epsilon transitions are present
    if '&' in alphabet:
        start_closure = epsilon_closure({start_state}, transitions)
    else:
        start_closure = {start_state}

    # Initialize a queue for processing states
    state_queue = [start_closure]
    processed_states = set()

    # Process states until the queue is empty
    while state_queue:
        current_states = state_queue.pop(0)
        if tuple(current_states) in processed_states:
            continue

        processed_states.add(tuple(current_states))

        for symbol in alphabet:
            if symbol != '&':
                target_states = set()
                for state in current_states:
                    target_states.update(get_target_states({state}, symbol, transitions))

                epsilon_target_states = epsilon_closure(target_states, transitions) if '&' in alphabet else sorted(target_states)
                if epsilon_target_states:
                    if tuple(epsilon_target_states) not in processed_states:
                        state_queue.append(epsilon_target_states)

                    dfa_transitions.append((set(current_states), symbol, set(epsilon_target_states)))


    # ESTADOS FINAIS
    dfa_final_states = set()
    for state_set in processed_states:
        # Verifique se algum estado do conjunto está presente nos estados finais originais
        if any(state in final_states for state in state_set):
            # Se estiver presente, adicione o conjunto de estados à lista de estados finais do DFA
            dfa_final_states.add(''.join(sorted(state_set)))
    formatted_str = '{{' + '},{'.join(sorted(dfa_final_states)) + '}}'

    # TRANSIÇÕES
    formatted_transitions = []
    for state, symbol, next_state in dfa_transitions:
        formatted_transitions.append(f'{{{"".join(sorted(state))}}},{symbol},{"{" + "".join(sorted(next_state)) + "}"}')
    formatted_transitions = sorted(formatted_transitions, key=lambda x: (x.split(',')[0].replace("{", "").replace("}", ""), x.split(',')[1].replace("{", "").replace("}", "")))

    # ALFABETO
    if '&' in alphabet:
        alphabet.remove('&')

    dfa_output = f'{len(processed_states)};{{{"".join(sorted(start_closure))}}};{formatted_str};{{{",".join(sorted(alphabet))}}};{";".join(formatted_transitions)}'

    return dfa_output

af = determine_afd("4;P;{S};{0,1};P,0,P;P,0,Q;P,1,P;Q,0,R;Q,1,R;R,0,S;S,0,S;S,1,S")
print(af)

# --- Input ---
#  4;A;{D};{a,b};A,a,A;A,a,B;A,b,A;B,b,C;C,b,D

# --- Expected output (text)---
#  4;{A};{{AD}};{a,b};{A},a;{AB};{A},b,{A};{AB},a,{AB};{AB};b,{AC};{AC},a,{AB};{AC},b,{AD};{AD},a,{AB};{AD},b,{A}

# 2
# --- Input ---
#  3;A;{C};{1,2,3,&};A,1,A;A,&,B;B,2,B;B,&,C;C,3,C
#  --- Expected output (text)---
#  3;{ABC};{{ABC},{BC},{C}};{1,2,3};{ABC},1,{ABC};{ABC},2,{BC};{ABC},3,{C};{BC},2,{BC};{BC},3,{C};{C},3,{C}
 
# 3
# --- Input ---
#  4;P;{S};{0,1};P,0,P;P,0,Q;P,1,P;Q,0,R;Q,1,R;R,0,S;S,0,S;S,1,S
#  --- Expected output (text)---
# 8;{P};{{PQRS},{PQS},{PRS},{PS}};{0,1};{P},0,{PQ};{P},1,{P};{PQ},0,{PQR};{PQ},1,{PR};{PQR},0,{PQRS};{PQR},1,{PR};{PQRS},0,{PQRS};{PQRS},1,{PRS};{PQS},0,{PQRS};{PQS},1,{PRS};{PR},0,{PQS};{PR},1,{P};{PRS},0,{PQS};{PRS},1,{PS};{PS},0,{PQS};{PS},1,{PS}