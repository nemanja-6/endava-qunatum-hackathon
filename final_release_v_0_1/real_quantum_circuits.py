from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np
from typing import List, Dict, Tuple, Optional




def __init__(self):
    """Initialize the quantum circuits library"""
    self.circuits = {}


def create_bell_states(self) -> Dict[str, QuantumCircuit]:
    """Create all four Bell states (maximally entangled two-qubit states)"""
    bell_circuits = {}

    # Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2
    bell_00 = QuantumCircuit(2, name='Bell_Phi_Plus')
    bell_00.h(0)
    bell_00.cx(0, 1)
    bell_circuits['phi_plus'] = bell_00

    # Bell state |Φ-⟩ = (|00⟩ - |11⟩)/√2
    bell_01 = QuantumCircuit(2, name='Bell_Phi_Minus')
    bell_01.h(0)
    bell_01.z(0)
    bell_01.cx(0, 1)
    bell_circuits['phi_minus'] = bell_01

    # Bell state |Ψ+⟩ = (|01⟩ + |10⟩)/√2
    bell_10 = QuantumCircuit(2, name='Bell_Psi_Plus')
    bell_10.h(0)
    bell_10.cx(0, 1)
    bell_10.x(1)
    bell_circuits['psi_plus'] = bell_10

    # Bell state |Ψ-⟩ = (|01⟩ - |10⟩)/√2
    bell_11 = QuantumCircuit(2, name='Bell_Psi_Minus')
    bell_11.h(0)
    bell_11.z(0)
    bell_11.cx(0, 1)
    bell_11.x(1)
    bell_circuits['psi_minus'] = bell_11

    print("✅ Created 4 Bell state circuits")
    return bell_circuits


def create_ghz_state(self, n_qubits: int = 3) -> QuantumCircuit:
    """Create GHZ state |GHZ⟩ = (|000...⟩ + |111...⟩)/√2"""
    qc = QuantumCircuit(n_qubits, name=f'GHZ_{n_qubits}')

    # Create superposition on first qubit
    qc.h(0)

    # Entangle all qubits
    for i in range(1, n_qubits):
        qc.cx(0, i)

    print(f"✅ Created {n_qubits}-qubit GHZ state")
    return qc


def create_quantum_teleportation(self) -> QuantumCircuit:
    """Create quantum teleportation protocol"""
    # 3 qubits: message, Alice's ancilla, Bob's qubit
    qc = QuantumCircuit(3, 2, name='Quantum_Teleportation')

    # Prepare message state |ψ⟩ = α|0⟩ + β|1⟩
    # For demo, create |+⟩ state
    qc.h(0)  # Message qubit

    qc.barrier(label="Message prepared")

    # Create Bell pair between Alice and Bob
    qc.h(1)  # Alice's ancilla
    qc.cx(1, 2)  # Entangle with Bob's qubit

    qc.barrier(label="Bell pair created")

    # Alice's measurement
    qc.cx(0, 1)  # Entangle message with ancilla
    qc.h(0)  # Hadamard on message

    # Measure Alice's qubits
    qc.measure(0, 0)
    qc.measure(1, 1)

    qc.barrier(label="Alice measures")

    # Bob's correction based on Alice's measurements
    qc.cx(1, 2)  # Correct based on ancilla measurement
    qc.cz(0, 2)  # Correct based on message measurement

    print("✅ Created quantum teleportation circuit")
    return qc


def create_deutsch_jozsa(self, n_qubits: int = 3, oracle_type: str = 'constant') -> QuantumCircuit:
    """Create Deutsch-Jozsa algorithm circuit"""
    # n input qubits + 1 ancilla
    qc = QuantumCircuit(n_qubits + 1, n_qubits, name=f'Deutsch_Jozsa_{oracle_type}')

    # Initialize ancilla in |1⟩
    qc.x(n_qubits)

    # Apply Hadamard to all qubits
    for i in range(n_qubits + 1):
        qc.h(i)

    qc.barrier(label="Superposition")

    # Oracle implementation
    if oracle_type == 'constant_0':
        # Do nothing - f(x) = 0 for all x
        pass
    elif oracle_type == 'constant_1':
        # Flip ancilla - f(x) = 1 for all x
        qc.x(n_qubits)
    elif oracle_type == 'balanced':
        # Example balanced function: f(x) = x_0 ⊕ x_1 ⊕ ... (XOR of all inputs)
        for i in range(n_qubits):
            qc.cx(i, n_qubits)

    qc.barrier(label="Oracle")

    # Apply Hadamard to input qubits
    for i in range(n_qubits):
        qc.h(i)

    # Measure input qubits
    for i in range(n_qubits):
        qc.measure(i, i)

    print(f"✅ Created Deutsch-Jozsa algorithm ({oracle_type})")
    return qc


