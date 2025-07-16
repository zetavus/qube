"""
# DEBUG 비활성화 (기본)
circuit = QuantumCircuit(5)

# DEBUG 활성화
circuit_debug = QuantumCircuit(5, debug_mode=True)

# 실행 중 토글
circuit.set_debug(True)   # 활성화
circuit.set_debug(False)  # 비활성화

# N큐빗 제어 Z 게이트 사용
circuit.controlled_z_n(0, 1, 2, 3, 4)  # 5큐빗 제어 Z
"""

import numpy as np
from typing import Dict, Any, Union, List, Tuple
import cmath

class QuantumState:
    def __init__(self, state_vector: np.ndarray, n_qubits: int = None):
        self.state_vector = state_vector
        self.n_qubits = n_qubits or int(np.log2(len(state_vector)))
        self.is_measured = False
        self._validate_state()
    
    def _validate_state(self):
        """Validate that the state is normalized"""
        norm = np.linalg.norm(self.state_vector)
        if abs(norm - 1.0) > 1e-10:
            self.state_vector = self.state_vector / norm
    
    def prob_zero(self) -> float:
        """Probability of measuring |0⟩ on the first qubit"""
        if len(self.state_vector) >= 1:
            return abs(self.state_vector[0]) ** 2
        return 0.0
    
    def prob_one(self) -> float:
        """Probability of measuring |1⟩ on the first qubit"""
        if len(self.state_vector) >= 2:
            return abs(self.state_vector[1]) ** 2
        return 0.0
    
    def purity(self) -> float:
        """Calculate the purity of the quantum state"""
        # For pure states, purity = 1
        return 1.0  # Assuming pure states for now
    
    def entropy(self) -> float:
        """Calculate von Neumann entropy"""
        # For pure states, entropy = 0
        return 0.0
    
    def get_amplitudes(self) -> List[complex]:
        """Get the complex amplitudes"""
        return self.state_vector.tolist()
    
    def tensor_product(self, other: 'QuantumState') -> 'QuantumState':
        """Compute tensor product with another quantum state"""
        new_state = np.kron(self.state_vector, other.state_vector)
        return QuantumState(new_state, self.n_qubits + other.n_qubits)
    
    def measure(self, qubit_index: int = 0) -> int:
        """Simulate measurement and collapse the state"""
        if self.is_measured:
            raise RuntimeError("Qubit already measured!")
        
        if qubit_index >= self.n_qubits:
            raise ValueError(f"Qubit index {qubit_index} out of range")
        
        # Calculate probabilities for the specified qubit
        prob_0 = self._calculate_qubit_prob(qubit_index, 0)
        
        result = 0 if np.random.random() < prob_0 else 1
        
        # Collapse the state
        self._collapse_state(qubit_index, result)
        self.is_measured = True
        
        return result
    
    def _calculate_qubit_prob(self, qubit_index: int, value: int) -> float:
        """Calculate probability of measuring specific value on specific qubit"""
        prob = 0.0
        for i, amplitude in enumerate(self.state_vector):
            binary_rep = format(i, f'0{self.n_qubits}b')
            if int(binary_rep[qubit_index]) == value:
                prob += abs(amplitude) ** 2
        return prob
    
    def _collapse_state(self, qubit_index: int, measured_value: int):
        """Collapse the state after measurement"""
        new_amplitudes = []
        norm_factor = 0.0
        
        for i, amplitude in enumerate(self.state_vector):
            binary_rep = format(i, f'0{self.n_qubits}b')
            if int(binary_rep[qubit_index]) == measured_value:
                new_amplitudes.append(amplitude)
                norm_factor += abs(amplitude) ** 2
            else:
                new_amplitudes.append(0.0)
        
        # Normalize
        norm_factor = np.sqrt(norm_factor)
        if norm_factor > 0:
            self.state_vector = np.array(new_amplitudes) / norm_factor
    
    def __str__(self) -> str:
        """String representation of the quantum state"""
        if self.n_qubits == 1:
            a0, a1 = self.state_vector[0], self.state_vector[1]
            if abs(a0.imag) < 1e-10 and abs(a1.imag) < 1e-10:
                return f"{a0.real:.3f}|0⟩ + {a1.real:.3f}|1⟩"
            else:
                return f"({a0.real:.3f}+{a0.imag:.3f}i)|0⟩ + ({a1.real:.3f}+{a1.imag:.3f}i)|1⟩"
        else:
            parts = []
            for i, amp in enumerate(self.state_vector):
                if abs(amp) > 1e-10:
                    binary = format(i, f'0{self.n_qubits}b')
                    if abs(amp.imag) < 1e-10:
                        parts.append(f"{amp.real:.3f}|{binary}⟩")
                    else:
                        parts.append(f"({amp.real:.3f}+{amp.imag:.3f}i)|{binary}⟩")
            return " + ".join(parts)

