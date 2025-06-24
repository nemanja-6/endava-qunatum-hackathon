"""
Simple Quantum Circuit Transpiler
Demonstrates core transpilation concepts for educational purposes
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Gate, Instruction
from qiskit.circuit.library import CXGate, RZGate, SXGate, XGate, HGate, RYGate, RXGate
from typing import List, Dict, Tuple, Set
import numpy as np


class SimpleTranspiler:
    """A simple transpiler demonstrating core concepts"""
    
    def __init__(self, coupling_map: List[Tuple[int, int]] = None, basis_gates: List[str] = None):
        """
        Initialize the transpiler
        
        Args:
            coupling_map: List of (control, target) qubit pairs representing connectivity
            basis_gates: List of supported gate names for the target backend
        """
        self.coupling_map = coupling_map or []
        self.basis_gates = basis_gates or ['cx', 'rz', 'sx', 'x']
        self.coupling_graph = self._build_coupling_graph()
        
    def _build_coupling_graph(self) -> Dict[int, Set[int]]:
        """Build adjacency graph from coupling map"""
        graph = {}
        for control, target in self.coupling_map:
            if control not in graph:
                graph[control] = set()
            if target not in graph:
                graph[target] = set()
            graph[control].add(target)
            graph[target].add(control)  # Bidirectional
        return graph
    
    def transpile(self, circuit: QuantumCircuit, optimization_level: int = 1) -> QuantumCircuit:
        """
        Main transpilation function
        
        Args:
            circuit: Input quantum circuit
            optimization_level: 0=no optimization, 1=basic, 2=advanced
            
        Returns:
            Transpiled quantum circuit
        """
        print(f"🔄 Starting transpilation (level {optimization_level})")
        
        # Step 1: Analysis
        print("📊 Analyzing circuit...")
        stats = self._analyze_circuit(circuit)
        print(f"   - Original: {stats['gates']} gates, depth {stats['depth']}")
        
        # Step 2: Basic optimizations (if requested)
        if optimization_level >= 1:
            print("⚡ Applying basic optimizations...")
            circuit = self._basic_optimize(circuit)
        
        # Step 3: Gate decomposition to basis gates
        print("🔧 Decomposing to basis gates...")
        circuit = self._decompose_to_basis(circuit)
        
        # Step 4: Layout and routing (if coupling map provided)
        if self.coupling_map:
            print("🗺️  Applying layout and routing...")
            circuit = self._layout_and_route(circuit)
        
        # Step 5: Final optimizations
        if optimization_level >= 2:
            print("🚀 Applying advanced optimizations...")
            circuit = self._advanced_optimize(circuit)
        
        # Final statistics
        final_stats = self._analyze_circuit(circuit)
        print(f"✅ Transpilation complete!")
        print(f"   - Final: {final_stats['gates']} gates, depth {final_stats['depth']}")
        
        return circuit
    
    def _analyze_circuit(self, circuit: QuantumCircuit) -> Dict:
        """Analyze circuit properties"""
        gate_count = 0
        two_qubit_gates = 0
        
        for instruction in circuit.data:
            gate_count += 1
            if len(instruction.qubits) == 2:
                two_qubit_gates += 1
                
        return {
            'gates': gate_count,
            'depth': circuit.depth(),
            'two_qubit_gates': two_qubit_gates,
            'qubits': circuit.num_qubits
        }
    
    def _basic_optimize(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Apply basic circuit optimizations"""
        # Create new circuit with same registers
        optimized = QuantumCircuit()
        for qreg in circuit.qregs:
            optimized.add_register(qreg)
        for creg in circuit.cregs:
            optimized.add_register(creg)
        
        # Simple gate cancellation: X-X = I, H-H = I
        gates_to_apply = []
        
        for instruction in circuit.data:
            gate_name = instruction.operation.name
            qubits = instruction.qubits
            
            # Check for immediate cancellation with previous gate
            if (gates_to_apply and 
                gates_to_apply[-1]['name'] == gate_name and
                gates_to_apply[-1]['qubits'] == qubits and
                gate_name in ['x', 'h']):  # Self-inverse gates
                # Cancel both gates
                gates_to_apply.pop()
                print(f"   ❌ Cancelled {gate_name} gates on qubit {circuit.find_bit(qubits[0]).index}")
            else:
                gates_to_apply.append({
                    'instruction': instruction,
                    'name': gate_name,
                    'qubits': qubits
                })
        
        # Apply remaining gates
        for gate_info in gates_to_apply:
            optimized.append(gate_info['instruction'])
            
        return optimized
    
    def _decompose_to_basis(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Decompose gates to basis gate set"""
        decomposed = QuantumCircuit()
        for qreg in circuit.qregs:
            decomposed.add_register(qreg)
        for creg in circuit.cregs:
            decomposed.add_register(creg)
        
        for instruction in circuit.data:
            gate_name = instruction.operation.name
            qubits = instruction.qubits
            params = instruction.operation.params if hasattr(instruction.operation, 'params') else []
            
            if gate_name in self.basis_gates:
                # Gate is already in basis set
                decomposed.append(instruction)
            else:
                # Decompose to basis gates
                print(f"   🔧 Decomposing {gate_name} gate")
                self._decompose_gate(decomposed, gate_name, qubits, params)
        
        return decomposed
    
    def _decompose_gate(self, circuit: QuantumCircuit, gate_name: str, 
                       qubits: List, params: List):
        """Decompose specific gate types to basis gates"""
        
        if gate_name == 'h':
            # H = RZ(π) SX RZ(π/2)
            circuit.rz(np.pi, qubits[0])
            circuit.sx(qubits[0])
            circuit.rz(np.pi/2, qubits[0])
            
        elif gate_name == 'ry':
            # RY(θ) = RZ(-π/2) RX(θ) RZ(π/2)
            angle = params[0]
            circuit.rz(-np.pi/2, qubits[0])
            # RX(θ) = SX RZ(θ) SX
            circuit.sx(qubits[0])
            circuit.rz(angle, qubits[0])
            circuit.sx(qubits[0])
            circuit.rz(np.pi/2, qubits[0])
            
        elif gate_name == 'rx':
            # RX(θ) = SX RZ(θ) SX
            angle = params[0]
            circuit.sx(qubits[0])
            circuit.rz(angle, qubits[0])
            circuit.sx(qubits[0])
            
        else:
            print(f"   ⚠️  Unknown gate {gate_name}, keeping as-is")
            # Keep original gate if decomposition not implemented
            if gate_name == 'cx':
                circuit.cx(qubits[0], qubits[1])
            elif gate_name == 'x':
                circuit.x(qubits[0])
    
    def _layout_and_route(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Apply initial layout and route around coupling constraints"""
        if not self.coupling_map:
            return circuit
            
        routed = QuantumCircuit()
        for qreg in circuit.qregs:
            routed.add_register(qreg)
        for creg in circuit.cregs:
            routed.add_register(creg)
        
        for instruction in circuit.data:
            qubits = instruction.qubits
            
            if len(qubits) == 2:  # Two-qubit gate
                q0, q1 = circuit.find_bit(qubits[0]).index, circuit.find_bit(qubits[1]).index
                
                # Check if qubits are connected
                if self._are_connected(q0, q1):
                    routed.append(instruction)
                else:
                    # Need to add SWAP gates to route
                    print(f"   🔄 Routing {instruction.operation.name} gate: q{q0} -> q{q1}")
                    self._add_routing_swaps(routed, q0, q1)
                    routed.append(instruction)
            else:
                # Single qubit gate, no routing needed
                routed.append(instruction)
                
        return routed
    
    def _are_connected(self, q0: int, q1: int) -> bool:
        """Check if two qubits are directly connected"""
        return (q0, q1) in self.coupling_map or (q1, q0) in self.coupling_map
    
    def _add_routing_swaps(self, circuit: QuantumCircuit, source: int, target: int):
        """Add SWAP gates to route between qubits (simplified)"""
        # This is a very simplified routing - in practice, you'd use 
        # sophisticated algorithms like SABRE
        
        # Find a path using simple BFS
        path = self._find_shortest_path(source, target)
        
        if len(path) > 2:  # Need intermediate SWAPs
            # Add SWAP to move source closer to target
            intermediate = path[1]
            print(f"     ↔️  Adding SWAP: q{source} <-> q{intermediate}")
            circuit.swap(source, intermediate)
    
    def _find_shortest_path(self, start: int, end: int) -> List[int]:
        """Find shortest path between qubits (BFS)"""
        if start == end:
            return [start]
            
        visited = set()
        queue = [(start, [start])]
        
        while queue:
            node, path = queue.pop(0)
            
            if node in visited:
                continue
                
            visited.add(node)
            
            if node == end:
                return path
                
            if node in self.coupling_graph:
                for neighbor in self.coupling_graph[node]:
                    if neighbor not in visited:
                        queue.append((neighbor, path + [neighbor]))
        
        return [start, end]  # Fallback
    
    def _advanced_optimize(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Apply advanced optimizations"""
        # Commutation-based optimization
        print("   🧠 Applying commutation analysis...")
        
        # Simple example: commute single-qubit gates
        optimized = QuantumCircuit()
        for qreg in circuit.qregs:
            optimized.add_register(qreg)
        for creg in circuit.cregs:
            optimized.add_register(creg)
        
        # Group consecutive single-qubit gates on same qubit
        qubit_gates = {i: [] for i in range(circuit.num_qubits)}
        
        for instruction in circuit.data:
            if len(instruction.qubits) == 1:
                qubit = optimized.find_bit(instruction.qubits[0]).index
                qubit_gates[qubit].append(instruction)
            else:
                # Flush all single-qubit gates before two-qubit gate
                self._flush_single_qubit_gates(optimized, qubit_gates)
                optimized.append(instruction)
        
        # Flush remaining gates
        self._flush_single_qubit_gates(optimized, qubit_gates)
        
        return optimized
    
    def _flush_single_qubit_gates(self, circuit: QuantumCircuit, qubit_gates: Dict):
        """Add accumulated single-qubit gates to circuit"""
        for qubit, gates in qubit_gates.items():
            for gate in gates:
                circuit.append(gate)
            qubit_gates[qubit] = []


# Demonstration function
def demo_transpiler():
    """Demonstrate the simple transpiler"""
    print("🚀 Simple Transpiler Demo\n")
    
    # Create a test circuit
    print("📝 Creating test circuit...")
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.ry(np.pi/4, 1)
    qc.cx(0, 1)
    qc.rx(np.pi/3, 2)
    qc.cx(1, 2)
    qc.h(0)  # This will be cancelled with first H gate
    qc.x(2)
    qc.x(2)  # This will be cancelled
    qc.measure_all()
    
    print(f"Original circuit:\n{qc.draw()}\n")
    
    # Define a simple coupling map (linear connectivity)
    coupling_map = [(0, 1), (1, 2)]
    
    # Create and run transpiler
    transpiler = SimpleTranspiler(
        coupling_map=coupling_map,
        basis_gates=['cx', 'rz', 'sx', 'x']
    )
    
    # Transpile with different optimization levels
    print("=" * 60)
    transpiled = transpiler.transpile(qc, optimization_level=2)
    print("=" * 60)
    
    print(f"\nTranspiled circuit:\n{transpiled.draw()}")


if __name__ == "__main__":
    demo_transpiler() 