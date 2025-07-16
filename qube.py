#!/usr/bin/env python3
"""
qube.py
Qube CLI 실행기 - 확장된 도움말 시스템 포함
"""

import argparse
import sys
import os

def create_parser():
    """CLI 파서 생성 - 확장된 기능 포함"""
    parser = argparse.ArgumentParser(
        prog='qube',
        description='Qube Quantum Programming Language',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  qube hello.qb              # Run a Qube program
  qube --repl                # Start interactive mode  
  qube --check syntax.qb     # Check syntax only
  qube --debug program.qb    # Run with debug output
  qube --api                 # Show API reference
  qube --help measure        # Help for measure function
        """
    )
    
    # 기존 인수들
    parser.add_argument('file', nargs='?', help='Qube source file to execute')
    parser.add_argument('--version', action='version', version='Qube 0.1.0')
    parser.add_argument('--repl', action='store_true', help='Start interactive REPL')
    parser.add_argument('--check', action='store_true', help='Check syntax only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    
    # 🆕 새로운 도움말 기능들
    parser.add_argument('--api', action='store_true', help='Show API reference')
    parser.add_argument('--help-topic', metavar='TOPIC', 
                       help='Show help for specific topic (measure, Circuit, gates, syntax, examples, errors)')
    parser.add_argument('--examples', action='store_true', help='List available examples')
    parser.add_argument('--info', action='store_true', help='Show system information')
    
    return parser

def main():
    """메인 실행 함수 - 확장된 기능 포함"""
    parser = create_parser()
    
    # 🔧 --help topic 특별 처리
    if len(sys.argv) >= 3 and sys.argv[1] == '--help':
        # qube --help measure 형태 처리
        topic = sys.argv[2]
        from qube.cli_help import show_function_help
        show_function_help(topic)
        return
    
    args = parser.parse_args()
    
    try:
        # 🆕 새로운 도움말 기능들
        if args.api:
            from qube.cli_help import show_api_reference
            show_api_reference()
            return
            
        if args.help_topic:
            from qube.cli_help import show_function_help
            show_function_help(args.help_topic)
            return
            
        if args.examples:
            from qube.cli_help import show_examples_help
            show_examples_help()
            return
            
        if args.info:
            from qube.cli_help import show_version_info
            show_version_info()
            return
        
        # 기존 기능들
        if args.repl:
            start_repl(args.debug, args.verbose)
            return
            
        if not args.file:
            print("오류: 실행할 파일을 지정하거나 --repl 모드를 사용하세요")
            print("도움말: qube --help")
            sys.exit(1)
            
        if not os.path.exists(args.file):
            print(f"오류: 파일을 찾을 수 없습니다: {args.file}")
            sys.exit(1)
            
        # 파일 실행
        execute_file(args.file, args.check, args.debug, args.verbose)
        
    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        if args.debug:
            import traceback
            traceback.print_exc()
        else:
            print(f"Qube 오류: {e}")
        sys.exit(1)

def execute_file(filename, check_only=False, debug_mode=False, verbose_mode=False):
    """파일 실행 - 기존 로직 유지"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        from qube import QubeInterpreter
        interpreter = QubeInterpreter()
        
        # 🔧 디버그/verbose 모드 설정
        if debug_mode:
            interpreter.debug_mode = True
        if verbose_mode:
            interpreter.verbose_mode = True
            
        if check_only:
            # 문법 검사만
            from qube.lexer import QubeLexer
            from qube.parser import QubeParser
            
            lexer = QubeLexer(code)
            tokens = lexer.tokenize()
            parser = QubeParser(tokens)
            ast = parser.parse()
            
            print(f"✅ {filename}: 문법 검사 통과")
        else:
            # 실제 실행
            interpreter.run(code)
            
    except Exception as e:
        if debug_mode:
            raise  # 전체 스택 트레이스 표시
        else:
            # 간단한 에러 메시지 + 도움말 제안
            error_msg = str(e)
            print(f"❌ 실행 오류: {error_msg}")
            
            # 🆕 에러별 도움말 제안
            if "measure" in error_msg.lower():
                print("💡 도움말: qube --help measure")
            elif "circuit" in error_msg.lower():
                print("💡 도움말: qube --help Circuit")
            elif "gate" in error_msg.lower():
                print("💡 도움말: qube --help gates")
            elif "syntax" in error_msg.lower():
                print("💡 도움말: qube --help syntax")
            else:
                print("💡 도움말: qube --help errors")
                
            raise

def start_repl(debug_mode=False, verbose_mode=False):
    """REPL 모드 시작 - 개선된 도움말 포함"""
    print("🚀 Qube 대화형 모드 (REPL)")
    print("종료: exit() 또는 Ctrl+C")
    print("도움말: help() 또는 qube --api")
    print()
    
    from qube import QubeInterpreter
    interpreter = QubeInterpreter()
    
    if debug_mode:
        interpreter.debug_mode = True
    if verbose_mode:
        interpreter.verbose_mode = True
    
    while True:
        try:
            code = input("qube> ")
            
            if code.strip() in ['exit()', 'quit()', 'exit', 'quit']:
                break
            elif code.strip() in ['help()', 'help']:
                print("🔧 REPL 도움말:")
                print("  help()     - 이 도움말")
                print("  exit()     - 종료")
                print("  qube --api - 전체 API 레퍼런스")
                print()
                continue
            elif code.strip() == '':
                continue
                
            interpreter.run(code)
            
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except Exception as e:
            if debug_mode:
                import traceback
                traceback.print_exc()
            else:
                print(f"❌ 오류: {e}")

if __name__ == "__main__":
    main()