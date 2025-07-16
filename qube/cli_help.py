"""
cli_help.py - Qube CLI 도움말 시스템
완전한 7개 도움말 명령어 구현
"""

import sys
import os

def show_api_reference():
    """전체 API 레퍼런스 출력"""
    print("""
🚀 Qube 양자 프로그래밍 언어 - 완전한 API 레퍼런스

=== 📖 핵심 기능 ===
• 양자 회로 빌더: circuit 키워드로 회로 정의
• 범위 문법: apply H to ~ (모든 큐빗)
• 스마트 게이트: 자동 N큐빗 제어 Z
• 완전한 측정: measure(circuit, [0,1,2])
• 15개 내장 함수: 완전한 표준 라이브러리

=== ⚛️ 양자 회로 생성 ===
circuit MyCircuit(n_qubits) {
    apply H to q0;              // 단일 큐빗 게이트
    apply H to ~;               // 🚀 범위 문법 - 모든 큐빗
    apply CNOT to (q0, q1);     // 2큐빗 게이트
    apply CZ to (q0, q1, q2);   // 다중 큐빗 제어
}

=== 📊 측정 시스템 ===
circuit = MyCircuit();
result = measure(circuit, [0, 1, 2]);  // 선택된 큐빗만
all_result = measure(circuit, [0, 1, 2, 3, 4]);  // 전체 회로

=== 🎛️ 지원 게이트 ===
• 단일 큐빗: H, X, Y, Z, S, T
• 회전: RX(angle), RY(angle), RZ(angle)
• 2큐빗: CNOT, CZ
• 다중 큐빗: CCZ, CCCZ, 스마트 CZ

=== 📦 표준 라이브러리 (15개 함수) ===
• 타입 변환: toString()
• 수학: abs(), sqrt(), pow(), sin(), cos(), tan(), log()
• 컬렉션: len(), max(), min(), sum(), range()
• 랜덤: random(), randomInt()

=== 🔧 CLI 도움말 ===
qube --help measure     # 측정 시스템 가이드
qube --help gates       # 게이트 사용법
qube --help circuit     # 회로 생성 방법
qube --help examples    # 예제 파일 안내
qube --help syntax      # 문법 가이드
qube --help debug       # 디버그 도구

=== 📚 더 자세한 정보 ===
• 완전한 API 문서: docs/api/complete_api.md
• 표준 라이브러리: docs/api/stdlib_api.md
• 시작 가이드: docs/guides/getting_started.md
• 예제 코드: examples/ 디렉토리

💡 Happy Quantum Programming! 🌟⚛️
""")

