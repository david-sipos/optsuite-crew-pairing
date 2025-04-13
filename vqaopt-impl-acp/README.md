Basic integration of the crew pairing problem into VQAOpt.

The provided `ProblemLoader`s load flight legs and use plugins to generate pairings based on `ACPRule`s.
The costs of the generated pairings are determined by a `CostModel`.
The included result processor, "acp-pairings",  charts the solution set. 