"""
Large-Scale Quantum Circuits
Demonstrates quantum algorithms scaled to 20+ qubits
"""

from qiskit import QuantumCircuit
import numpy as np
from typing import List, Dict
import time
from real_quantum_circuits import RealQuantumCircuits


class LargeScaleQuantumCircuits(RealQuantumCircuits):
    """Large-scale quantum circuits with 20+ qubits"""

    def create_large_ghz_state(self, n_qubits: int = 25) -> QuantumCircuit:
        """Create large GHZ state with 20+ qubits"""
        qc = QuantumCircuit(n_qubits, name=f'Large_GHZ_{n_qubits}')

        # Create superposition on first qubit
        qc.h(0)

        # Entangle all qubits with the first one
        for i in range(1, n_qubits):
            qc.cx(0, i)

        print(f"✅ Created {n_qubits}-qubit large GHZ state")
        return qc

    def create_large_deutsch_jozsa(self, n_qubits: int = 20, oracle_type: str = 'balanced') -> QuantumCircuit:
        """Create large Deutsch-Jozsa algorithm with 20+ qubits"""
        qc = QuantumCircuit(n_qubits + 1, n_qubits, name=f'Large_DJ_{n_qubits}_{oracle_type}')

        # Initialize ancilla in |1⟩
        qc.x(n_qubits)

        # Apply Hadamard to all qubits
        for i in range(n_qubits + 1):
            qc.h(i)

        qc.barrier(label="Superposition")

        # Oracle implementation
        if oracle_type == 'balanced':
            for i in range(n_qubits // 2):
                qc.cx(i, n_qubits)
        elif oracle_type == 'parity':
            for i in range(n_qubits):
                qc.cx(i, n_qubits)

        qc.barrier(label="Oracle")

        # Apply Hadamard to input qubits
        for i in range(n_qubits):
            qc.h(i)

        # Measure input qubits
        for i in range(n_qubits):
            qc.measure(i, i)

        print(f"✅ Created large Deutsch-Jozsa ({n_qubits} qubits, {oracle_type})")
        return qc

    def create_large_qft(self, n_qubits: int = 20) -> QuantumCircuit:
        """Create large Quantum Fourier Transform with 20+ qubits"""
        qc = QuantumCircuit(n_qubits, name=f'Large_QFT_{n_qubits}')

        def qft_rotations(circuit, n):
            if n == 0:
                return circuit
            n -= 1
            circuit.h(n)
            for qubit in range(n):
                circuit.cp(np.pi / 2 ** (n - qubit), qubit, n)
            qft_rotations(circuit, n)

        qft_rotations(qc, n_qubits)

        # Swap qubits to get correct order
        for qubit in range(n_qubits // 2):
            qc.swap(qubit, n_qubits - qubit - 1)

        print(f"✅ Created large {n_qubits}-qubit QFT")
        return qc

    def create_large_vqe_ansatz(self, n_qubits: int = 24, layers: int = 3) -> QuantumCircuit:
        """Create large VQE ansatz with 20+ qubits"""
        qc = QuantumCircuit(n_qubits, name=f'Large_VQE_{n_qubits}q_{layers}L')

        for layer in range(layers):
            # Single-qubit rotations on all qubits
            for qubit in range(n_qubits):
                theta = np.pi / 4 + layer * 0.1
                phi = np.pi / 6 + layer * 0.1
                qc.ry(theta, qubit)
                qc.rz(phi, qubit)

            # Entangling layer
            for qubit in range(n_qubits - 1):
                qc.cx(qubit, qubit + 1)
            if n_qubits > 2:
                qc.cx(n_qubits - 1, 0)  # Close the loop

            qc.barrier(label=f"Layer {layer + 1}")

        print(f"✅ Created large VQE ansatz ({n_qubits} qubits, {layers} layers)")
        return qc

    def create_large_qaoa(self, n_qubits: int = 22, p: int = 3) -> QuantumCircuit:
        """Create large QAOA circuit with 20+ qubits"""
        qc = QuantumCircuit(n_qubits, name=f'Large_QAOA_{n_qubits}q_p{p}')

        # Initial state: equal superposition
        for qubit in range(n_qubits):
            qc.h(qubit)

        qc.barrier(label="Initial state")

        # QAOA layers
        for round_num in range(p):
            # Problem Hamiltonian - MaxCut on ring graph
            gamma = np.pi / 4 * (1 + round_num * 0.1)
            for qubit in range(n_qubits):
                next_qubit = (qubit + 1) % n_qubits
                qc.rzz(2 * gamma, qubit, next_qubit)

            qc.barrier(label=f"Problem Ham {round_num + 1}")

            # Mixer Hamiltonian
            beta = np.pi / 8 * (1 + round_num * 0.1)
            for qubit in range(n_qubits):
                qc.rx(2 * beta, qubit)

            qc.barrier(label=f"Mixer Ham {round_num + 1}")

        print(f"✅ Created large QAOA ({n_qubits} qubits, p={p})")
        return qc

    def create_large_bernstein_vazirani(self, secret_length: int = 25) -> QuantumCircuit:
        """Create large Bernstein-Vazirani with 20+ qubit secret"""
        secret_string = ''.join(np.random.choice(['0', '1']) for _ in range(secret_length))

        qc = QuantumCircuit(secret_length + 1, secret_length, name=f'Large_BV_{secret_length}')

        # Initialize ancilla in |1⟩
        qc.x(secret_length)

        # Apply Hadamard to all qubits
        for i in range(secret_length + 1):
            qc.h(i)

        qc.barrier(label="Superposition")

        # Oracle: f(x) = s·x (dot product with secret string)
        for i, bit in enumerate(secret_string):
            if bit == '1':
                qc.cx(i, secret_length)

        qc.barrier(label="Oracle")

        # Apply Hadamard to input qubits
        for i in range(secret_length):
            qc.h(i)

        # Measure input qubits
        qc.measure_all()

        print(f"✅ Created large Bernstein-Vazirani ({secret_length} qubits)")
        print(f"   Secret: {secret_string[:10]}...{secret_string[-10:]}")
        return qc

    def generate_large_scale_circuits(self) -> Dict[str, QuantumCircuit]:
        """Generate all large-scale quantum circuits"""
        large_circuits = {}

        print("🚀 Generating Large-Scale Quantum Circuits (20+ Qubits)")
        print("=" * 60)

        # Large entanglement states
        large_circuits['ghz_25'] = self.create_large_ghz_state(25)
        large_circuits['ghz_50'] = self.create_large_ghz_state(50)

        # Large quantum algorithms
        large_circuits['deutsch_jozsa_20'] = self.create_large_deutsch_jozsa(20, 'balanced')
        large_circuits['deutsch_jozsa_30'] = self.create_large_deutsch_jozsa(30, 'parity')

        # Large transforms
        large_circuits['qft_20'] = self.create_large_qft(20)
        large_circuits['qft_32'] = self.create_large_qft(32)

        # Large variational circuits
        large_circuits['vqe_24'] = self.create_large_vqe_ansatz(24, 3)
        large_circuits['vqe_40'] = self.create_large_vqe_ansatz(40, 2)
        large_circuits['qaoa_22'] = self.create_large_qaoa(22, 3)
        large_circuits['qaoa_30'] = self.create_large_qaoa(30, 2)

        # Large hidden string problems
        large_circuits['bernstein_vazirani_25'] = self.create_large_bernstein_vazirani(25)
        large_circuits['bernstein_vazirani_40'] = self.create_large_bernstein_vazirani(40)

        print(f"\n✅ Generated {len(large_circuits)} large-scale quantum circuits!")
        return large_circuits

    def analyze_scaling(self, circuits: Dict[str, QuantumCircuit]):
        """Analyze scaling properties of large circuits"""
        print(f"\n📈 Scaling Analysis:")
        print("-" * 80)
        print(f"{'Circuit':<30} | {'Qubits':>6} | {'Gates':>7} | {'Depth':>6} | {'2Q Gates':>8}")
        print("-" * 80)

        total_qubits = 0
        total_gates = 0

        for name, circuit in circuits.items():
            n_qubits = circuit.num_qubits
            n_gates = len(circuit.data)
            depth = circuit.depth()

            # Count two-qubit gates
            two_qubit_gates = 0
            for instruction in circuit.data:
                if len(instruction.qubits) == 2 and instruction.operation.name not in ['measure', 'barrier']:
                    two_qubit_gates += 1

            total_qubits += n_qubits
            total_gates += n_gates

            print(f"{name:<30} | {n_qubits:>6} | {n_gates:>7} | {depth:>6} | {two_qubit_gates:>8}")

        print("-" * 80)
        print(f"{'TOTALS':<30} | {total_qubits:>6} | {total_gates:>7} |        |")
        print(f"Average qubits per circuit: {total_qubits / len(circuits):.1f}")
        print(f"Average gates per circuit: {total_gates / len(circuits):.1f}")

        print(f"\n💡 Scaling Insights:")
        print(f"• GHZ states scale linearly: O(n) gates for n qubits")
        print(f"• QFT scales quadratically: O(n²) gates for n qubits")
        print(f"• VQE/QAOA complexity depends on connectivity and layers")
        print(f"• Two-qubit gates are the bottleneck on real hardware")


def demo_large_scale_circuits():
    """Demonstration of large-scale quantum circuits"""
    print("🚀 Large-Scale Quantum Circuits Demo")
    print("=" * 45)

    # Create the large circuits library
    large_lib = LargeScaleQuantumCircuits()

    # Generate large circuits
    start_time = time.time()
    large_circuits = large_lib.generate_large_scale_circuits()
    generation_time = time.time() - start_time

    print(f"\n⏱️  Generation time: {generation_time:.2f} seconds")

    # Analyze scaling
    large_lib.analyze_scaling(large_circuits)

    print(f"\n🔬 Hardware Scaling Challenges:")
    print(f"• Gate fidelity: ~99.9% for 1Q, ~99% for 2Q gates")
    print(f"• Decoherence: T1 ~100μs, T2 ~50μs typical")
    print(f"• Connectivity: Limited qubit coupling on real devices")
    print(f"• Crosstalk: Gates on nearby qubits can interfere")

    print(f"\n🎯 Current Quantum Hardware:")
    print(f"• IBM: Up to 1000+ qubits (IBM Condor)")
    print(f"• Google: 70 qubits (Sycamore)")
    print(f"• Rigetti: 80 qubits (Aspen series)")
    print(f"• IonQ: 32 qubits (trapped ion)")

    return large_circuits


if __name__ == "__main__":
    circuits = demo_large_scale_circuits()
    print("\n🎯 Large-scale circuits push quantum computing to its limits!")
    print("🔬 These test the boundaries of current quantum hardware")
    print("🚀 Essential for quantum hardware benchmarking")