def show_function_help(topic: str):
    """특정 주제별 도움말 출력"""
    
    if topic == "measure":
        print("""
📊 measure() 함수 완전 가이드

=== 📖 기본 사용법 ===
measure(circuit, qubit_indices) -> List[int]

=== 🎯 예제 ===
# 1. 전체 회로 측정
circuit = Circuit(5);
result = measure(circuit, [0, 1, 2, 3, 4]);
// 반환: [0, 1, 0, 1, 1] 같은 비트 배열

# 2. 부분 측정
result = measure(circuit, [0, 2, 4]);
// 반환: [bit0, bit2, bit4]

# 3. 단일 큐빗 측정
result = measure(circuit, [2]);
// 반환: [bit2]

=== ⚠️ 주의사항 ===
• 큐빗 인덱스는 0부터 시작
• 측정 후 상태가 붕괴됨
• 결과는 항상 0 또는 1의 비트 배열

=== 🔧 에러 처리 ===
• 범위 오류: "Qubit index 5 out of range for 3-qubit circuit"
• 타입 오류: "Cannot measure string type"

=== 💡 팁 ===
• 십진수 변환: result[0] + result[1]*2 + result[2]*4
• 이진 문자열: toString(result)
""")
    
    elif topic == "gates":
        print("""
🎛️ Qube 양자 게이트 완전 가이드

=== 🔧 단일 큐빗 게이트 ===
apply H to q0;      // 하다마드 (중첩 상태)
apply X to q0;      // Pauli-X (비트 플립)
apply Y to q0;      // Pauli-Y
apply Z to q0;      // Pauli-Z (위상 플립)
apply S to q0;      // S = √Z
apply T to q0;      // T = √S

=== 🔄 회전 게이트 ===
apply RX(π/2) to q0;    // X축 회전
apply RY(π/4) to q0;    // Y축 회전
apply RZ(π/3) to q0;    // Z축 회전

=== 🔗 2큐빗 게이트 ===
apply CNOT to (q0, q1);     // 제어-NOT
apply CZ to (q0, q1);       // 제어-Z

=== 🎯 다중 큐빗 제어 게이트 ===
apply CCZ to (q0, q1, q2);          // 3큐빗 제어 Z
apply CCCZ to (q0, q1, q2, q3);     // 4큐빗 제어 Z
apply CZ to (q0, q1, q2, q3, q4);   // 5큐빗 스마트 CZ

=== 🚀 범위 문법 (혁신 기능) ===
apply H to ~;               // 모든 큐빗에 H 적용
// 기존: 5줄 코드 → 범위: 1줄 (80% 간소화)

=== 💡 사용 팁 ===
• 각도는 라디안 단위 (π 사용 가능)
• 큐빗 인덱스는 0부터 시작
• 게이트는 회로 정의 내에서만 사용
""")
    
    elif topic == "circuit":
        print("""
⚛️ Circuit 생성자 완전 가이드

=== 🏗️ 기본 사용법 ===
circuit CircuitName(n_qubits) {
    // 게이트 적용
    apply GATE to target;
}

=== 🎯 예제 ===
# 1. 기본 회로
circuit HelloQuantum(1) {
    apply H to q0;
}

# 2. 벨 상태 회로
circuit Bell(2) {
    apply H to q0;
    apply CNOT to (q0, q1);
}

# 3. 범위 문법 사용
circuit SuperPosition(5) {
    apply H to ~;  // 모든 큐빗에 H
}

=== 🔧 인스턴스 생성 ===
my_circuit = HelloQuantum();
result = measure(my_circuit, [0]);

=== ⚠️ 제한사항 ===
• 최대 20큐빗 지원
• 큐빗 수는 1 이상이어야 함
• 회로 정의 내에서만 게이트 사용

=== 💡 베스트 프랙티스 ===
• 의미 있는 회로명 사용
• 복잡한 회로는 단계별로 구성
• 범위 문법으로 코드 간소화
""")
    
    elif topic == "examples":
        print("""
💡 Qube 예제 파일 안내

=== 📁 예제 디렉토리 구조 ===
examples/
├── basic/
│   ├── hello_world.qb          # 첫 번째 프로그램
│   ├── basic_gates.qb          # 기본 게이트 사용법
│   └── stdlib_demo.qb          # 표준 라이브러리 데모
├── quantum/
│   ├── bell_state.qb           # 벨 상태 생성
│   ├── superposition.qb        # 중첩 상태 실험
│   └── quantum_teleportation.qb # 양자 순간이동
└── advanced/
    ├── grover_3qubit.qb        # 3큐빗 Grover
    ├── grover_5qubit.qb        # 5큐빗 Grover (100% 성공률)
    └── quantum_fourier.qb      # 양자 푸리에 변환

=== 🎯 학습 순서 ===
1. hello_world.qb              # 기본 문법 학습
2. basic_gates.qb              # 양자 게이트 이해
3. bell_state.qb               # 양자 얽힘 실험
4. grover_3qubit.qb            # 양자 알고리즘 입문
5. grover_5qubit.qb            # 고급 최적화 기법

=== 🚀 실행 방법 ===
qube examples/basic/hello_world.qb
qube examples/quantum/bell_state.qb
qube algorithms/search/grover_5qubit_performance.qb

=== 🏆 핵심 예제 ===
• grover_5qubit_performance.qb: 100% 성공률 달성
• bell_state.qb: 양자 얽힘 실험
• stdlib_simple_test.qb: 표준 라이브러리 테스트

=== 💡 추천 학습 경로 ===
초급 → 중급 → 고급
30분  1시간  2시간 (총 3.5시간)
""")
    
    elif topic == "syntax":
        print("""
📝 Qube 문법 가이드

=== 🔤 기본 문법 ===
// 주석
/* 여러 줄 주석 */

// 변수 선언
x = 42;                    // int
y = 3.14;                  // float
z = "Hello";               // string
w = true;                  // bool
arr = [1, 2, 3];          // array

=== 🔄 제어 구조 ===
// 조건문
if condition {
    // 실행
} else {
    // 다른 실행
}

// 반복문
for i in range(10) {
    // 반복 실행
}

=== ⚛️ 양자 회로 문법 ===
circuit CircuitName(n_qubits) {
    apply GATE to target;
    apply GATE(param) to target;
    apply GATE to (control, target);
}

=== 🎯 범위 문법 (혁신 기능) ===
apply H to ~;               // 모든 큐빗
apply CZ to (q0, q1, q2);   // 다중 큐빗

=== 📦 함수 정의 ===
fn function_name(param: type) -> type {
    return value;
}

=== 💡 특별한 기능 ===
• 그리스 문자: alpha@ → α
• 유니코드 연산자: ⊗, ∘, †
• 브라-켓 표기법: |0⟩, |1⟩, |+⟩
""")
    
    elif topic == "debug":
        print("""
🔧 Qube 디버그 도구 가이드

=== 🎯 디버그 모드 실행 ===
qube --debug my_program.qb
qube --verbose my_program.qb

=== 📊 상태 벡터 확인 ===
circuit = Circuit(3, true);  // 디버그 모드 활성화
// 자동으로 게이트 적용 전후 상태 출력

=== 🔍 단계별 디버깅 ===
# 1. 문법 검사
qube --check my_program.qb

# 2. 단계별 실행
qube --trace my_program.qb

# 3. 상태 확인
debug_var("variable_name");

=== ⚠️ 일반적인 오류들 ===
• "Qubit index out of range" → 큐빗 인덱스 확인
• "Cannot measure string type" → 타입 확인
• "No active circuit" → 회로 정의 내에서 게이트 사용

=== 💡 디버깅 팁 ===
• 복잡한 회로는 단계별로 나누어 테스트
• 측정 전에 상태 벡터 확인
• 에러 메시지 주의깊게 읽기
""")
    
    elif topic in ["errors", "error"]:
        print("""
⚠️ Qube 에러 해결 가이드

=== 🔧 자주 발생하는 오류들 ===

1. 측정 관련 오류
   ❌ circuit.measure()  // 잘못된 방법
   ✅ measure(circuit, [0, 1, 2])  // 올바른 방법

2. 게이트 적용 오류
   ❌ apply H to q0;  // 회로 밖에서 사용
   ✅ circuit MyCircuit(1) { apply H to q0; }

3. 큐빗 인덱스 오류
   ❌ measure(circuit, [0, 1, 2, 3])  // 3큐빗 회로에서
   ✅ measure(circuit, [0, 1, 2])

=== 📋 에러 타입별 해결법 ===
• QubeRuntimeError: 실행 시간 오류
• QubeTypeError: 잘못된 타입 사용
• QubeQuantumError: 양자 연산 오류
• QubeCircuitError: 회로 관련 오류

=== 💡 디버깅 전략 ===
1. 에러 메시지 정확히 읽기
2. 단계별로 코드 나누어 테스트
3. --debug 모드로 상세 정보 확인
4. 예제 코드와 비교해보기

=== 🆘 도움 요청 ===
• GitHub Issues: github.com/zetavus/qube/issues
• 문서 확인: qube --api
• 예제 참고: qube --help examples
""")
    
    else:
        print(f"""
❌ 알 수 없는 도움말 주제: {topic}

📋 사용 가능한 주제:
• measure    - 측정 시스템 완전 가이드
• gates      - 모든 게이트 사용법
• circuit    - 회로 생성 방법
• examples   - 예제 파일 안내
• syntax     - 문법 가이드
• debug      - 디버그 도구
• errors     - 에러 해결 가이드

💡 사용법: qube --help [topic]
""")

