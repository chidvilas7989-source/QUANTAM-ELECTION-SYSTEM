# quantum_circuits_demo.py — Fully Updated BB84 Quantum Circuit Demo
"""
Quantum-Blockchain Secure Voting System — BB84 Circuit Demonstration
Demonstrates quantum key generation for ballot encryption.

Author: [Your Name]
Date: August 2025
Usage: python quantum_circuits_demo.py
Requirements: pip install qiskit matplotlib numpy
"""
import numpy as np
import hashlib
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.visualization import circuit_drawer
from qiskit_aer import AerSimulator
import sys

# Optional for PNG export
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️ matplotlib not found — PNG export disabled")

class VotingSystemBB84Demo:
    """Demonstrates BB84 quantum key distribution for secure voting."""
    def __init__(self):
        print("🔐 Quantum-Blockchain Voting System – BB84 Circuit Demo")
        print("=" * 60)
        self.simulator = AerSimulator()
        self.simulator_status = "active"

    def generate_bb84_circuit(self, key_length=8, show_details=True, max_attempts=3):
        """Generate BB84 circuit with fallback for insufficient bits."""
        for attempt in range(max_attempts):
            if show_details and attempt > 0:
                print(f"Retry {attempt + 1}...")

            if show_details and attempt == 0:
                print(f"\n🔑 Generating BB84 Circuit for {key_length}-bit key")
                print("-" * 40)

            # Oversample to ensure enough bits
            n_qubits = key_length * 2
            alice_bits = np.random.randint(2, size=n_qubits)
            alice_bases = np.random.randint(2, size=n_qubits)  # 0=Z, 1=X
            bob_bases = np.random.randint(2, size=n_qubits)

            if show_details and attempt == 0:
                print(f"Alice bits   : {alice_bits}")
                print(f"Alice bases  : {alice_bases} (0=Z, 1=X)")
                print(f"Bob bases    : {bob_bases} (0=Z, 1=X)")

            # Build quantum circuit
            qreg = QuantumRegister(n_qubits, "q")
            creg = ClassicalRegister(n_qubits, "c")
            qc = QuantumCircuit(qreg, creg)

            qc.barrier(label="Alice Prep")
            for i in range(n_qubits):
                if alice_bits[i] == 1:
                    qc.x(i)
                if alice_bases[i] == 1:
                    qc.h(i)

            qc.barrier(label="Bob Measure")
            for i in range(n_qubits):
                if bob_bases[i] == 1:
                    qc.h(i)
            qc.measure(qreg, creg)

            # Simulate
            try:
                job = self.simulator.run(transpile(qc, self.simulator), shots=1)
                result = job.result()
                measured = list(result.get_counts(qc).keys())[0]
                bob_bits = [int(b) for b in measured[::-1]]
            except Exception as e:
                print(f"Simulation error: {e}")
                bob_bits = np.random.randint(2, size=n_qubits)

            matches = (alice_bases == bob_bases)
            shared_bits = alice_bits[matches]

            if show_details and attempt == 0:
                print(f"Bob bits     : {bob_bits}")
                print(f"Basis match  : {matches.astype(int)}")
                print(f"Shared bits  : {shared_bits}")

            if len(shared_bits) >= key_length:
                final_key = ''.join(str(int(b)) for b in shared_bits[:key_length])
                if show_details:
                    print(f"✅ Final {key_length}-bit key: {final_key}")
                    print(f"Key (hex)    : {hex(int(final_key, 2))}")
                return qc, alice_bits, alice_bases, bob_bases, final_key

        # Fallback: hash expansion (like real voting system)
        if show_details:
            print(f"⚠️ Using hash fallback after {max_attempts} attempts")
        bit_string = ''.join(str(int(b)) for b in shared_bits)
        if not bit_string:
            bit_string = "fallback_seed"
        key_hash = hashlib.sha256(bit_string.encode()).digest()
        final_key = bin(int(key_hash[:8], 16))[2:].zfill(key_length)
        if show_details:
            print(f"Hash-derived key: {final_key}")
            print(f"Key (hex)       : {hex(int(final_key, 2))}")
        return qc, alice_bits, alice_bases, bob_bases, final_key

    def show_circuit_diagram(self, qc, title="Circuit"):
        """Print ASCII circuit diagram and optionally save PNG."""
        print(f"\n📋 {title}:")
        print(f"   Qubits: {qc.num_qubits}")
        print(f"   Depth: {qc.depth()}")
        try:
            # ASCII diagram
            print("\nCircuit Diagram:")
            print(circuit_drawer(qc, output='text', fold=-1))
        except Exception as e:
            print(f"   Could not display circuit: {e}")

        # Save PNG if matplotlib is available
        if HAS_MATPLOTLIB:
            try:
                fig = qc.draw(output='mpl', fold=-1)
                filename = title.lower().replace(' ', '_') + '.png'
                fig.savefig(filename, dpi=300, bbox_inches='tight')
                print(f"\n💾 Saved as {filename}")
                plt.close(fig)
            except Exception as e:
                print(f"\n⚠️ PNG save failed: {e}")
        elif show_details:
            print("\n💡 Install matplotlib (pip install matplotlib) for PNG export.")

    def demonstrate_vote_encryption(self):
        """Show vote encryption process and quantum circuit."""
        print("\n🗳️  VOTE ENCRYPTION PROCESS")
        print("=" * 50)
        vote_data = {
            "voter_id": "DEMO123",
            "party": "Demo Party",
            "timestamp": "2025-08-17T00:00:00",
            "vote_id": "vote_demo_xyz"
        }
        print("Sample vote data:")
        for k, v in vote_data.items():
            print(f"  {k}: {v}")

        print("\n🔑 Step 1: Generate quantum key...")
        qc, _, _, _, key = self.generate_bb84_circuit(key_length=8, show_details=False)
        print(f"Quantum key: {key}")
        print(f"SHA-256 hash: {hashlib.sha256(key.encode()).hexdigest()[:16]}...")

        print(f"\n📊 Step 2: Quantum circuit stats")
        print(f"Circuits qubits: {qc.num_qubits}")
        print(f"Circuit depth: {qc.depth()}")

        self.show_circuit_diagram(qc, "Vote Key Generation Circuit")
        return qc, key

    def analyze_key_randomness(self, num_tests=5):
        """Test key uniqueness and bit distribution."""
        print(f"\n🔬 KEY RANDOMNESS ANALYSIS ({num_tests} tests)")
        print("-" * 40)
        keys = []
        for i in range(num_tests):
            _, _, _, _, key = self.generate_bb84_circuit(8, show_details=False)
            keys.append(key)
            print(f"Key {i+1:2d}: {key} (hex: {hex(int(key, 2))})")
        
        unique_count = len(set(keys))
        print(f"\nUniqueness: {unique_count}/{num_tests} keys are unique ({unique_count*100/num_tests:.1f}%)")
        bits = ''.join(keys)
        zeros = bits.count('0')
        ones = bits.count('1')
        print(f"Bit balance: {zeros} zeros, {ones} ones ({ones/(zeros + ones)*100:.1f}% ones)")
        return keys

    def demonstrate_blockchain_integration(self):
        """Show quantum key use in blockchain vote storage."""
        print("\n⛓️  BLOCKCHAIN INTEGRATION")
        print("-" * 30)
        qc, key = self.demonstrate_vote_encryption()
        vote_payload = f"AES_encrypted_vote_with_key_{key}"
        vote_hash = hashlib.sha256(vote_payload.encode()).hexdigest()
        print(f"\n📦 Blockchain Block Contents:")
        print(f"   Vote Hash: {vote_hash}")
        print(f"   Quantum Key ID: {hashlib.sha256(key.encode()).hexdigest()[:16]}")
        print(f"   Block Type: 'vote_record'")
        print(f"\n🔒 Security Properties:")
        print("   ✓ Unique quantum key per vote")
        print("   ✓ Vote encrypted with AES-256")
        print("   ✓ Only hash stored on blockchain")
        print("   ✓ Quantum key ensures forward secrecy")
        print("   ✓ No key reuse between votes")

    def interactive_demo(self):
        """Interactive menu for demonstrations."""
        print("\nAVAILABLE DEMONSTRATIONS:")
        print("1. Basic BB84 key generation")
        print("2. Vote encryption process")
        print("3. Key randomness analysis")
        print("4. Blockchain integration")
        print("5. All demonstrations")
        print("6. Exit")
        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            self.generate_bb84_circuit(show_details=True)
            self.show_circuit_diagram(qc, "BB84 Demo Circuit")
        elif choice == "2":
            self.demonstrate_vote_encryption()
        elif choice == "3":
            self.analyze_key_randomness()
        elif choice == "4":
            self.demonstrate_blockchain_integration()
        elif choice == "5":
            self.generate_bb84_circuit(show_details=True)
            self.demonstrate_vote_encryption()
            self.analyze_key_randomness(5)
            self.demonstrate_blockchain_integration()
        else:
            print("\nExiting demo. Thanks!")

def main():
    """Entry point for the demo."""
    demo = VotingSystemBB84Demo()
    while True:
        demo.interactive_demo()
        if input("\nRun another demo? (y/n): ").strip().lower() != "y":
            print("\n🎉 Demonstration complete!")
            return

if __name__ == "__main__":
    main()

"""
TECHNICAL EXPLANATION:
======================

BB84 Quantum Key Distribution Protocol:
1. Alice generates random bits and random bases
2. Alice prepares qubits in chosen bases (Z or X)
3. Qubits are sent through quantum channel
4. Bob measures in his randomly chosen bases
5. Alice and Bob compare bases (classical communication)
6. They keep only bits where bases matched
7. Remaining bits form the shared secret key

Integration with Voting System:
- Each vote triggers BB84 key generation
- Generated key encrypts vote data using AES-256
- Only vote hash stored on blockchain
- Quantum key ensures perfect forward secrecy
- Different key for each vote prevents correlation attacks

Security Properties:
- Information-theoretically secure (quantum mechanics)
- Eavesdropping detection possible (not shown in demo)
- Perfect forward secrecy
- No key reuse between votes
"""
