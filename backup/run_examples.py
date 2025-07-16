#!/usr/bin/env python3
"""
run_examples.py
QyTum 예제 실행 스크립트
"""

import os
import sys
from pathlib import Path

# Add qytum to path
sys.path.insert(0, str(Path(__file__).parent))

from qytum.interpreter import QyTumInterpreter

def run_example(filename):
    """Run a QyTum example file"""
    filepath = Path("examples") / filename
    
    if not filepath.exists():
        print(f"Error: Example file '{filepath}' not found.")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        print(f"\n{'='*60}")
        print(f"Running: {filename}")
        print(f"{'='*60}")
        
        interpreter = QyTumInterpreter()
        interpreter.run(code)
        
        print(f"\n✓ {filename} completed successfully.")
        return True
        
    except Exception as e:
        print(f"\n✗ Error running {filename}: {e}")
        return False

def main():
    """Run all examples"""
    examples = [
        "comprehensive_demo.qyt",
        "advanced_control_flow.qyt", 
        "advanced_functions.qyt",
        "quantum_algorithms_advanced.qyt",
    ]
    
    print("QyTum 고급 예제 실행")
    print("=" * 60)
    
    success_count = 0
    
    for example in examples:
        if run_example(example):
            success_count += 1
    
    print(f"\n\n{'='*60}")
    print(f"실행 완료: {success_count}/{len(examples)} 성공")
    print(f"{'='*60}")
    
    if success_count == len(examples):
        print("🎉 모든 예제가 성공적으로 실행되었습니다!")
    else:
        print("⚠️  일부 예제에서 오류가 발생했습니다.")

if __name__ == "__main__":
    main()