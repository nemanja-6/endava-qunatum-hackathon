"""
Template-Based W-State Synthesizer  ·  Qiskit ≥ 2.0
--------------------------------------------------
* Skips tiny W-states (n < 8, linear template is already optimal)
* Uses a balanced-tree template with ⌈log₂ n⌉ depth
* If the chosen physical qubits are disconnected, builds a connectivity-
  agnostic binary-heap tree that never overruns the qubit list (fixes the
  n = 18 crash you saw).
"""
from __future__ import annotations
import math
from collections import defaultdict
from typing import List

from qiskit.circuit import QuantumCircuit, Gate
from qiskit.transpiler.basepasses import TransformationPass
from qiskit.transpiler import Target
from qiskit.converters import circuit_to_dag


# ───────────────────────────
#  tiny linear W-state helper
# ───────────────────────────
class WState(Gate):
    """Linear-depth W-state; kept only for pattern-matching."""
    def __init__(self, n: int):
        super().__init__("w_state", n, [])

    def _define(self):
        n = self.num_qubits
        qc = QuantumCircuit(n, name="w_linear")
        qc.x(0)
        for k in range(n - 1):
            theta = 2 * math.asin(1 / math.sqrt(n - k))
            qc.ry(theta, k)
            qc.cx(k, k + 1)
        self.definition = qc.to_instruction().definition


# ───────────────────────────
#  main transpiler pass
# ───────────────────────────
class WStateSynthesizer(TransformationPass):
    """Replace each WState with a balanced-tree version when beneficial."""

    _MIN_SIZE = 8    # for n < 8 keep the original linear template

    def __init__(self, *, target: Target | None = None):
        super().__init__()
        self._cmap = target.build_coupling_map() if target else None

    # ---------------- entry-point ----------------
    def run(self, dag):
        for node in dag.op_nodes():
            if node.op.name != "w_state":
                continue

            n = len(node.qargs)
            if n < self._MIN_SIZE:
                continue                              # tiny → leave as-is

            phys = [dag.qubits.index(q) for q in node.qargs]
            new_sub = self._balanced_or_agnostic(n, phys)
            dag.substitute_node_with_dag(node, circuit_to_dag(new_sub))

        return dag

    # -------- decide which synthesis path to take --------
    def _balanced_or_agnostic(self, n: int, phys: List[int]) -> QuantumCircuit:
        if not self._cmap:
            return self._agnostic_tree(n)             # no coupling map at all

        # try to span the subset with a BFS tree
        root = phys[0]
        parent, frontier = {root: None}, [root]
        while frontier and len(parent) < n:
            cur = frontier.pop(0)
            for nb in self._cmap.neighbors(cur):
                if nb in phys and nb not in parent:
                    parent[nb] = cur
                    frontier.append(nb)
                    if len(parent) == n:
                        break

        if len(parent) < n:                           # disconnected subset
            return self._agnostic_tree(n)

        return self._connected_balanced_tree(n, phys, parent)

    # -------- connected, coupling-aware balanced tree --------
    def _connected_balanced_tree(
        self, n: int, phys: List[int], parent_map: dict[int, int | None]
    ) -> QuantumCircuit:
        qc = QuantumCircuit(n, name=f"W_bal_{n}")
        qc.x(0)

        # bucket edges by depth for parallel layers
        depths, layers = {phys[0]: 0}, defaultdict(list)
        for child, par in parent_map.items():
            if par is not None:
                depths[child] = depths[par] + 1
                layers[depths[child]].append((par, child))

        angle_iter = iter(2 * math.asin(1 / math.sqrt(k)) for k in range(n, 1, -1))
        for depth in sorted(layers, reverse=True):
            for ctrl, tgt in layers[depth]:
                qc.ry(next(angle_iter), phys.index(ctrl))
                qc.cx(phys.index(ctrl), phys.index(tgt))
            qc.barrier()
        return qc

    # -------- connectivity-agnostic, crash-safe tree --------
    @staticmethod
    def _agnostic_tree(n: int) -> QuantumCircuit:
        """Balanced binary-heap tree that never exceeds n qubits."""
        qc = QuantumCircuit(n, name=f"W_bal_{n}_agnostic")
        qc.x(0)

        # layer buckets: depth(d) = floor(log₂(child+1))
        layers = defaultdict(list)
        for child in range(1, n):
            parent = (child - 1) // 2
            depth = int(math.log2(child + 1))
            layers[depth].append((parent, child))

        angle_iter = iter(2 * math.asin(1 / math.sqrt(k)) for k in range(n, 1, -1))
        for depth in sorted(layers, reverse=True):
            for parent, child in layers[depth]:
                qc.ry(next(angle_iter), parent)
                qc.cx(parent, child)
            qc.barrier()
        return qc