def create_grovers_algorithm(self, n_qubits: int = 3, marked_item: int = 5) -> QuantumCircuit:
    """Create Grover's search algorithm"""
    N = 2 ** n_qubits
    optimal_iterations = int(np.pi / 4 * np.sqrt(N))

    qc = QuantumCircuit(n_qubits, n_qubits, name=f'Grovers_{n_qubits}qubits')

    # Initialize superposition
    for i in range(n_qubits):
        qc.h(i)

    qc.barrier(label="Superposition")

    # Grover iterations
    for iteration in range(optimal_iterations):
        # Oracle: mark the target item
        self._grover_oracle(qc, n_qubits, marked_item)

        qc.barrier(label=f"Oracle {iteration + 1}")

        # Diffusion operator (amplitude amplification)
        self._grover_diffusion(qc, n_qubits)

        qc.barrier(label=f"Diffusion {iteration + 1}")

    # Measure all qubits
    qc.measure_all()

    print(f"✅ Created Grover's algorithm (n={n_qubits}, target={marked_item}, iterations={optimal_iterations})")
    return qc


def _grover_oracle(self, qc: QuantumCircuit, n_qubits: int, marked_item: int):
    """Oracle that marks a specific item in Grover's algorithm"""
    # Convert marked item to binary and apply multi-controlled Z
    binary = format(marked_item, f'0{n_qubits}b')

    # Flip qubits that should be 0 in the marked state
    for i, bit in enumerate(binary):
        if bit == '0':
            qc.x(i)

    # Multi-controlled Z gate
    if n_qubits == 1:
        qc.z(0)
    elif n_qubits == 2:
        qc.cz(0, 1)
    else:
        # Use multi-controlled Z (implemented with CCX gates)
        qc.h(n_qubits - 1)
        qc.ccx(0, 1, n_qubits - 1)  # Simplified for 3 qubits
        qc.h(n_qubits - 1)

    # Flip back the qubits that were flipped
    for i, bit in enumerate(binary):
        if bit == '0':
            qc.x(i)


def _grover_diffusion(self, qc: QuantumCircuit, n_qubits: int):
    """Diffusion operator for Grover's algorithm"""
    # Apply Hadamard to all qubits
    for i in range(n_qubits):
        qc.h(i)

    # Apply X to all qubits
    for i in range(n_qubits):
        qc.x(i)

    # Multi-controlled Z on |111...⟩ state
    if n_qubits == 1:
        qc.z(0)
    elif n_qubits == 2:
        qc.cz(0, 1)
    else:
        qc.h(n_qubits - 1)
        qc.ccx(0, 1, n_qubits - 1)  # Simplified for 3 qubits
        qc.h(n_qubits - 1)

    # Apply X to all qubits
    for i in range(n_qubits):
        qc.x(i)

    # Apply Hadamard to all qubits
    for i in range(n_qubits):
        qc.h(i)


def create_qft(self, n_qubits: int = 3) -> QuantumCircuit:
    """Create Quantum Fourier Transform circuit"""
    qc = QuantumCircuit(n_qubits, name=f'QFT_{n_qubits}')

    def qft_rotations(circuit, n):
        """Apply the rotations for QFT"""
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

    print(f"✅ Created {n_qubits}-qubit QFT circuit")
    return qc


def create_vqe_ansatz(self, n_qubits: int = 4, layers: int = 2) -> QuantumCircuit:
    """Create a Variational Quantum Eigensolver (VQE) ansatz"""
    qc = QuantumCircuit(n_qubits, name=f'VQE_Ansatz_{n_qubits}q_{layers}L')

    for layer in range(layers):
        # Single-qubit rotations
        for qubit in range(n_qubits):
            # Use example parameter values (in practice, these would be optimized)
            theta = np.pi / 4  # Example parameter value
            phi = np.pi / 6  # Example parameter value
            qc.ry(theta, qubit)
            qc.rz(phi, qubit)

        # Entangling layer
        for qubit in range(n_qubits - 1):
            qc.cx(qubit, qubit + 1)

        # Add barrier for visualization
        qc.barrier(label=f"Layer {layer + 1}")

    print(f"✅ Created VQE ansatz ({n_qubits} qubits, {layers} layers)")
    return qc


