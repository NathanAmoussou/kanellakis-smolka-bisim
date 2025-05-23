from collections import defaultdict
from typing import Set, Dict, Tuple, List, Optional

class LTS:
    def __init__(self, name=''):
        self.transitions: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
        self.states: Set[str] = set()
        self.actions: Set[str] = set()
        self.name: str = name

    def add_transition(self, source, action, target):
        self.transitions[source].append((action, target))
        self.states.update([source, target])
        self.actions.add(action)

    def prefix_states(self, prefix: str) -> Dict[str, str]:
        new_transitions: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
        state_map: Dict[str, str] = {}
        for state in self.states:
            state_map[state] = f"{prefix}_{state}"

        # for src in self.transitions:
        #     for (act, tgt) in self.transitions[src]:
        #         new_src = state_map[src]
        #         new_tgt = state_map[tgt]
        #         new_transitions[new_src].append((act, new_tgt))

        for src_orig, trans_list in self.transitions.items():
            new_src = state_map[src_orig]
            for (act, tgt_orig) in trans_list:
                new_tgt = state_map[tgt_orig]
                new_transitions[new_src].append((act, new_tgt))

        self.transitions = new_transitions
        self.states = set(state_map.values())
        return state_map

    def __repr__(self):
        return f"LTS(name='{self.name}', states={len(self.states)}, actions={len(self.actions)}, transitions_count={sum(len(t) for t in self.transitions.values())})"

# def load_lts(path: str) -> Tuple[LTS, str]:
#     """
#     Loads a file . lts and returns the LTS object representing'.
#     Format . lts: each non-empty line or how (#) contains:
#         src action tgt
#     and the src of the first line of the file will be considered as the initial state.
#     """
#     init: Optional[str] = None
#     lts = LTS(path)
#     with open(path) as f:
#         for line in f:
#             if not line.strip() or line.startswith('#'):
#                 continue
#             src, act, tgt = line.split()
#             if init is None:
#                 init = src
#             lts.add_transition(src, act, tgt)
#     return lts, init

def load_lts(path: str) -> Tuple[LTS, str]:
    """
    Loads a file .lts and returns the LTS object and its initial state.
    Format .lts: each non-empty line not starting with # contains:
        src action tgt
    The src of the first valid line is considered the initial state.
    Raises ValueError if no initial state can be determined (e.g., empty file).
    """
    init: Optional[str] = None
    lts = LTS(path)
    with open(path) as f:
        for line in f:
            line_strip = line.strip()
            if not line_strip or line_strip.startswith('#'):
                continue
            parts = line_strip.split()
            if len(parts) != 3:
                # Handle malformed lines, or raise an error
                print(f"Warning: Malformed line in {path}: '{line_strip}' - skipping")
                continue
            src, act, tgt = parts
            if init is None:
                init = src
            lts.add_transition(src, act, tgt)

    if init is None:
        # This also handles the case where the file was empty or only comments
        lts.states.clear() # Ensure states is empty if no transitions
        raise ValueError(f"No valid transitions found in {path}, cannot determine initial state.")
    if not lts.states: # If init was set but no transitions were added (e.g. first line ok, rest bad)
        lts.states.add(init) # ensure initial state is in the set of states for consistency

    return lts, init

# def split_block(block: Set[str], action: str, partition: List[Set[str]],
#                 transitions: Dict[Tuple[str, str], Set[str]]) -> List[Set[str]]:
#     """
#     Splits a block according to the transitions labeled ‘action’ into two sub-blocks,
#     by grouping states that reach the same target blocks.
#     """
#     reach_map: Dict[frozenset, Set[str]] = defaultdict(set)
#     for state in block:
#         reachable_blocks = set()
#         for (act, tgt) in transitions.get(state, []):
#             # Find the block containing tgt
#             for blk in partition:
#                 if tgt in blk:
#                     reachable_blocks.add(frozenset(blk))
#                     break
#         key = frozenset(reachable_blocks)
#         reach_map[key].add(state)
#     # Return the list of obtained sub-blocks
#     return [sub for sub in reach_map.values()]

