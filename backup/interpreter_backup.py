"""
interpreter.py - 회로 빌더 완전 지원 버전
"""

from typing import Dict, Any, List, Union
import numpy as np
import cmath
import random
from .lexer import QubeLexer
from .parser import (QubeParser, ASTNode, Program, FunctionDef, VarDecl, Assignment, 
                     BinaryOp, UnaryOp, FunctionCall, Literal, Identifier, ArrayLiteral, 
                     ArrayAccess, IfStatement, WhileLoop, ForLoop, Range,
                     MatchStatement, BreakStatement, ContinueStatement, ReturnStatement,
                     LoopStatement, QuantumIfStatement, SuperposeStatement, MeasureStatement,
                     LambdaFunction, ArrowFunction, PipeExpression, TryStatement, CatchClause, 
                     ThrowStatement, MemberAccess, ClassDef, MethodCall, SelfReference, ObjectLiteral,
                     ImportStatement, ExportStatement,
                     # 🆕 회로 관련 AST 노드들
                     CircuitDefinition, CircuitInstantiation, GateOperation, ApplyStatement,
                     ResetStatement, BarrierStatement, CircuitCall, QubitReference,
                     # 🆕 범위 문법 관련 AST 노드들
                     AllQubitsReference, RangeExpression)

from .quantum import QuantumSimulator, QuantumState, QuantumCircuit

class QubeValue:
    """Wrapper for all Qube values with type information"""
    def __init__(self, value: Any, type_name: str):
        self.value = value
        self.type_name = type_name
    
    def __str__(self):
        if self.type_name == "quantum_state":
            return str(self.value)
        elif self.type_name == "quantum_circuit":
            return f"QuantumCircuit({self.value.n_qubits} qubits)"
        return str(self.value)
    
    def __repr__(self):
        return f"QubeValue({self.value}, {self.type_name})"

class QubeClass:
    """클래스 정의 런타임 표현"""
    def __init__(self, name: str, parent_class, fields: List[tuple], methods: dict, 
                constructors: List = None, destructor = None):
        self.name = name
        self.parent_class = parent_class
        self.fields = fields      
        self.methods = methods    
        self.constructors = constructors or []  
        self.destructor = destructor            
        self.all_fields = self._compute_all_fields()
        self.all_methods = self._compute_all_methods()
        self.public_fields = [f for f in self.all_fields if f[0] == "public"]
        self.private_fields = [f for f in self.all_fields if f[0] == "private"]
        self.protected_fields = [f for f in self.all_fields if f[0] == "protected"]
        self.public_methods = {k: v for k, v in self.all_methods.items() if v.access_level == "public"}
        self.private_methods = {k: v for k, v in self.all_methods.items() if v.access_level == "private"}
        self.protected_methods = {k: v for k, v in self.all_methods.items() if v.access_level == "protected"}

    def _compute_all_fields(self):
        all_fields = []
        if self.parent_class:
            all_fields.extend(self.parent_class.all_fields)
        all_fields.extend(self.fields)
        return all_fields
    
    def _compute_all_methods(self):
        all_methods = {}
        if self.parent_class:
            all_methods.update(self.parent_class.all_methods)
        all_methods.update(self.methods)  
        return all_methods    

class QubeInstance:
    """클래스 인스턴스"""
    def __init__(self, class_def: QubeClass, field_values: dict):
        self.class_def = class_def
        self.field_values = field_values  

    def __str__(self):
        return f"<{self.class_def.name} instance>"    

class QubeException(Exception):
    """Qube 런타임 예외 기본 클래스"""
    def __init__(self, message: str, exception_type: str = "RuntimeError"):
        self.message = message
        self.exception_type = exception_type
        super().__init__(message)

class QubeRuntimeError(QubeException):
    def __init__(self, message: str):
        super().__init__(message, "RuntimeError")

class QubeTypeError(QubeException):
    def __init__(self, message: str):
        super().__init__(message, "TypeError")

class QubeValueError(QubeException):
    def __init__(self, message: str):
        super().__init__(message, "ValueError")

class QubeDivisionByZeroError(QubeException):
    def __init__(self, message: str = "Division by zero"):
        super().__init__(message, "DivisionByZeroError")   

class QubeQuantumError(QubeException):
    """양자 연산 관련 에러"""
    def __init__(self, message: str):
        super().__init__(message, "QuantumError")

class QubeCircuitError(QubeException):
    """회로 관련 에러"""
    def __init__(self, message: str):
        super().__init__(message, "CircuitError")

class ArrowFunctionValue(QubeValue):
    """화살표 함수 값"""
    def __init__(self, parameters: List[str], body: ASTNode, closure_env: dict):
        super().__init__(None, "arrow_function")  
        self.parameters = parameters
        self.body = body
        self.closure_env = closure_env

class ReturnException(Exception):
    """Exception to handle return statements"""
    def __init__(self, value):
        self.value = value