def show_examples_help():
    """예제 목록 출력"""
    print("""
📚 Qube 예제 파일 목록

=== 🎯 기본 예제 ===
• hello_world.qb            - 첫 번째 Qube 프로그램
• basic_gates.qb            - 기본 게이트 사용법
• stdlib_demo.qb            - 표준 라이브러리 데모

=== ⚛️ 양자 예제 ===
• bell_state.qb             - 벨 상태 생성 실험
• superposition.qb          - 중첩 상태 실험
• quantum_teleportation.qb  - 양자 순간이동

=== 🏆 고급 알고리즘 ===
• grover_3qubit.qb          - 3큐빗 Grover 알고리즘
• grover_5qubit.qb          - 5큐빗 Grover (100% 성공률)
• quantum_fourier.qb        - 양자 푸리에 변환

=== 🧪 테스트 파일 ===
• stdlib_simple_test.qb     - 표준 라이브러리 기본 테스트
• stdlib_advanced_test.qb   - 고급 기능 테스트
• performance_test.qb       - 성능 벤치마크

=== 🚀 실행 방법 ===
qube examples/basic/hello_world.qb
qube examples/quantum/bell_state.qb
qube algorithms/search/grover_5qubit_performance.qb

=== 💡 추천 학습 순서 ===
1. hello_world.qb (5분)
2. basic_gates.qb (10분)
3. bell_state.qb (15분)
4. grover_3qubit.qb (20분)
5. grover_5qubit.qb (30분)

총 학습 시간: 약 1시간 20분
""")

def show_version_info():
    """시스템 정보 출력"""
    print(f"""
🚀 Qube 양자 프로그래밍 언어

=== 📊 버전 정보 ===
• Qube 언어 버전: v0.1.0
• 표준 라이브러리: v1.0.0
• 내장 함수: 15개
• 지원 게이트: 20개+
• 최대 큐빗: 20개

=== 🏆 주요 성과 ===
• 5큐빗 Grover 100% 성공률 달성
• 33.3배 성능 향상 (고전 알고리즘 대비)
• 77% 코드 간소화 (범위 문법)
• 완전한 CLI 도움말 시스템

=== 💻 시스템 요구사항 ===
• Python 3.8+
• NumPy 1.20.0+
• 메모리: 최소 512MB

=== 🔧 지원 기능 ===
• 양자 회로 빌더
• 범위 문법 (apply H to ~)
• 스마트 CZ 게이트
• 완전한 측정 시스템
• 디버그 모드
• 풍부한 표준 라이브러리

=== 📚 문서 ===
• GitHub: github.com/zetavus/qube
• 완전한 API: qube --api
• 예제 코드: qube --help examples

=== 👨‍💻 개발자 ===
• 개발자: zetavus
• 라이선스: MIT
• 언어: Python + Qube

💡 "양자 프로그래밍을 모든 개발자에게" - Qube 프로젝트
""")

# 메인 함수들
__all__ = [
    'show_api_reference',
    'show_function_help', 
    'show_examples_help',
    'show_version_info'
]