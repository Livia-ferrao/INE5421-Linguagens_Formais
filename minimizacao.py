def read_input(input_str):
    lines = input_str.strip().split('\n')
    num_states, initial_state, final_states, alphabet, *transitions = lines[0].split(';')
    num_states = int(num_states)
    final_states = set(final_states[1:-1].split(','))
    alphabet = sorted(set(alphabet[1:-1].split(',')))

    afn = {}
    for transition in transitions:
        src, symbol, dest = transition.split(',')
        afn[(src, symbol)] = dest
    
    return num_states, initial_state, final_states, alphabet, afn

def remove_unreachable_states(num_states, initial_state, final_states, alphabet, afn):
    all_states = set()

    for (src, _), _ in afn.items():
        all_states.add(src)

    reachable_states = set()
    stack = [initial_state]
    
    while stack:
        state = stack.pop()
        if state not in reachable_states:
            reachable_states.add(state)
            for symbol in alphabet:
                next_state = afn.get((state, symbol), None)
                if next_state:
                    stack.append(next_state)

    unreachable_states = all_states - reachable_states
    
    for state in unreachable_states:
        for symbol in alphabet:
            afn.pop((str(state), symbol), None)
    
    return num_states - len(unreachable_states), initial_state, final_states - unreachable_states, alphabet, afn

def remove_dead_states(num_states, initial_state, final_states, alphabet, afn):
    all_states = set()
    for (src, _), _ in afn.items():
        all_states.add(src)

    live_states = set(final_states)
    while True:
        # Clone o conjunto de estados vivos atual
        prev_live_states = live_states.copy()

        # Percorra todas as transições do AFD
        for (src, symbol), dest in afn.items():
            # Se o estado de destino já estiver em live_states, adicione src a live_states
            if dest in live_states:
                live_states.add(src)

        # Verifique se houve alguma mudança nos estados vivos
        if prev_live_states == live_states:
            break

    # Calcule os estados mortos
    dead_states = all_states - live_states
    # Remova as transições que envolvem estados mortos do dicionário afn
    for state in dead_states:
        for symbol in alphabet:
            afn.pop((str(state), symbol), None)
    
    return num_states - len(dead_states), initial_state, final_states - dead_states, alphabet, afn

def minimize_afd(num_states, initial_state, final_states, alphabet, afn):
    states = set()
    for (src, _), dest in afn.items():
        states.add(src)
        # states.add(dest)

    # Inicializa a lista de partições com estados finais e não finais
    partition = [set(final_states), states - set(final_states)]

    while True:
        new_partition = []
        for group in partition:
            if len(group) <= 1:
                new_partition.append(group)
                continue

            split_dict = {}
            for state in group:
                transitions = {}
                for symbol in alphabet:
                    next_state = afn.get((state, symbol), None)
                    if next_state:
                        for existing_group in partition:
                            next_state_group = set()
                            if next_state in existing_group:
                                next_state_group = existing_group
                                break
                        transitions[tuple(next_state_group)] = set(next_state)

                transitions_tuple = tuple(sorted(transitions.keys()))
                if transitions_tuple not in split_dict:
                    split_dict[transitions_tuple] = set()
                split_dict[transitions_tuple].add(state)

            new_partition.extend(split_dict.values())

        if new_partition == partition:
            break
        else:
            partition = new_partition

    # Construir um novo AFD minimizado
    new_afn = {}
    new_final_states = set()
    new_partitions = []  # Lista para armazenar os novos estados de equivalência

    for part in partition:
        representative_state = list(sorted(part))[0]
        new_partitions.append({representative_state})
    new_partitions_sort = sorted(new_partitions, key=lambda x: list(x)[0])

    for group in new_partitions_sort:
        representative_state = list(sorted(group))[0]  # Escolhe um representante para o grupo

        # Verifica se o representante é um estado final e adiciona-o aos estados finais do novo AFD
        if representative_state in final_states:
            new_final_states.add(representative_state)

        for symbol in alphabet:
            next_state = afn.get((representative_state, symbol), None)
            if next_state:
                # Encontre a classe de equivalência do próximo estado
                for subgroup in partition:
                    if next_state in subgroup:
                        new_afn[(representative_state, symbol)] = list(sorted(subgroup))[0]
                        break

    # Ajuste o estado inicial do novo AFD
    new_initial_state = None
    for i, group in enumerate(partition):
        if initial_state in group:
            new_initial_state = list(sorted(group))[0]
            break

    # Retorne as informações do novo AFD minimizado
    return len(partition), new_initial_state, sorted(new_final_states), alphabet, new_afn


