from collections import defaultdict
from typing import Set, Dict, Tuple, List

class LTS:
    def __init__(self, name=''):
        self.transitions = defaultdict(list)
        self.states = set()
        self.actions = set()
        self.name = name

    def add_transition(self, source, action, target):
        self.transitions[source].append((action, target))
        self.states.update([source, target])
        self.actions.add(action)

    def prefix_states(self, prefix):
        new_transitions = defaultdict(list)
        state_map = {}
        for state in self.states:
            state_map[state] = f"{prefix}_{state}"
        for src in self.transitions:
            for (act, tgt) in self.transitions[src]:
                new_src = state_map[src]
                new_tgt = state_map[tgt]
                new_transitions[new_src].append((act, new_tgt))
        self.transitions = new_transitions
        self.states = set(state_map.values())
        return state_map


def load_lts(path: str) -> Tuple[LTS, str]:
    """
    Charge un fichier .lts et retourne l'objet LTS le représentant'.
    Format .lts : chaque ligne non vide ou comment (#) contient :
        src action tgt
    et la src de la première ligne du fichier sera considéré comme l'état initiale.
    """
    init = None
    lts = LTS(path)
    with open(path) as f:
        for line in f:
            if not line.strip() or line.startswith('#'):
                continue
            src, act, tgt = line.split()
            if init is None:
                init = src
            lts.add_transition(src, act, tgt)
    return lts, init


def split_block(block: Set[str], action: str, partition: List[Set[str]],
                transitions: Dict[Tuple[str, str], Set[str]]) -> List[Set[str]]:
    """
    Scinde un bloc selon les transitions étiquetées `action` sous forme de deux sous-blocs,
    en regroupant les états qui atteignent les mêmes blocs cibles.
    """
    reach_map: Dict[frozenset, Set[str]] = defaultdict(set)
    for state in block:
        reachable_blocks = set()
        for (act, tgt) in transitions.get(state, []):
            # Trouver le bloc contenant tgt
            for blk in partition:
                if tgt in blk:
                    reachable_blocks.add(frozenset(blk))
                    break
        key = frozenset(reachable_blocks)
        reach_map[key].add(state)
    # Retourner la liste de sous-blocs obtenus
    return [sub for sub in reach_map.values()]

def kanellakis_smolka(lts : LTS) -> List[Set[str]]:
    """
    Implémente l'algorithme de Kanellakis-Smolka pour le raffinement de partitions.
    Retourne la partition finale correspondant aux classes de bisimilarité forte.
    Complexité O(n * m) selon Aceto et al. 2011.
    """
    # Partition initiale : un seul bloc contenant tous les états
    partition: List[Set[str]] = [set(lts.states)]
    changed = True
    while changed:
        changed = False
        new_partition: List[Set[str]] = []
        for block in partition:
            refined = False
            for action in lts.actions:
                sub_blocks = split_block(block, action, partition, lts.transitions)
                if len(sub_blocks) > 1:
                    new_partition.extend(sub_blocks)
                    refined = True
                    changed = True
                    break
            if not refined:
                new_partition.append(block)
        partition = new_partition
    return partition


def are_bisimilar(file1: str, file2: str) -> bool:
    """
    Charge deux LTS depuis leurs fichiers, calcule leurs partitions,
    et compare si les partitions finales sont identiques.
    Renvoie True si ils sont bisimilaires (partition identique), False sinon.
    """
    lts1, init1 = load_lts(file1)
    lts2, init2 = load_lts(file2)

    # Vérifier que les alphabets d'actions sont identiques
    if lts1.actions != lts2.actions:
        return False

    # Renommer les états pour éviter conflits
    map1 = lts1.prefix_states("L1")
    map2 = lts2.prefix_states("L2")
    init1 = map1[init1]
    init2 = map2[init2]
    
    # Fusionner les deux LTS
    combined = LTS("combined")
    for s, trans in lts1.transitions.items():
        for (a, t) in trans:
            combined.add_transition(s, a, t)
    for s, trans in lts2.transitions.items():
        for (a, t) in trans:
            combined.add_transition(s, a, t)

    # Appliquer l'algo de Kanellakis-Smolka
    partition = kanellakis_smolka(combined)

    # Vérifier si les deux états initiaux sont dans le même bloc
    for block in partition:
        if init1 in block and init2 in block:
            return True
    return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} model1.lts model2.lts")
        sys.exit(1)
    file1, file2 = sys.argv[1], sys.argv[2]
    result = are_bisimilar(file1, file2)
    print("Bisimilar" if result else "Not bisimilar")
