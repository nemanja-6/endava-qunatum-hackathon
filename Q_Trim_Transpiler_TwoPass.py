from qiskit.transpiler.basepasses import TransformationPass
from qiskit.transpiler import PassManager
from qiskit.dagcircuit import DAGCircuit
from qiskit.circuit.library import IGate, XGate
import numpy as np

class RedundantGateCancellationPass(TransformationPass):
    def run(self, dag: DAGCircuit) -> DAGCircuit:
        for node in dag.topological_op_nodes():
            next_node = dag.next_op(node)
            if next_node and node.op == next_node.op:
                dag.remove_op_node(node)
                dag.remove_op_node(next_node)
        return dag

class IdleQubitDecouplingPass(TransformationPass):
    def __init__(self, idle_threshold=2):
        super().__init__()
        self.idle_threshold = idle_threshold

    def run(self, dag: DAGCircuit) -> DAGCircuit:
        qubit_timeline = {q: [] for q in dag.qubits}

        # Pass 1: Record gate layers per qubit
        for i, node in enumerate(dag.topological_op_nodes()):
            for q in node.qargs:
                qubit_timeline[q].append(i)

        # Pass 2: Identify idle gaps and insert X-I-X
        for qubit, indices in qubit_timeline.items():
            indices = sorted(indices)
            for i in range(len(indices) - 1):
                gap = indices[i+1] - indices[i]
                if gap >= self.idle_threshold:
                    dag.apply_operation_back(XGate(), qargs=[qubit])
                    dag.apply_operation_back(IGate(), qargs=[qubit])
                    dag.apply_operation_back(XGate(), qargs=[qubit])

        return dag

# Compose Pass Manager
pm = PassManager([
    RedundantGateCancellationPass(),
    IdleQubitDecouplingPass()
])