def split_block(block: Set[str], action: str, partition: List[Set[str]],
                transitions: Dict[str, List[Tuple[str, str]]]) -> List[Set[str]]:
    """
    Splits a block according to transitions labeled 'action' into sub-blocks.
    States are grouped if they reach the same set of target blocks in the partition.
    """
    reach_map: Dict[frozenset[frozenset[str]], Set[str]] = defaultdict(set)
    for state in block:
        reachable_target_blocks: Set[frozenset[str]] = set()
        # Consider only transitions for the current 'action'
        for act_trans, tgt_trans in transitions.get(state, []):
            if act_trans == action:
                # Find the block in 'partition' containing tgt_trans
                for blk_in_partition in partition:
                    if tgt_trans in blk_in_partition:
                        reachable_target_blocks.add(frozenset(blk_in_partition))
                        break
                        # tgt_trans can only be in one block of the partition

        # The key is the set of blocks reachable from 'state' via 'action'
        key = frozenset(reachable_target_blocks)
        reach_map[key].add(state)

    return [sub_block for sub_block in reach_map.values() if sub_block]


# def kanellakis_smolka(lts : LTS) -> List[Set[str]]:
#     """
#     Implements the Kanellakis-Smolka algorithm for score refinement.
#     Returns the final partition corresponding to the strong bisimilarity classes.
#     Complexity O(n * m) according to Aceto et al. 2011.
#     """
#     # Initial partition: a single block containing all states
#     partition: List[Set[str]] = [set(lts.states)]
#     changed = True
#     while changed:
#         changed = False
#         new_partition: List[Set[str]] = []
#         for block in partition:
#             refined = False
#             for action in lts.actions:
#                 sub_blocks = split_block(block, action, partition, lts.transitions)
#                 if len(sub_blocks) > 1:
#                     new_partition.extend(sub_blocks)
#                     refined = True
#                     changed = True
#                     break
#             if not refined:
#                 new_partition.append(block)
#         partition = new_partition
#     return partition

def kanellakis_smolka(lts : LTS) -> List[Set[str]]:
    """
    Implements the Kanellakis-Smolka partition refinement algorithm.
    Returns the final partition corresponding to strong bisimilarity classes.
    """
    if not lts.states: # Handle empty LTS
        return []

    partition: List[Set[str]] = [set(lts.states)]
    worklist = [set(lts.states)] # Or some other strategy to pick splitters

    # The pseudocode uses 'changed' flag. A worklist approach is also common.
    # For simplicity, let's stick to the 'changed' flag structure similar to the original.
    changed = True
    while changed:
        changed = False
        new_partition: List[Set[str]] = []
        for block_to_refine in partition:
            if len(block_to_refine) <= 1: # Cannot refine singletons or empty blocks
                new_partition.append(block_to_refine)
                continue

            refined_this_iteration = False
            # Try to split block_to_refine using each action
            for action in lts.actions: # 'action' acts as part of the splitter
                sub_blocks = split_block(block_to_refine, action, partition, lts.transitions)

                if len(sub_blocks) > 1: # block_to_refine was split
                    new_partition.extend(sub_blocks)
                    changed = True
                    refined_this_iteration = True
                    break # block_to_refine has been replaced, move to next in old partition

            if not refined_this_iteration:
                new_partition.append(block_to_refine)

        if changed:
            partition = new_partition
            # For next iteration, the splitters could be chosen more carefully (e.g. smaller of split parts)
            # but iterating through all actions and blocks is the basic KS approach.

    return partition


