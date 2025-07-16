#!/usr/bin/env python3
"""
Qube 언어 메인 모듈
qube/__main__.py 파일로 저장하면 python -m qube으로 실행 가능
"""

import sys
import os
import argparse
from pathlib import Path

# 현재 패키지 경로 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))

def create_parser():
    """명령행 인자 파서 생성"""
    parser = argparse.ArgumentParser(
        description='Qube 양자 프로그래밍 언어 인터프리터',
        prog='qube'
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='실행할 Qube 파일 (.qyt)'
    )
    
    parser.add_argument(
        '--repl', '-i',
        action='store_true',
        help='대화형 REPL 모드 시작'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='store_true',
        help='버전 정보 표시'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='디버그 모드 활성화'
    )
    
    parser.add_argument(
        '--ast',
        action='store_true',
        help='AST 트리 출력 (파싱만)'
    )
    
    parser.add_argument(
        '--tokens',
        action='store_true',
        help='토큰 목록 출력 (렉싱만)'
    )
    
    return parser

def print_version():
    """버전 정보 출력"""
    print("Qube 양자 프로그래밍 언어")
    print("버전: 0.1.0")
    print("작성자: Qube 개발팀")
    print("설명: 양자 컴퓨팅을 위한 도메인 특화 언어")

def run_file(filepath: str, debug: bool = False, ast_only: bool = False, tokens_only: bool = False):
    """Qube 파일 실행"""
    try:
        from qube.interpreter import QubeInterpreter
        from qube.lexer import QubeLexer
        from qube.parser import QubeParser
        
        # 파일 존재 확인
        if not os.path.exists(filepath):
            print(f"오류: 파일 '{filepath}'을 찾을 수 없습니다.")
            return False
        
        # 파일 읽기
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        print(f"🚀 실행: {filepath}")
        if debug:
            print(f"📄 코드 ({len(code)} 문자):")
            print("-" * 40)
            print(code)
            print("-" * 40)
        
        # 토큰만 출력
        if tokens_only:
            print("🔍 토큰 분석:")
            lexer = QubeLexer()
            tokens = lexer.tokenize(code)
            for i, token in enumerate(tokens):
                print(f"  {i:3d}: {token.type:15} '{token.value}'")
            return True
        
        # AST만 출력
        if ast_only:
            print("🌳 AST 분석:")
            lexer = QubeLexer()
            tokens = lexer.tokenize(code)
            
            parser = QubeParser()
            ast = parser.parse(tokens)
            
            print_ast(ast, 0)
            return True
        
        # 정상 실행
        interpreter = QubeInterpreter()
        if debug:
            interpreter.debug = True
        
        interpreter.run(code)
        
        if debug:
            print("\n🔍 실행 후 변수 상태:")
            for name, value in interpreter.variables.items():
                print(f"  {name} = {value.value} ({value.type_name})")
        
        return True
        
    except ImportError as e:
        print(f"오류: 필요한 모듈을 찾을 수 없습니다: {e}")
        return False
    except Exception as e:
        print(f"실행 오류: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return False

def print_ast(node, indent=0):
    """AST 노드를 들여쓰기와 함께 출력"""
    indent_str = "  " * indent
    
    if hasattr(node, '__class__'):
        print(f"{indent_str}{node.__class__.__name__}")
        
        # 노드의 속성들 출력
        for attr_name in dir(node):
            if not attr_name.startswith('_'):
                attr_value = getattr(node, attr_name)
                if not callable(attr_value):
                    if isinstance(attr_value, list):
                        if attr_value:  # 비어있지 않은 리스트만
                            print(f"{indent_str}  {attr_name}:")
                            for item in attr_value:
                                print_ast(item, indent + 2)
                    elif hasattr(attr_value, '__class__') and hasattr(attr_value, '__dict__'):
                        print(f"{indent_str}  {attr_name}:")
                        print_ast(attr_value, indent + 2)
                    else:
                        print(f"{indent_str}  {attr_name}: {attr_value}")

def start_repl(debug: bool = False):
    """대화형 REPL 시작"""
    try:
        from qube.interpreter import QubeInterpreter
        
        print("🌟 Qube 대화형 모드")
        print("종료하려면 'exit' 또는 Ctrl+C를 입력하세요.")
        print("-" * 40)
        
        interpreter = QubeInterpreter()
        if debug:
            interpreter.debug = True
        
        while True:
            try:
                # 입력 받기
                code = input("qube> ")
                
                if code.strip() in ['exit', 'quit']:
                    break
                
                if code.strip() == '':
                    continue
                
                # 특별 명령어 처리
                if code.strip() == 'vars':
                    print("현재 변수들:")
                    for name, value in interpreter.variables.items():
                        print(f"  {name} = {value.value} ({value.type_name})")
                    continue
                
                if code.strip() == 'clear':
                    interpreter.variables.clear()
                    print("변수가 모두 삭제되었습니다.")
                    continue
                
                if code.strip() == 'help':
                    print("사용 가능한 명령어:")
                    print("  vars  - 현재 변수 목록 표시")
                    print("  clear - 모든 변수 삭제")
                    print("  help  - 이 도움말 표시")
                    print("  exit  - REPL 종료")
                    continue
                
                # 코드 실행
                result = interpreter.run(code)
                
                if debug and result:
                    print(f"결과: {result}")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Qube REPL을 종료합니다.")
                break
            except EOFError:
                print("\n\n👋 Qube REPL을 종료합니다.")
                break
            except Exception as e:
                print(f"오류: {e}")
                if debug:
                    import traceback
                    traceback.print_exc()
    
    except ImportError as e:
        print(f"오류: Qube 모듈을 찾을 수 없습니다: {e}")

def main():
    """메인 함수"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 버전 정보
    if args.version:
        print_version()
        return
    
    # REPL 모드
    if args.repl or not args.file:
        start_repl(args.debug)
        return
    
    # 파일 실행
    success = run_file(
        args.file, 
        debug=args.debug,
        ast_only=args.ast,
        tokens_only=args.tokens
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()