class QubeInterpreter:
    def __init__(self):
        self.variables: Dict[str, QubeValue] = {}
        self.functions: Dict[str, FunctionDef] = {}
        self.classes: Dict[str, QubeClass] = {}
        self.circuits: Dict[str, CircuitDefinition] = {}  # 🆕 회로 정의 저장소
        self.quantum_sim = QuantumSimulator()
        self.loop_stack = []  
        self.call_stack = []  
        self.scope_stack = []  

        # Module system
        self.module_cache = {}  
        self.exported_symbols = {}  
        self.current_module_path = None  
        
        # Built-in functions
        self.builtin_functions = {
            "println": self._builtin_println,
            "print": self._builtin_print,
            
            # Quantum gates
            "H": self._builtin_hadamard,
            "X": self._builtin_pauli_x,
            "Y": self._builtin_pauli_y,
            "Z": self._builtin_pauli_z,
            "S": self._builtin_s_gate,
            "T": self._builtin_t_gate,
            
            # Rotation gates
            "RX": self._builtin_rx,
            "RY": self._builtin_ry,
            "RZ": self._builtin_rz,
            
            # Two-qubit gates
            "CNOT": self._builtin_cnot,
            
            # Measurement
            "measure": self._builtin_measure,
            
            # 🆕 회로 빌더 함수들
            "Circuit": self._builtin_circuit_constructor,
            "draw_circuit": self._builtin_draw_circuit,
            "run_circuit": self._builtin_run_circuit,
            
            # Utility functions
            "sqrt": lambda x: QubeValue(np.sqrt(x.value), "float"),
            "sin": lambda x: QubeValue(np.sin(x.value), "float"),
            "cos": lambda x: QubeValue(np.cos(x.value), "float"),
            "exp": lambda x: QubeValue(np.exp(x.value), "complex"),
            
            # Array functions
            "len": self._builtin_len,
            "range": self._builtin_range,

            # 고차 함수들
            "map": self._builtin_map,
            "filter": self._builtin_filter,
            "reduce": self._builtin_reduce,
            "zip": self._builtin_zip,
            
            # 양자 특화 함수들
            "fidelity": self._builtin_fidelity,
            "entanglement": self._builtin_entanglement,
            "trace": self._builtin_trace,
            "clone_state": self._builtin_clone_state,
            
            # 수학 함수 확장
            "abs": lambda x: QubeValue(abs(x.value), x.type_name),
            "max": self._builtin_max,
            "min": self._builtin_min,
            "round": lambda x: QubeValue(round(x.value), "int"),

            # 디버그 함수 추가
            "debug_var": self._debug_variable_state,
        }
        
        # Constants
        self.variables["PI"] = QubeValue(np.pi, "float")
        self.variables["E"] = QubeValue(np.e, "float")
        self.variables["i"] = QubeValue(1j, "complex")

        # 🆕 유니코드 수학 상수들 추가
        self.variables["π"] = QubeValue(np.pi, "float")
        self.variables["e"] = QubeValue(np.e, "float")  # 오일러 수
        self.variables["φ"] = QubeValue((1 + np.sqrt(5)) / 2, "float")  # 황금비
        self.variables["∞"] = QubeValue(float('inf'), "float")  # 무한대
        self.variables["ℂ"] = QubeValue("complex", "type")  # 복소수 집합 표시용
        self.variables["ℝ"] = QubeValue("real", "type")     # 실수 집합 표시용
        self.variables["ℕ"] = QubeValue("natural", "type")  # 자연수 집합 표시용
        self.variables["ℤ"] = QubeValue("integer", "type")  # 정수 집합 표시용
        self.variables["ℚ"] = QubeValue("rational", "type") # 유리수 집합 표시용
    
    def run(self, code: str):
        """Main entry point to run Qube code"""
        try:
            # Tokenize
            lexer = QubeLexer(code)
            tokens = lexer.tokenize()
            
            # Parse
            parser = QubeParser(tokens)
            ast = parser.parse()
            
            # Execute
            self._execute_program(ast)
            
        except Exception as e:
            # print(f"Qube Error: {e}")
            raise
    
    def _execute_program(self, program: Program):
        """Execute the main program"""
        # First pass: collect function and circuit definitions
        for statement in program.statements:
            if isinstance(statement, FunctionDef):
                self.functions[statement.name] = statement
            elif isinstance(statement, CircuitDefinition):
                self.circuits[statement.name] = statement
                print(f"회로 정의 등록: {statement.name}")  # 디버그용
        
        # Second pass: execute statements
        for statement in program.statements:
            if not isinstance(statement, (FunctionDef, CircuitDefinition)):
                self._execute_statement(statement)
        
        # If there's a main function, call it
        if "main" in self.functions:
            self._call_function("main", [])
    
    def _execute_statement(self, node: ASTNode) -> Any:
        """확장된 statement 실행 - 회로 내부 함수 호출 및 반복문 지원"""
        
        try:
            # 🆕 회로 내부에서 함수 호출 지원 - 우선순위 높게
            if isinstance(node, FunctionCall):
                current_circuit = self._get_current_circuit()
                if current_circuit is not None:
                    return self._execute_function_call_in_circuit(node)
                else:
                    return self._call_function(node.name, node.args)
            
            # 🆕 회로 내부에서 ForLoop 지원
            elif isinstance(node, ForLoop):
                current_circuit = self._get_current_circuit()
                if current_circuit is not None:
                    return self._execute_for_loop_in_circuit(node)
                else:
                    return self._execute_for_loop_standard(node)
            
            # 🆕 회로 관련 처리 추가
            elif isinstance(node, CircuitDefinition):
                return self._execute_circuit_definition(node)
            elif isinstance(node, ApplyStatement):
                return self._execute_apply_statement(node)
            elif isinstance(node, ResetStatement):
                return self._execute_reset_statement(node)
            elif isinstance(node, BarrierStatement):
                return self._execute_barrier_statement(node)
            
            elif isinstance(node, VarDecl):
                value = self._evaluate_expression(node.value) if node.value else QubeValue(None, "null")
                
                # bit 타입 특별 처리 추가
                if node.var_type == "bit":
                    if value.type_name not in ["bit", "int"]:
                        raise QubeTypeError(f"Cannot assign {value.type_name} to bit variable")
                    
                    # int를 bit로 변환
                    if value.type_name == "int":
                        if value.value not in [0, 1]:
                            raise QubeValueError(f"bit variable can only hold 0 or 1, got {value.value}")
                        value = QubeValue(value.value, "bit")
                
                self.variables[node.name] = value
                
            elif isinstance(node, Assignment):
                if isinstance(node.target, Identifier):
                    value = self._evaluate_expression(node.value)
                    if node.operator == "=":
                        self.variables[node.target.name] = value
                    elif node.operator == "+=":
                        try:
                            if node.target.name not in self.variables:
                                raise NameError(f"Variable '{node.target.name}' not defined")
                            
                            old_val = self.variables[node.target.name]
                            new_val = self._apply_binary_op(old_val, "+", value)
                            self.variables[node.target.name] = new_val
                            
                        except Exception as e:
                            raise e
                    elif node.operator == "-=":
                        old_val = self.variables[node.target.name]
                        new_val = self._apply_binary_op(old_val, "-", value)
                        self.variables[node.target.name] = new_val
                    elif node.operator == "*=":
                        old_val = self.variables[node.target.name]
                        new_val = self._apply_binary_op(old_val, "*", value)
                        self.variables[node.target.name] = new_val

                elif isinstance(node.target, MemberAccess):
                    obj_value = self._evaluate_expression(node.target.object_expr)
                    member_name = node.target.member_name
                    value = self._evaluate_expression(node.value)
                    
                    if obj_value.type_name == "instance":
                        context = self._get_access_context()
                        field = self._check_field_access(obj_value, member_name, context)
                        
                        instance = obj_value.value
                        instance.field_values[member_name] = value
                    else:
                        raise QubeRuntimeError(f"Cannot assign to member of {obj_value.type_name}")          
                
            elif isinstance(node, Assignment) and isinstance(node.target, ArrayAccess):
                array = self._evaluate_expression(node.target.array)
                index = self._evaluate_expression(node.target.index)
                value = self._evaluate_expression(node.value)
                array.value[index.value] = value.value

            elif isinstance(node, FunctionDef):
                self.functions[node.name] = node
                return None

            elif isinstance(node, Identifier) and node.name.startswith("'"):
                return None

            elif isinstance(node, MatchStatement):
                return self._execute_match(node)
                
            elif isinstance(node, LoopStatement):
                return self._execute_loop(node)
                
            elif isinstance(node, BreakStatement):
                return self._execute_break(node)
                
            elif isinstance(node, ContinueStatement):
                return self._execute_continue(node)
                
            elif isinstance(node, ReturnStatement):
                value = None
                if node.value:
                    value = self._evaluate_expression(node.value)
                raise ReturnException(value)
            
            elif isinstance(node, ImportStatement):
                return self._execute_import_statement(node)
            elif isinstance(node, ExportStatement):
                return self._execute_export_statement(node)
                
            elif isinstance(node, QuantumIfStatement):
                return self._execute_quantum_if(node)
                
            elif isinstance(node, SuperposeStatement):
                return self._execute_superpose(node)
                
            elif isinstance(node, MeasureStatement):
                return self._execute_measure_statement(node)

            elif isinstance(node, MethodCall):
                return self._evaluate_method_call(node)

            elif isinstance(node, MemberAccess):
                return self._evaluate_member_access(node)

            elif isinstance(node, Identifier):
                return self._evaluate_expression(node)
            elif isinstance(node, TryStatement):
                return self._execute_try_statement(node)
            elif isinstance(node, ThrowStatement):
                return self._execute_throw_statement(node)
                
            elif isinstance(node, IfStatement):
                condition = self._evaluate_expression(node.condition)
                if self._is_truthy(condition):
                    for stmt in node.then_body:
                        result = self._execute_statement(stmt)
                        # 🔧 명시적 return만 처리 (2번째 방법)
                        if isinstance(result, dict) and result.get("type") == "return":
                            return result
                elif node.else_body:
                    for stmt in node.else_body:
                        result = self._execute_statement(stmt)
                        if isinstance(result, dict) and result.get("type") == "return":
                            return result
                            
            elif isinstance(node, WhileLoop):
                while True:
                    condition = self._evaluate_expression(node.condition)
                    if not self._is_truthy(condition):
                        break
                    for stmt in node.body:
                        result = self._execute_statement(stmt)
                        if result is not None:
                            return result
            elif isinstance(node, ClassDef):
                return self._execute_class_definition(node)

            else:
                raise QubeRuntimeError(f"Unknown statement type: {type(node)}")
                    
        except QubeException:
            # Qube 예외는 그대로 전파 (중복 로그 방지)
            raise
        except ReturnException:
            raise  
        except Exception as e:
            # 시스템 예외를 Qube 예외로 변환 (한 번만)
            raise QubeRuntimeError(f"실행 중 오류: {str(e)}")
        
    def _execute_function_call_in_circuit(self, node: FunctionCall):
        """🆕 회로 내부에서 함수 호출 실행"""
        
        print(f"🔧 회로 내부에서 함수 호출: {node.name}()")
        
        # 내장 함수 확인
        if node.name in self.builtin_functions:
            arg_values = [self._evaluate_expression(arg) for arg in node.args]
            
            # measure 함수의 특별 처리
            if node.name == "measure":
                if len(arg_values) == 1:
                    result = self.builtin_functions[node.name](arg_values[0])
                elif len(arg_values) == 2:
                    result = self.builtin_functions[node.name](arg_values[0], arg_values[1].value)
                else:
                    raise QubeRuntimeError(f"measure() takes 1 or 2 arguments, got {len(arg_values)}")
            else:
                result = self.builtin_functions[node.name](*arg_values)
            
            return result if isinstance(result, QubeValue) else QubeValue(result, "auto")
        
        # 사용자 정의 함수 확인
        elif node.name in self.functions:
            func_def = self.functions[node.name]
            arg_values = [self._evaluate_expression(arg) for arg in node.args]
            
            # 함수 스코프 생성
            old_vars = self.variables.copy()
            
            try:
                # 매개변수 바인딩
                for i, (param_name, param_type) in enumerate(func_def.params):
                    if i < len(arg_values):
                        self.variables[param_name] = arg_values[i]
                
                # 🔑 핵심: 회로 컨텍스트 유지하면서 함수 본문 실행
                result = None
                for statement in func_def.body:
                    self._execute_statement(statement)  # 재귀 호출로 회로 컨텍스트 유지
                    
            except ReturnException as e:
                result = e.value
            finally:
                # 변수 상태 복원
                self.variables = old_vars
            
            print(f"✅ 함수 {node.name}() 실행 완료")
            return result if result is not None else QubeValue(None, "null")
        
        else:
            raise NameError(f"Unknown function: {node.name}")

    def _execute_for_loop_in_circuit(self, node: ForLoop):
        """🆕 회로 내부에서 for 반복문 실행"""
        
        print(f"🔄 회로 내부에서 반복문 시작: {node.variable}")
        
        # iterable 평가
        iterable = self._evaluate_expression(node.iterable)
        
        print(f"🔄 반복 대상: {iterable.value}")
        
        for item in iterable.value:
            print(f"  🔄 반복 {node.variable} = {item}")
            
            # 반복 변수 설정
            old_value = self.variables.get(node.variable)
            self.variables[node.variable] = QubeValue(item, "auto")
            
            try:
                # 반복문 본문 실행 (회로 컨텍스트 유지)
                for stmt in node.body:
                    self._execute_statement(stmt)  # 재귀 호출
                    
            except ReturnException as e:
                raise e
            finally:
                # 반복 변수 복원
                if old_value is not None:
                    self.variables[node.variable] = old_value
                elif node.variable in self.variables:
                    del self.variables[node.variable]
        
        print(f"🔄 반복문 완료")
        return None

    def _execute_for_loop_standard(self, node: ForLoop):
        """기존 for 반복문 실행 (회로 외부)"""
        iterable = self._evaluate_expression(node.iterable)
        
        for item in iterable.value:
            self.variables[node.variable] = QubeValue(item, "auto")
            for stmt in node.body:
                try:
                    self._execute_statement(stmt)
                except ReturnException as e:
                    raise e
        
        return None

    # 🆕 회로 관련 실행 메서드들
    def _execute_circuit_definition(self, node: CircuitDefinition):
        """회로 정의 처리 - 단순히 저장소에 등록"""
        self.circuits[node.name] = node
        # 회로를 변수로도 등록 (Constructor처럼 사용 가능)
        self.variables[node.name] = QubeValue(node, "circuit_definition")
        return None

    def _execute_apply_statement(self, node: ApplyStatement):
        """apply 문 실행 - 범위 문법 지원 추가"""
        current_circuit = self._get_current_circuit()
        
        if not current_circuit:
            raise QubeCircuitError("활성 회로가 없습니다. 회로 정의 내에서 사용해주세요.")
        
        gate_name = node.gate_name.upper()
        
        # 타겟 큐빗들 평가 - 범위 문법 지원
        target_indices = []
        
        for target in node.targets:
            if hasattr(target, '__class__') and target.__class__.__name__ == 'AllQubitsReference':
                # apply H to ~; - 모든 큐빗에 적용
                all_qubits = list(range(current_circuit.n_qubits))
                target_indices.extend(all_qubits)
                
            elif hasattr(target, '__class__') and target.__class__.__name__ == 'RangeExpression':
                # 범위 표현식 처리
                resolved_qubits = self._resolve_range_expression(target, current_circuit.n_qubits)
                target_indices.extend(resolved_qubits)
                
            elif isinstance(target, QubitReference):
                # 기존 큐빗 참조
                index = self._evaluate_qubit_reference(target)
                if not isinstance(index, int) or index < 0 or index >= current_circuit.n_qubits:
                    raise QubeQuantumError(f"큐빗 인덱스 q{index}가 범위를 벗어났습니다.")
                target_indices.append(index)
                
            elif hasattr(target, '__class__') and target.__class__.__name__ == 'ArrayLiteral':
                # [q0, q1, q2] 형태
                for qubit_ref in target.elements:
                    if isinstance(qubit_ref, QubitReference):
                        index = self._evaluate_qubit_reference(qubit_ref)
                        target_indices.append(index)
            else:
                # 기존 방식 호환성
                target_val = self._evaluate_expression(target)
                index = target_val.value
                if not isinstance(index, int) or index < 0 or index >= current_circuit.n_qubits:
                    raise QubeQuantumError(f"큐빗 인덱스 q{index}가 범위를 벗어났습니다.")
                target_indices.append(index)
        
        # 매개변수 평가
        parameters = []
        for param in node.parameters:
            param_val = self._evaluate_expression(param)
            parameters.append(param_val.value)
        
        # 게이트 적용 - 범위 문법 지원
        self._apply_gate_with_range_support(current_circuit, gate_name, target_indices, parameters)
        
        return None

    def _execute_reset_statement(self, node: ResetStatement):
        """reset 문 실행"""
        # 간단 구현: 큐빗을 |0⟩ 상태로 리셋
        print("Reset operation (simulation)")
        return None

    def _execute_barrier_statement(self, node: BarrierStatement):
        """barrier 문 실행"""
        # 간단 구현: 로그만 출력
        print("Barrier operation (simulation)")
        return None

    def _execute_measure_statement(self, node: MeasureStatement):
        """통합된 측정 문 실행 - 최종 정리 버전"""
        current_circuit = self._get_current_circuit()
        
        if not current_circuit:
            # 회로가 없으면 개별 큐빗 측정
            return self._execute_individual_qubit_measurement(node)
        
        # 측정할 큐빗 찾기
        qubit_ref = None
        
        if hasattr(node, 'qubits') and node.qubits:
            qubit_ref = node.qubits[0] if node.qubits else None
        elif hasattr(node, 'qubit') and node.qubit:
            qubit_ref = node.qubit
        elif hasattr(node, 'target') and node.target:
            qubit_ref = node.target
        
        if not qubit_ref:
            raise QubeRuntimeError("No qubit specified for measurement")
        
        # 큐빗 인덱스 결정
        if isinstance(qubit_ref, QubitReference):
            qubit_index = self._evaluate_qubit_reference(qubit_ref)
        elif isinstance(qubit_ref, Identifier):
            # q0, q1 같은 식별자인 경우
            import re
            match = re.search(r'\d+', qubit_ref.name)
            if match:
                qubit_index = int(match.group())
            else:
                raise QubeRuntimeError(f"Invalid qubit reference: {qubit_ref.name}")
        else:
            raise QubeRuntimeError(f"Unsupported qubit reference type: {type(qubit_ref)}")
        
        # 범위 검사
        if qubit_index < 0 or qubit_index >= current_circuit.n_qubits:
            raise QubeRuntimeError(f"Qubit index {qubit_index} out of range [0, {current_circuit.n_qubits-1}]")
        
        # 측정 실행
        result = self._measure_circuit_qubit(current_circuit, qubit_index)
        
        # 결과 변수에 저장 (선택사항)
        if hasattr(node, 'result_var') and node.result_var:
            self.variables[node.result_var] = QubeValue(result, "bit")
        
        return QubeValue(result, "bit")

    def _get_current_circuit(self):
        """현재 활성 회로 반환"""
        # 1. current_circuit 속성에서 직접 찾기
        if hasattr(self, 'current_circuit') and self.current_circuit is not None:
            return self.current_circuit
        
        # 2. 변수에서 quantum_circuit 타입 찾기 (기존 로직)
        for name, value in self.variables.items():
            if value.type_name == "quantum_circuit":
                return value.value
        
        return None

    def _evaluate_qubit_reference(self, node: QubitReference):
        """큐빗 참조 평가: q0, q[i] 등"""
        if node.index is None:
            # q0 형태 - 이름에서 숫자 추출 (정규식 캐싱)
            if not hasattr(self, '_qubit_name_regex'):
                import re
                self._qubit_name_regex = re.compile(r'\d+')
            
            match = self._qubit_name_regex.search(node.name)
            if match:
                return int(match.group())
            else:
                raise QubeRuntimeError(f"Invalid qubit reference: {node.name}")
        else:
            # q[i] 형태
            index_val = self._evaluate_expression(node.index)
            if not isinstance(index_val.value, int):
                raise QubeRuntimeError(f"Qubit index must be integer, got {type(index_val.value)}")
            return index_val.value

    # 🆕 회로 관련 내장 함수들
    def _builtin_circuit_constructor(self, n_qubits: QubeValue) -> QubeValue:
        """Circuit(n) - 새로운 양자 회로 생성"""
        if n_qubits.type_name != "int":
            raise QubeTypeError("Circuit constructor requires integer argument")
        
        circuit = QuantumCircuit(n_qubits.value)
        return QubeValue(circuit, "quantum_circuit")

    def _builtin_draw_circuit(self, circuit: QubeValue) -> QubeValue:
        """회로 그리기"""
        if circuit.type_name != "quantum_circuit":
            raise QubeTypeError("draw_circuit requires a quantum circuit")
        
        drawing = circuit.value.draw()
        print(drawing)
        return QubeValue(drawing, "string")

    def _builtin_run_circuit(self, circuit: QubeValue) -> QubeValue:
        """회로 실행"""
        if circuit.type_name != "quantum_circuit":
            raise QubeTypeError("run_circuit requires a quantum circuit")
        
        result = circuit.value.run(self.quantum_sim)
        return QubeValue(result, "dict")

    # 기존 메서드들은 그대로 유지...
    def _execute_match(self, node: MatchStatement) -> Any:
        expr_value = self._evaluate_expression(node.expr)
        
        for pattern, guard, body in node.arms:
            if self._match_pattern(pattern, expr_value):
                if guard is None or self._is_truthy(self._evaluate_expression(guard)):
                    result = None
                    for stmt in body:
                        result = self._execute_statement(stmt)
                        if result is not None:
                            return result
                    return result
        
        raise RuntimeError("No matching pattern found")
    
    def _match_pattern(self, pattern: ASTNode, value: QubeValue) -> bool:
        if isinstance(pattern, Literal):
            return pattern.value == value.value
        elif isinstance(pattern, Identifier):
            if pattern.name == "_":
                return True  
            else:
                self.variables[pattern.name] = value
                return True
        else:
            return False
    
    def _execute_loop(self, node: LoopStatement) -> Any:
        self.loop_stack.append(node.label)
        
        try:
            while True:
                for stmt in node.body:
                    result = self._execute_statement(stmt)
                    if isinstance(result, dict):
                        if result.get("type") == "break":
                            if result.get("label") is None or result.get("label") == node.label:
                                return None
                        elif result.get("type") == "continue":
                            if result.get("label") is None or result.get("label") == node.label:
                                break
                        elif result.get("type") == "return":
                            return result
        finally:
            self.loop_stack.pop()
    
    def _execute_break(self, node: BreakStatement) -> dict:
        return {"type": "break", "label": node.label}
    
    def _execute_continue(self, node: ContinueStatement) -> dict:
        return {"type": "continue", "label": node.label}
    
    def _execute_quantum_if(self, node: QuantumIfStatement) -> Any:
        condition_value = self._evaluate_expression(node.condition)
        
        if condition_value.type_name == "bit":
            if condition_value.value == 1:
                for stmt in node.then_body:
                    result = self._execute_statement(stmt)
                    if result is not None:
                        return result
            elif node.else_body:
                for stmt in node.else_body:
                    result = self._execute_statement(stmt)
                    if result is not None:
                        return result
        else:
            if self._is_truthy(condition_value):
                for stmt in node.then_body:
                    result = self._execute_statement(stmt)
                    if result is not None:
                        return result
            elif node.else_body:
                for stmt in node.else_body:
                    result = self._execute_statement(stmt)
                    if result is not None:
                        return result
    
    def _execute_superpose(self, node: SuperposeStatement) -> Any:
        if node.target:
            target_value = self._evaluate_expression(node.target)
            
            for pattern, body in node.branches:
                pattern_value = self._evaluate_expression(pattern)
                
                print(f"Superpose branch for {pattern_value}:")
                for stmt in body:
                    self._execute_statement(stmt)
    
    def _evaluate_pipe_expression(self, node):
        left_value = self._evaluate_expression(node.left)
        func_name = node.right.name
        
        if func_name in self.functions:
            func_def = self.functions[func_name]
            
            old_vars = self.variables.copy()
            
            try:
                if len(func_def.params) > 0:
                    param_name = func_def.params[0][0]  
                    self.variables[param_name] = left_value
                
                for stmt in func_def.body:
                    if hasattr(stmt, 'value') and stmt.value is not None:
                        return self._evaluate_expression(stmt.value)
                
                return QubeValue(None, "null")
            finally:
                self.variables = old_vars
        else:
            raise RuntimeError(f"Function '{func_name}' not found")

    def _evaluate_expression(self, node: ASTNode) -> QubeValue:
        """Evaluate an expression and return its value"""
        if isinstance(node, Literal):
            if node.type_name == "quantum_state":
                quantum_state = self.quantum_sim.create_qubit(node.value)
                return QubeValue(quantum_state, "quantum_state")
            elif node.type_name == "complex":
                return QubeValue(node.value, "complex")
            else:
                return QubeValue(node.value, node.type_name)
                
        elif isinstance(node, Identifier):
            if node.name in self.variables:
                return self.variables[node.name]
            elif node.name in self.functions:
                return QubeValue(node.name, "function")
            else:
                raise NameError(f"Unknown variable: {node.name}")

        elif isinstance(node, ArrowFunction):
            closure_env = self.variables.copy()
            return ArrowFunctionValue(node.parameters, node.body, closure_env)
                
        elif isinstance(node, BinaryOp):
            left = self._evaluate_expression(node.left)
            right = self._evaluate_expression(node.right)
            return self._apply_binary_op(left, node.operator, right)
            
        elif isinstance(node, UnaryOp):
            operand = self._evaluate_expression(node.operand)
            return self._apply_unary_op(node.operator, operand)
            
        elif isinstance(node, FunctionCall):
            return self._call_function(node.name, node.args)
        
        elif isinstance(node, MatchStatement):
            return self._evaluate_match(node)
            
        elif isinstance(node, ArrayLiteral):
            elements = [self._evaluate_expression(elem) for elem in node.elements]
            values = [elem.value for elem in elements]
            return QubeValue(values, "array")
            
        elif isinstance(node, ArrayAccess):
            array = self._evaluate_expression(node.array)
            index = self._evaluate_expression(node.index)
            value = array.value[index.value]
            return QubeValue(value, "auto")
            
        elif isinstance(node, Range):
            start = self._evaluate_expression(node.start)
            end = self._evaluate_expression(node.end)
            if node.inclusive:
                values = list(range(start.value, end.value + 1))
            else:
                values = list(range(start.value, end.value))
            return QubeValue(values, "range")
        
        elif isinstance(node, PipeExpression):
            return self._evaluate_pipe_expression(node)
        
        elif isinstance(node, MemberAccess):
            return self._evaluate_member_access(node)

        elif isinstance(node, MethodCall):
            return self._evaluate_method_call(node)
        elif isinstance(node, SelfReference):
            return self._evaluate_self_reference(node)   
        elif isinstance(node, ObjectLiteral):
            return self._evaluate_object_literal(node) 
        else:
            raise RuntimeError(f"Cannot evaluate expression: {type(node)}")
    
    def _call_function_value(self, func_value, args):
        """함수 값 호출 (기존 함수에 화살표 함수 지원 추가)"""
        
        if isinstance(func_value, ArrowFunctionValue):
            return self._call_arrow_function(func_value, args)
        
        elif isinstance(func_value, LambdaFunctionValue):
            return self._call_lambda_function(func_value, args)
        
        else:
            raise RuntimeError(f"Cannot call value of type: {type(func_value)}")

    def _call_arrow_function(self, arrow_func: QubeValue, args: List[QubeValue]) -> QubeValue:
        """화살표 함수 실행"""
        if len(args) != len(arrow_func.parameters):
            raise RuntimeError(f"Arrow function expects {len(arrow_func.parameters)} arguments, got {len(args)}")
        
        old_vars = self.variables.copy()
        
        self.variables.update(arrow_func.closure_env)
        
        for param, arg in zip(arrow_func.parameters, args):
            self.variables[param] = arg
        
        try:
            result = self._evaluate_expression(arrow_func.body)
            return result
        finally:
            self.variables = old_vars

    def _apply_binary_op(self, left: QubeValue, operator: str, right: QubeValue) -> QubeValue:
        """Apply binary operations"""
        if operator == "+":
            if left.type_name == "quantum_state" and right.type_name == "quantum_state":
                return QubeValue(left.value, "quantum_state")
            else:
                return QubeValue(left.value + right.value, self._infer_type(left.value + right.value))
                
        elif operator == "-":
            return QubeValue(left.value - right.value, self._infer_type(left.value - right.value))
            
        elif operator == "*":
            if isinstance(left.value, (int, float, complex)) and right.type_name == "quantum_state":
                new_amplitudes = left.value * right.value.state_vector
                new_state = self.quantum_sim.create_custom_state(new_amplitudes)
                return QubeValue(new_state, "quantum_state")
            else:
                return QubeValue(left.value * right.value, self._infer_type(left.value * right.value))
                
        elif operator == "/":
            if right.value == 0:
                raise QubeDivisionByZeroError("Cannot divide by zero")
            return QubeValue(left.value / right.value, self._infer_type(left.value / right.value))
            
        elif operator == "%":
            return QubeValue(left.value % right.value, self._infer_type(left.value % right.value))
            
        elif operator == "**":
            return QubeValue(left.value ** right.value, self._infer_type(left.value ** right.value))
            
        elif operator == "⊗":
            if left.type_name == "quantum_state" and right.type_name == "quantum_state":
                new_state = left.value.tensor_product(right.value)
                return QubeValue(new_state, "quantum_state")
            else:
                raise TypeError("Tensor product can only be applied to quantum states")
        
        elif operator == "==":
            return QubeValue(left.value == right.value, "bool")
        elif operator == "!=":
            return QubeValue(left.value != right.value, "bool")
        elif operator == "<":
            return QubeValue(left.value < right.value, "bool")
        elif operator == "<=":
            return QubeValue(left.value <= right.value, "bool")
        elif operator == ">":
            return QubeValue(left.value > right.value, "bool")
        elif operator == ">=":
            return QubeValue(left.value >= right.value, "bool")
        elif operator == "≈":
            return QubeValue(abs(left.value - right.value) < 1e-10, "bool")
            
        elif operator == "&&":
            return QubeValue(self._is_truthy(left) and self._is_truthy(right), "bool")
        elif operator == "||":
            return QubeValue(self._is_truthy(left) or self._is_truthy(right), "bool")
        elif operator == "^":
            return QubeValue(self._is_truthy(left) != self._is_truthy(right), "bool")
            
        else:
            raise RuntimeError(f"Unknown binary operator: {operator}")
    
    def _evaluate_match(self, node: MatchStatement) -> QubeValue:
        """Match 표현식 평가"""
        match_value = self._evaluate_expression(node.expr)
        
        for pattern, guard, body in node.arms:
            if self._match_pattern(pattern, match_value):
                if guard is not None:
                    old_vars = self.variables.copy()
                    self._bind_pattern_variables(pattern, match_value)
                    
                    guard_result = self._evaluate_expression(guard)
                    self.variables = old_vars  
                    
                    if not self._is_truthy(guard_result):
                        continue  
                
                return self._execute_match_body(pattern, match_value, body)
        
        raise RuntimeError(f"Non-exhaustive match: no pattern matched value {match_value.value}")

    def _bind_pattern_variables(self, pattern: ASTNode, value: QubeValue):
        """패턴에 포함된 변수들을 값에 바인딩"""
        if isinstance(pattern, Identifier) and pattern.name != "_":
            self.variables[pattern.name] = value

    def _execute_match_body(self, pattern: ASTNode, value: QubeValue, body: List[ASTNode]) -> QubeValue:
        """매치된 패턴의 body 실행"""
        old_vars = self.variables.copy()
        
        self._bind_pattern_variables(pattern, value)
        
        result = None
        for stmt in body:
            try:
                result = self._evaluate_expression(stmt)
            except RuntimeError:
                result = self._execute_statement(stmt)
        
        self.variables = old_vars
        
        return result if result is not None else QubeValue(None, "null")
    
    def _apply_unary_op(self, operator: str, operand: QubeValue) -> QubeValue:
        """Apply unary operations"""
        if operator == "-":
            return QubeValue(-operand.value, operand.type_name)
        elif operator == "!":
            return QubeValue(not self._is_truthy(operand), "bool")
        elif operator == "&":
            return QubeValue(operand.value, f"&{operand.type_name}")
        else:
            raise RuntimeError(f"Unknown unary operator: {operator}")
    
    def _call_function(self, name: str, args: List[ASTNode]) -> QubeValue:
        """Call a function with arguments"""
        arg_values = [self._evaluate_expression(arg) for arg in args]

        # 🆕 회로 생성자 확인 (클래스보다 먼저)
        if name in self.circuits:
            print(f"회로 생성: {name}")  # 디버그용
            return self._create_circuit_instance(name, arg_values)                                                              
        
        if name in self.classes:
            return self._create_class_instance(name, arg_values)
        
        if name in self.builtin_functions:
            # measure 함수의 특별 처리
            if name == "measure":
                if len(arg_values) == 1:
                    result = self.builtin_functions[name](arg_values[0])
                elif len(arg_values) == 2:
                    result = self.builtin_functions[name](arg_values[0], arg_values[1].value)
                else:
                    raise QubeRuntimeError(f"measure() takes 1 or 2 arguments, got {len(arg_values)}")
            else:
                result = self.builtin_functions[name](*arg_values)
            
            return result if isinstance(result, QubeValue) else QubeValue(result, "auto")
            
        elif name in self.functions:
            func = self.functions[name]
            
            old_vars = self.variables.copy()
            
            for i, (param_name, param_type) in enumerate(func.params):
                if i < len(arg_values):
                    self.variables[param_name] = arg_values[i]
            
            result = None
            try:
                for statement in func.body:
                    self._execute_statement(statement)
            except ReturnException as e:
                result = e.value
            
            self.variables = old_vars

            return result if result is not None else QubeValue(None, "null")
        else:
            raise NameError(f"Unknown function: {name}")
        
    def _create_circuit_instance(self, circuit_name: str, args: list = None):
        """회로 인스턴스 생성 - 에러 처리 개선"""
        if circuit_name not in self.circuits:
            raise QubeCircuitError(f"회로 '{circuit_name}'을 찾을 수 없습니다")
        
        circuit_def = self.circuits[circuit_name]
        n_qubits = circuit_def.n_qubits
        
        # 큐빗 수 검증
        if n_qubits <= 0:
            raise QubeCircuitError(f"잘못된 큐빗 수: {n_qubits}")
        if n_qubits > 20:  # 메모리 제한
            raise QubeCircuitError(f"큐빗 수가 너무 많습니다: {n_qubits} (최대 20)")
        
        try:
            from .quantum import QuantumCircuit
            circuit_instance = QuantumCircuit(n_qubits)
        except Exception as e:
            raise QubeCircuitError(f"회로 생성 실패: {str(e)}")
        
        old_vars = self.variables.copy()
        old_current_circuit = getattr(self, 'current_circuit', None)
        
        try:
            # 회로 설정
            self.current_circuit = circuit_instance
            self.variables['__current_circuit__'] = QubeValue(circuit_instance, "quantum_circuit")
            
            # 회로 본문 실행
            for i, stmt in enumerate(circuit_def.body):
                try:
                    self._execute_statement(stmt)
                except QubeException as e:
                    # 위치 정보 추가
                    raise QubeCircuitError(f"회로 '{circuit_name}' {i+1}번째 명령에서 오류: {e.message}")
                    
            return QubeValue(circuit_instance, "quantum_circuit")
            
        finally:
            # 환경 복원 (항상 실행)
            self.variables = old_vars
            if old_current_circuit is not None:
                self.current_circuit = old_current_circuit
            elif hasattr(self, 'current_circuit'):
                delattr(self, 'current_circuit')
    
    def _is_truthy(self, value: QubeValue) -> bool:
        """Determine if a value is truthy"""
        if value.type_name == "bool":
            return value.value
        elif value.type_name in ["int", "float"]:
            return value.value != 0
        elif value.type_name == "string":
            return len(value.value) > 0
        elif value.type_name == "null":
            return False
        else:
            return True
    
    def _infer_type(self, value: Any) -> str:
        """Infer the type of a value"""
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, complex):
            return "complex"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        else:
            return "auto"
    
    # 고차 함수들 구현
    def _builtin_map(self, func: QubeValue, iterable: QubeValue) -> QubeValue:
        if iterable.type_name != "array":
            raise TypeError("Map requires an array")
        
        if func.type_name not in ["function", "arrow_function"]:
            raise TypeError("Map requires a function as first argument")
        
        results = []
        for item in iterable.value:
            if func.type_name == "arrow_function":
                item_value = QubeValue(item, self._infer_type(item))
                result = self._call_arrow_function(func, [item_value])
            else:
                result = self._call_function(func.value, [Literal(item, self._infer_type(item))])
            
            results.append(result.value)
        
        return QubeValue(results, "array")
    
    def _builtin_filter(self, predicate: QubeValue, iterable: QubeValue) -> QubeValue:
        if iterable.type_name != "array":
            raise TypeError("Filter requires an array")
        
        if predicate.type_name not in ["function", "arrow_function"]:
            raise TypeError("Filter requires a function as first argument")
        
        results = []
        for item in iterable.value:
            if predicate.type_name == "arrow_function":
                item_value = QubeValue(item, self._infer_type(item))
                test_result = self._call_arrow_function(predicate, [item_value])
            else:
                test_result = self._call_function(predicate.value, [Literal(item, self._infer_type(item))])
            
            if self._is_truthy(test_result):
                results.append(item)
        
        return QubeValue(results, "array")
    
    def _builtin_reduce(self, func: QubeValue, iterable: QubeValue, initial: QubeValue = None) -> QubeValue:
        if iterable.type_name != "array":
            raise TypeError("Reduce requires an array")
        
        if func.type_name not in ["function", "arrow_function"]:
            raise TypeError("Reduce requires a function as first argument")
        
        items = iterable.value
        if not items:
            return initial if initial else QubeValue(None, "null")
        
        if initial is not None:
            accumulator = initial.value
            start_index = 0
        else:
            accumulator = items[0]
            start_index = 1
        
        for i in range(start_index, len(items)):
            if func.type_name == "arrow_function":
                acc_value = QubeValue(accumulator, self._infer_type(accumulator))
                item_value = QubeValue(items[i], self._infer_type(items[i]))
                result = self._call_arrow_function(func, [acc_value, item_value])
            else:
                acc_literal = Literal(accumulator, self._infer_type(accumulator))
                item_literal = Literal(items[i], self._infer_type(items[i]))
                result = self._call_function(func.value, [acc_literal, item_literal])
            
            accumulator = result.value
        
        return QubeValue(accumulator, self._infer_type(accumulator))
    
    def _builtin_zip(self, *arrays) -> QubeValue:
        if not all(arr.type_name == "array" for arr in arrays):
            raise TypeError("Zip requires arrays")
        
        values = [arr.value for arr in arrays]
        zipped = list(zip(*values))
        return QubeValue(zipped, "array")
    
    def _builtin_fidelity(self, state1: QubeValue, state2: QubeValue) -> QubeValue:
        if state1.type_name != "quantum_state" or state2.type_name != "quantum_state":
            raise TypeError("Fidelity requires two quantum states")
        
        fidelity = self.quantum_sim.calculate_fidelity(state1.value, state2.value)
        return QubeValue(fidelity, "float")
    
    def _builtin_entanglement(self, state: QubeValue) -> QubeValue:
        if state.type_name != "quantum_state":
            raise TypeError("Entanglement measure requires a quantum state")
        
        entanglement = self.quantum_sim.calculate_entanglement_measure(state.value)
        return QubeValue(entanglement, "float")
    
    def _builtin_trace(self, state: QubeValue) -> QubeValue:
        if state.type_name != "quantum_state":
            raise TypeError("Trace requires a quantum state")
        
        return QubeValue(1.0, "float")
    
    def _builtin_clone_state(self, state: QubeValue) -> QubeValue:
        if state.type_name != "quantum_state":
            raise TypeError("Can only clone quantum states")
        
        from .quantum import QuantumState
        new_state = QuantumState(state.value.state_vector.copy(), state.value.n_qubits)
        return QubeValue(new_state, "quantum_state")
    
    def _builtin_max(self, *args) -> QubeValue:
        if len(args) == 1 and args[0].type_name == "array":
            values = args[0].value
        else:
            values = [arg.value for arg in args]
        
        return QubeValue(max(values), "auto")
    
    def _builtin_min(self, *args) -> QubeValue:
        if len(args) == 1 and args[0].type_name == "array":
            values = args[0].value
        else:
            values = [arg.value for arg in args]
        
        return QubeValue(min(values), "auto")
    
    # Built-in function implementations
    def _builtin_println(self, *args) -> QubeValue:
        if not args:
            print()
            return QubeValue(None, "null")
        
        first_arg = args[0]
        first_value = first_arg.value if hasattr(first_arg, 'value') else str(first_arg)
        
        if isinstance(first_value, str) and '{}' in first_value:
            format_str = first_value
            format_str = format_str.replace('\\n', '\n').replace('\\t', '\t')

            values = []
            
            for arg in args[1:]:
                if hasattr(arg, 'value'):
                    values.append(str(arg.value))
                else:
                    values.append(str(arg))
            
            placeholder_count = format_str.count('{}')
            
            while len(values) < placeholder_count:
                values.append('')
            
            result = format_str
            for value in values[:placeholder_count]:
                result = result.replace('{}', str(value), 1)
            
            print(result)
        else:
            message = " ".join(str(arg.value) if hasattr(arg, 'value') else str(arg) for arg in args)
            print(message)
        
        return QubeValue(None, "null")
    
    def _builtin_print(self, *args) -> QubeValue:
        message = " ".join(str(arg.value) if hasattr(arg, 'value') else str(arg) for arg in args)
        print(message, end='')
        return QubeValue(None, "null")
    
    def _builtin_hadamard(self, qubit: QubeValue) -> QubeValue:
        if qubit.type_name != "quantum_state":
            raise TypeError("H gate can only be applied to quantum states")
        new_state = self.quantum_sim.apply_single_gate("H", qubit.value)
        return QubeValue(new_state, "quantum_state")
    
    def _builtin_pauli_x(self, qubit: QubeValue) -> QubeValue:
        if qubit.type_name != "quantum_state":
            raise TypeError("X gate can only be applied to quantum states")
        new_state = self.quantum_sim.apply_single_gate("X", qubit.value)
        return QubeValue(new_state, "quantum_state")
    
    def _builtin_pauli_y(self, qubit: QubeValue) -> QubeValue:
        if qubit.type_name != "quantum_state":
            raise TypeError("Y gate can only be applied to quantum states")
        new_state = self.quantum_sim.apply_single_gate("Y", qubit.value)
        return QubeValue(new_state, "quantum_state")
    
    def _builtin_pauli_z(self, qubit: QubeValue) -> QubeValue:
        if qubit.type_name != "quantum_state":
            raise TypeError("Z gate can only be applied to quantum states")
        new_state = self.quantum_sim.apply_single_gate("Z", qubit.value)
        return QubeValue(new_state, "quantum_state")
    
    def _builtin_s_gate(self, qubit: QubeValue) -> QubeValue:
        if qubit.type_name != "quantum_state":
            raise TypeError("S gate can only be applied to quantum states")
        new_state = self.quantum_sim.apply_single_gate("S", qubit.value)
        return QubeValue(new_state, "quantum_state")
    
    def _builtin_t_gate(self, qubit: QubeValue) -> QubeValue:
        if qubit.type_name != "quantum_state":
            raise TypeError("T gate can only be applied to quantum states")
        new_state = self.quantum_sim.apply_single_gate("T", qubit.value)
        return QubeValue(new_state, "quantum_state")
    
    def _builtin_rx(self, angle: QubeValue, qubit: QubeValue) -> QubeValue:
        if qubit.type_name != "quantum_state":
            raise TypeError("RX gate can only be applied to quantum states")
        new_state = self.quantum_sim.apply_rotation_gate("X", angle.value, qubit.value)
        return QubeValue(new_state, "quantum_state")
    
    def _builtin_ry(self, angle: QubeValue, qubit: QubeValue) -> QubeValue:
        if qubit.type_name != "quantum_state":
            raise TypeError("RY gate can only be applied to quantum states")
        new_state = self.quantum_sim.apply_rotation_gate("Y", angle.value, qubit.value)
        return QubeValue(new_state, "quantum_state")
    
    def _builtin_rz(self, angle: QubeValue, qubit: QubeValue) -> QubeValue:
        if qubit.type_name != "quantum_state":
            raise TypeError("RZ gate can only be applied to quantum states")
        new_state = self.quantum_sim.apply_rotation_gate("Z", angle.value, qubit.value)
        return QubeValue(new_state, "quantum_state")
    
    def _builtin_cnot(self, control: QubeValue, target: QubeValue) -> QubeValue:
        if control.type_name != "quantum_state" or target.type_name != "quantum_state":
            raise TypeError("CNOT gate can only be applied to quantum states")
        new_state = self.quantum_sim.apply_cnot(control.value, target.value)
        return QubeValue(new_state, "quantum_state")
    
    def _builtin_measure(self, target, qubit_indices=None):
        """Enhanced measure function supporting both individual qubits and circuits"""
        
        # Case 1: measure(qubit) - 기존 개별 qubit 측정
        if qubit_indices is None:
            if not isinstance(target, QubeValue) or target.type_name != "qubit":
                raise QubeTypeError(f"Can only measure quantum states, got {target.type_name if hasattr(target, 'type_name') else type(target)}")
            
            if hasattr(target.value, 'measure'):
                result = target.value.measure()
            else:
                raise QubeQuantumError(f"Invalid measurement target")
            
            if not isinstance(result, int) or result not in [0, 1]:
                raise QubeQuantumError(f"Invalid measurement result: {result}")
            
            return QubeValue(result, "bit")
        
        # Case 2: measure(circuit, [0,1,2]) - 새로운 회로 전체 측정
        else:
            return self._measure_circuit_with_indices(target, qubit_indices)
        
    def _measure_circuit_with_indices(self, circuit_value, qubit_indices):
        """Measure specific qubits from a quantum circuit"""
        
        # Circuit 타입 검증
        if not hasattr(circuit_value, 'value') or not hasattr(circuit_value.value, 'circuit_state'):
            raise QubeTypeError("First argument must be a quantum circuit for multi-qubit measurement")
        
        circuit = circuit_value.value
        
        # 인덱스 유효성 검사
        if not isinstance(qubit_indices, list):
            raise QubeTypeError("Qubit indices must be provided as a list")
        
        for idx in qubit_indices:
            if not isinstance(idx, int) or idx < 0 or idx >= circuit.n_qubits:
                raise QubeRuntimeError(f"Invalid qubit index {idx} for {circuit.n_qubits}-qubit circuit")
        
        # 회로의 현재 상태에서 측정
        try:
            measurement_results = []
            
            # 모든 큐빗을 한 번에 측정 (상태 붕괴 방지)
            measurement_results = self._measure_all_qubits_simultaneously(circuit, qubit_indices)
            
            return QubeValue(measurement_results, "list")
            
        except Exception as e:
            raise QubeQuantumError(f"Circuit measurement failed: {str(e)}")

    
    def _builtin_len(self, obj: QubeValue) -> QubeValue:
        if obj.type_name == "array":
            return QubeValue(len(obj.value), "int")
        elif obj.type_name == "string":
            return QubeValue(len(obj.value), "int")
        else:
            raise TypeError(f"Cannot get length of {obj.type_name}")
    
    def _builtin_range(self, start: QubeValue, end: QubeValue = None) -> QubeValue:
        if end is None:
            values = list(range(start.value))
        else:
            values = list(range(start.value, end.value))
        return QubeValue(values, "range")
    
    
    def _execute_try_statement(self, node: TryStatement):
        """Try-catch-finally 문 실행"""
        finally_executed = False
        
        try:
            # try 블록 실행
            for stmt in node.try_block:
                self._execute_statement(stmt)
                
        except QubeException as e:
            # Qube 예외 처리
            caught = False
            
            for catch_clause in node.catch_clauses:
                # 예외 타입 매칭
                if (catch_clause.exception_type is None or 
                    catch_clause.exception_type == e.exception_type):
                    
                    # 예외 변수에 예외 객체 저장
                    old_value = self.variables.get(catch_clause.exception_var)
                    exception_obj = QubeValue({
                        'type': e.exception_type,
                        'message': e.message
                    }, "exception")
                    self.variables[catch_clause.exception_var] = exception_obj
                    
                    try:
                        # catch 블록 실행
                        for stmt in catch_clause.body:
                            self._execute_statement(stmt)
                    finally:
                        # 예외 변수 복원
                        if old_value is None:
                            self.variables.pop(catch_clause.exception_var, None)
                        else:
                            self.variables[catch_clause.exception_var] = old_value
                    
                    caught = True
                    break
            
            if not caught:
                # 처리되지 않은 예외는 다시 발생
                raise
                
        except Exception as e:
            # Python 예외를 Qube 예외로 변환
            qube_exception = QubeRuntimeError(str(e))
            
            caught = False
            for catch_clause in node.catch_clauses:
                if (catch_clause.exception_type is None or 
                    catch_clause.exception_type == "RuntimeError"):
                    
                    old_value = self.variables.get(catch_clause.exception_var)
                    exception_obj = QubeValue({
                        'type': 'RuntimeError',
                        'message': str(e)
                    }, "exception")
                    self.variables[catch_clause.exception_var] = exception_obj
                    
                    try:
                        for stmt in catch_clause.body:
                            self._execute_statement(stmt)
                    finally:
                        if old_value is None:
                            self.variables.pop(catch_clause.exception_var, None)
                        else:
                            self.variables[catch_clause.exception_var] = old_value
                    
                    caught = True
                    break
            
            if not caught:
                raise qube_exception
                
        finally:
            # finally 블록 실행
            if node.finally_block:
                for stmt in node.finally_block:
                    self._execute_statement(stmt)
            finally_executed = True

    def _execute_throw_statement(self, node: ThrowStatement):
        exception_value = self._evaluate_expression(node.exception)
        raise QubeRuntimeError(str(exception_value.value))
        
    def _evaluate_member_access(self, node: MemberAccess) -> QubeValue:
        obj_value = self._evaluate_expression(node.object_expr)
        member_name = node.member_name
        
        if obj_value.type_name == "quantum_circuit":
            # 회로 메서드 호출
            if member_name == "draw":
                return QubeValue(obj_value.value.draw(), "string")
            elif member_name == "run":
                result = obj_value.value.run(self.quantum_sim)
                return QubeValue(result, "dict")
            else:
                raise QubeRuntimeError(f"Quantum circuit has no method '{member_name}'")
        
        # 기타 멤버 접근 로직...
        return QubeValue(None, "null")
        
    def _execute_class_definition(self, node: ClassDef):
        """클래스 정의 실행 - 상속 + 생성자/소멸자 지원"""
        # 부모 클래스 찾기
        parent_class_obj = None
        if node.parent_class:
            if node.parent_class not in self.classes:
                raise QubeRuntimeError(f"Parent class '{node.parent_class}' not found")
            parent_class_obj = self.classes[node.parent_class]

        # 메서드들을 딕셔너리로 변환
        methods = {}
        for method in node.methods:
            methods[method.name] = method
        
        # 생성자들을 리스트로 저장 (다중 생성자 지원)
        constructors = node.constructors if hasattr(node, 'constructors') else []
        
        # 소멸자 저장 (하나만 허용)
        destructor = node.destructor if hasattr(node, 'destructor') else None
        
        # 클래스 객체 생성 (생성자/소멸자 포함)
        class_obj = QubeClass(node.name, parent_class_obj, node.fields, methods, constructors, destructor)
        
        # 클래스 저장소에 등록
        self.classes[node.name] = class_obj
        
        # 클래스를 변수로도 등록 (ClassName.new() 같은 호출을 위해)
        self.variables[node.name] = QubeValue(class_obj, "class")

    def _evaluate_method_call(self, node: MethodCall) -> QubeValue:
        """메서드 호출 실행 - 접근 제어 적용"""
        obj_value = self._evaluate_expression(node.object_expr)
        
        # 접근 컨텍스트 확인
        context = self._get_access_context()
        
        if obj_value.type_name == "class":
            # 클래스 메서드 호출 - 접근 제어 검사
            method_def = self._check_method_access(obj_value, node.method_name, context)
            arg_values = [self._evaluate_expression(arg) for arg in node.args]
            return self._call_function_method(method_def, arg_values, None)
        
        elif obj_value.type_name == "instance":
            # 인스턴스 메서드 호출 - 접근 제어 검사
            method_def = self._check_method_access(obj_value, node.method_name, context)
            arg_values = [self._evaluate_expression(arg) for arg in node.args]
            return self._call_function_method(method_def, arg_values, obj_value.value)
        
        else:
            raise QubeRuntimeError(f"Cannot call method on {obj_value.type_name}")

    def _evaluate_self_reference(self, node: SelfReference) -> QubeValue:
        """self 키워드 평가"""
        if hasattr(self, 'current_instance') and self.current_instance:
            return QubeValue(self.current_instance, "instance")
        else:
            raise QubeRuntimeError("'self' can only be used inside instance methods")

    def _evaluate_object_literal(self, node: ObjectLiteral) -> QubeValue:
        """객체 리터럴 실행 - 접근 제어 적용"""
        if node.class_name not in self.classes:
            raise QubeRuntimeError(f"Class '{node.class_name}' not found")
        
        class_def = self.classes[node.class_name]
        
        # 필드 값들 평가 (상속된 필드 포함, 접근 제어 확인)
        field_values = {}
        
        # ✅ 모든 필드를 기본값으로 초기화 (private 포함!)
        for field in class_def.all_fields:
            field_name = field[1]  # field[1]이 필드명
            field_access = field[0]  # field[0]이 접근 제어자
            
            # 기본값으로 초기화
            if field[2] == "f64":  # field[2]가 타입
                field_values[field_name] = QubeValue(0.0, "float")
            elif field[2] == "str":
                field_values[field_name] = QubeValue("", "string")
            elif field[2] == "i32":
                field_values[field_name] = QubeValue(0, "int")
            else:
                field_values[field_name] = QubeValue(None, "null")
        
        # 사용자가 명시적으로 제공한 값들로 덮어쓰기
        for field_name, value_expr in node.field_values.items():
            # 필드 찾기 및 접근 권한 확인
            field_exists = False
            field_access_level = "public"
            
            for field in class_def.all_fields:
                if field[1] == field_name:  # field[1]이 field_name
                    field_exists = True
                    field_access_level = field[0]  # field[0]이 access_level
                    break
            
            if not field_exists:
                raise QubeRuntimeError(f"Class '{node.class_name}' has no field '{field_name}'")
            
            # 객체 리터럴에서는 public 필드만 초기화 가능 - PROTECTED 제한 추가!
            if field_access_level in ["private", "protected"]:  # ← protected 추가!
                raise QubeRuntimeError(f"Cannot initialize {field_access_level} field '{field_name}' in object literal")
            
            field_values[field_name] = self._evaluate_expression(value_expr)
        
        # 인스턴스 생성
        instance = QubeInstance(class_def, field_values)
        return QubeValue(instance, "instance")   
    
    def _check_field_access(self, obj, field_name, context="external"):
        """필드 접근 권한 검사 - PROTECTED 지원"""
        if obj.type_name != "instance":
            raise QubeRuntimeError("Cannot access field on non-instance")
        
        instance = obj.value
        class_def = instance.class_def
        
        # 필드 찾기
        field = None
        for f in class_def.all_fields:
            if f[1] == field_name:  # f[1]이 field_name
                field = f
                break
        
        if not field:
            raise QubeRuntimeError(f"Field '{field_name}' not found")
        
        # 접근 권한 검사 - PROTECTED 추가!
        access_level = field[0]  # f[0]이 access_level
        
        if access_level == "private" and context != "internal":
            raise QubeRuntimeError(f"Cannot access private field '{field_name}' from outside class")
        elif access_level == "protected" and context not in ["internal", "inherited"]: 
            raise QubeRuntimeError(f"Cannot access protected field '{field_name}' from outside class hierarchy")
        
        return field

    def _check_method_access(self, obj, method_name, context="external"):
        """메서드 접근 권한 검사 - PROTECTED 지원"""
        class_def = None
        
        if obj.type_name == "class":
            class_def = obj.value
        elif obj.type_name == "instance":
            class_def = obj.value.class_def
        else:
            raise QubeRuntimeError("Cannot call method on non-object")
        
        if method_name not in class_def.all_methods:
            raise QubeRuntimeError(f"Method '{method_name}' not found")
        
        method = class_def.all_methods[method_name]
        
        # 접근 권한 검사 - PROTECTED 추가!
        if method.access_level == "private" and context != "internal":
            raise QubeRuntimeError(f"Cannot access private method '{method_name}' from outside class")
        elif method.access_level == "protected" and context not in ["internal", "inherited"]: 
            raise QubeRuntimeError(f"Cannot access protected method '{method_name}' from outside class hierarchy")
        
        return method

    def _get_access_context(self):
        """현재 접근 컨텍스트 판단 (internal/inherited/external) - PROTECTED 지원"""
        # 현재 메서드 실행 중인지 확인
        if hasattr(self, 'current_instance') and self.current_instance:
            return "internal"
        # TODO: 상속 관계에서의 접근인지 확인하는 로직 추가
        # (현재는 간단히 internal만 구분, 추후 상속 계층 확인 로직 필요)
        return "external"
    
    def _create_class_instance(self, class_name: str, args: list = None):
        """클래스 인스턴스 생성 - 생성자 자동 호출"""
        if class_name not in self.classes:
            raise QubeRuntimeError(f"Class '{class_name}' not found")
        
        class_obj = self.classes[class_name]
        args = args or []
        
        # 인스턴스 생성 (기본값으로 필드 초기화)
        field_values = {}
        for field in class_obj.all_fields:
            field_name = field[1]  # field[1]이 필드명
            field_type = field[2]  # field[2]가 타입
            
            # 타입별 기본값 설정
            if field_type == "str":
                field_values[field_name] = QubeValue("", "string")
            elif field_type == "i32":
                field_values[field_name] = QubeValue(0, "int")
            elif field_type == "f64":
                field_values[field_name] = QubeValue(0.0, "float")
            elif field_type == "bool":
                field_values[field_name] = QubeValue(False, "bool")
            else:
                field_values[field_name] = QubeValue(None, "null")
        
        instance = QubeInstance(class_obj, field_values)
        
        # 적절한 생성자 찾기 (매개변수 개수로 구분)
        matching_constructor = None
        for constructor in class_obj.constructors:
            if len(constructor.params) == len(args):
                matching_constructor = constructor
                break
        
        # 생성자 실행
        if matching_constructor:
            # 새로운 스코프 생성
            old_vars = self.variables.copy()
            old_current_instance = getattr(self, 'current_instance', None)
            
            try:
                # self 바인딩
                self.variables['self'] = QubeValue(instance, "instance")
                self.current_instance = instance
                
                # 매개변수 바인딩
                for i, (param_name, param_type) in enumerate(matching_constructor.params):
                    if i < len(args):
                        self.variables[param_name] = args[i]
                
                # 생성자 본문 실행
                for stmt in matching_constructor.body:
                    self._execute_statement(stmt)
                    
            except ReturnException:
                pass  # 생성자에서 return은 무시
            finally:
                # 스코프 정리
                self.variables = old_vars
                if old_current_instance is not None:
                    self.current_instance = old_current_instance
                elif hasattr(self, 'current_instance'):
                    delattr(self, 'current_instance')
                    
        elif class_obj.constructors:
            # 생성자가 있는데 매개변수가 맞지 않음
            raise QubeRuntimeError(f"No matching constructor for {len(args)} arguments")
        
        return QubeValue(instance, "instance")
    
    def _execute_import_statement(self, node: ImportStatement):
        """import 문 처리"""
        module_symbols = self._load_module(node.module_name)
        
        if "*" in node.imports:
            # import * 의 경우 모든 export된 심볼 가져오기
            if node.alias:
                # import * from "math" as math
                self.variables[node.alias] = QubeValue(module_symbols, "module")
            else:
                # import * from "math" 
                for symbol_name, symbol_value in module_symbols.items():
                    self.variables[symbol_name] = symbol_value
                    # 함수인 경우 functions에도 추가
                    if symbol_value.type_name == "function":
                        self.functions[symbol_name] = symbol_value.value
                    # 🆕 클래스인 경우 classes에도 추가
                    elif symbol_value.type_name == "class":
                        self.classes[symbol_name] = symbol_value.value
        else:
            # 특정 심볼들만 가져오기
            for symbol_name in node.imports:
                if symbol_name in module_symbols:
                    symbol_value = module_symbols[symbol_name]
                    
                    if node.alias:
                        # import { add } from "math" as m
                        if node.alias not in self.variables:
                            self.variables[node.alias] = QubeValue({}, "module")
                        module_dict = self.variables[node.alias].value
                        module_dict[symbol_name] = symbol_value
                    else:
                        # import { add } from "math"
                        self.variables[symbol_name] = symbol_value
                        # 🔥 중요: 함수인 경우 functions에도 추가!
                        if symbol_value.type_name == "function":
                            self.functions[symbol_name] = symbol_value.value
                        # 🆕 클래스인 경우 classes에도 추가!
                        elif symbol_value.type_name == "class":
                            self.classes[symbol_name] = symbol_value.value
                else:
                    raise QubeRuntimeError(f"Symbol '{symbol_name}' not exported from module '{node.module_name}'")

    def _execute_export_statement(self, node: ExportStatement):
        """export 문 처리"""
        # 먼저 선언문을 실행
        result = self._execute_statement(node.declaration)
        
        # 함수나 클래스인 경우 export 목록에 추가
        if isinstance(node.declaration, FunctionDef):
            func_name = node.declaration.name
            if func_name in self.functions:
                self.exported_symbols[func_name] = QubeValue(self.functions[func_name], "function")
            elif func_name in self.variables:
                self.exported_symbols[func_name] = self.variables[func_name]
                
        elif isinstance(node.declaration, ClassDef):
            class_name = node.declaration.name
            if class_name in self.classes:
                self.exported_symbols[class_name] = QubeValue(self.classes[class_name], "class")
            elif class_name in self.variables:
                self.exported_symbols[class_name] = self.variables[class_name]
                
        elif isinstance(node.declaration, VarDecl):
            var_name = node.declaration.name
            if var_name in self.variables:
                self.exported_symbols[var_name] = self.variables[var_name]
        
        return result
    
    def _load_module(self, module_name: str) -> dict:
        """모듈 로드 및 캐싱"""
        if module_name in self.module_cache:
            return self.module_cache[module_name]
        
        # 모듈 파일 찾기
        module_path = self._resolve_module_path(module_name)
        
        if not module_path:
            raise QubeRuntimeError(f"Module '{module_name}' not found")
        
        # 모듈 파일 읽기 및 파싱
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                module_code = f.read()
        except Exception as e:
            raise QubeRuntimeError(f"Failed to read module '{module_name}': {e}")
        
        # 모듈 코드 실행
        lexer = QubeLexer(module_code)
        tokens = lexer.tokenize()
        parser = QubeParser(tokens)
        ast = parser.parse()
        
        # 새로운 인터프리터 인스턴스로 모듈 실행
        module_interpreter = QubeInterpreter()
        module_interpreter.current_module_path = module_path
        module_interpreter._execute_program(ast)
        
        # export된 심볼들만 캐시에 저장
        exported_dict = {}
        for symbol_name, symbol_value in module_interpreter.exported_symbols.items():
            exported_dict[symbol_name] = symbol_value
        
        self.module_cache[module_name] = exported_dict
        return exported_dict

    def _resolve_module_path(self, module_name: str) -> str:
        """모듈 경로 해결"""
        import os
        
        # 현재 파일과 같은 디렉토리에서 찾기
        if self.current_module_path:
            current_dir = os.path.dirname(self.current_module_path)
            module_path = os.path.join(current_dir, f"{module_name}.qyt")
            if os.path.exists(module_path):
                return module_path
        
        # 현재 작업 디렉토리에서 찾기
        module_path = f"{module_name}.qyt"
        if os.path.exists(module_path):
            return module_path
        
        # examples 디렉토리에서 찾기 (테스트용)
        module_path = f"examples/{module_name}.qyt"
        if os.path.exists(module_path):
            return module_path
        
        return None
    
    def _execute_individual_qubit_measurement(self, node: MeasureStatement):
        """개별 큐빗 측정 (기존 로직)"""
        if not hasattr(node, 'qubit') or not node.qubit:
            raise QubeRuntimeError("No qubit specified for measurement")
            
        qubit_value = self._evaluate_expression(node.qubit)
        
        if qubit_value.type_name != "quantum_state":
            raise TypeError("Can only measure quantum states")
        
        result = qubit_value.value.measure()
        
        # 결과에 따른 분기 처리
        if hasattr(node, 'branches') and node.branches:
            for result_pattern, body in node.branches:
                pattern_value = self._evaluate_expression(result_pattern)
                
                if (pattern_value.type_name == "int" and pattern_value.value == result) or \
                (isinstance(pattern_value, Identifier) and pattern_value.name == "_"):
                    for stmt in body:
                        stmt_result = self._execute_statement(stmt)
                        if stmt_result is not None:
                            return stmt_result
                    break
        
        return QubeValue(result, "bit")

    def _measure_circuit_qubit(self, circuit, qubit_index: int) -> int:
        """회로 내 특정 큐빗 측정 - 정리 버전"""
        # 상태 벡터 가져오기
        state_vector = circuit.circuit_state.state_vector
        
        # |0⟩ 확률 계산
        prob_0 = 0.0
        for i in range(len(state_vector)):
            if (i >> qubit_index) & 1 == 0:
                prob_0 += abs(state_vector[i])**2
        
        # 확률적 측정
        import random
        result = 0 if random.random() < prob_0 else 1
        
        # 상태 붕괴
        self._collapse_circuit_state(circuit, qubit_index, result)
        
        return result

    def _collapse_circuit_state(self, circuit, qubit_index: int, result: int):
        """측정 후 상태 붕괴 - 실제 구현"""
        import numpy as np
        
        state_vector = circuit.circuit_state.state_vector
        n_qubits = circuit.n_qubits
        
        # 새로운 상태 벡터 생성
        new_state = np.zeros_like(state_vector)
        
        # 측정 결과에 해당하는 진폭들만 유지
        norm = 0.0
        for i in range(len(state_vector)):
            # i의 이진 표현에서 qubit_index 번째 비트 확인
            bit_value = (i >> qubit_index) & 1
            
            if bit_value == result:
                new_state[i] = state_vector[i]
                norm += abs(state_vector[i])**2
        
        # 정규화
        if norm > 1e-10:  # 0이 아닌 경우만
            new_state = new_state / np.sqrt(norm)
        else:
            # 불가능한 측정 결과인 경우 (이론적으로는 발생하지 않아야 함)
            print(f"경고: 측정 결과 {result}의 확률이 0에 가까움")
            new_state[0] = 1.0  # |000...⟩ 상태로 리셋
        
        # 회로 상태 업데이트
        circuit.circuit_state.state_vector = new_state
        
        print(f"측정: q{qubit_index} = {result}, 상태 붕괴 완료")
        
        # 디버그 정보 (선택사항)
        if hasattr(self, 'debug_mode') and self.debug_mode:
            print(f"새로운 상태 벡터: {new_state[:8]}...")  # 처음 8개 진폭만 표시

    def _validate_and_apply_gate(self, circuit, gate_name: str, targets: list, params: list):
        """게이트 검증 및 적용"""
        
        # 매개변수 개수 검증
        if gate_name in ["RX", "RY", "RZ"]:
            if len(params) != 1:
                raise QubeQuantumError(f"{gate_name} 게이트는 정확히 1개의 각도 매개변수가 필요합니다")
        elif gate_name in ["H", "X", "Y", "Z", "S", "T"]:
            if len(params) != 0:
                raise QubeQuantumError(f"{gate_name} 게이트는 매개변수가 필요하지 않습니다")
        
        # 큐빗 개수 검증
        if gate_name in ["CNOT", "CZ"]:
            if len(targets) != 2:
                raise QubeQuantumError(f"{gate_name} 게이트는 정확히 2개의 큐빗이 필요합니다")
            if targets[0] == targets[1]:
                raise QubeQuantumError(f"{gate_name} 게이트의 제어 큐빗과 타겟 큐빗은 달라야 합니다")
        else:
            if len(targets) != 1:
                raise QubeQuantumError(f"{gate_name} 게이트는 정확히 1개의 큐빗이 필요합니다")
        
        # 게이트 적용
        if gate_name == "H":
            circuit.h(targets[0])
        elif gate_name == "X":
            circuit.x(targets[0])
        elif gate_name == "Y":
            circuit.y(targets[0])
        elif gate_name == "Z":
            circuit.z(targets[0])
        elif gate_name == "S":
            circuit.s(targets[0])
        elif gate_name == "T":
            circuit.t(targets[0])
        elif gate_name == "RX":
            circuit.rx(params[0], targets[0])
        elif gate_name == "RY":
            circuit.ry(params[0], targets[0])
        elif gate_name == "RZ":
            circuit.rz(params[0], targets[0])
        elif gate_name == "CNOT":
            circuit.cnot(targets[0], targets[1])
        elif gate_name == "CZ":
            circuit.cz(targets[0], targets[1])
        else:
            raise QubeQuantumError(f"지원하지 않는 게이트: {gate_name}")        
        
    def _debug_variable_state(self, var_name: str = None):
        """변수 상태 디버깅"""
        if var_name:
            if var_name in self.variables:
                var = self.variables[var_name]
                print(f"DEBUG: {var_name} = {var.value} (type: {var.type_name})")
            else:
                print(f"DEBUG: {var_name} not found")
        else:
            print("DEBUG: All variables:")
            for name, var in self.variables.items():
                print(f"  {name} = {var.value} (type: {var.type_name})")


    def _measure_all_qubits_simultaneously(self, circuit, qubit_indices):
        """모든 큐빗을 동시에 측정하여 상태 붕괴 방지 - 비트 순서 수정"""
        state_vector = circuit.circuit_state.state_vector
        n_qubits = circuit.n_qubits
        
        # 🔍 디버깅: 상태 벡터와 확률 출력
        probabilities = [abs(amp)**2 for amp in state_vector]
        
        print(f"DEBUG: 상태 벡터 확률:")
        for i, prob in enumerate(probabilities):
            if prob > 1e-10:  # 0이 아닌 확률만 출력
                binary = format(i, f'0{n_qubits}b')
                print(f"  |{binary}⟩: {prob:.4f} ({prob*100:.1f}%)")
        
        # 확률에 따라 하나의 기저 상태 선택
        import random
        rand_val = random.random()
        print(f"DEBUG: 랜덤값 = {rand_val:.4f}")
        
        cumulative_prob = 0.0
        
        for i, prob in enumerate(probabilities):
            cumulative_prob += prob
            if rand_val < cumulative_prob:
                # i번째 기저 상태가 측정됨
                binary_result = format(i, f'0{n_qubits}b')
                print(f"DEBUG: 선택된 상태 = |{binary_result}⟩ (인덱스 {i})")
                
                # 🔧 비트 순서 수정: 뒤에서부터 읽기 (LSB first)
                results = []
                for idx in qubit_indices:
                    # 비트 순서를 뒤집어서 접근
                    reversed_idx = n_qubits - 1 - idx
                    results.append(int(binary_result[reversed_idx]))
                
                print(f"DEBUG: 수정된 반환 결과 = {results}")
                return results
        
        # 안전장치 (확률 합이 1이 아닌 경우)
        print("DEBUG: 안전장치 발동 - 모든 0 반환")
        return [0] * len(qubit_indices)
    
    def _resolve_range_expression(self, range_expr, n_qubits: int):
        """범위 표현식을 큐빗 인덱스 리스트로 변환"""
        
        if range_expr.range_type == "all_to_target":
            # (~, q5) - 모든 큐빗을 q5에 제어
            target_idx = self._evaluate_qubit_reference(range_expr.target)
            all_qubits = list(range(n_qubits))
            # 타겟을 제외한 모든 큐빗 + 타겟 (CZ 게이트 순서: 제어들, 타겟)
            controls = [q for q in all_qubits if q != target_idx]
            return controls + [target_idx]
        
        elif range_expr.range_type == "source_to_all":
            # (q0, ~) - q0을 모든 다른 큐빗들에 제어
            source_idx = self._evaluate_qubit_reference(range_expr.start)
            all_qubits = list(range(n_qubits))
            # 소스를 제외한 모든 큐빗들 + 소스 (마지막에 소스)
            others = [q for q in all_qubits if q != source_idx]
            return others + [source_idx]
        
        elif range_expr.range_type == "range":
            # (q0:q4) - q0부터 q4까지
            start_idx = self._evaluate_qubit_reference(range_expr.start)
            end_idx = self._evaluate_qubit_reference(range_expr.end)
            return list(range(start_idx, end_idx + 1))
        
        else:
            raise QubeQuantumError(f"알 수 없는 범위 표현식: {range_expr.range_type}")

    def _apply_gate_with_range_support(self, circuit, gate_name: str, target_indices: list, parameters: list):
        """범위 문법을 지원하는 게이트 적용"""
        
        if gate_name in ['H', 'X', 'Y', 'Z', 'S', 'T']:
            # 단일 큐빗 게이트 - 모든 타겟에 개별 적용
            for qubit_idx in target_indices:
                if gate_name == "H":
                    circuit.h(qubit_idx)
                elif gate_name == "X":
                    circuit.x(qubit_idx)
                elif gate_name == "Y":
                    circuit.y(qubit_idx)
                elif gate_name == "Z":
                    circuit.z(qubit_idx)
                elif gate_name == "S":
                    circuit.s(qubit_idx)
                elif gate_name == "T":
                    circuit.t(qubit_idx)
                print(f"DEBUG: {gate_name} 게이트 적용됨 - 큐빗 [{qubit_idx}]")
        
        elif gate_name == 'CZ':
            # 다중 제어 CZ 게이트
            if len(target_indices) < 2:
                raise QubeQuantumError("CZ 게이트는 최소 2개 큐빗이 필요합니다")
            elif len(target_indices) == 2:
                circuit.cz(target_indices[0], target_indices[1])
            elif len(target_indices) == 3:
                circuit.ccz(target_indices[0], target_indices[1], target_indices[2])
            elif len(target_indices) == 4:
                circuit.cccz(target_indices[0], target_indices[1], target_indices[2], target_indices[3])
            else:
                # 5큐빗 이상은 범용 구현 사용
                circuit.controlled_z_n(*target_indices)
            print(f"DEBUG: CZ 게이트 적용됨 - 큐빗 {target_indices}")
        
        elif gate_name == 'CNOT':
            # CNOT: 마지막이 타겟, 나머지가 제어
            if len(target_indices) >= 2:
                control = target_indices[0]
                target = target_indices[1]
                circuit.cnot(control, target)
                print(f"DEBUG: CNOT 게이트 적용됨 - 제어: {control}, 타겟: {target}")
            else:
                raise QubeQuantumError("CNOT 게이트는 최소 2개 큐빗이 필요합니다")
        
        elif gate_name in ['RX', 'RY', 'RZ']:
            # 회전 게이트 - 매개변수 필요
            if len(parameters) != 1:
                raise QubeQuantumError(f"{gate_name} 게이트는 1개의 각도 매개변수가 필요합니다")
            
            angle = parameters[0]
            for qubit_idx in target_indices:
                if gate_name == "RX":
                    circuit.rx(angle, qubit_idx)
                elif gate_name == "RY":
                    circuit.ry(angle, qubit_idx)
                elif gate_name == "RZ":
                    circuit.rz(angle, qubit_idx)
                print(f"DEBUG: {gate_name}({angle}) 게이트 적용됨 - 큐빗 [{qubit_idx}]")
        
        else:
            raise QubeQuantumError(f"지원하지 않는 게이트: {gate_name}")