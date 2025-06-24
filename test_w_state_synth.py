"""
Benchmark the W-State Synthesizer pass (Qiskit ≥ 2.0) - CORRECTED VERSION
------------------------------------------------------------------------
Includes proper state fidelity verification and comprehensive testing.

Examples
--------
python test_w_state_synth.py                          # FakeMontrealV2, n=8
python test_w_state_synth.py --backend FakeJakartaV2 -n 10
python test_w_state_synth.py --verify                 # Enable correctness checking
"""
from __future__ import annotations
import argparse
import importlib
import math
import time

from qiskit import transpile
from qiskit.circuit import QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.quantum_info import Statevector, state_fidelity

from w_state_synth_pass import (
    WStateSynthesizer, WState, create_ideal_w_state,
    create_linear_w_state, create_balanced_w_state
)


# ──────────────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────────────
def load_backend(name: str):
    """Load fake backend class and instantiate it."""
    try:
        pkg = importlib.import_module("qiskit_ibm_runtime.fake_provider")
        backend_cls = getattr(pkg, name)
        return backend_cls()
    except (ImportError, AttributeError) as exc:
        raise ImportError(f"Fake backend '{name}' not found. "
                         f"Make sure qiskit_ibm_runtime is installed.") from exc


def strip_idle(circ: QuantumCircuit) -> QuantumCircuit:
    """Remove idle qubits from circuit for state comparison."""
    active = {q for inst in circ.data for q in inst.qubits}
    if len(active) == len(circ.qubits):
        return circ
    
    active_list = sorted(active, key=lambda q: circ.qubits.index(q))
    index_map = {circ.qubits.index(q): i for i, q in enumerate(active_list)}
    
    new = QuantumCircuit(len(active), name=circ.name + "_stripped")
    for inst in circ.data:
        new_qubits = [new.qubits[index_map[circ.qubits.index(q)]] for q in inst.qubits]
        new.append(inst.operation, new_qubits, [])
    return new


def verify_w_state_correctness(circuit: QuantumCircuit, n: int) -> float:
    """Verify that a circuit produces a valid W-state."""
    try:
        ideal_w = create_ideal_w_state(n)
        stripped_circuit = strip_idle(circuit)
        
        if stripped_circuit.num_qubits != n:
            print(f"Warning: Circuit has {stripped_circuit.num_qubits} active qubits, expected {n}")
            return 0.0
        
        actual_state = Statevector.from_instruction(stripped_circuit)
        fidelity = state_fidelity(ideal_w, actual_state)
        return fidelity
    
    except Exception as e:
        print(f"Error verifying W-state: {e}")
        return 0.0


def analyze_circuit_structure(circuit: QuantumCircuit) -> dict:
    """Analyze circuit structure and return metrics."""
    ops = circuit.count_ops()
    return {
        'depth': circuit.depth(),
        'size': circuit.size(),
        'cx_count': ops.get('cx', 0),
        'ry_count': ops.get('ry', 0),
        'x_count': ops.get('x', 0),
        'total_gates': sum(ops.values())
    }


