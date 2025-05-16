from collections import defaultdict
from typing import Set, Dict, Tuple, List


def load_lts(path: str) -> Tuple[Set[str], Set[str], Dict[Tuple[str, str], Set[str]]]:
    """
    Charge un fichier .lts et retourne les états, actions, et transitions.
    Format .lts : chaque ligne non vide ou comment (#) contient :
        src action tgt
    """
    states: Set[str] = set()
    actions: Set[str] = set()
    transitions: Dict[Tuple[str, str], Set[str]] = {}
    with open(path) as f:
        for line in f:
            if not line.strip() or line.startswith('#'):
                continue
            src, act, tgt = line.split()
            states |= {src, tgt}
            actions.add(act)
            transitions.setdefault((src, act), set()).add(tgt)
    return states, actions, transitions


def split_block(block: Set[str], action: str, partition: List[Set[str]],
                transitions: Dict[Tuple[str, str], Set[str]]) -> List[Set[str]]:
    """
    Scinde un bloc selon les transitions étiquetées `action` sous forme de deux sous-blocs,
    en regroupant les états qui atteignent les mêmes blocs cibles.
    """
    reach_map: Dict[frozenset, Set[str]] = defaultdict(set)
    for state in block:
        reachable_blocks = set()
        for tgt in transitions.get((state, action), []):
            # Trouver le bloc contenant tgt
            for blk in partition:
                if tgt in blk:
                    reachable_blocks.add(frozenset(blk))
                    break
        key = frozenset(reachable_blocks)
        reach_map[key].add(state)
    # Retourner la liste de sous-blocs obtenus
    return [sub for sub in reach_map.values()]


def kanellakis_smolka(states: Set[str], actions: Set[str],
                       transitions: Dict[Tuple[str, str], Set[str]]) -> List[Set[str]]:
    """
    Implémente l'algorithme de Kanellakis-Smolka pour le raffinement de partitions.
    Retourne la partition finale correspondant aux classes de bisimilarité forte.
    Complexité O(n * m) selon Aceto et al. 2011.
    """
    # Partition initiale : un seul bloc contenant tous les états
    partition: List[Set[str]] = [set(states)]
    changed = True
    while changed:
        changed = False
        new_partition: List[Set[str]] = []
        for block in partition:
            refined = False
            for action in actions:
                sub_blocks = split_block(block, action, partition, transitions)
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
    S1, A1, T1 = load_lts(file1)
    S2, A2, T2 = load_lts(file2)
    # Vérifier que les alphabets d'actions sont identiques
    if A1 != A2:
        return False
    part1 = kanellakis_smolka(S1, A1, T1)
    part2 = kanellakis_smolka(S2, A1, T2)
    # Comparer les partitions finales (ensembles de blocs)
    set_blocks1 = {frozenset(b) for b in part1}
    set_blocks2 = {frozenset(b) for b in part2}
    return set_blocks1 == set_blocks2


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} model1.lts model2.lts")
        sys.exit(1)
    file1, file2 = sys.argv[1], sys.argv[2]
    result = are_bisimilar(file1, file2)
    print("Bisimilar" if result else "Not bisimilar")