# 🆕 양자 회로 빌더 클래스들
class QuantumGate:
    """양자 게이트 표현 클래스"""
    def __init__(self, name: str, target_qubits: List[int], control_qubits: List[int] = None, 
                 parameters: List[float] = None):
        self.name = name
        self.target_qubits = target_qubits
        self.control_qubits = control_qubits or []
        self.parameters = parameters or []
    
    def __str__(self) -> str:
        if self.control_qubits:
            return f"{self.name}(control={self.control_qubits}, target={self.target_qubits})"
        elif self.parameters:
            return f"{self.name}({self.parameters}, {self.target_qubits})"
        else:
            return f"{self.name}({self.target_qubits})"

class QuantumCircuit:
    """양자 회로 빌더 클래스"""
    def __init__(self, n_qubits: int, debug_mode: bool = False):
        self.n_qubits = n_qubits
        self.debug_mode = debug_mode  # 🆕 DEBUG 제어
        self.gates = []
        self.measurements = []
        self.qubits = [QuantumState(np.array([1.0, 0.0]), 1) for _ in range(n_qubits)]
        self.circuit_state = None
        self._initialize_circuit_state()
        self._gate_count = 0  # 디버깅용
    
    def _initialize_circuit_state(self):
        """모든 큐빗을 |000...⟩ 상태로 초기화"""
        initial_state = np.zeros(2**self.n_qubits, dtype=complex)
        initial_state[0] = 1.0  # |000...⟩
        self.circuit_state = QuantumState(initial_state, self.n_qubits)
    
    # === DEBUG 헬퍼 메서드들 ===
    
    def _debug_print(self, message: str):
        """조건부 DEBUG 출력"""
        if self.debug_mode:
            print(f"DEBUG: {message}")

    def set_debug(self, enabled: bool):
        """DEBUG 모드 토글"""
        self.debug_mode = enabled
        return self

    def _format_state_vector(self, state_vector, max_states=16):
        """상태 벡터를 적절한 크기로 포맷"""
        probabilities = [abs(amp)**2 for amp in state_vector[:max_states]]
        if len(state_vector) > max_states:
            return probabilities + ["..."]
        return probabilities
    
    # === 단일 큐빗 게이트들 ===
    
    def h(self, qubit: int) -> 'QuantumCircuit':
        """하다마드 게이트 추가 및 상태 업데이트"""
        if qubit < 0 or qubit >= self.n_qubits:
            raise ValueError(f"Qubit index {qubit} out of range")
        
        self._debug_print(f"H 게이트 적용 전 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
            
        self.gates.append(QuantumGate("H", [qubit]))
        
        # 실제 상태 업데이트
        simulator = QuantumSimulator()
        self.circuit_state = simulator.apply_single_gate_to_circuit("H", self.circuit_state, qubit, self.debug_mode)
        
        self._debug_print(f"H 게이트 적용 후 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
        self._debug_print(f"H 게이트 적용됨 - 큐빗 {qubit}")
        
        self._gate_count += 1
        return self

    def x(self, qubit: int) -> 'QuantumCircuit':
        if qubit < 0 or qubit >= self.n_qubits:
            raise ValueError(f"Qubit index {qubit} out of range")
        
        self._debug_print(f"X 게이트 적용 전 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
        
        self.gates.append(QuantumGate("X", [qubit]))
        
        simulator = QuantumSimulator()
        self.circuit_state = simulator.apply_single_gate_to_circuit("X", self.circuit_state, qubit, self.debug_mode)
        
        self._debug_print(f"X 게이트 적용 후 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
        self._debug_print(f"X 게이트 적용됨 - 큐빗 {qubit}")
        
        self._gate_count += 1
        return self

    def y(self, qubit: int) -> 'QuantumCircuit':
        """Pauli-Y 게이트 추가 및 상태 업데이트"""
        if qubit < 0 or qubit >= self.n_qubits:
            raise ValueError(f"Qubit index {qubit} out of range")
        
        self._debug_print(f"Y 게이트 적용 전 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
            
        self.gates.append(QuantumGate("Y", [qubit]))
        
        simulator = QuantumSimulator()
        self.circuit_state = simulator.apply_single_gate_to_circuit("Y", self.circuit_state, qubit, self.debug_mode)
        
        self._debug_print(f"Y 게이트 적용 후 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
        self._debug_print(f"Y 게이트 적용됨 - 큐빗 {qubit}")
        
        self._gate_count += 1
        return self

    def z(self, qubit: int) -> 'QuantumCircuit':
        """Pauli-Z 게이트 추가 및 상태 업데이트"""
        if qubit < 0 or qubit >= self.n_qubits:
            raise ValueError(f"Qubit index {qubit} out of range")
        
        self._debug_print(f"Z 게이트 적용 전 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
            
        self.gates.append(QuantumGate("Z", [qubit]))
        
        simulator = QuantumSimulator()
        self.circuit_state = simulator.apply_single_gate_to_circuit("Z", self.circuit_state, qubit, self.debug_mode)
        
        self._debug_print(f"Z 게이트 적용 후 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
        self._debug_print(f"Z 게이트 적용됨 - 큐빗 {qubit}")
        
        self._gate_count += 1
        return self

    def s(self, qubit: int) -> 'QuantumCircuit':
        """S 게이트 추가 및 상태 업데이트"""
        if qubit < 0 or qubit >= self.n_qubits:
            raise ValueError(f"Qubit index {qubit} out of range")
        
        self._debug_print(f"S 게이트 적용 전 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
            
        self.gates.append(QuantumGate("S", [qubit]))
        
        simulator = QuantumSimulator()
        self.circuit_state = simulator.apply_single_gate_to_circuit("S", self.circuit_state, qubit, self.debug_mode)
        
        self._debug_print(f"S 게이트 적용 후 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
        self._debug_print(f"S 게이트 적용됨 - 큐빗 {qubit}")
        
        self._gate_count += 1
        return self

    def t(self, qubit: int) -> 'QuantumCircuit':
        """T 게이트 추가 및 상태 업데이트"""
        if qubit < 0 or qubit >= self.n_qubits:
            raise ValueError(f"Qubit index {qubit} out of range")
        
        self._debug_print(f"T 게이트 적용 전 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
            
        self.gates.append(QuantumGate("T", [qubit]))
        
        simulator = QuantumSimulator()
        self.circuit_state = simulator.apply_single_gate_to_circuit("T", self.circuit_state, qubit, self.debug_mode)
        
        self._debug_print(f"T 게이트 적용 후 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
        self._debug_print(f"T 게이트 적용됨 - 큐빗 {qubit}")
        
        self._gate_count += 1
        return self

    # === 회전 게이트들 ===
    def rx(self, angle: float, qubit: int) -> 'QuantumCircuit':
        """RX 회전 게이트 추가 및 상태 업데이트"""
        if qubit < 0 or qubit >= self.n_qubits:
            raise ValueError(f"Qubit index {qubit} out of range")
        
        self._debug_print(f"RX({angle:.3f}) 게이트 적용 전 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
            
        self.gates.append(QuantumGate("RX", [qubit], parameters=[angle]))
        
        simulator = QuantumSimulator()
        self.circuit_state = simulator.apply_rotation_to_circuit("X", angle, self.circuit_state, qubit, self.debug_mode)
        
        self._debug_print(f"RX({angle:.3f}) 게이트 적용 후 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
        self._debug_print(f"RX({angle:.3f}) 게이트 적용됨 - 큐빗 {qubit}")
        
        self._gate_count += 1
        return self

    def ry(self, angle: float, qubit: int) -> 'QuantumCircuit':
        """RY 회전 게이트 추가 및 상태 업데이트"""
        if qubit < 0 or qubit >= self.n_qubits:
            raise ValueError(f"Qubit index {qubit} out of range")
        
        self._debug_print(f"RY({angle:.3f}) 게이트 적용 전 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
            
        self.gates.append(QuantumGate("RY", [qubit], parameters=[angle]))
        
        simulator = QuantumSimulator()
        self.circuit_state = simulator.apply_rotation_to_circuit("Y", angle, self.circuit_state, qubit, self.debug_mode)
        
        self._debug_print(f"RY({angle:.3f}) 게이트 적용 후 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
        self._debug_print(f"RY({angle:.3f}) 게이트 적용됨 - 큐빗 {qubit}")
        
        self._gate_count += 1
        return self

    def rz(self, angle: float, qubit: int) -> 'QuantumCircuit':
        """RZ 회전 게이트 추가 및 상태 업데이트"""
        if qubit < 0 or qubit >= self.n_qubits:
            raise ValueError(f"Qubit index {qubit} out of range")
        
        self._debug_print(f"RZ({angle:.3f}) 게이트 적용 전 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
            
        self.gates.append(QuantumGate("RZ", [qubit], parameters=[angle]))
        
        simulator = QuantumSimulator()
        self.circuit_state = simulator.apply_rotation_to_circuit("Z", angle, self.circuit_state, qubit, self.debug_mode)
        
        self._debug_print(f"RZ({angle:.3f}) 게이트 적용 후 상태: {self._format_state_vector(self.circuit_state.state_vector, 8)}")
        self._debug_print(f"RZ({angle:.3f}) 게이트 적용됨 - 큐빗 {qubit}")
        
        self._gate_count += 1
        return self

    # === 2큐빗 게이트들 ===
    def cnot(self, control: int, target: int) -> 'QuantumCircuit':
        """CNOT 게이트 추가 및 상태 업데이트"""
        if control < 0 or control >= self.n_qubits or target < 0 or target >= self.n_qubits:
            raise ValueError(f"Qubit indices out of range")
        if control == target:
            raise ValueError("Control and target qubits must be different")
        
        self._debug_print(f"CNOT 게이트 적용 전 상태: {self._format_state_vector(self.circuit_state.state_vector)}")
            
        self.gates.append(QuantumGate("CNOT", [target], control_qubits=[control]))
        
        simulator = QuantumSimulator()
        self.circuit_state = simulator.apply_cnot_to_circuit(self.circuit_state, control, target, self.debug_mode)
        
        self._debug_print(f"CNOT 게이트 적용 후 상태: {self._format_state_vector(self.circuit_state.state_vector)}")
        self._debug_print(f"CNOT({control}, {target}) 게이트 적용됨")
        
        self._gate_count += 1
        return self

    def cz(self, control: int, target: int) -> 'QuantumCircuit':
        """CZ 게이트 추가 및 상태 업데이트"""
        if control < 0 or control >= self.n_qubits or target < 0 or target >= self.n_qubits:
            raise ValueError(f"Qubit indices out of range")
        if control == target:
            raise ValueError("Control and target qubits must be different")
        
        self._debug_print(f"CZ 게이트 적용 전 상태: {self._format_state_vector(self.circuit_state.state_vector)}")
            
        self.gates.append(QuantumGate("CZ", [target], control_qubits=[control]))
        
        simulator = QuantumSimulator()
        self.circuit_state = simulator.apply_cz_to_circuit(self.circuit_state, control, target, self.debug_mode)
        
        self._debug_print(f"CZ 게이트 적용 후 상태: {self._format_state_vector(self.circuit_state.state_vector)}")
        self._debug_print(f"CZ({control}, {target}) 게이트 적용됨")
        
        self._gate_count += 1
        return self
    
    def ccz(self, control1: int, control2: int, target: int) -> 'QuantumCircuit':
        """CCZ (Controlled-Controlled-Z) 게이트 추가 및 상태 업데이트"""
        if any(q < 0 or q >= self.n_qubits for q in [control1, control2, target]):
            raise ValueError(f"Qubit indices out of range")
        
        if len(set([control1, control2, target])) != 3:
            raise ValueError("Control and target qubits must be different")
        
        self.gates.append(QuantumGate("CCZ", [control1, control2, target]))
        
        # CCZ 게이트 직접 구현: 세 큐빗이 모두 1일 때만 위상 뒤집기
        n_qubits = self.n_qubits
        state_vector = self.circuit_state.state_vector.copy()
        
        self._debug_print(f"CCZ 적용 전 상태: {self._format_state_vector(state_vector)}")
        
        target_states = []
        
        # 각 상태에 대해 세 큐빗이 모두 1인지 확인
        for i in range(len(state_vector)):
            binary = format(i, f'0{n_qubits}b')
            
            # 큐빗 순서: Qube는 little-endian (q0가 최하위)
            control1_bit = int(binary[n_qubits-1-control1])
            control2_bit = int(binary[n_qubits-1-control2])
            target_bit = int(binary[n_qubits-1-target])
            
            # 세 큐빗이 모두 1이면 위상 뒤집기
            if control1_bit == 1 and control2_bit == 1 and target_bit == 1:
                state_vector[i] = -state_vector[i]
                target_states.append(f"|{binary}⟩")
                self._debug_print(f"CCZ 위상 뒤집기 - 상태 |{binary}⟩ (인덱스 {i})")
        
        # 상태 업데이트
        self.circuit_state.state_vector = state_vector
        
        self._debug_print(f"CCZ 적용 후 상태: {self._format_state_vector(state_vector)}")
        self._debug_print(f"CCZ({control1}, {control2}, {target}) 게이트 적용됨")
        
        if target_states:
            self._debug_print(f"위상 뒤집기 적용된 상태들: {', '.join(target_states)}")
        
        self._gate_count += 1
        return self
    
    def cccz(self, control1: int, control2: int, control3: int, target: int) -> 'QuantumCircuit':
        """CCCZ (Controlled-Controlled-Controlled-Z) 게이트 추가 및 상태 업데이트"""
        qubits = [control1, control2, control3, target]
        
        if any(q < 0 or q >= self.n_qubits for q in qubits):
            raise ValueError(f"Qubit indices out of range")
        
        if len(set(qubits)) != 4:
            raise ValueError("All control and target qubits must be different")
        
        self.gates.append(QuantumGate("CCCZ", qubits))
        
        # CCCZ 게이트 직접 구현: 네 큐빗이 모두 1일 때만 위상 뒤집기
        n_qubits = self.n_qubits
        state_vector = self.circuit_state.state_vector.copy()
        
        self._debug_print(f"CCCZ 적용 전 상태: {self._format_state_vector(state_vector)}")
        
        target_states = []
        
        # 각 상태에 대해 네 큐빗이 모두 1인지 확인
        for i in range(len(state_vector)):
            binary = format(i, f'0{n_qubits}b')
            
            # 지정된 큐빗들의 상태 확인
            control1_bit = int(binary[n_qubits-1-control1])
            control2_bit = int(binary[n_qubits-1-control2])
            control3_bit = int(binary[n_qubits-1-control3])
            target_bit = int(binary[n_qubits-1-target])
            
            # 네 큐빗이 모두 1이면 위상 뒤집기
            if (control1_bit == 1 and control2_bit == 1 and 
                control3_bit == 1 and target_bit == 1):
                state_vector[i] = -state_vector[i]
                target_states.append(f"|{binary}⟩")
                self._debug_print(f"CCCZ 위상 뒤집기 - 상태 |{binary}⟩ (인덱스 {i})")
        
        # 상태 업데이트
        self.circuit_state.state_vector = state_vector
        
        self._debug_print(f"CCCZ 적용 후 상태: {self._format_state_vector(state_vector)}")
        self._debug_print(f"CCCZ({control1}, {control2}, {control3}, {target}) 게이트 적용됨")
        
        if target_states:
            self._debug_print(f"위상 뒤집기 적용된 상태들: {', '.join(target_states)}")
        
        self._gate_count += 1
        return self
    
    # === 🆕 N큐빗 범용 제어 Z 게이트 ===
    
    def controlled_z_n(self, *qubits) -> 'QuantumCircuit':
        """N개 큐빗 제어 Z 게이트 (모든 지정된 큐빗이 1일 때 위상 뒤집기)"""
        n_controls = len(qubits)
        
        if n_controls < 2:
            raise ValueError("At least 2 qubits required for controlled Z gate")
        
        if any(q < 0 or q >= self.n_qubits for q in qubits):
            raise ValueError(f"Qubit indices out of range")
        
        if len(set(qubits)) != n_controls:
            raise ValueError("All qubits must be different")
        
        # 게이트 이름 생성 (CZ, CCZ, CCCZ, CCCCZ, ...)
        gate_name = "C" * (n_controls - 1) + "Z"
        self.gates.append(QuantumGate(gate_name, list(qubits)))
        
        # N큐빗 제어 Z 게이트 구현
        n_qubits = self.n_qubits
        state_vector = self.circuit_state.state_vector.copy()
        
        self._debug_print(f"{gate_name} 적용 전 상태: {self._format_state_vector(state_vector)}")
        
        target_states = []
        
        # 각 상태에 대해 모든 지정된 큐빗이 1인지 확인
        for i in range(len(state_vector)):
            binary = format(i, f'0{n_qubits}b')
            
            # 모든 지정된 큐빗이 1인지 확인
            all_ones = True
            for qubit in qubits:
                qubit_bit = int(binary[n_qubits-1-qubit])
                if qubit_bit != 1:
                    all_ones = False
                    break
            
            # 모든 큐빗이 1이면 위상 뒤집기
            if all_ones:
                state_vector[i] = -state_vector[i]
                target_states.append(f"|{binary}⟩")
                self._debug_print(f"{gate_name} 위상 뒤집기 - 상태 |{binary}⟩ (인덱스 {i})")
        
        # 상태 업데이트
        self.circuit_state.state_vector = state_vector
        
        self._debug_print(f"{gate_name} 적용 후 상태: {self._format_state_vector(state_vector)}")
        self._debug_print(f"{gate_name}({', '.join(map(str, qubits))}) 게이트 적용됨")
        
        if target_states:
            self._debug_print(f"위상 뒤집기 적용된 상태들: {', '.join(target_states)}")
        
        self._gate_count += 1
        return self
    
    # 상태 검사 메서드 추가
    def get_state_vector(self) -> np.ndarray:
        """현재 회로의 상태 벡터 반환"""
        return self.circuit_state.state_vector.copy()
    
    def get_probabilities(self) -> List[float]:
        """각 기저 상태의 확률 반환"""
        return [abs(amp)**2 for amp in self.circuit_state.state_vector]
    
    def is_normalized(self) -> bool:
        """상태가 정규화되었는지 확인"""
        norm = np.linalg.norm(self.circuit_state.state_vector)
        return abs(norm - 1.0) < 1e-10
    
    def depth(self) -> int:
        """회로 깊이 반환"""
        return self._gate_count
        
    # === 측정 ===
    def measure(self, qubit: int) -> 'QuantumCircuit':
        """단일 큐빗 측정 추가"""
        self.measurements.append(qubit)
        return self
    
    def measure_all(self) -> 'QuantumCircuit':
        """모든 큐빗 측정 추가"""
        self.measurements.extend(range(self.n_qubits))
        return self
    
    # === 회로 실행 ===
    def run(self, simulator=None) -> Dict[str, Any]:
        """회로를 실행하고 결과 반환"""
        if simulator is None:
            simulator = QuantumSimulator()
        
        # 초기 상태로 시작
        current_state = self.circuit_state
        
        # 모든 게이트 순서대로 적용
        for gate in self.gates:
            current_state = self._apply_gate(gate, current_state, simulator)
        
        # 측정 수행
        measurement_results = {}
        for qubit_index in self.measurements:
            if qubit_index < current_state.n_qubits:
                result = current_state.measure(qubit_index)
                measurement_results[f"qubit_{qubit_index}"] = result
        
        return {
            "final_state": current_state,
            "measurements": measurement_results,
            "circuit_depth": len(self.gates),
            "gate_count": len(self.gates)
        }
    
    def _apply_gate(self, gate: QuantumGate, state: QuantumState, simulator) -> QuantumState:
        """개별 게이트를 상태에 적용"""
        if gate.name == "H":
            return simulator.apply_single_gate_to_circuit("H", state, gate.target_qubits[0], self.debug_mode)
        elif gate.name == "X":
            return simulator.apply_single_gate_to_circuit("X", state, gate.target_qubits[0], self.debug_mode)
        elif gate.name == "Y":
            return simulator.apply_single_gate_to_circuit("Y", state, gate.target_qubits[0], self.debug_mode)
        elif gate.name == "Z":
            return simulator.apply_single_gate_to_circuit("Z", state, gate.target_qubits[0], self.debug_mode)
        elif gate.name == "S":
            return simulator.apply_single_gate_to_circuit("S", state, gate.target_qubits[0], self.debug_mode)
        elif gate.name == "T":
            return simulator.apply_single_gate_to_circuit("T", state, gate.target_qubits[0], self.debug_mode)
        elif gate.name in ["RX", "RY", "RZ"]:
            axis = gate.name[1]  # "X", "Y", "Z"
            angle = gate.parameters[0]
            return simulator.apply_rotation_to_circuit(axis, angle, state, gate.target_qubits[0], self.debug_mode)
        elif gate.name == "CNOT":
            return simulator.apply_cnot_to_circuit(state, gate.control_qubits[0], gate.target_qubits[0], self.debug_mode)
        elif gate.name == "CZ":
            return simulator.apply_cz_to_circuit(state, gate.control_qubits[0], gate.target_qubits[0], self.debug_mode)
        else:
            raise ValueError(f"Unknown gate: {gate.name}")
    
    # === 회로 시각화 ===
    def draw(self) -> str:
        """회로를 ASCII 아트로 그리기"""
        lines = [f"q{i}: |0⟩──" for i in range(self.n_qubits)]
        
        # 게이트들을 시간순으로 그리기
        for gate in self.gates:
            if gate.name in ["H", "X", "Y", "Z", "S", "T"]:
                # 단일 큐빗 게이트
                qubit = gate.target_qubits[0]
                lines[qubit] += f"[{gate.name}]──"
                # 다른 큐빗들은 선만 그리기
                for i in range(self.n_qubits):
                    if i != qubit:
                        lines[i] += "─────"
            elif gate.name in ["RX", "RY", "RZ"]:
                # 회전 게이트
                qubit = gate.target_qubits[0]
                angle = gate.parameters[0]
                lines[qubit] += f"[{gate.name}({angle:.2f})]──"
                # 다른 큐빗들은 선만 그리기
                for i in range(self.n_qubits):
                    if i != qubit:
                        lines[i] += "─────────────"
            elif gate.name == "CNOT":
                # CNOT 게이트
                control = gate.control_qubits[0]
                target = gate.target_qubits[0]
                for i in range(self.n_qubits):
                    if i == control:
                        lines[i] += "●────"
                    elif i == target:
                        lines[i] += "⊕────"
                    else:
                        lines[i] += "│────"
        
        # 측정 추가
        for qubit in self.measurements:
            lines[qubit] += "[M]"
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        return self.draw()

class QuantumSimulator:
    def __init__(self):
        
        self.predefined_states = {
            "|0⟩": np.array([1.0, 0.0]),
            "|1⟩": np.array([0.0, 1.0]),
            "|+⟩": np.array([1/np.sqrt(2), 1/np.sqrt(2)]),
            "|-⟩": np.array([1/np.sqrt(2), -1/np.sqrt(2)]),
            "|+i⟩": np.array([1/np.sqrt(2), 1j/np.sqrt(2)]),
            "|-i⟩": np.array([1/np.sqrt(2), -1j/np.sqrt(2)]),
            
            # Multi-qubit states
            "|00⟩": np.array([1.0, 0.0, 0.0, 0.0]),
            "|01⟩": np.array([0.0, 1.0, 0.0, 0.0]),
            "|10⟩": np.array([0.0, 0.0, 1.0, 0.0]),
            "|11⟩": np.array([0.0, 0.0, 0.0, 1.0]),
            
            # Bell states
            "|Φ+⟩": np.array([1/np.sqrt(2), 0.0, 0.0, 1/np.sqrt(2)]),
            "|Φ-⟩": np.array([1/np.sqrt(2), 0.0, 0.0, -1/np.sqrt(2)]),
            "|Ψ+⟩": np.array([0.0, 1/np.sqrt(2), 1/np.sqrt(2), 0.0]),
            "|Ψ-⟩": np.array([0.0, 1/np.sqrt(2), -1/np.sqrt(2), 0.0]),
            
            # 3-qubit states
            "|000⟩": np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            "|GHZ⟩": np.array([1/np.sqrt(2), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1/np.sqrt(2)]),
            "|W⟩": np.array([0.0, 1/np.sqrt(3), 1/np.sqrt(3), 0.0, 1/np.sqrt(3), 0.0, 0.0, 0.0]),
        }
        
        # Quantum gates
        self.gates = {
            'I': np.array([[1, 0], [0, 1]]),
            'X': np.array([[0, 1], [1, 0]]),
            'Y': np.array([[0, -1j], [1j, 0]]),
            'Z': np.array([[1, 0], [0, -1]]),
            'H': np.array([[1, 1], [1, -1]]) / np.sqrt(2),
            'S': np.array([[1, 0], [0, 1j]]),
            'T': np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]]),
        }
    
    def create_qubit(self, state_notation: str) -> QuantumState:
        """Create a quantum state from notation"""
        if state_notation in self.predefined_states:
            return QuantumState(self.predefined_states[state_notation].copy())
        else:
            raise ValueError(f"Unknown quantum state: {state_notation}")
    
    def create_custom_state(self, amplitudes: List[complex]) -> QuantumState:
        """Create a custom quantum state from amplitudes"""
        state_vector = np.array(amplitudes, dtype=complex)
        return QuantumState(state_vector)
    
    def apply_single_gate(self, gate_name: str, qubit: QuantumState) -> QuantumState:
        """Apply a single-qubit gate"""
        if qubit.is_measured:
            raise RuntimeError("Cannot apply gate to measured qubit!")
        
        if gate_name not in self.gates:
            raise ValueError(f"Unknown gate: {gate_name}")
        
        gate = self.gates[gate_name]
        
        if qubit.n_qubits == 1:
            new_state = gate @ qubit.state_vector
            return QuantumState(new_state, 1)
        else:
            # For multi-qubit states, apply to the first qubit
            return self._apply_gate_to_qubit(gate, qubit, 0)
    
    # 🆕 회로용 게이트 적용 메서드들 (DEBUG 제어 추가)
    def apply_single_gate_to_circuit(self, gate_name: str, circuit_state: QuantumState, qubit_index: int, debug_mode: bool = False) -> QuantumState:
        """회로의 특정 큐빗에 단일 게이트 적용"""
        if gate_name not in self.gates:
            raise ValueError(f"Unknown gate: {gate_name}")
        
        gate = self.gates[gate_name]
        return self._apply_gate_to_qubit(gate, circuit_state, qubit_index, debug_mode)
    
    def apply_rotation_to_circuit(self, axis: str, angle: float, circuit_state: QuantumState, qubit_index: int, debug_mode: bool = False) -> QuantumState:
        """회로의 특정 큐빗에 회전 게이트 적용"""
        if axis.upper() == 'X':
            gate = np.array([
                [np.cos(angle/2), -1j*np.sin(angle/2)],
                [-1j*np.sin(angle/2), np.cos(angle/2)]
            ])
        elif axis.upper() == 'Y':
            gate = np.array([
                [np.cos(angle/2), -np.sin(angle/2)],
                [np.sin(angle/2), np.cos(angle/2)]
            ])
        elif axis.upper() == 'Z':
            gate = np.array([
                [np.exp(-1j*angle/2), 0],
                [0, np.exp(1j*angle/2)]
            ])
        else:
            raise ValueError(f"Unknown rotation axis: {axis}")
        
        return self._apply_gate_to_qubit(gate, circuit_state, qubit_index, debug_mode)
    
    def apply_cnot_to_circuit(self, circuit_state: QuantumState, control_qubit: int, target_qubit: int, debug_mode: bool = False) -> QuantumState:
        """회로에 CNOT 게이트 적용"""
        n_qubits = circuit_state.n_qubits
        
        if debug_mode:
            print(f"DEBUG: CNOT 게이트 적용 - control={control_qubit}, target={target_qubit}")
        
        # CNOT 행렬을 전체 힐베르트 공간에서 구성
        cnot_matrix = np.eye(2**n_qubits, dtype=complex)
        
        for i in range(2**n_qubits):
            binary = format(i, f'0{n_qubits}b')
            control_bit = int(binary[control_qubit])
            
            if control_bit == 1:
                # 컨트롤 큐빗이 1이면 타겟 큐빗 플립
                new_binary = list(binary)
                new_binary[target_qubit] = '1' if new_binary[target_qubit] == '0' else '0'
                j = int(''.join(new_binary), 2)
                
                # i번째 행을 j번째 행과 교체
                cnot_matrix[i, i] = 0
                cnot_matrix[i, j] = 1
        
        new_state_vector = cnot_matrix @ circuit_state.state_vector
        return QuantumState(new_state_vector, n_qubits)
    
    def apply_cz_to_circuit(self, circuit_state: QuantumState, control_qubit: int, target_qubit: int, debug_mode: bool = False) -> QuantumState:
        """회로에 CZ 게이트 적용"""
        n_qubits = circuit_state.n_qubits
        
        if debug_mode:
            print(f"DEBUG: CZ 게이트 적용 - control={control_qubit}, target={target_qubit}")
        
        # CZ 행렬 구성
        cz_matrix = np.eye(2**n_qubits, dtype=complex)
        
        for i in range(2**n_qubits):
            binary = format(i, f'0{n_qubits}b')
            control_bit = int(binary[control_qubit])
            target_bit = int(binary[target_qubit])
            
            if control_bit == 1 and target_bit == 1:
                cz_matrix[i, i] = -1
        
        new_state_vector = cz_matrix @ circuit_state.state_vector
        return QuantumState(new_state_vector, n_qubits)
    
    def apply_rotation_gate(self, axis: str, angle: float, qubit: QuantumState) -> QuantumState:
        """Apply rotation gates RX, RY, RZ"""
        if qubit.is_measured:
            raise RuntimeError("Cannot apply gate to measured qubit!")
        
        if axis.upper() == 'X':
            gate = np.array([
                [np.cos(angle/2), -1j*np.sin(angle/2)],
                [-1j*np.sin(angle/2), np.cos(angle/2)]
            ])
        elif axis.upper() == 'Y':
            gate = np.array([
                [np.cos(angle/2), -np.sin(angle/2)],
                [np.sin(angle/2), np.cos(angle/2)]
            ])
        elif axis.upper() == 'Z':
            gate = np.array([
                [np.exp(-1j*angle/2), 0],
                [0, np.exp(1j*angle/2)]
            ])
        else:
            raise ValueError(f"Unknown rotation axis: {axis}")
        
        if qubit.n_qubits == 1:
            new_state = gate @ qubit.state_vector
            return QuantumState(new_state, 1)
        else:
            return self._apply_gate_to_qubit(gate, qubit, 0)
    
    def apply_cnot(self, control: QuantumState, target: QuantumState) -> QuantumState:
        """Apply CNOT gate to two single qubits"""
        if control.n_qubits != 1 or target.n_qubits != 1:
            raise ValueError("CNOT requires two single qubits")
        
        if control.is_measured or target.is_measured:
            raise RuntimeError("Cannot apply gate to measured qubit!")
        
        # Create 2-qubit system
        combined = control.tensor_product(target)
        
        # CNOT matrix
        cnot = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ])
        
        new_state = cnot @ combined.state_vector
        return QuantumState(new_state, 2)
    
    def _apply_gate_to_qubit(self, gate: np.ndarray, state: QuantumState, qubit_index: int, debug_mode: bool = False) -> QuantumState:
        """Apply a single-qubit gate to a specific qubit in a multi-qubit system"""
        n = state.n_qubits
        
        # 🔧 큐빗 순서 수정: Qube는 little-endian (q0가 최하위 비트)
        # 텐서곱에서는 big-endian (가장 왼쪽이 첫 번째)이므로 인덱스 변환 필요
        tensor_index = n - 1 - qubit_index
        
        if debug_mode:
            print(f"DEBUG: _apply_gate_to_qubit 호출됨 - qubit_index={qubit_index} → tensor_index={tensor_index}, n_qubits={n}")
            print(f"DEBUG: 입력 상태: {[abs(amp)**2 for amp in state.state_vector[:min(16, len(state.state_vector))]]}")
            print(f"DEBUG: 게이트 행렬:\n{gate}")
        
        if tensor_index == 0:
            # Apply to first position in tensor product
            identity = np.eye(2**(n-1))
            full_gate = np.kron(gate, identity)
            if debug_mode:
                print(f"DEBUG: 텐서 첫 번째 위치에 적용 - gate shape: {gate.shape}")
        elif tensor_index == n-1:
            # Apply to last position in tensor product
            identity = np.eye(2**(n-1))
            full_gate = np.kron(identity, gate)
            if debug_mode:
                print(f"DEBUG: 텐서 마지막 위치에 적용 - gate shape: {gate.shape}")
        else:
            # Apply to middle position in tensor product
            left_identity = np.eye(2**tensor_index)
            right_identity = np.eye(2**(n-tensor_index-1))
            full_gate = np.kron(np.kron(left_identity, gate), right_identity)
            if debug_mode:
                print(f"DEBUG: 텐서 중간 위치에 적용 - position {tensor_index}")
        
        if debug_mode:
            print(f"DEBUG: full_gate shape: {full_gate.shape}")
        
        new_state = full_gate @ state.state_vector
        
        if debug_mode:
            print(f"DEBUG: 출력 상태: {[abs(amp)**2 for amp in new_state[:min(16, len(new_state))]]}")
        
        return QuantumState(new_state, n)
    
    def calculate_fidelity(self, state1: QuantumState, state2: QuantumState) -> float:
        """Calculate fidelity between two quantum states"""
        if state1.n_qubits != state2.n_qubits:
            raise ValueError("States must have the same number of qubits")
        
        overlap = np.vdot(state1.state_vector, state2.state_vector)
        return abs(overlap) ** 2
    
    def calculate_entanglement_measure(self, state: QuantumState) -> float:
        """Calculate a simple entanglement measure"""
        if state.n_qubits < 2:
            return 0.0
        
        # For 2-qubit states, calculate concurrence (simplified)
        if state.n_qubits == 2:
            # Reshape state vector into 2x2 matrix
            rho = np.outer(state.state_vector, np.conj(state.state_vector))
            
            # Calculate von Neumann entropy of reduced density matrix
            # This is a simplified measure
            trace_rho_squared = np.trace(rho @ rho)
            return 1.0 - trace_rho_squared.real
        
        return 0.5  # Placeholder for higher-dimensional states