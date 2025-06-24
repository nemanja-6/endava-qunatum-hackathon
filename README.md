# Simple Qiskit Transpiler

A demonstration of quantum circuit transpilation concepts implemented from scratch.

# Authors
- Brandon Dennis
- Alessandro Rama
- Leonardo Calderon
- Nemanja Todorovic

## 🎯 What This Demonstrates

This simple transpiler shows the **core concepts** behind quantum circuit compilation:

### 1. **Circuit Analysis** 📊
- Gate counting and depth analysis
- Two-qubit gate identification
- Circuit statistics tracking

### 2. **Basic Optimizations** ⚡
- **Gate Cancellation**: Removes self-inverse gates (H-H = I, X-X = I)
- **Peephole Optimization**: Local pattern recognition and removal

### 3. **Gate Decomposition** 🔧
- **Basis Gate Translation**: Converts arbitrary gates to hardware-supported gates
- **Gate Synthesis**: Decomposes complex gates into sequences of basis gates

Examples:
- `H` → `RZ(π) SX RZ(π/2)` 
- `RY(θ)` → `RZ(-π/2) SX RZ(θ) SX RZ(π/2)`
- `RX(θ)` → `SX RZ(θ) SX`

### 4. **Layout & Routing** 🗺️
- **Coupling Map Constraints**: Respects hardware connectivity
- **SWAP Insertion**: Routes two-qubit gates to adjacent qubits
- **Path Finding**: BFS algorithm for qubit routing

### 5. **Advanced Optimizations** 🚀
- **Commutation Analysis**: Reorders gates based on commutation rules
- **Gate Scheduling**: Groups consecutive single-qubit operations

## 🏗️ Architecture

```
Input Circuit
      ↓
[ Circuit Analysis ]
      ↓
[ Basic Optimizations ] ← Level 1+
      ↓
[ Gate Decomposition ]
      ↓
[ Layout & Routing ] ← If coupling_map provided
      ↓
[ Advanced Optimizations ] ← Level 2+
      ↓
Output Circuit
```

## 📝 Usage

### Basic Usage
```python
from simple_transpiler import SimpleTranspiler

# Create transpiler with backend constraints
transpiler = SimpleTranspiler(
    coupling_map=[(0, 1), (1, 2), (2, 3)],  # Linear connectivity
    basis_gates=['cx', 'rz', 'sx', 'x']       # IBM basis gates
)

# Transpile a circuit
transpiled_circuit = transpiler.transpile(
    your_circuit, 
    optimization_level=2
)
```

### Optimization Levels
- **Level 0**: No optimization, basic decomposition only
- **Level 1**: Basic optimizations (gate cancellation)
- **Level 2**: Advanced optimizations (commutation analysis)

## 🔬 Key Features Demonstrated

### Gate Cancellation Example
```
Before: H-H-X-X
After:  (empty) - both pairs cancelled!
```

### Gate Decomposition Example
```
Before: RY(π/4)
After:  RZ(-π/2) → SX → RZ(π/4) → SX → RZ(π/2)
```

### Routing Example
```
Before: CX(q0, q2) on linear topology
After:  SWAP(q0,q1) → CX(q1,q2) → SWAP(q0,q1)
```

## 🆚 Comparison with Qiskit

Our transpiler implements simplified versions of:
- **Qiskit's PassManager**: Sequential optimization passes
- **UnrollCustomDefinitions**: Gate decomposition
- **BasicSwap**: Simple routing with SWAP insertion
- **Optimize1qGatesDecomposition**: Single-qubit gate optimization

**Differences:**
- **Simplified**: Educational focus, not production-optimized
- **Limited**: Basic routing algorithm vs. SABRE/STAQ
- **Readable**: Clear, documented implementation
- **Modular**: Easy to understand and extend

## 🚀 Running the Demo

```bash
# Install Qiskit
pip install qiskit

# Run the demo
python simple_transpiler.py

# Run comprehensive examples
python transpiler_example.py
```

## 📚 Educational Value

This implementation teaches:
1. **How transpilation works** under the hood
2. **Why each step is necessary** for quantum hardware
3. **Trade-offs** between optimization and compilation time
4. **Algorithms** used in production transpilers

## 🔧 Extension Ideas

- Add more gate decomposition rules
- Implement SABRE routing algorithm
- Add noise-aware optimization
- Implement template matching
- Add circuit equivalence checking

## 📖 Further Reading

- [Qiskit Transpiler Documentation](https://qiskit.org/documentation/apidoc/transpiler.html)
- [SABRE Routing Paper](https://arxiv.org/abs/1809.02573)
- [Quantum Circuit Optimization Survey](https://arxiv.org/abs/1807.02686)

---

*This is a simplified educational implementation. For production use, rely on Qiskit's battle-tested transpiler!* 
=======
2025-06-24

