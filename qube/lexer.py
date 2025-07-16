"""
lexer.py - 회로 빌더 키워드 추가
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # Keywords
    IMPORT = "import"
    EXPORT = "export" 
    FROM = "from"
    AS = "as"

    FN = "fn"
    SCALAR = "scalar"
    QUBIT = "qubit" 
    BIT = "bit"
    CONST = "const"
    MUT = "mut"
    IF = "if"
    ELSE = "else"
    FOR = "for"
    WHILE = "while"
    LOOP = "loop"
    BREAK = "break"
    CONTINUE = "continue"
    RETURN = "return"
    MATCH = "match"
    
    # 🆕 양자 회로 빌더 키워드들
    CIRCUIT = "circuit"
    WITH = "with"
    APPLY = "apply"
    TO = "to"
    ON = "on"
    GATE = "gate"
    MEASURE = "measure"
    RESET = "reset"
    BARRIER = "barrier"
    
    # Type keywords
    I8 = "i8"
    I16 = "i16" 
    I32 = "i32"
    I64 = "i64"
    U8 = "u8"
    U16 = "u16"
    U32 = "u32"
    U64 = "u64"
    F32 = "f32"
    F64 = "f64"
    BOOL = "bool"
    CHAR = "char"
    STR = "str"
    
    # Literals
    IDENTIFIER = "IDENTIFIER"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    CHAR_LITERAL = "CHAR_LITERAL"
    BOOL_LITERAL = "BOOL_LITERAL"
    COMPLEX = "COMPLEX"
    
    # Quantum states
    QUANTUM_STATE = "QUANTUM_STATE"
    
    # Operators - Assignment
    ASSIGN = "="
    PLUS_ASSIGN = "+="
    MINUS_ASSIGN = "-="
    MULT_ASSIGN = "*="
    DIV_ASSIGN = "/="
    LEFT_SHIFT_ASSIGN = "<<="
    RIGHT_SHIFT_ASSIGN = ">>="
    BITWISE_AND_ASSIGN = "&="
    BITWISE_OR_ASSIGN = "|="
    BITWISE_XOR_ASSIGN = "^="
    TENSOR_ASSIGN = "⊗="
    
    # Operators - Arithmetic
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    POWER = "**"
    
    # Operators - Bitwise
    BITWISE_AND = "&"
    BITWISE_OR = "|"        
    BITWISE_XOR = "^"
    BITWISE_NOT = "~"
    LEFT_SHIFT = "<<"
    RIGHT_SHIFT = ">>"
    PIPE_OP = "|>"   
    
    # Operators - Comparison
    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    APPROX_EQ = "≈"
    
    # Operators - Logical
    AND = "&&"
    OR = "||"               
    NOT = "!"
    XOR = "^" 
    AMPERSAND = "&"  
    
    # Quantum operators
    TENSOR = "⊗"
    COMPOSE = "∘"
    DAGGER = "†"
    INNER_PRODUCT = "⟨⟩"    
    
    # Arrows
    ARROW = "->"            
    FAT_ARROW = "=>"        
    
    # Delimiters
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    LANGLE = "⟨"
    RANGLE = "⟩"
    PIPE = "|" 
    
    SEMICOLON = ";"
    COMMA = ","
    DOT = "."
    COLON = ":"
    DOUBLE_COLON = "::"
    
    # Special
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    RANGE = ".."
    RANGE_INCLUSIVE = "..="
    
    # 양자 특화
    COMMUTATOR = "[,]"      
    ANTICOMMUTATOR = "{,}"  
    EXPECTATION = "⟪⟫"      
    FIDELITY = "F"          
    TRACE = "Tr"            

    # 예외 처리 토큰들
    TRY = "TRY"
    CATCH = "CATCH" 
    FINALLY = "FINALLY"
    THROW = "THROW"

    CLASS = "CLASS"
    EXTENDS = "EXTENDS"
    SELF = "SELF"
    NEW = "NEW"
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC" 
    PROTECTED = "PROTECTED"
    CONSTRUCTOR = "CONSTRUCTOR"
    DESTRUCTOR = "DESTRUCTOR"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

class QubeLexer:
    def __init__(self, code: str):
        self.code = self._convert_at_symbols(code)
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        # 수정된 패턴 - 회로 키워드 추가
        self.patterns = [
            # --- 1. 주석 및 공백 ---
            (r'//[^\n]*', None),    
            (r'#[^\n]*', None),     
            (r'/\*[\s\S]*?\*/', None),  
            (r'[ \t]+', None),          
            (r'\n', TokenType.NEWLINE), 

            # --- 2. 양자 상태 패턴 ---
            (r'\|[01+\-]\>', TokenType.QUANTUM_STATE),
            (r'\|[01+\-]\⟩', TokenType.QUANTUM_STATE),
            (r'\|[01+\-ΦΨφψGHZWijklmnopqrstuvwxyzαβγδεζηθικλμνξοπρστυφχψω]+[⁺⁻]?\>', TokenType.QUANTUM_STATE),
            (r'\|[01+\-ΦΨφψGHZWijklmnopqrstuvwxyzαβγδεζηθικλμνξοπρστυφχψω]+[⁺⁻]?\⟩', TokenType.QUANTUM_STATE),
            
            # --- 3. 다중 문자 연산자 및 특수 기호 ---
            (r'\|\>', TokenType.PIPE_OP),
            (r'<<=', TokenType.LEFT_SHIFT_ASSIGN),
            (r'>>=', TokenType.RIGHT_SHIFT_ASSIGN),
            (r'&=', TokenType.BITWISE_AND_ASSIGN),
            (r'\|=', TokenType.BITWISE_OR_ASSIGN),
            (r'\^=', TokenType.BITWISE_XOR_ASSIGN),
            
            (r'==', TokenType.EQ),
            (r'!=', TokenType.NE),
            (r'<=', TokenType.LE),
            (r'>=', TokenType.GE),
            (r'&&', TokenType.AND),
            (r'\|\|', TokenType.OR),
            (r'≈', TokenType.APPROX_EQ),

            (r'\*\*', TokenType.POWER),        
            (r'\+=', TokenType.PLUS_ASSIGN),   
            (r'-=', TokenType.MINUS_ASSIGN),
            (r'\*=', TokenType.MULT_ASSIGN),
            (r'/=', TokenType.DIV_ASSIGN),
            
            (r'⊗=', TokenType.TENSOR_ASSIGN),  
            (r'::', TokenType.DOUBLE_COLON),   
            (r'->', TokenType.ARROW),          
            (r'=>', TokenType.FAT_ARROW),      
            (r'\.\.=', TokenType.RANGE_INCLUSIVE), 
            (r'\.\.', TokenType.RANGE),        
            (r'\[,\]', TokenType.COMMUTATOR),  
            (r'\{,\}', TokenType.ANTICOMMUTATOR), 
            (r'⟨[^⟩]*⟩', TokenType.EXPECTATION), 
            (r'Tr', TokenType.TRACE),          

            (r'<<', TokenType.LEFT_SHIFT),
            (r'>>', TokenType.RIGHT_SHIFT),
            
            # --- 4. 리터럴 ---
            (r'\d+\.\d+\s*[+-]\s*\d+\.\d*i', TokenType.COMPLEX),
            (r'\d+\s*[+-]\s*\d+\.\d*i', TokenType.COMPLEX),
            (r'\d+\.\d*i', TokenType.COMPLEX),
            (r'\d+i', TokenType.COMPLEX),

            (r'0[xX][0-9a-fA-F_]+', TokenType.INTEGER), 
            (r'0[bB][01_]+', TokenType.INTEGER),        
            (r'0[oO][0-7_]+', TokenType.INTEGER),       
            (r'\d+\.\d+f32', TokenType.FLOAT),          
            (r'\d+\.\d+f64', TokenType.FLOAT),          
            (r'\d+\.\d+', TokenType.FLOAT),             
            (r'\d+i8', TokenType.INTEGER),              
            (r'\d+i16', TokenType.INTEGER),
            (r'\d+i32', TokenType.INTEGER),
            (r'\d+i64', TokenType.INTEGER),
            (r'\d+u8', TokenType.INTEGER),              
            (r'\d+u16', TokenType.INTEGER),
            (r'\d+u32', TokenType.INTEGER),
            (r'\d+u64', TokenType.INTEGER),
            (r'\d+', TokenType.INTEGER),                

            (r'r#"[^"]*"#', TokenType.STRING),  
            (r'r"[^"]*"', TokenType.STRING),    
            (r'"[^"]*"', TokenType.STRING),     
            
            (r"'[a-zA-Z_][a-zA-Z0-9_]*", TokenType.IDENTIFIER),  
            
            (r"'[^']'", TokenType.CHAR_LITERAL),        
            (r"'\\[ntr\\']'", TokenType.CHAR_LITERAL),  
            
            (r'\btrue\b', TokenType.BOOL_LITERAL),
            (r'\bfalse\b', TokenType.BOOL_LITERAL),

            # --- 5. 키워드 ---
            # 모듈 키워드 
            (r'\bimport\b', TokenType.IMPORT),
            (r'\bexport\b', TokenType.EXPORT),
            (r'\bfrom\b', TokenType.FROM),
            (r'\bas\b', TokenType.AS),

            # 🆕 회로 빌더 키워드들 (키워드 섹션에 추가)
            (r'\bcircuit\b', TokenType.CIRCUIT),
            (r'\bwith\b', TokenType.WITH),
            (r'\bapply\b', TokenType.APPLY),
            (r'\bto\b', TokenType.TO),
            (r'\bon\b', TokenType.ON),
            (r'\bgate\b', TokenType.GATE),
            (r'\bmeasure\b', TokenType.MEASURE),
            (r'\breset\b', TokenType.RESET),
            (r'\bbarrier\b', TokenType.BARRIER),

            # 기본 키워드
            (r'\bfn\b', TokenType.FN),
            (r'\bscalar\b', TokenType.SCALAR),
            (r'\bqubit\b', TokenType.QUBIT),
            (r'\bbit\b', TokenType.BIT),
            (r'\bconst\b', TokenType.CONST),
            (r'\bmut\b', TokenType.MUT),
            (r'\bif\b', TokenType.IF),
            (r'\belse\b', TokenType.ELSE),
            (r'\bfor\b', TokenType.FOR),
            (r'\bwhile\b', TokenType.WHILE),
            (r'\bloop\b', TokenType.LOOP),
            (r'\bbreak\b', TokenType.BREAK),
            (r'\bcontinue\b', TokenType.CONTINUE),
            (r'\breturn\b', TokenType.RETURN),
            (r'\bmatch\b', TokenType.MATCH),

            (r'\btry\b', TokenType.TRY),
            (r'\bcatch\b', TokenType.CATCH),
            (r'\bfinally\b', TokenType.FINALLY),
            (r'\bthrow\b', TokenType.THROW),

            (r'\bclass\b', TokenType.CLASS),
            (r'\bextends\b', TokenType.EXTENDS),
            (r'\bself\b', TokenType.SELF),
            (r'\bnew\b', TokenType.NEW),
            (r'\bprivate\b', TokenType.PRIVATE),
            (r'\bpublic\b', TokenType.PUBLIC),
            (r'\bprotected\b', TokenType.PROTECTED), 
            (r'\bconstructor\b', TokenType.CONSTRUCTOR), 
            (r'\bdestructor\b', TokenType.DESTRUCTOR),   
                        
            # 내장 타입 키워드
            (r'\bi8\b', TokenType.I8),
            (r'\bi16\b', TokenType.I16),
            (r'\bi32\b', TokenType.I32),
            (r'\bi64\b', TokenType.I64),
            (r'\bu8\b', TokenType.U8),
            (r'\bu16\b', TokenType.U16),
            (r'\bu32\b', TokenType.U32),
            (r'\bu64\b', TokenType.U64),
            (r'\bf32\b', TokenType.F32),
            (r'\bf64\b', TokenType.F64),
            (r'\bbool\b', TokenType.BOOL),
            (r'\bchar\b', TokenType.CHAR),
            (r'\bstr\b', TokenType.STR),
            
            # --- 6. 식별자 ---
            (r'[a-zA-Z_αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ∑∏∫∂∇∞√±∓×÷≠≤≥≈⊂⊃∈∉∧∨¬∀∃∅ℝℂℕℤℚ][a-zA-Z0-9_αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ∑∏∫∂∇∞√±∓×÷≠≤≥≈⊂⊃∈∉∧∨¬∀∃∅ℝℂℕℤℚ₀₁₂₃₄₅₆₇₈₉]*', TokenType.IDENTIFIER),
            
            # --- 7. 단일 문자 연산자 및 구분자 ---
            (r'\(', TokenType.LPAREN),     
            (r'\)', TokenType.RPAREN),
            (r'\{', TokenType.LBRACE),     
            (r'\}', TokenType.RBRACE),
            (r'\[', TokenType.LBRACKET),   
            (r'\]', TokenType.RBRACKET),
            (r'⟨', TokenType.LANGLE),     
            (r'⟩', TokenType.RANGLE),
            (r'\|', TokenType.BITWISE_OR),       
            (r';', TokenType.SEMICOLON),   
            (r',', TokenType.COMMA),       
            (r'\.', TokenType.DOT),        
            (r':', TokenType.COLON),       

            (r'⊗', TokenType.TENSOR),      
            (r'∘', TokenType.COMPOSE),     
            (r'†', TokenType.DAGGER),      

            (r'=', TokenType.ASSIGN),      
            (r'\+', TokenType.PLUS),       
            (r'-', TokenType.MINUS),       
            (r'\*', TokenType.MULTIPLY),   
            (r'/', TokenType.DIVIDE),      
            (r'%', TokenType.MODULO),      
            (r'<', TokenType.LT),          
            (r'>', TokenType.GT),          
            (r'!', TokenType.NOT),         
            (r'\^', TokenType.XOR),        
            (r'&', TokenType.AMPERSAND),   
            (r'~', TokenType.BITWISE_NOT), 
            (r'F', TokenType.FIDELITY),    
        ]
    
    def _convert_at_symbols(self, code: str) -> str:
        """@ 기호를 유니코드로 변환하는 전처리"""
        
        # 그리스 문자 변환표
        conversions = {
            'alpha@': 'α',
            'beta@': 'β', 
            'gamma@': 'γ',
            'delta@': 'δ',
            'epsilon@': 'ε',
            'zeta@': 'ζ',
            'eta@': 'η',
            'theta@': 'θ',
            'iota@': 'ι',
            'kappa@': 'κ',
            'lambda@': 'λ',
            'mu@': 'μ',
            'nu@': 'ν',
            'xi@': 'ξ',
            'omicron@': 'ο',
            'pi@': 'π',
            'rho@': 'ρ',
            'sigma@': 'σ',
            'tau@': 'τ',
            'upsilon@': 'υ',
            'phi@': 'φ',
            'chi@': 'χ',
            'psi@': 'ψ',
            'omega@': 'ω',
            
            # 대문자 그리스 문자
            'Alpha@': 'Α',
            'Beta@': 'Β',
            'Gamma@': 'Γ',
            'Delta@': 'Δ',
            'Theta@': 'Θ',
            'Lambda@': 'Λ',
            'Pi@': 'Π',
            'Sigma@': 'Σ',
            'Phi@': 'Φ',
            'Psi@': 'Ψ',
            'Omega@': 'Ω',
            
            # 수학 기호들
            'sum@': '∑',
            'prod@': '∏',
            'integral@': '∫',
            'partial@': '∂',
            'nabla@': '∇',
            'infinity@': '∞',
            'sqrt@': '√',
            'pm@': '±',
            'mp@': '∓',
            'times@': '×',
            'div@': '÷',
            'ne@': '≠',
            'le@': '≤',
            'ge@': '≥',
            'approx@': '≈',
            'subset@': '⊂',
            'supset@': '⊃',
            'in@': '∈',
            'notin@': '∉',
            'and@': '∧',
            'or@': '∨',
            'not@': '¬',
            'forall@': '∀',
            'exists@': '∃',
            'empty@': '∅',
            'real@': 'ℝ',
            'complex@': 'ℂ',
            'natural@': 'ℕ',
            'integer@': 'ℤ',
            'rational@': 'ℚ'
        }
        
        # 변환 적용 (긴 것부터 먼저 처리)
        sorted_keys = sorted(conversions.keys(), key=len, reverse=True)
        
        for key in sorted_keys:
            code = code.replace(key, conversions[key])
        
        return code

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.code):
            if self.pos >= len(self.code):
                break
                
            token = self._next_token()
            if token:
                self.tokens.append(token)
        
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens
    
    def _next_token(self) -> Optional[Token]:
        # Skip whitespace first
        while self.pos < len(self.code) and self.code[self.pos] in ' \t':
            if self.code[self.pos] == '\t':
                self.column += 4
            else:
                self.column += 1
            self.pos += 1
        
        if self.pos >= len(self.code):
            return None
            
        for pattern, token_type in self.patterns:
            regex = re.compile(pattern)
            match = regex.match(self.code, self.pos)
            
            if match:
                value = match.group(0)
                token = None
                
                if token_type is not None:
                    token = Token(token_type, value, self.line, self.column)
                else:
                    pass  # Skip comments and whitespace

                # Update position
                if value == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += len(value)
                
                self.pos = match.end()
                return token
        
        # Unknown character
        char = self.code[self.pos]
        self.pos += 1
        self.column += 1
        raise SyntaxError(f"Unknown character '{char}' at line {self.line}, column {self.column}")