# ──────────────────────────────────────────────────────────────────────
# Core benchmark function
# ──────────────────────────────────────────────────────────────────────
def benchmark(n: int, backend_name: str, verify_correctness: bool = False, verbose: bool = False):
    """Run comprehensive benchmark of W-state synthesis."""
    
    print(f"\n{'='*60}")
    print(f"W-State Synthesis Benchmark")
    print(f"{'='*60}")
    print(f"Qubits: {n}")
    print(f"Backend: {backend_name}")
    print(f"Verification: {'Enabled' if verify_correctness else 'Disabled'}")
    print(f"{'='*60}")
    
    # Load backend
    try:
        backend = load_backend(backend_name)
        target = backend.target
        print(f"Backend loaded: {backend.num_qubits} physical qubits")
    except Exception as e:
        print(f"Error loading backend: {e}")
        return
    
    # Create naïve W-state circuit
    circ0 = QuantumCircuit(n, name=f"W{n}")
    circ0.append(WState(n), circ0.qubits)
    
    # Decompose to get actual circuit for baseline
    circ0_decomposed = circ0.decompose()
    
    if verbose:
        print(f"\nOriginal circuit structure (before decomposition):")
        original_metrics = analyze_circuit_structure(circ0)
        for key, value in original_metrics.items():
            print(f"  {key}: {value}")
        print(f"\nAfter decomposition:")
        decomposed_metrics = analyze_circuit_structure(circ0_decomposed)
        for key, value in decomposed_metrics.items():
            print(f"  {key}: {value}")
    
    # Benchmark 1: Baseline transpilation (using decomposed circuit)
    print(f"\n1. Baseline transpilation...")
    start_time = time.time()
    circ_def = transpile(circ0_decomposed, backend=backend, optimization_level=3)
    baseline_time = time.time() - start_time
    
    # Benchmark 2: Our synthesizer + transpilation
    print(f"2. Synthesizer + transpilation...")
    start_time = time.time()
    pm = PassManager([WStateSynthesizer(target=target, verify_correctness=verify_correctness)])
    circ_after = pm.run(circ0)
    synth_time = time.time() - start_time
    
    start_time = time.time()
    circ_opt = transpile(circ_after, backend=backend, optimization_level=3)
    transpile_time = time.time() - start_time
    total_synth_time = synth_time + transpile_time
    
    # Analyze results
    baseline_metrics = analyze_circuit_structure(circ_def)
    optimized_metrics = analyze_circuit_structure(circ_opt)
    
    # Verify correctness if requested
    baseline_fidelity = optimized_fidelity = None
    if verify_correctness:
        print(f"3. Verifying correctness...")
        baseline_fidelity = verify_w_state_correctness(circ_def, n)
        optimized_fidelity = verify_w_state_correctness(circ_opt, n)
        
        # Also verify the original decomposed circuit
        original_fidelity = verify_w_state_correctness(circ0_decomposed, n)
        print(f"   Original decomposed fidelity: {original_fidelity:.6f}")
        if original_fidelity < 0.99:
            print(f"   ⚠️ Warning: Original W-state has low fidelity!")
    
    # Calculate theoretical optimum
    theoretical_depth = math.ceil(math.log2(n))
    
    # Use decomposed circuit for fair baseline comparison
    baseline_pre_transpile = analyze_circuit_structure(circ0_decomposed)
    
    print(f"\n{'Pre-transpilation Comparison':^60}")
    print(f"{'-'*60}")
    print(f"{'Metric':<20} {'Linear W':<12} {'Balanced W':<12} {'Improvement':<15}")
    print(f"{'-'*60}")
    
    synth_pre_transpile = analyze_circuit_structure(circ_after)
    
    pre_depth_improvement = (baseline_pre_transpile['depth'] - synth_pre_transpile['depth']) / baseline_pre_transpile['depth'] * 100 if baseline_pre_transpile['depth'] > 0 else 0
    pre_size_improvement = (baseline_pre_transpile['size'] - synth_pre_transpile['size']) / baseline_pre_transpile['size'] * 100 if baseline_pre_transpile['size'] > 0 else 0
    
    print(f"{'Depth':<20} {baseline_pre_transpile['depth']:<12} {synth_pre_transpile['depth']:<12} {pre_depth_improvement:>+6.1f}%")
    print(f"{'Total gates':<20} {baseline_pre_transpile['size']:<12} {synth_pre_transpile['size']:<12} {pre_size_improvement:>+6.1f}%")
    
    # Report results
    print(f"\n{'Post-transpilation Results':^60}")
    print(f"{'-'*60}")
    print(f"{'Metric':<20} {'Baseline':<12} {'Optimized':<12} {'Improvement':<15}")
    print(f"{'-'*60}")
    
    depth_improvement = (baseline_metrics['depth'] - optimized_metrics['depth']) / baseline_metrics['depth'] * 100
    cx_improvement = (baseline_metrics['cx_count'] - optimized_metrics['cx_count']) / baseline_metrics['cx_count'] * 100 if baseline_metrics['cx_count'] > 0 else 0
    size_improvement = (baseline_metrics['size'] - optimized_metrics['size']) / baseline_metrics['size'] * 100
    
    print(f"{'Depth':<20} {baseline_metrics['depth']:<12} {optimized_metrics['depth']:<12} {depth_improvement:>+6.1f}%")
    print(f"{'CX gates':<20} {baseline_metrics['cx_count']:<12} {optimized_metrics['cx_count']:<12} {cx_improvement:>+6.1f}%")
    print(f"{'Total gates':<20} {baseline_metrics['size']:<12} {optimized_metrics['size']:<12} {size_improvement:>+6.1f}%")
    print(f"{'Compile time (s)':<20} {baseline_time:<12.3f} {total_synth_time:<12.3f} {(total_synth_time-baseline_time)/baseline_time*100:>+6.1f}%")
    
    if verify_correctness and baseline_fidelity is not None and optimized_fidelity is not None:
        print(f"{'-'*60}")
        print(f"{'State Fidelity':<20} {baseline_fidelity:<12.6f} {optimized_fidelity:<12.6f}")
        if baseline_fidelity < 0.99:
            print(f"⚠️  Warning: Baseline fidelity is low!")
        if optimized_fidelity < 0.99:
            print(f"⚠️  Warning: Optimized fidelity is low!")
    
    print(f"{'-'*60}")
    print(f"Theoretical optimal depth: {theoretical_depth}")
    print(f"Original linear depth: {baseline_pre_transpile['depth']}")
    print(f"Synthesized balanced depth: {synth_pre_transpile['depth']}")
    print(f"Baseline transpiled vs optimal: {baseline_metrics['depth']/theoretical_depth:.1f}x")
    print(f"Optimized transpiled vs optimal: {optimized_metrics['depth']/theoretical_depth:.1f}x")
    
    # Performance assessment
    print(f"\n{'Assessment':^60}")
    print(f"{'-'*60}")
    if depth_improvement > 10:
        print("✅ Significant depth improvement achieved!")
    elif depth_improvement > 0:
        print("✅ Modest depth improvement achieved.")
    else:
        print("❌ No depth improvement (synthesis may not be beneficial).")
    
    if verify_correctness:
        if optimized_fidelity and optimized_fidelity > 0.999:
            print("✅ High fidelity maintained.")
        elif optimized_fidelity and optimized_fidelity > 0.99:
            print("⚠️  Acceptable fidelity maintained.")
        else:
            print("❌ Low fidelity - potential correctness issue!")
    
    if verbose:
        print(f"\nDetailed gate counts:")
        print(f"Baseline: {baseline_metrics}")
        print(f"Optimized: {optimized_metrics}")


