"""
Benchmark the W-State Synthesizer pass (Qiskit ≥ 2.0).

Examples
--------
python test_w_state_synth.py                          # FakeMontrealV2, n=8
python test_w_state_synth.py --backend FakeJakartaV2 -n 10
"""
from __future__ import annotations
import argparse
import importlib
import math

from qiskit import transpile
from qiskit.circuit import QuantumCircuit
from qiskit.transpiler import PassManager

from w_state_synth_pass import WStateSynthesizer, WState


# ──────────────────────────────────────────────────────────────────────
# helper: load fake backend class and instantiate it
# ──────────────────────────────────────────────────────────────────────
def load_backend(name: str):
    pkg = importlib.import_module("qiskit_ibm_runtime.fake_provider")
    try:
        backend_cls = getattr(pkg, name)
    except AttributeError as exc:
        raise ImportError(f"Fake backend '{name}' not found") from exc
    return backend_cls()


# ──────────────────────────────────────────────────────────────────────
# optional helper: strip idle qubits (kept for completeness)
# ──────────────────────────────────────────────────────────────────────
def strip_idle(circ: QuantumCircuit) -> QuantumCircuit:
    active = {q for inst in circ.data for q in inst.qubits}
    if len(active) == len(circ.qubits):
        return circ
    index_map = {circ.qubits.index(q): i for i, q in enumerate(sorted(active))}
    new = QuantumCircuit(len(active), name=circ.name + "_stripped")
    for inst in circ.data:
        new_qubits = [new.qubits[index_map[circ.qubits.index(q)]] for q in inst.qubits]
        new.append(inst.operation, new_qubits, [])
    return new


# ──────────────────────────────────────────────────────────────────────
# core benchmark
# ──────────────────────────────────────────────────────────────────────
def benchmark(n: int, backend_name: str):
    backend = load_backend(backend_name)
    target = backend.target

    # naïve W-state circuit
    circ0 = QuantumCircuit(n, name=f"W{n}")
    circ0.append(WState(n), circ0.qubits)

    # 1 · baseline transpilation
    circ_def = transpile(circ0, backend=backend, optimization_level=3)

    # 2 · run our synthesizer, then standard transpiler
    pm = PassManager([WStateSynthesizer(target=target)])
    circ_after = pm.run(circ0)
    circ_opt = transpile(circ_after, backend=backend, optimization_level=3)

    # metrics
    depth_def, depth_opt = circ_def.depth(), circ_opt.depth()
    cx_def = circ_def.count_ops().get("cx", 0)
    cx_opt = circ_opt.count_ops().get("cx", 0)

    # (Optional) state fidelity — requires mapping logical→physical first
    # ideal = Statevector.from_instruction(circ0)
    # red_def = strip_idle(circ_def)
    # red_opt = strip_idle(circ_opt)
    # fid_def = state_fidelity(ideal, Statevector.from_instruction(red_def))
    # fid_opt = state_fidelity(ideal, Statevector.from_instruction(red_opt))

    # report
    print(f"\n=== Backend: {backend_name} (phys-qubits = {backend.num_qubits}) ===")
    print(f"Ideal depth ≈ ⌈log₂ n⌉ = {math.ceil(math.log2(n))}\n")
    print(f"Default   : depth = {depth_def:<3}  CX = {cx_def}")
    print(f"Synth pass: depth = {depth_opt:<3}  CX = {cx_opt}")
    print(f"\nDepth ↓ {100*(depth_def-depth_opt)/depth_def:4.1f}% | "
          f"CX ↓ {100*(cx_def-cx_opt)/cx_def:4.1f}%\n")


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="FakeMontrealV2",
                    help="Fake backend class name (see qiskit_ibm_runtime.fake_provider)")
    ap.add_argument("-n", "--qubits", type=int, default=8,
                    help="Number of qubits in the W-state")
    args = ap.parse_args()

    benchmark(args.qubits, args.backend)