# def are_bisimilar(file1: str, file2: str) -> bool:
#     """
#     Charge deux LTS depuis leurs fichiers, calcule leurs partitions,
#     et compare si les partitions finales sont identiques.
#     Renvoie True si ils sont bisimilaires (partition identique), False sinon.
#     """
#     lts1, init1 = load_lts(file1)
#     lts2, init2 = load_lts(file2)

#     # Check that the action alphabets are identical
#     if lts1.actions != lts2.actions:
#         return False

#     # Rename states to avoid conflicts
#     map1 = lts1.prefix_states("L1")
#     map2 = lts2.prefix_states("L2")
#     init1 = map1[init1]
#     init2 = map2[init2]

#     # Merge the two LTS
#     combined = LTS("combined")
#     for s, trans in lts1.transitions.items():
#         for (a, t) in trans:
#             combined.add_transition(s, a, t)
#     for s, trans in lts2.transitions.items():
#         for (a, t) in trans:
#             combined.add_transition(s, a, t)

#     # Apply the algo of Kanellakis-Smolka
#     partition = kanellakis_smolka(combined)

#     # Check if the two initial states are in the same block
#     for block in partition:
#         if init1 in block and init2 in block:
#             return True
#     return False

def are_bisimilar(file1: str, file2: str) -> bool:
    """
    Loads two LTS from files, computes their bisimilarity partition,
    and checks if their initial states are in the same block.
    Returns True if they are bisimilar, False otherwise.
    """
    try:
        lts1, init1_orig = load_lts(file1)
        lts2, init2_orig = load_lts(file2)
    except ValueError as e:
        print(f"Error loading LTS: {e}")
        return False # Or re-raise, depending on desired behavior

    # Check that the action alphabets are identical.
    # This is a common prerequisite for many bisimilarity tools.
    # Alternatively, one could take the union of actions.
    if lts1.actions != lts2.actions:
        # print("Warning: Action sets differ. Proceeding with union of actions might be an alternative.")
        # print(f"LTS1 actions: {lts1.actions}")
        # print(f"LTS2 actions: {lts2.actions}")
        return False # Sticking to current behavior

    # Rename states to avoid conflicts when merging
    map1 = lts1.prefix_states("L1")
    map2 = lts2.prefix_states("L2")
    init1 = map1[init1_orig]
    init2 = map2[init2_orig]

    # Merge the two LTSs
    combined = LTS("combined")
    # Add all states from both LTSs first
    combined.states.update(lts1.states)
    combined.states.update(lts2.states)
    # Add all actions (already checked they are the same)
    combined.actions.update(lts1.actions)

    for s, trans_list in lts1.transitions.items():
        for (a, t) in trans_list:
            combined.transitions[s].append((a,t)) # Already prefixed states
    for s, trans_list in lts2.transitions.items():
        for (a, t) in trans_list:
            combined.transitions[s].append((a,t)) # Already prefixed states

    # Apply the Kanellakis-Smolka algorithm
    final_partition = kanellakis_smolka(combined)

    # Check if the two (prefixed) initial states are in the same block
    for block in final_partition:
        if init1 in block and init2 in block:
            return True
    return False

# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) != 3:
#         print(f"Usage: python {sys.argv[0]} model1.lts model2.lts")
#         sys.exit(1)
#     file1, file2 = sys.argv[1], sys.argv[2]
#     result = are_bisimilar(file1, file2)
#     print("Bisimilar" if result else "Not bisimilar")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} model1.lts model2.lts")
        sys.exit(1)

    file1, file2 = sys.argv[1], sys.argv[2]

    # Correcting typos in test files before running for demonstration
    # This should be done manually in the files themselves.
    # For test1.lts.txt: s3 c s---  => s3 c s
    # For test2.lts.txt: t3 c t---  => t3 c t
    # Example: if file1 == "test1.lts.txt": fix_file("test1.lts.txt", "s3 c s---", "s3 c s") # pseudo-code

    result = are_bisimilar(file1, file2)
    print("Bisimilar" if result else "Not bisimilar")