def create_qaoa_circuit(self, n_qubits: int = 4, p: int = 2) -> QuantumCircuit:
    """Create Quantum Approximate Optimization Algorithm (QAOA) circuit"""
    qc = QuantumCircuit(n_qubits, name=f'QAOA_{n_qubits}q_p{p}')

    # Initial state: equal superposition
    for qubit in range(n_qubits):
        qc.h(qubit)

    qc.barrier(label="Initial state")

    # QAOA layers
    for round in range(p):
        # Problem Hamiltonian (example: MaxCut on linear chain)
        gamma = np.pi / 4  # Example parameter
        for qubit in range(n_qubits - 1):
            qc.rzz(2 * gamma, qubit, qubit + 1)

        qc.barrier(label=f"Problem Ham {round + 1}")

        # Mixer Hamiltonian
        beta = np.pi / 8  # Example parameter
        for qubit in range(n_qubits):
            qc.rx(2 * beta, qubit)

        qc.barrier(label=f"Mixer Ham {round + 1}")

    print(f"✅ Created QAOA circuit ({n_qubits} qubits, p={p} rounds)")
    return qc


def create_bernstein_vazirani(self, secret_string: str = "101") -> QuantumCircuit:
    """Create Bernstein-Vazirani algorithm"""
    n_qubits = len(secret_string)
    qc = QuantumCircuit(n_qubits + 1, n_qubits, name='Bernstein_Vazirani')

    # Initialize ancilla in |1⟩
    qc.x(n_qubits)

    # Apply Hadamard to all qubits
    for i in range(n_qubits + 1):
        qc.h(i)

    qc.barrier(label="Superposition")

    # Oracle: f(x) = s·x (dot product with secret string)
    for i, bit in enumerate(secret_string):
        if bit == '1':
            qc.cx(i, n_qubits)

    qc.barrier(label="Oracle")

    # Apply Hadamard to input qubits
    for i in range(n_qubits):
        qc.h(i)

    # Measure input qubits
    qc.measure_all()

    print(f"✅ Created Bernstein-Vazirani algorithm (secret: {secret_string})")
    return qc


def create_superdense_coding(self) -> QuantumCircuit:
    """Create superdense coding protocol"""
    qc = QuantumCircuit(2, 2, name='Superdense_Coding')

    # Create Bell pair
    qc.h(0)
    qc.cx(0, 1)

    qc.barrier(label="Bell pair shared")

    # Alice encodes 2-bit message (example: "11")
    qc.z(0)  # Encode second bit
    qc.x(0)  # Encode first bit

    qc.barrier(label="Alice encodes")

    # Bob decodes by Bell measurement
    qc.cx(0, 1)
    qc.h(0)

    # Measure both qubits
    qc.measure_all()

    print("✅ Created superdense coding circuit")
    return qc


def create_quantum_adder(self, n_bits: int = 2) -> QuantumCircuit:
    """Create quantum ripple-carry adder"""
    # Need n_bits for each number + n_bits for carry + 1 for final carry
    total_qubits = 3 * n_bits + 1
    qc = QuantumCircuit(total_qubits, name=f'Quantum_Adder_{n_bits}bit')

    # Initialize with example values (A=2, B=1 for 2-bit case)
    if n_bits >= 2:
        qc.x(1)  # A = 10 (binary) = 2
        qc.x(2 * n_bits)  # B = 01 (binary) = 1

    qc.barrier(label="Input preparation")

    # Quantum full adder implementation (simplified)
    for i in range(n_bits):
        a_qubit = i
        b_qubit = n_bits + i
        carry_qubit = 2 * n_bits + i
        sum_qubit = 2 * n_bits + i + 1 if i < n_bits - 1 else 2 * n_bits + n_bits

        # Simplified adder logic using Toffoli gates
        qc.ccx(a_qubit, b_qubit, carry_qubit)
        qc.cx(a_qubit, b_qubit)
        qc.ccx(carry_qubit, b_qubit, sum_qubit)

    print(f"✅ Created {n_bits}-bit quantum adder")
    return qc


