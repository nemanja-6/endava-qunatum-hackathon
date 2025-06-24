"""
Example Usage of Simple Transpiler
Compare with Qiskit's built-in transpiler
"""

from simple_transpiler import SimpleTranspiler
from qiskit import QuantumCircuit, transpile
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit_ibm_runtime.fake_provider import FakeAlmadenV2

import numpy as np


def create_test_circuits():
    """Create various test circuits for transpilation"""

    circuits = {}

    # 1. Simple circuit with gate cancellations
    qc1 = QuantumCircuit(2, 2)
    qc1.h(0)
    qc1.cx(0, 1)
    qc1.h(0)  # Cancels with first H
    qc1.x(1)
    qc1.x(1)  # Cancels with previous X
    qc1.measure_all()
    circuits["cancellation"] = qc1

    # 2. Circuit requiring gate decomposition
    qc2 = QuantumCircuit(3)
    qc2.ry(np.pi / 4, 0)
    qc2.rx(np.pi / 3, 1)
    qc2.rz(np.pi / 6, 2)
    qc2.h(0)
    qc2.cx(0, 1)
    qc2.cx(1, 2)
    circuits["decomposition"] = qc2

    # 3. Circuit requiring routing (for non-adjacent qubits)
    qc3 = QuantumCircuit(4)
    qc3.h(0)
    qc3.cx(0, 2)  # Non-adjacent on linear topology
    qc3.cx(1, 3)  # Non-adjacent
    qc3.cx(0, 3)  # Long-distance
    circuits["routing"] = qc3

    return circuits


def compare_transpilers():
    """Compare our simple transpiler with Qiskit's transpiler"""

    print("🔬 Transpiler Comparison\n")

    # Create test circuits
    circuits = create_test_circuits()

    # Define backend constraints
    # . ``CouplingMap`` instance
    # . List, must be given as an adjacency matrix, where each entry
    #    specifies all directed two-qubit interactions supported by backend,
    #    e.g: ``[[0, 1], [0, 3], [1, 2], [1, 5], [2, 5], [4, 1], [5, 3]]``
    coupling_map = [(0, 1), (1, 2), (2, 3)]  # Linear topology
    coupling_map_2 = [[0, 1], [1, 2], [2, 3]]  # Linear topology
    basis_gates = ["cx", "rz", "sx", "x"]

    # Initialize our transpiler
    simple_transpiler = SimpleTranspiler(
        coupling_map=coupling_map, basis_gates=basis_gates
    )

    for name, circuit in circuits.items():
        print(f"\n{'='*50}")
        print(f"🧪 Testing: {name.upper()} CIRCUIT")
        print(f"{'='*50}")

        print(
            f"Original circuit ({circuit.num_qubits} qubits, {len(circuit.data)} gates):"
        )
        print(circuit.draw())
        print()

        # Our simple transpiler
        print("🔧 OUR SIMPLE TRANSPILER:")
        print("-" * 30)
        our_result = simple_transpiler.transpile(circuit, optimization_level=2)

        print(
            f"\nOur result ({our_result.num_qubits} qubits, {len(our_result.data)} gates):"
        )
        print(our_result.draw())
        print()

        # Qiskit's transpiler (for comparison)
        print("⚙️  QISKIT'S TRANSPILER:")
        print("-" * 30)
        qiskit_result = transpile(
            circuit,
            coupling_map=coupling_map_2,
            basis_gates=basis_gates,
            optimization_level=2,
        )

        print(
            f"Qiskit result ({qiskit_result.num_qubits} qubits, {len(qiskit_result.data)} gates):"
        )
        print(qiskit_result.draw())
        print()


def demonstrate_optimization_levels():
    """Show the effect of different optimization levels"""

    print("📈 Optimization Level Comparison\n")

    # Create a circuit with optimization opportunities
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.h(0)  # Cancellation opportunity
    qc.ry(np.pi / 4, 1)
    qc.rx(np.pi / 3, 2)
    qc.cx(0, 1)
    qc.x(2)
    qc.x(2)  # Another cancellation
    qc.cx(1, 2)
    qc.h(1)

    print(f"Original circuit:\n{qc.draw()}\n")

    transpiler = SimpleTranspiler(
        coupling_map=[(0, 1), (1, 2)], basis_gates=["cx", "rz", "sx", "x"]
    )

    # Test different optimization levels
    for level in [0, 1, 2]:
        print(f"{'='*40}")
        print(f"🎯 OPTIMIZATION LEVEL {level}")
        print(f"{'='*40}")

        result = transpiler.transpile(qc.copy(), optimization_level=level)

        print(f"\nResult ({len(result.data)} gates, depth {result.depth()}):")
        print(result.draw())
        print()


def analyze_real_backend():
    """Demonstrate transpilation for a real IBM backend"""

    print("🏭 Real Backend Analysis\n")

    # Use GenericBackendV2 as an example IBM backend
    backend = GenericBackendV2(num_qubits=5)

    print(f"Backend: {backend.name}")
    print(f"Qubits: {backend.num_qubits}")
    print(f"Coupling map: {backend.coupling_map}")
    print(f"Basis gates: {backend._basis_gates}")
    print()

    # Create a circuit that challenges the backend constraints
    qc = QuantumCircuit(5)
    qc.h(0)
    qc.cx(0, 4)  # Long-distance connection
    qc.ry(np.pi / 4, 2)
    qc.cx(2, 0)
    qc.cx(4, 1)
    qc.measure_all()

    print(f"Test circuit:\n{qc.draw()}\n")

    # Our transpiler
    our_transpiler = SimpleTranspiler(
        coupling_map=backend.coupling_map,
        basis_gates=["cx", "rz", "sx", "x"],  # Simplified basis
    )

    print("🔧 Our transpiler result:")
    our_result = our_transpiler.transpile(qc, optimization_level=2)
    print(f"Gates: {len(our_result.data)}, Depth: {our_result.depth()}")
    print()

    # Qiskit's transpiler
    print("⚙️  Qiskit transpiler result:")
    qiskit_result = transpile(qc, backend=backend, optimization_level=2)
    print(f"Gates: {len(qiskit_result.data)}, Depth: {qiskit_result.depth()}")


if __name__ == "__main__":
    print("🚀 Simple Transpiler Examples\n")

    # Run demonstrations
    compare_transpilers()
    demonstrate_optimization_levels()
    analyze_real_backend()

    print("\n✅ All demonstrations complete!")
    print("\n💡 Key Concepts Demonstrated:")
    print("   - Gate cancellation optimization")
    print("   - Gate decomposition to basis sets")
    print("   - Qubit routing with SWAP insertion")
    print("   - Commutation-based optimization")
    print("   - Comparison with Qiskit's transpiler")