def run_parameter_sweep():
    """Run benchmark across different parameter ranges."""
    print("Running parameter sweep...")
    backends = ["FakeMontrealV2", "FakeJakartaV2"]
    qubit_counts = [4, 6, 8, 10, 12, 16]
    
    for backend_name in backends:
        try:
            backend = load_backend(backend_name)
            max_qubits = min(backend.num_qubits, max(qubit_counts))
            valid_counts = [n for n in qubit_counts if n <= max_qubits]
            
            print(f"\n{'='*60}")
            print(f"Parameter Sweep: {backend_name}")
            print(f"{'='*60}")
            
            for n in valid_counts:
                benchmark(n, backend_name, verify_correctness=False, verbose=False)
                
        except Exception as e:
            print(f"Skipping {backend_name}: {e}")


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Benchmark W-state synthesis optimization")
    ap.add_argument("--backend", default="FakeMontrealV2",
                    help="Fake backend class name (see qiskit_ibm_runtime.fake_provider)")
    ap.add_argument("-n", "--qubits", type=int, default=8,
                    help="Number of qubits in the W-state")
    ap.add_argument("--verify", action="store_true",
                    help="Enable state fidelity verification (slower)")
    ap.add_argument("--verbose", action="store_true",
                    help="Enable verbose output")
    ap.add_argument("--sweep", action="store_true",
                    help="Run parameter sweep instead of single benchmark")
    
    args = ap.parse_args()
    
    if args.sweep:
        run_parameter_sweep()
    else:
        benchmark(args.qubits, args.backend, args.verify, args.verbose)