def create_quantum_phase_kickback(self) -> QuantumCircuit:
    """Create quantum phase kickback demonstration"""
    qc = QuantumCircuit(2, name='Phase_Kickback')

    # Prepare control in superposition
    qc.h(0)

    # Prepare target in eigenstate of Z gate (|1⟩)
    qc.x(1)

    qc.barrier(label="State preparation")

    # Controlled-Z creates phase kickback
    qc.cz(0, 1)

    qc.barrier(label="Phase kickback")

    # Measure control qubit to see phase effect
    qc.h(0)  # Transform phase to amplitude

    print("✅ Created phase kickback demonstration")
    return qc


def generate_all_circuits(self) -> Dict[str, QuantumCircuit]:
    """Generate all quantum circuits in the library"""
    all_circuits = {}

    print("🔮 Generating Real Quantum Circuits Library")
    print("=" * 50)

    # Basic states and protocols
    all_circuits.update(self.create_bell_states())
    all_circuits['ghz_3'] = self.create_ghz_state(3)
    all_circuits['ghz_4'] = self.create_ghz_state(4)
    all_circuits['teleportation'] = self.create_quantum_teleportation()
    all_circuits['superdense_coding'] = self.create_superdense_coding()

    # Quantum algorithms
    all_circuits['deutsch_jozsa_constant'] = self.create_deutsch_jozsa(3, 'constant_0')
    all_circuits['deutsch_jozsa_balanced'] = self.create_deutsch_jozsa(3, 'balanced')
    all_circuits['grovers_3q'] = self.create_grovers_algorithm(3, 5)
    all_circuits['bernstein_vazirani'] = self.create_bernstein_vazirani("101")

    # Quantum transforms
    all_circuits['qft_3'] = self.create_qft(3)
    all_circuits['qft_4'] = self.create_qft(4)

    # Variational algorithms
    all_circuits['vqe_ansatz'] = self.create_vqe_ansatz(4, 2)
    all_circuits['qaoa'] = self.create_qaoa_circuit(4, 2)

    # Advanced concepts
    all_circuits['quantum_adder'] = self.create_quantum_adder(2)
    all_circuits['phase_kickback'] = self.create_quantum_phase_kickback()

    print(f"\n✅ Generated {len(all_circuits)} real quantum circuits!")
    return all_circuits


def analyze_circuits(self, circuits: Dict[str, QuantumCircuit]):
    """Analyze the generated circuits"""
    print(f"\n📊 Circuit Analysis:")
    print("-" * 70)
    print(f"{'Name':<25} | {'Qubits':>6} | {'Gates':>5} | {'Depth':>5} | {'Type'}")
    print("-" * 70)

    total_gates = 0
    total_qubits = 0

    # Categorize circuits
    categories = {
        'Entanglement': ['phi_plus', 'phi_minus', 'psi_plus', 'psi_minus', 'ghz_3', 'ghz_4'],
        'Protocols': ['teleportation', 'superdense_coding'],
        'Algorithms': ['deutsch_jozsa_constant', 'deutsch_jozsa_balanced', 'grovers_3q', 'bernstein_vazirani'],
        'Transforms': ['qft_3', 'qft_4'],
        'Variational': ['vqe_ansatz', 'qaoa'],
        'Advanced': ['quantum_adder', 'phase_kickback']
    }

    for category, circuit_names in categories.items():
        for name in circuit_names:
            if name in circuits:
                circuit = circuits[name]
                n_qubits = circuit.num_qubits
                n_gates = len(circuit.data)
                depth = circuit.depth()

                total_gates += n_gates
                total_qubits += n_qubits

                print(f"{name:<25} | {n_qubits:>6} | {n_gates:>5} | {depth:>5} | {category}")

    print("-" * 70)
    print(f"{'TOTAL':<25} | {total_qubits:>6} | {total_gates:>5} |       |")
    print(f"Average gates per circuit: {total_gates / len(circuits):.1f}")
    print(f"Average qubits per circuit: {total_qubits / len(circuits):.1f}")

