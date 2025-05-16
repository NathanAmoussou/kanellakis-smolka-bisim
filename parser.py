def load_lts(path):
    states, actions, trans = set(), set(), {}
    with open(path) as f:
        for line in f:
            if not line.strip() or line.startswith('#'): continue
            src, act, tgt = line.split()
            states |= {src, tgt}
            actions.add(act)
            trans.setdefault((src, act), set()).add(tgt)
    return states, actions, trans

def print_lts(parsed_lts):
    print(f"States: {parsed_lts[0]}")
    print(f"Actions: {parsed_lts[1]}")
    print(f"Transitions: {parsed_lts[2]}")

print_lts(load_lts("simple_test.lts"))