def format_output(num_states, initial_state, final_states, alphabet, afn):
    final_states_str = ",".join(final_states)
    alphabet_str = ",".join(alphabet)
    transitions_str = ";".join([f"{src},{symbol},{dest}" for (src, symbol), dest in afn.items()])
    
    return f"{num_states};{initial_state};{{{final_states_str}}};{{{alphabet_str}}};{transitions_str}"

def minimize_dfa(input_str):
    num_states, initial_state, final_states, alphabet, afn = read_input(input_str)
    num_states, initial_state, final_states, alphabet, afn = remove_unreachable_states(num_states, initial_state, final_states, alphabet, afn)
    num_states, initial_state, final_states, alphabet, afn = remove_dead_states(num_states, initial_state, final_states, alphabet, afn)
    num_states, initial_state, final_states, alphabet, afn = minimize_afd(num_states, initial_state, final_states, alphabet, afn)
    return format_output(num_states, initial_state, final_states, alphabet, afn)

# Teste com os exemplos fornecidos
input1 = "8;P;{S,U,V,X};{0,1};P,0,Q;P,1,P;Q,0,T;Q,1,R;R,0,U;R,1,P;S,0,U;S,1,S;T,0,X;T,1,R;U,0,X;U,1,V;V,0,U;V,1,S;X,0,X;X,1,V"
input1 = "17;A;{A,D,F,M,N,P};{a,b,c,d};A,a,B;A,b,E;A,c,K;A,d,G;B,a,C;B,b,H;B,c,L;B,d,Q;C,a,D;C,b,I;C,c,M;C,d,Q;D,a,B;D,b,J;D,c,K;D,d,O;E,a,Q;E,b,F;E,c,H;E,d,N;F,a,Q;F,b,E;F,c,K;F,d,G;G,a,Q;G,b,Q;G,c,Q;G,d,N;H,a,Q;H,b,K;H,c,I;H,d,Q;I,a,Q;I,b,L;I,c,J;I,d,Q;J,a,Q;J,b,M;J,c,H;J,d,P;K,a,Q;K,b,H;K,c,L;K,d,Q;L,a,Q;L,b,I;L,c,M;L,d,Q;M,a,Q;M,b,J;M,c,K;M,d,O;N,a,R;N,b,R;N,c,R;N,d,G;O,a,R;O,b,R;O,c,R;O,d,P;P,a,R;P,b,R;P,c,Q;P,d,O;Q,a,R;Q,b,Q;Q,c,R;Q,d,Q;R,a,Q;R,b,R;R,c,Q;R,d,R"
output1 = minimize_dfa(input1)
print(output1)

# -- Input ---
#   8;P;{S,U,V,X};{0,1};P,0,Q;P,1,P;Q,0,T;Q,1,R;R,0,U;R,1,P;S,0,U;S,1,S;T,0,X;T,1,R;U,0,X;U,1,V;V,0,U;V,1,S;X,0,X;X,1,V

# --- Expected output (text)---
#  5;P;{S};{0,1};P,0,Q;P,1,P;Q,0,T;Q,1,R;R,0,S;R,1,P;S,0,S;S,1,S;T,0,S;T,1,R


# --- Input ---
#  17;A;{A,D,F,M,N,P};{a,b,c,d};A,a,B;A,b,E;A,c,K;A,d,G;B,a,C;B,b,H;B,c,L;B,d,Q;C,a,D;C,b,I;C,c,M;C,d,Q;D,a,B;D,b,J;D,c,K;D,d,O;E,a,Q;E,b,F;E,c,H;E,d,N;F,a,Q;F,b,E;F,c,K;F,d,G;G,a,Q;G,b,Q;G,c,Q;G,d,N;H,a,Q;H,b,K;H,c,I;H,d,Q;I,a,Q;I,b,L;I,c,J;I,d,Q;J,a,Q;J,b,M;J,c,H;J,d,P;K,a,Q;K,b,H;K,c,L;K,d,Q;L,a,Q;L,b,I;L,c,M;L,d,Q;M,a,Q;M,b,J;M,c,K;M,d,O;N,a,R;N,b,R;N,c,R;N,d,G;O,a,R;O,b,R;O,c,R;O,d,P;P,a,R;P,b,R;P,c,Q;P,d,O;Q,a,R;Q,b,Q;Q,c,R;Q,d,Q;R,a,Q;R,b,R;R,c,Q;R,d,R

# --- Expected output (text)---
#  11;A;{A,F,N};{a,b,c,d};A,a,B;A,b,E;A,c,K;A,d,G;B,a,C;B,b,H;B,c,L;C,a,A;C,b,I;C,c,F;E,b,F;E,c,H;E,d,N;F,b,E;F,c,K;F,d,G;G,d,N;H,b,K;H,c,I;I,b,L;I,c,E;K,b,H;K.c,L;L,b,I;L,c,F;N,d,G
