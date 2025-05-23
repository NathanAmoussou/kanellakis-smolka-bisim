# kanellakis-smolka-bisim
- **Authors:** Florent Belot, Nathan Amoussou
- **University:** Université Côte d'Azur
---
### Abstract
Python Implementation of the Kanellakis and Smolka algorithm to test if two finite transition systems are bisimilar. We will use a custom `.lts` file format for LTS models definition.
### LTS format
Each line represent a transition as a triplet such that the first element represents the starting vertex, the second the action and the third the finishing vertex. The initial vertex of an LTS is considered to be the starting vertex of the first line in the file.
Example (s0 will be considered as the initial vertex): 
```
s0 a s1
s1 b s2
```
### Ressources
- Timed Analysis of Security Protocols, [Corin et al. 2005](http://arxiv.org/abs/cs/0503036)
- The Algorithmics of Bisimilarity, [Aceto et al. 2011](https://www.cambridge.org/core/product/identifier/CBO9780511792588A028/type/book_part)
- [UPPAAL](https://uppaal.org)
### The algorithm by Kanellakis and Smolka
- Let (Pr, Act, -->) be a finite labelled transition system.
- π = {B0, . . . , Bk}, k ≥ 0 a partition of the set of states Pr.
```
π := {Pr}
changed := true
while changed do
	changed := false
	for each block B ∈ π do
		for each action a do
			sort the a-labelled transitions from states in B
			if split(B, a, π) = {B1, B2} ≠ {B}
			then refine π by replacing B with B1 and B2, and set changed to true
```
Using:
```
function split(B, a, π)
choose some state s ∈ B
B1, B2 := ∅
for each state t ∈ B do
	if s and t can reach the same set of blocks in π via a-labelled transitions
	then B1 := B1 ∪ {t}
	else B2 := B2 ∪ {t}
if B2 is empty then return {B1}
else return {B1, B2}
```
With:
> Theorem 0.2.6 (Kanellakis and Smolka) When applied to a finite labelled transition system with n states and m transitions, the algorithm by Kanellakis and Smolka computes the partition corresponding to strong bisimilarity in time O(nm).

– [Aceto et al. 2011](https://www.cambridge.org/core/product/identifier/CBO9780511792588A028/type/book_part)
### Project Realization Steps
1. Theory (LTS, bisimilarity, Kanellakis and Smolka)
2. Parser definition
	- After experimentation, UPPAAL seems to complicated for our needs.
	- We chose to use `.lts` files.
3. Algorithm implementation
4. Testing and examples
