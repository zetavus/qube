from typing import List, Any, Optional, Union
from .lexer import Token, TokenType

class ASTNode:
    pass

class AllQubitsReference(ASTNode):
    """모든 큐빗 참조: ~ 또는 all"""
    def __init__(self):
        pass

class RangeExpression(ASTNode):
    """범위 표현식: (~, q5), (q0, ~), (q0:q4)"""
    def __init__(self, range_type: str, start=None, end=None, target=None):
        self.range_type = range_type  # 'all_to_target', 'source_to_all', 'range'
        self.start = start            # 시작 큐빗 (있는 경우)
        self.end = end               # 끝 큐빗 (있는 경우)  
        self.target = target         # 타겟 큐빗 (있는 경우)

class Program(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements

# 🆕 양자 회로 관련 AST 노드들
class CircuitDefinition(ASTNode):
    """circuit 정의: circuit Bell(2) { ... }"""
    def __init__(self, name: str, n_qubits: int, body: List[ASTNode]):
        self.name = name
        self.n_qubits = n_qubits
        self.body = body

class CircuitInstantiation(ASTNode):
    """회로 인스턴스화: circuit = Bell(2)"""
    def __init__(self, name: str, args: List[ASTNode]):
        self.name = name
        self.args = args

class GateOperation(ASTNode):
    """게이트 연산: H(q0), CNOT(q0, q1), RX(π/2, q0)"""
    def __init__(self, gate_name: str, args: List[ASTNode]):
        self.gate_name = gate_name
        self.args = args

class ApplyStatement(ASTNode):
    """apply 문: apply H to q0; apply CNOT to (q0, q1)"""
    def __init__(self, gate_name: str, targets: List[ASTNode], parameters: List[ASTNode] = None):
        self.gate_name = gate_name
        self.targets = targets
        self.parameters = parameters or []

class MeasureStatement(ASTNode):
    """measure 문: measure q0 -> bit0; measure all -> results"""
    def __init__(self, qubits: List[ASTNode], result_var: Optional[str] = None):
        self.qubits = qubits
        self.result_var = result_var

class ResetStatement(ASTNode):
    """reset 문: reset q0; reset all"""
    def __init__(self, qubits: List[ASTNode]):
        self.qubits = qubits

class BarrierStatement(ASTNode):
    """barrier 문: barrier q0, q1; barrier all"""
    def __init__(self, qubits: List[ASTNode]):
        self.qubits = qubits

class CircuitCall(ASTNode):
    """회로 호출: mycircuit.run(), mycircuit.draw()"""
    def __init__(self, circuit_expr: ASTNode, method_name: str, args: List[ASTNode] = None):
        self.circuit_expr = circuit_expr
        self.method_name = method_name
        self.args = args or []

class QubitReference(ASTNode):
    """큐빗 참조: q0, q[i], qubits[0:2]"""
    def __init__(self, name: str, index: Optional[ASTNode] = None, slice_end: Optional[ASTNode] = None):
        self.name = name
        self.index = index
        self.slice_end = slice_end

# 기존 AST 노드들...
class FunctionDef(ASTNode):
    def __init__(self, access_level: str, name: str, params: List[tuple], return_type: Optional[str], body: List[ASTNode]):
        self.access_level = access_level  
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body

class VarDecl(ASTNode):
    def __init__(self, var_type: str, name: str, value: Optional[ASTNode], is_mutable: bool = False):
        self.var_type = var_type
        self.name = name
        self.value = value
        self.is_mutable = is_mutable

class Assignment(ASTNode):
    def __init__(self, target: ASTNode, value: ASTNode, operator: str = "="):
        self.target = target
        self.value = value
        self.operator = operator

class ConstructorDef(ASTNode):
    def __init__(self, params: List[tuple], body: List[ASTNode]):
        self.params = params
        self.body = body

class DestructorDef(ASTNode):
    def __init__(self, body: List[ASTNode]):
        self.body = body

class ImportStatement(ASTNode):
    def __init__(self, imports: List[str], module_name: str, alias: Optional[str] = None):
        self.imports = imports      
        self.module_name = module_name  
        self.alias = alias         

class ExportStatement(ASTNode):
    def __init__(self, declaration: ASTNode):
        self.declaration = declaration  

class BinaryOp(ASTNode):
    def __init__(self, left: ASTNode, operator: str, right: ASTNode):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryOp(ASTNode):
    def __init__(self, operator: str, operand: ASTNode):
        self.operator = operator
        self.operand = operand

class FunctionCall(ASTNode):
    def __init__(self, name: str, args: List[ASTNode]):
        self.name = name
        self.args = args

class Literal(ASTNode):
    def __init__(self, value: Any, type_name: str):
        self.value = value
        self.type_name = type_name

class Identifier(ASTNode):
    def __init__(self, name: str):
        self.name = name

class ArrayLiteral(ASTNode):
    def __init__(self, elements: List[ASTNode]):
        self.elements = elements

class ArrayAccess(ASTNode):
    def __init__(self, array: ASTNode, index: ASTNode):
        self.array = array
        self.index = index

class IfStatement(ASTNode):
    def __init__(self, condition: ASTNode, then_body: List[ASTNode], else_body: Optional[List[ASTNode]] = None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

class WhileLoop(ASTNode):
    def __init__(self, condition: ASTNode, body: List[ASTNode]):
        self.condition = condition
        self.body = body

class ForLoop(ASTNode):
    def __init__(self, variable: str, iterable: ASTNode, body: List[ASTNode]):
        self.variable = variable
        self.iterable = iterable
        self.body = body

class Range(ASTNode):
    def __init__(self, start: ASTNode, end: ASTNode, inclusive: bool = False):
        self.start = start
        self.end = end
        self.inclusive = inclusive

class MatchStatement(ASTNode):
    def __init__(self, expr: ASTNode, arms: List[tuple]):
        self.expr = expr
        self.arms = arms  

class BreakStatement(ASTNode):
    def __init__(self, label: Optional[str] = None):
        self.label = label

class ContinueStatement(ASTNode):
    def __init__(self, label: Optional[str] = None):
        self.label = label

class ReturnStatement(ASTNode):
    def __init__(self, value: Optional[ASTNode] = None):
        self.value = value

class LoopStatement(ASTNode):
    def __init__(self, body: List[ASTNode], label: Optional[str] = None):
        self.body = body
        self.label = label

class QuantumIfStatement(ASTNode):
    def __init__(self, condition: ASTNode, then_body: List[ASTNode], else_body: Optional[List[ASTNode]] = None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

class SuperposeStatement(ASTNode):
    def __init__(self, branches: List[tuple], target: ASTNode):
        self.branches = branches  
        self.target = target

class LambdaFunction(ASTNode):
    def __init__(self, params: List[str], body: ASTNode):
        self.params = params
        self.body = body

class ClosureCapture(ASTNode):
    def __init__(self, variables: List[str], function: ASTNode):
        self.variables = variables
        self.function = function

class OracleFunction(ASTNode):
    def __init__(self, access_level: str, name: str, params: List[tuple], body: List[ASTNode]):
        self.access_level = access_level  
        self.name = name
        self.params = params
        self.body = body
        self.function_type = "oracle"

class ReversibleFunction(ASTNode):
    def __init__(self, access_level: str, name: str, params: List[tuple], return_type: str, body: List[ASTNode]):
        self.access_level = access_level  
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
        self.function_type = "reversible"

class UnitaryFunction(ASTNode):
    def __init__(self, access_level: str, name: str, params: List[tuple], return_type: str, body: List[ASTNode]):
        self.access_level = access_level  
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
        self.function_type = "unitary"     

class ArrowFunction(ASTNode):
    def __init__(self, parameters, body):
        self.parameters = parameters  
        self.body = body             

class PipeExpression(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left    
        self.right = right      

class MemberAccess(ASTNode):
    def __init__(self, object_expr: ASTNode, member_name: str):
        self.object_expr = object_expr  
        self.member_name = member_name        

class TryStatement(ASTNode):
    def __init__(self, try_block: List[ASTNode], catch_clauses: List['CatchClause'], finally_block: Optional[List[ASTNode]] = None):
        self.try_block = try_block
        self.catch_clauses = catch_clauses
        self.finally_block = finally_block

class CatchClause(ASTNode):
    def __init__(self, exception_type: Optional[str], exception_var: str, body: List[ASTNode]):
        self.exception_type = exception_type  
        self.exception_var = exception_var     
        self.body = body

class ThrowStatement(ASTNode):
    def __init__(self, exception: ASTNode):
        self.exception = exception       

class ClassDef(ASTNode):
    def __init__(self, name: str, parent_class: str, fields: List[tuple], methods: List[ASTNode], 
                 constructors: List[ConstructorDef] = None, destructor: DestructorDef = None):
        self.name = name                                    
        self.parent_class = parent_class                   
        self.fields = fields                               
        self.methods = methods                             
        self.constructors = constructors or []             
        self.destructor = destructor                       

class FieldDecl(ASTNode):
    def __init__(self, access_level: str, name: str, field_type: str):
        self.access_level = access_level  
        self.name = name
        self.field_type = field_type

class MethodCall(ASTNode):
    def __init__(self, object_expr: ASTNode, method_name: str, args: List[ASTNode]):
        self.object_expr = object_expr
        self.method_name = method_name
        self.args = args

class ObjectCreation(ASTNode):
    def __init__(self, class_name: str, field_values: dict):
        self.class_name = class_name
        self.field_values = field_values  

class SelfReference(ASTNode):
    def __init__(self):
        pass               

class ObjectLiteral(ASTNode):
    def __init__(self, class_name: str, field_values: dict):
        self.class_name = class_name
        self.field_values = field_values  

class QubeParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self) -> Program:
        
        statements = []
        while not self._is_at_end():
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
            
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)
    
    def _parse_statement(self) -> Optional[ASTNode]:
        token = self._current_token()
        
        
        # 🆕 회로 관련 키워드 처리 추가
        if token.type == TokenType.CIRCUIT:
            return self._parse_circuit_definition()
        elif token.type == TokenType.APPLY:
            return self._parse_apply_statement()
        elif token.type == TokenType.MEASURE:
            return self._parse_measure_statement()
        elif token.type == TokenType.RESET:
            return self._parse_reset_statement()
        elif token.type == TokenType.BARRIER:
            return self._parse_barrier_statement()
        elif token.type == TokenType.FN:
            return self._parse_function()
        elif token.type in [TokenType.SCALAR, TokenType.QUBIT, TokenType.BIT, TokenType.CONST, TokenType.MUT]:
            return self._parse_variable_declaration()
        elif token.type == TokenType.IF:
            return self._parse_if_statement()
        elif token.type == TokenType.WHILE:
            return self._parse_while_loop()
        elif token.type == TokenType.FOR:
            return self._parse_for_loop()
        elif token.type == TokenType.LOOP:
            return self._parse_loop_statement()
        elif token.type == TokenType.MATCH:
            return self._parse_match_statement()
        elif token.type == TokenType.BREAK:
            return self._parse_break_statement()
        elif token.type == TokenType.CONTINUE:
            return self._parse_continue_statement()
        elif token.type == TokenType.RETURN:
            return self._parse_return_statement()
        elif token.type == TokenType.IMPORT:
            return self._parse_import_statement()
        elif token.type == TokenType.EXPORT:
            return self._parse_export_statement()
        elif token.type == TokenType.TRY:
            return self._parse_try_statement()
        elif token.type == TokenType.THROW:
            return self._parse_throw_statement()
        elif token.value == "quantum" and self._peek_token().type == TokenType.IF:
            return self._parse_quantum_if_statement()
        elif token.value == "superpose":
            return self._parse_superpose_statement()
        elif token.type == TokenType.IDENTIFIER:
            result = self._parse_assignment_or_call()
            return result
        elif token.type == TokenType.SELF:  
            result = self._parse_assignment_or_call()
            return result
        elif token.type == TokenType.CLASS:
            return self._parse_class()
        else:
            self._advance()
            return None

    # 🆕 회로 관련 파싱 메서드들
    def _parse_circuit_definition(self) -> CircuitDefinition:
        """circuit 정의 파싱: circuit Bell(2) { H(q0); CNOT(q0, q1); }"""
        self._advance()  # Skip 'circuit'
        
        # 회로 이름
        circuit_name = self._current_token().value
        self._advance()
        
        # 매개변수 (큐빗 개수)
        self._expect(TokenType.LPAREN)
        n_qubits = int(self._current_token().value)
        self._advance()
        self._expect(TokenType.RPAREN)
        
        # 회로 본문
        self._expect(TokenType.LBRACE)
        body = []
        
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
            stmt = self._parse_statement()
            if stmt:
                body.append(stmt)
        
        self._expect(TokenType.RBRACE)
        return CircuitDefinition(circuit_name, n_qubits, body)
    
    def _parse_apply_statement(self) -> ApplyStatement:
        """apply 문 파싱: 범위 문법 지원
        - apply H to q0; 
        - apply RX(π/2) to q1; 
        - apply CNOT to (q0, q1)
        - apply CZ to (~, q5);      # 새로운: 모든 큐빗 → q5 제어
        - apply H to (~);           # 새로운: 모든 큐빗에 적용
        - apply CZ to (q0, ~);      # 새로운: q0 → 모든 큐빗 제어
        - apply X to (q0:q4);       # 새로운: 범위 적용
        """
        self._advance()  # Skip 'apply'
        
        # 게이트 이름과 매개변수 파싱
        gate_name = self._current_token().value
        self._advance()
        
        parameters = []
        if self._current_token().type == TokenType.LPAREN:
            self._advance()  # Skip '('
            while self._current_token().type != TokenType.RPAREN:
                parameters.append(self._parse_expression())
                if self._current_token().type == TokenType.COMMA:
                    self._advance()
            self._expect(TokenType.RPAREN)
        
        # 'to' 키워드
        self._expect_keyword("to")
        
        # 타겟 파싱 - 범위 문법 지원
        targets = []
        
        if self._current_token().type == TokenType.LPAREN:
            # 괄호 내 표현식: (q0, q1), (~, q5), (q0, ~), (q0:q4)
            self._advance()  # Skip '('
            
            # 범위 표현식 파싱
            range_expr = self._parse_range_expression()
            targets.append(range_expr)
            
            self._expect(TokenType.RPAREN)
        
        elif self._current_token().type == TokenType.BITWISE_NOT:
            # 단독 ~ : apply H to ~;
            self._advance()  # Skip '~'
            targets.append(AllQubitsReference())
        
        else:
            # 단일 큐빗: apply H to q0;
            targets.append(self._parse_qubit_reference())
        
        if self._current_token().type == TokenType.SEMICOLON:
            self._advance()
        
        return ApplyStatement(gate_name, targets, parameters)
    
    def _parse_measure_statement(self) -> MeasureStatement:
        """measure 문 파싱: measure q0; measure q0 -> result; measure all"""
        self._advance()  # Skip 'measure'
        
        qubits = []
        
        if self._current_token().value == "all":
            # measure all
            self._advance()
            qubits.append(Identifier("all"))
        else:
            # 특정 큐빗들
            qubits.append(self._parse_qubit_reference())
            
            while self._current_token().type == TokenType.COMMA:
                self._advance()
                qubits.append(self._parse_qubit_reference())
        
        # 결과 변수 (선택적)
        result_var = None
        if self._current_token().type == TokenType.ARROW:
            self._advance()
            result_var = self._current_token().value
            self._advance()
        
        if self._current_token().type == TokenType.SEMICOLON:
            self._advance()
        
        return MeasureStatement(qubits, result_var)
    
    def _parse_reset_statement(self) -> ResetStatement:
        """reset 문 파싱: reset q0; reset all"""
        self._advance()  # Skip 'reset'
        
        qubits = []
        
        if self._current_token().value == "all":
            self._advance()
            qubits.append(Identifier("all"))
        else:
            qubits.append(self._parse_qubit_reference())
            
            while self._current_token().type == TokenType.COMMA:
                self._advance()
                qubits.append(self._parse_qubit_reference())
        
        if self._current_token().type == TokenType.SEMICOLON:
            self._advance()
        
        return ResetStatement(qubits)
    
    def _parse_barrier_statement(self) -> BarrierStatement:
        """barrier 문 파싱: barrier q0, q1; barrier all"""
        self._advance()  # Skip 'barrier'
        
        qubits = []
        
        if self._current_token().value == "all":
            self._advance()
            qubits.append(Identifier("all"))
        else:
            qubits.append(self._parse_qubit_reference())
            
            while self._current_token().type == TokenType.COMMA:
                self._advance()
                qubits.append(self._parse_qubit_reference())
        
        if self._current_token().type == TokenType.SEMICOLON:
            self._advance()
        
        return BarrierStatement(qubits)
    
    def _parse_qubit_reference(self) -> QubitReference:
        """큐빗 참조 파싱: q0, q[i], qubits[0:2]"""
        name = self._current_token().value
        self._advance()
        
        index = None
        slice_end = None
        
        if self._current_token().type == TokenType.LBRACKET:
            self._advance()
            index = self._parse_expression()
            
            # 슬라이스 확인
            if self._current_token().type == TokenType.COLON:
                self._advance()
                slice_end = self._parse_expression()
            
            self._expect(TokenType.RBRACKET)
        
        return QubitReference(name, index, slice_end)

    # 기존 메서드들... (나머지 구현은 동일)
    def _parse_match_expression(self) -> MatchStatement:
        self._advance()  # Skip 'match'
        
        expr = self._parse_expression()
        self._expect(TokenType.LBRACE)
        
        arms = []
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
                
            pattern = self._parse_pattern()
            
            guard = None
            if self._current_token().value == "if":
                self._advance()
                guard = self._parse_expression()
            
            self._expect(TokenType.FAT_ARROW)
            
            if self._current_token().type == TokenType.LBRACE:
                self._advance()
                body = []
                while self._current_token().type != TokenType.RBRACE:
                    if self._current_token().type == TokenType.NEWLINE:
                        self._advance()
                        continue
                    stmt = self._parse_statement()
                    if stmt:
                        body.append(stmt)
                self._expect(TokenType.RBRACE)
            else:
                body = [self._parse_expression()]
            
            arms.append((pattern, guard, body))
            
            if self._current_token().type == TokenType.COMMA:
                self._advance()
        
        self._expect(TokenType.RBRACE)
        return MatchStatement(expr, arms)

    def _parse_match_statement(self) -> MatchStatement:
        self._advance()  # Skip 'match'
        
        expr = self._parse_expression()
        self._expect(TokenType.LBRACE)
        
        arms = []
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
                
            pattern = self._parse_pattern()
            
            guard = None
            if self._current_token().value == "if":
                self._advance()
                guard = self._parse_expression()
            
            self._expect(TokenType.FAT_ARROW)
            
            if self._current_token().type == TokenType.LBRACE:
                self._advance()
                body = []
                while self._current_token().type != TokenType.RBRACE:
                    if self._current_token().type == TokenType.NEWLINE:
                        self._advance()
                        continue
                    stmt = self._parse_statement()
                    if stmt:
                        body.append(stmt)
                self._expect(TokenType.RBRACE)
            else:
                body = [self._parse_expression()]
            
            arms.append((pattern, guard, body))
            
            if self._current_token().type == TokenType.COMMA:
                self._advance()
        
        self._expect(TokenType.RBRACE)
        return MatchStatement(expr, arms)
    
    def _parse_pattern(self) -> ASTNode:
        token = self._current_token()
        
        if token.type == TokenType.INTEGER:
            self._advance()
            return Literal(int(token.value), "int")
        elif token.type == TokenType.STRING:
            self._advance()
            return Literal(token.value[1:-1], "string")
        elif token.type == TokenType.IDENTIFIER:
            if token.value == "_":
                self._advance()
                return Identifier("_")  
            else:
                self._advance()
                return Identifier(token.value)
        elif token.type == TokenType.QUANTUM_STATE:
            self._advance()
            return Literal(token.value, "quantum_state")
        else:
            return self._parse_expression()
    
    def _parse_loop_statement(self) -> LoopStatement:
        self._advance()  # Skip 'loop'
        
        label = None
        if self._current_token().type == TokenType.IDENTIFIER and self._peek_token().type == TokenType.COLON:
            label = self._current_token().value
            self._advance()
            self._advance()
        
        self._expect(TokenType.LBRACE)
        
        body = []
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
            stmt = self._parse_statement()
            if stmt:
                body.append(stmt)
        
        self._expect(TokenType.RBRACE)
        return LoopStatement(body, label)
    
    def _parse_break_statement(self) -> BreakStatement:
        self._advance()  # Skip 'break'
        
        label = None
        if self._current_token().type == TokenType.IDENTIFIER:
            label = self._current_token().value
            self._advance()
        
        if self._current_token().type == TokenType.SEMICOLON:
            self._advance()
        
        return BreakStatement(label)
    
    def _parse_continue_statement(self) -> ContinueStatement:
        self._advance()  # Skip 'continue'
        
        label = None
        if self._current_token().type == TokenType.IDENTIFIER:
            label = self._current_token().value
            self._advance()
        
        if self._current_token().type == TokenType.SEMICOLON:
            self._advance()
        
        return ContinueStatement(label)
    
    def _parse_return_statement(self) -> ReturnStatement:
        self._advance()  # Skip 'return'
        
        value = None
        if (self._current_token().type != TokenType.SEMICOLON and 
            self._current_token().type != TokenType.NEWLINE):
            value = self._parse_expression()
        
        if self._current_token().type == TokenType.SEMICOLON:
            self._advance()
        
        return ReturnStatement(value)
    
    def _parse_quantum_if_statement(self) -> QuantumIfStatement:
        self._advance()  # Skip 'quantum'
        self._advance()  # Skip 'if'
        
        condition = self._parse_expression()
        self._expect(TokenType.LBRACE)
        
        then_body = []
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
            stmt = self._parse_statement()
            if stmt:
                then_body.append(stmt)
        
        self._expect(TokenType.RBRACE)
        
        else_body = None
        if self._current_token().type == TokenType.ELSE:
            self._advance()
            self._expect(TokenType.LBRACE)
            
            else_body = []
            while self._current_token().type != TokenType.RBRACE:
                if self._current_token().type == TokenType.NEWLINE:
                    self._advance()
                    continue
                stmt = self._parse_statement()
                if stmt:
                    else_body.append(stmt)
            
            self._expect(TokenType.RBRACE)
        
        return QuantumIfStatement(condition, then_body, else_body)
    
    def _parse_superpose_statement(self) -> SuperposeStatement:
        self._advance()  # Skip 'superpose'
        
        self._expect(TokenType.LBRACE)
        
        branches = []
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
            
            if self._current_token().value == "branch":
                self._advance()
            
            pattern = self._parse_expression()
            self._expect(TokenType.COLON)
            
            self._expect(TokenType.LBRACE)
            body = []
            while self._current_token().type != TokenType.RBRACE:
                if self._current_token().type == TokenType.NEWLINE:
                    self._advance()
                    continue
                stmt = self._parse_statement()
                if stmt:
                    body.append(stmt)
            self._expect(TokenType.RBRACE)
            
            branches.append((pattern, body))
            
            if self._current_token().type == TokenType.COMMA:
                self._advance()
        
        self._expect(TokenType.RBRACE)
        
        target = None
        if self._current_token().value == "on":
            self._advance()
            target = self._parse_expression()
        
        return SuperposeStatement(branches, target)
    
    def _peek_token(self) -> Token:
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return self.tokens[-1]  # EOF
    
    # 나머지 기존 메서드들 (간단히 핵심만 포함)
    def _parse_function(self) -> ASTNode:
        
        access_level = "public"
        if self._current_token().type in [TokenType.PRIVATE, TokenType.PUBLIC, TokenType.PROTECTED]:
            access_level = self._current_token().value
            self._advance()
        
        special_type = None
        if self._current_token().value in ["oracle", "reversible", "unitary"]:
            special_type = self._current_token().value
            self._advance()
        
        self._advance()  # Skip 'fn'
        
        name = self._current_token().value
        self._advance()
        
        self._expect(TokenType.LPAREN)
        params = []
        
        while self._current_token().type != TokenType.RPAREN:
            param_name = self._current_token().value
            self._advance()
            
            param_type = None
            if self._current_token().type == TokenType.COLON:
                self._advance()
                param_type = self._current_token().value
                self._advance()
            
            params.append((param_name, param_type))
            
            if self._current_token().type == TokenType.COMMA:
                self._advance()
        
        self._expect(TokenType.RPAREN)
        
        return_type = None
        if self._current_token().type == TokenType.ARROW:
            self._advance()
            return_type = self._current_token().value
            self._advance()
        
        self._expect(TokenType.LBRACE)

        
        body = []
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
            
            stmt = self._parse_statement()
            if stmt:
                body.append(stmt)
        
        self._expect(TokenType.RBRACE)

              
        if special_type == "oracle":
            return OracleFunction(access_level, name, params, body)
        elif special_type == "reversible":
            return ReversibleFunction(access_level, name, params, return_type, body)
        elif special_type == "unitary":
            return UnitaryFunction(access_level, name, params, return_type, body)
        else:
            return FunctionDef(access_level, name, params, return_type, body)

    def _parse_variable_declaration(self) -> VarDecl:
        is_mutable = False
        if self._current_token().type == TokenType.MUT:
            is_mutable = True
            self._advance()
        
        var_type = self._current_token().value
        self._advance()
        
        name = self._current_token().value
        self._advance()
        
        value = None
        if self._current_token().type == TokenType.ASSIGN:
            self._advance()
            value = self._parse_expression()
        
        if self._current_token().type == TokenType.SEMICOLON:
            self._advance()
        
        return VarDecl(var_type, name, value, is_mutable)
    
    def _parse_if_statement(self) -> IfStatement:
        
        self._advance()  # Skip 'if'
        
        condition = self._parse_expression()
        self._expect(TokenType.LBRACE)
        
        then_body = []
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
            stmt = self._parse_statement()
            if stmt:
                then_body.append(stmt)
        
        self._expect(TokenType.RBRACE)
        
        else_body = None
        if self._current_token().type == TokenType.ELSE:
            self._advance()
            self._expect(TokenType.LBRACE)
            
            else_body = []
            while self._current_token().type != TokenType.RBRACE:
                if self._current_token().type == TokenType.NEWLINE:
                    self._advance()
                    continue
                stmt = self._parse_statement()
                if stmt:
                    else_body.append(stmt)
            
            self._expect(TokenType.RBRACE)
        
        return IfStatement(condition, then_body, else_body)
    
    def _parse_while_loop(self) -> WhileLoop:
        self._advance()  # Skip 'while'
        
        condition = self._parse_expression()
        self._expect(TokenType.LBRACE)
        
        body = []
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
            stmt = self._parse_statement()
            if stmt:
                body.append(stmt)
        
        self._expect(TokenType.RBRACE)
        return WhileLoop(condition, body)
    
    def _parse_for_loop(self) -> ForLoop:
        
        self._advance()  # Skip 'for'
        
        variable = self._current_token().value
        
        self._advance()
        
        self._expect_keyword("in")
        
        
        iterable = self._parse_expression()
        
        if self._current_token().type in [TokenType.RANGE, TokenType.RANGE_INCLUSIVE]:
            inclusive = (self._current_token().type == TokenType.RANGE_INCLUSIVE)
            
            self._advance()
            
            end = self._parse_expression() 
            
            iterable = Range(iterable, end, inclusive)
        
        
        self._expect(TokenType.LBRACE)
        
        body = []
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
            
            
            stmt = self._parse_statement() 
            if stmt:
                body.append(stmt)
        
        
        self._expect(TokenType.RBRACE)
        return ForLoop(variable, iterable, body)
    
    def _parse_assignment_or_call(self) -> ASTNode:
        if self._current_token().type == TokenType.SELF:
            name = "self"  
        else:
            name = self._current_token().value
        
        self._advance()
            
        if self._current_token().type in [TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN, 
                                        TokenType.MULT_ASSIGN, TokenType.DIV_ASSIGN, TokenType.TENSOR_ASSIGN]:
            op = self._current_token().value
            self._advance()
            value = self._parse_expression()
            if self._current_token().type == TokenType.SEMICOLON:
                self._advance()
            result = Assignment(Identifier(name), value, op)
            return result
        elif self._current_token().type == TokenType.LPAREN:
            return self._parse_function_call(name)
        elif self._current_token().type == TokenType.LBRACKET:
            self._advance()
            index = self._parse_expression()
            self._expect(TokenType.RBRACKET)
            return ArrayAccess(Identifier(name), index)
        elif self._current_token().type == TokenType.DOT: 
            left = Identifier(name)
            result = self._parse_member_access_chain(left)
            return result
        else:
            return Identifier(name)
    
    def _parse_function_call(self, name: str) -> FunctionCall:
        self._expect(TokenType.LPAREN)
        
        args = []
        while self._current_token().type != TokenType.RPAREN:
            args.append(self._parse_expression())
            if self._current_token().type == TokenType.COMMA:
                self._advance()
        
        self._expect(TokenType.RPAREN)
        
        if self._current_token().type == TokenType.SEMICOLON:
            self._advance()
        
        return FunctionCall(name, args)

    def _is_definitely_object_literal(self):
        """여러 토큰 미리보기로 정확한 객체 리터럴 판단 - 안전한 버전"""
                
        saved_pos = self.pos
        try:
            # 안전한 토큰 체크
            if self.pos >= len(self.tokens):
                
                return False
                
            current_token = self._current_token()
                        
            if current_token.type != TokenType.LBRACE:
                
                return False
                
            # 안전하게 다음 토큰으로 이동
            if self.pos + 1 >= len(self.tokens):
                
                return False
                
            self._advance()  # { 넘어가기
            
            # 빈 객체 {} 체크
            if self.pos >= len(self.tokens):
                
                return False
                
            next_token = self._current_token()
            
            
            if next_token.type == TokenType.RBRACE:
                
                return True
            
            # 객체 리터럴의 명확한 패턴들 확인 (안전하게)
            check_count = 0
            while not self._is_at_end() and check_count < 5:  # 최대 5개 토큰만 확인
                if self.pos >= len(self.tokens):
                    break
                    
                token = self._current_token()
                
                
                # 객체 필드 패턴: identifier: value 또는 "string": value
                if token.type in [TokenType.IDENTIFIER, TokenType.STRING]:
                    if self.pos + 1 < len(self.tokens):
                        next_token = self.tokens[self.pos + 1]  # 안전한 미리보기
                        if next_token.type == TokenType.COLON:
                            
                            return True
                            
                # 명확히 코드 블록인 패턴들
                elif token.type in [TokenType.IF, TokenType.FOR, TokenType.WHILE, 
                                TokenType.PRINTLN, TokenType.SCALAR, TokenType.QUBIT,
                                TokenType.APPLY, TokenType.MEASURE, TokenType.RETURN]:
                    
                    return False
                    
                # 함수 호출 패턴
                elif token.type == TokenType.IDENTIFIER:
                    if self.pos + 1 < len(self.tokens):
                        next_token = self.tokens[self.pos + 1]
                        if next_token.type == TokenType.LPAREN:
                            
                            return False
                            
                # 안전하게 다음 토큰으로
                if self.pos + 1 < len(self.tokens):
                    self._advance()
                    check_count += 1
                else:
                    break
                    
            
            return False
            
        except Exception as e:
            
            return False
        finally:
            # 원래 위치로 복원
            self.pos = saved_pos
            
    
    def _parse_expression(self) -> ASTNode:
        
        result = self._parse_pipe_expression()
        
        return result

    def _parse_pipe_expression(self) -> ASTNode:
        left = self._parse_logical_or()
        
        while self._current_token().type == TokenType.PIPE_OP:
            self._advance()  
            right = self._parse_logical_or()  
            left = PipeExpression(left, right)
        
        return left
    
    def _parse_logical_or(self) -> ASTNode:
        left = self._parse_logical_and()
        
        while self._current_token().type == TokenType.OR:
            op = self._current_token().value
            self._advance()
            right = self._parse_logical_and()
            left = BinaryOp(left, op, right)
        
        return left
    
    def _parse_logical_and(self) -> ASTNode:
        left = self._parse_equality()
        
        while self._current_token().type == TokenType.AND:
            op = self._current_token().value
            self._advance()
            right = self._parse_equality()
            left = BinaryOp(left, op, right)
        
        return left
    
    def _parse_equality(self) -> ASTNode:
        left = self._parse_comparison()
        
        while self._current_token().type in [TokenType.EQ, TokenType.NE, TokenType.APPROX_EQ]:
            op = self._current_token().value
            self._advance()
            right = self._parse_comparison()
            left = BinaryOp(left, op, right)
        
        return left
    
    def _parse_comparison(self) -> ASTNode:
        left = self._parse_term()
        
        while self._current_token().type in [TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE]:
            op = self._current_token().value
            self._advance()
            right = self._parse_term()
            left = BinaryOp(left, op, right)
        
        return left
    
    def _parse_term(self) -> ASTNode:
        left = self._parse_factor()
        
        while self._current_token().type in [TokenType.PLUS, TokenType.MINUS, TokenType.TENSOR]:
            op = self._current_token().value
            self._advance()
            right = self._parse_factor()
            left = BinaryOp(left, op, right)
        
        return left
    
    def _parse_factor(self) -> ASTNode:
        left = self._parse_unary()
        
        while self._current_token().type in [TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO, TokenType.POWER]:
            op = self._current_token().value
            self._advance()
            right = self._parse_unary()
            left = BinaryOp(left, op, right)
        
        return left
    
    def _parse_unary(self) -> ASTNode:
        if self._current_token().type in [TokenType.NOT, TokenType.MINUS, TokenType.AMPERSAND]:
            op = self._current_token().value
            self._advance()
            operand = self._parse_unary()
            return UnaryOp(op, operand)
        
        return self._parse_primary()
    
    def _parse_primary(self) -> ASTNode:
        if self._is_arrow_function():
            return self._parse_arrow_function()
        
        token = self._current_token()
        

        if token.type == TokenType.INTEGER:
            
            self._advance()
            try:
                value = token.value
                import re
                numeric_match = re.match(r'(\d+)', value)
                if numeric_match:
                    numeric_part = numeric_match.group(1)
                    val = int(numeric_part)
                else:
                    if value.startswith('0x') or value.startswith('0X'):
                        val = int(value, 16)
                    elif value.startswith('0b') or value.startswith('0B'):
                        val = int(value, 2)
                    elif value.startswith('0o') or value.startswith('0O'):
                        val = int(value, 8)
                    else:
                        val = int(value)
                
                
                return Literal(val, "int")
            except ValueError as e:
                raise SyntaxError(f"Invalid integer literal '{token.value}' at line {token.line}")
                
        elif token.type == TokenType.FLOAT:
            
            self._advance()
            value = token.value
            import re
            numeric_match = re.match(r'(\d+\.\d+)', value)
            if numeric_match:
                numeric_part = numeric_match.group(1)
                val = float(numeric_part)
            else:
                val = float(value)
            
            return Literal(val, "float")
            
        elif token.type == TokenType.STRING:
            
            self._advance()
            return Literal(token.value[1:-1], "string")
            
        elif token.type == TokenType.CHAR_LITERAL:
            
            self._advance()
            return Literal(token.value[1:-1], "char")
            
        elif token.type == TokenType.BOOL_LITERAL:
            
            self._advance()
            return Literal(token.value == "true", "bool")
            
        elif token.type == TokenType.COMPLEX:
            
            self._advance()
            return Literal(self._parse_complex(token.value), "complex")
            
        elif token.type == TokenType.QUANTUM_STATE:
            
            self._advance()
            return Literal(token.value, "quantum_state")
            
        elif token.type == TokenType.PIPE:
            
            if self._is_lambda_expression():
                return self._parse_lambda()
            else:
                return self._parse_manual_quantum_state()
                
        elif token.type in [TokenType.IDENTIFIER, TokenType.SELF, TokenType.MEASURE]:  
            name = token.value
            
            self._advance()
            
            # 🔧 현재 토큰 상태 확인
            current = self._current_token()
            
            
            if current.type == TokenType.LPAREN:
                
                return self._parse_function_call(name)
            elif current.type == TokenType.LBRACKET:
                
                self._advance()
                index = self._parse_expression()
                self._expect(TokenType.RBRACKET)
                return ArrayAccess(Identifier(name), index)
            elif current.type == TokenType.LBRACE:
                
                
                try:
                    is_object = self._is_definitely_object_literal()
                    
                    
                    if is_object:
                        
                        return self._parse_object_literal(name)
                    else:
                        
                        return Identifier(name)
                except Exception as e:
                    
                                       
                    return Identifier(name)

            elif current.type == TokenType.DOT:  
                
                left = Identifier(name)
                return self._parse_member_access_chain(left)
            else:
                
                return Identifier(name)
                
        elif token.type == TokenType.LPAREN:
            
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN)
            return expr
            
        elif token.type == TokenType.LBRACKET:
            
            return self._parse_array_literal()
            
        elif token.type == TokenType.MATCH:
            
            return self._parse_match_expression()
            
        else:
            
            raise SyntaxError(f"Unexpected token: {token.value}")
        
    def _is_arrow_function(self):
        if (self._check(TokenType.IDENTIFIER) and 
            self._peek_token_with_offset(1).type == TokenType.FAT_ARROW):
            return True
        
        if self._check(TokenType.LPAREN):
            return self._lookahead_for_arrow()
        
        return False
    
    def _lookahead_for_arrow(self):
        pos = 1  
        paren_count = 1
        
        while self.pos + pos < len(self.tokens):
            token = self._peek_token_with_offset(pos)
            
            if token.type == TokenType.LPAREN:
                paren_count += 1
            elif token.type == TokenType.RPAREN:
                paren_count -= 1
                if paren_count == 0:
                    next_token = self._peek_token_with_offset(pos + 1)
                    return next_token and next_token.type == TokenType.FAT_ARROW
            
            pos += 1
        
        return False
    
    def _parse_arrow_function(self):
        parameters = []
        
        if self._check(TokenType.IDENTIFIER):
            param_token = self._current_token()
            parameters.append(param_token.value)
            self._advance()
        
        elif self._check(TokenType.LPAREN):
            self._advance()  
            
            if not self._check(TokenType.RPAREN):
                if not self._check(TokenType.IDENTIFIER):
                    raise SyntaxError(f"Expected parameter name at line {self._current_token().line}")
                
                parameters.append(self._current_token().value)
                self._advance()
                
                while self._match(TokenType.COMMA):
                    if not self._check(TokenType.IDENTIFIER):
                        raise SyntaxError(f"Expected parameter name at line {self._current_token().line}")
                    
                    parameters.append(self._current_token().value)
                    self._advance()
            
            self._expect(TokenType.RPAREN)  
        
        else:
            raise SyntaxError(f"Invalid arrow function syntax at line {self._current_token().line}")
        
        self._expect(TokenType.FAT_ARROW)
        
        body = self._parse_expression()
        
        return ArrowFunction(parameters, body)
    
    def _peek_token_with_offset(self, offset):
        peek_pos = self.pos + offset
        if peek_pos >= len(self.tokens):
            return self.tokens[-1]  
        return self.tokens[peek_pos]
    
    def _check(self, token_type):
        if self._is_at_end():
            return False
        return self._current_token().type == token_type
    
    def _match(self, token_type):
        if self._check(token_type):
            self._advance()
            return True
        return False
   
    def _parse_array_literal(self) -> ArrayLiteral:
        self._expect(TokenType.LBRACKET)
        
        elements = []
        while self._current_token().type != TokenType.RBRACKET:
            elements.append(self._parse_expression())
            if self._current_token().type == TokenType.COMMA:
                self._advance()
        
        self._expect(TokenType.RBRACKET)
        return ArrayLiteral(elements)
    
    def _parse_complex(self, value: str) -> complex:
        import re
        match = re.match(r'([+-]?\d*\.?\d*)\s*([+-])\s*(\d*\.?\d*)i', value)
        if match:
            real_part = float(match.group(1)) if match.group(1) else 0
            sign = 1 if match.group(2) == '+' else -1
            imag_part = float(match.group(3)) if match.group(3) else 1
            return complex(real_part, sign * imag_part)
        
        match = re.match(r'([+-]?\d*\.?\d*)i', value)
        if match:
            imag_part = float(match.group(1)) if match.group(1) else 1
            return complex(0, imag_part)
        
        return complex(0, 0)
    
    def _current_token(self) -> Token:
        if self.pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos]
    
    def _advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
    
    def _expect(self, token_type: TokenType):
        if self._current_token().type != token_type:
            raise SyntaxError(f"Expected {token_type}, got {self._current_token().type} at line {self._current_token().line}")
        self._advance()
    
    def _expect_keyword(self, keyword: str):
        if self._current_token().value != keyword:
            raise SyntaxError(f"Expected '{keyword}', got '{self._current_token().value}'")
        self._advance()
    
    def _is_at_end(self) -> bool:
        return self._current_token().type == TokenType.EOF
    
    # 나머지 필수 메서드들 (간략 구현)
    def _parse_try_statement(self) -> TryStatement:
        self._advance()  # Skip 'try'
        
        self._expect(TokenType.LBRACE)
        try_block = []
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
            stmt = self._parse_statement()
            if stmt:
                try_block.append(stmt)
        self._expect(TokenType.RBRACE)
        
        catch_clauses = []
        while self._current_token().type == TokenType.CATCH:
            self._advance()
            catch_clauses.append(self._parse_catch_clause())
        
        finally_block = None
        if self._current_token().type == TokenType.FINALLY:
            self._advance()
            self._expect(TokenType.LBRACE)
            finally_block = []
            while self._current_token().type != TokenType.RBRACE:
                if self._current_token().type == TokenType.NEWLINE:
                    self._advance()
                    continue
                stmt = self._parse_statement()
                if stmt:
                    finally_block.append(stmt)
            self._expect(TokenType.RBRACE)
        
        return TryStatement(try_block, catch_clauses, finally_block)

    def _parse_catch_clause(self) -> CatchClause:
        self._expect(TokenType.LPAREN)
        
        exception_type = None
        exception_var = None
        
        if self._current_token().type == TokenType.IDENTIFIER:
            first_name = self._current_token().value
            self._advance()
            
            if self._current_token().type == TokenType.IDENTIFIER:
                exception_type = first_name
                exception_var = self._current_token().value
                self._advance()
            else:
                exception_var = first_name
        
        self._expect(TokenType.RPAREN)
        
        self._expect(TokenType.LBRACE)
        body = []
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
            stmt = self._parse_statement()
            if stmt:
                body.append(stmt)
        self._expect(TokenType.RBRACE)
        
        return CatchClause(exception_type, exception_var, body)

    def _parse_throw_statement(self) -> ThrowStatement:
        self._advance()  # Skip 'throw'
        exception = self._parse_expression()
        if self._current_token().type == TokenType.SEMICOLON:
            self._advance()
        return ThrowStatement(exception)
    
    def _parse_member_access_chain(self, left: ASTNode) -> ASTNode:
        while self._current_token().type == TokenType.DOT:
            self._advance()
            member_name = self._current_token().value
            self._advance()
            
            if self._current_token().type == TokenType.LPAREN:
                self._advance()
                args = []
                while self._current_token().type != TokenType.RPAREN:
                    args.append(self._parse_expression())
                    if self._current_token().type == TokenType.COMMA:
                        self._advance()
                self._expect(TokenType.RPAREN)
                left = MethodCall(left, member_name, args)  
            else:
                left = MemberAccess(left, member_name)
        
        if self._current_token().type in [TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN, 
                                        TokenType.MULT_ASSIGN, TokenType.DIV_ASSIGN, TokenType.TENSOR_ASSIGN]:
            op = self._current_token().value
            self._advance()
            value = self._parse_expression()
            if self._current_token().type == TokenType.SEMICOLON:
                self._advance()
            return Assignment(left, value, op) 
        
        return left
    
    def _parse_class(self) -> ClassDef:
        self._advance()  # 'class' 토큰 소비
        
        class_name = self._current_token().value
        self._advance()
        
        parent_class = None
        if self._current_token().type == TokenType.EXTENDS:
            self._advance()
            parent_class = self._current_token().value
            self._advance()

        self._expect(TokenType.LBRACE)
        
        fields = []
        methods = []
        constructors = []
        destructor = None
        
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
            elif self._current_token().type == TokenType.SEMICOLON:  
                self._advance()
                continue
            elif self._current_token().type == TokenType.CONSTRUCTOR:
                constructor = self._parse_constructor()
                constructors.append(constructor)
            elif self._current_token().type == TokenType.DESTRUCTOR:
                if destructor is not None:
                    raise SyntaxError("Only one destructor is allowed per class")
                destructor = self._parse_destructor()
            elif self._current_token().type in [TokenType.PRIVATE, TokenType.PUBLIC, TokenType.PROTECTED]:
                next_pos = self.pos + 1
                if next_pos < len(self.tokens) and self.tokens[next_pos].type == TokenType.FN:
                    method = self._parse_function()
                    methods.append(method)
                else:
                    field = self._parse_field_declaration()
                    fields.append(field)
            elif self._current_token().type == TokenType.FN:
                method = self._parse_function()
                methods.append(method)
            elif self._current_token().type == TokenType.IDENTIFIER:
                field = self._parse_field_declaration()
                fields.append(field)
            else:
                raise SyntaxError(f"Unexpected token in class body: {self._current_token().type}")
        
        self._expect(TokenType.RBRACE)
        return ClassDef(class_name, parent_class, fields, methods, constructors, destructor)

    def _parse_field_declaration(self) -> tuple:
        access_level = "public"
        if self._current_token().type in [TokenType.PRIVATE, TokenType.PUBLIC, TokenType.PROTECTED]:
            access_level = self._current_token().value
            self._advance()
        
        field_name = self._current_token().value
        self._advance()
        
        self._expect(TokenType.COLON)
        
        if self._current_token().type not in [TokenType.IDENTIFIER, TokenType.STR, TokenType.I32, 
                                            TokenType.I8, TokenType.I16, TokenType.I64,
                                            TokenType.U8, TokenType.U16, TokenType.U32, TokenType.U64,
                                            TokenType.F32, TokenType.F64, TokenType.BOOL, TokenType.CHAR]:
            raise SyntaxError(f"Expected field type, got {self._current_token().type}")
        
        field_type = self._current_token().value
        self._advance()
        
        self._expect(TokenType.SEMICOLON)
        
        return (access_level, field_name, field_type)
    
    def _parse_object_literal(self, class_name: str) -> ObjectLiteral:
        self._expect(TokenType.LBRACE)
        
        field_values = {}
        
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
                
            if self._current_token().type != TokenType.IDENTIFIER:
                raise SyntaxError(f"Expected field name, got {self._current_token().type}")
            
            field_name = self._current_token().value
            self._advance()
            
            self._expect(TokenType.COLON)
            
            value_expr = self._parse_expression()
            field_values[field_name] = value_expr
            
            if self._current_token().type == TokenType.COMMA:
                self._advance()
            elif self._current_token().type == TokenType.RBRACE:
                break
            else:
                raise SyntaxError(f"Expected ',' or '}}' in object literal")
        
        self._expect(TokenType.RBRACE)
        return ObjectLiteral(class_name, field_values)
    
    def _parse_constructor(self) -> ConstructorDef:
        self._advance()  # 'constructor' 토큰 소비
        
        self._expect(TokenType.LPAREN)
        params = []
        
        if self._current_token().type != TokenType.RPAREN:
            param_name = self._current_token().value
            self._advance()
            
            param_type = None
            if self._current_token().type == TokenType.COLON:
                self._advance()
                param_type = self._current_token().value
                self._advance()
            
            params.append((param_name, param_type))
            
            while self._current_token().type == TokenType.COMMA:
                self._advance()
                param_name = self._current_token().value
                self._advance()
                
                param_type = None
                if self._current_token().type == TokenType.COLON:
                    self._advance()
                    param_type = self._current_token().value
                    self._advance()
                
                params.append((param_name, param_type))
        
        self._expect(TokenType.RPAREN)
        
        self._expect(TokenType.LBRACE)
        body = []
        
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
            stmt = self._parse_statement()
            body.append(stmt)
        
        self._expect(TokenType.RBRACE)
        return ConstructorDef(params, body)

    def _parse_destructor(self) -> DestructorDef:
        self._advance()  # 'destructor' 토큰 소비
        self._expect(TokenType.LPAREN)
        self._expect(TokenType.RPAREN)
        
        self._expect(TokenType.LBRACE)
        body = []
        
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
            stmt = self._parse_statement()
            body.append(stmt)
        
        self._expect(TokenType.RBRACE)
        return DestructorDef(body)
    
    def _parse_import_statement(self) -> ImportStatement:
        self._advance()  # Skip 'import'
        
        imports = []
        alias = None
        
        if self._current_token().type == TokenType.LBRACE:
            self._advance()
            
            while self._current_token().type != TokenType.RBRACE:
                if self._current_token().type == TokenType.MULTIPLY:
                    imports.append("*")
                    self._advance()
                elif self._current_token().type == TokenType.IDENTIFIER:
                    imports.append(self._current_token().value)
                    self._advance()
                
                if self._current_token().type == TokenType.COMMA:
                    self._advance()
            
            self._expect(TokenType.RBRACE)
        
        elif self._current_token().type == TokenType.MULTIPLY:
            imports.append("*")
            self._advance()
        
        self._expect_keyword("from")
        
        if self._current_token().type != TokenType.STRING:
            raise SyntaxError(f"Expected module name string, got {self._current_token().type}")
        
        module_name = self._current_token().value[1:-1]
        self._advance()
        
        if self._current_token().type == TokenType.AS:
            self._advance()
            if self._current_token().type != TokenType.IDENTIFIER:
                raise SyntaxError(f"Expected alias name, got {self._current_token().type}")
            alias = self._current_token().value
            self._advance()
        
        if self._current_token().type == TokenType.SEMICOLON:
            self._advance()
        
        return ImportStatement(imports, module_name, alias)

    def _parse_export_statement(self) -> ExportStatement:
        self._advance()  # Skip 'export'
        
        declaration = self._parse_statement()
        
        if declaration is None:
            raise SyntaxError("Expected declaration after 'export'")
        
        return ExportStatement(declaration)

    # 간단한 구현 (람다와 수동 양자 상태는 나중에)
    def _is_lambda_expression(self):
        return False
    
    def _parse_lambda(self):
        pass
    
    def _parse_manual_quantum_state(self):
        pass

    def _parse_range_expression(self) -> ASTNode:
        """범위 표현식 파싱: (~, q5), (q0, ~), (q0:q4), (q0, q1, q2)"""
        
        first_token = self._current_token()
        
        # Case 1: (~, target) - 모든 큐빗 → 타겟
        if first_token.type == TokenType.BITWISE_NOT:
            self._advance()  # Skip '~'
            self._expect(TokenType.COMMA)
            target = self._parse_qubit_reference()
            return RangeExpression("all_to_target", target=target)
        
        # Case 2: 첫 번째가 큐빗 참조
        else:
            first_qubit = self._parse_qubit_reference()
            
            # Case 2a: (source, ~) - 소스 → 모든 큐빗
            if (self._current_token().type == TokenType.COMMA and 
                self._peek_token().type == TokenType.BITWISE_NOT):
                self._advance()  # Skip ','
                self._advance()  # Skip '~'
                return RangeExpression("source_to_all", start=first_qubit)
            
            # Case 2b: (q0:q4) - 범위
            elif self._current_token().type == TokenType.COLON:
                self._advance()  # Skip ':'
                end_qubit = self._parse_qubit_reference()
                return RangeExpression("range", start=first_qubit, end=end_qubit)
            
            # Case 2c: (q0, q1, q2) - 명시적 리스트
            elif self._current_token().type == TokenType.COMMA:
                qubits = [first_qubit]
                while self._current_token().type == TokenType.COMMA:
                    self._advance()  # Skip ','
                    # ~가 아닌 경우만 큐빗 추가
                    if self._current_token().type != TokenType.BITWISE_NOT:
                        qubits.append(self._parse_qubit_reference())
                    else:
                        # (q0, ~) 패턴 처리
                        self._advance()  # Skip '~'
                        return RangeExpression("source_to_all", start=first_qubit)
                return ArrayLiteral(qubits)  # 기존 ArrayLiteral 재사용
            
            # Case 2d: (q0) - 단일 큐빗
            else:
                return first_qubit