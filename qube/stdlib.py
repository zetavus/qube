"""
Qube 표준 라이브러리 (Standard Library)
stdlib.py - Qube 표준 라이브러리 구현
15개 내장 함수 제공
"""

import math
import random

class QubeStdlib:
    """Qube 표준 라이브러리 함수들 - 간단한 Python 값 반환"""
    
    @staticmethod
    def str_convert(value):
        """값을 문자열로 변환"""
        # QubeValue 객체인 경우 value 속성 사용
        if hasattr(value, 'value'):
            actual_value = value.value
        else:
            actual_value = value
            
        if isinstance(actual_value, bool):
            return "true" if actual_value else "false"
        return str(actual_value)
    
    @staticmethod
    def to_string(value):
        """str()의 별칭"""
        return QubeStdlib.str_convert(value)
    
    @staticmethod
    def abs_value(value):
        """절댓값 반환"""
        actual_value = value.value if hasattr(value, 'value') else value
        return abs(actual_value)
    
    @staticmethod
    def sqrt_value(value):
        """제곱근 반환"""
        actual_value = value.value if hasattr(value, 'value') else value
        if actual_value < 0:
            raise ValueError("음수의 제곱근은 계산할 수 없습니다")
        return math.sqrt(actual_value)
    
    @staticmethod
    def sin_value(value):
        """사인 값 반환"""
        actual_value = value.value if hasattr(value, 'value') else value
        return math.sin(actual_value)
    
    @staticmethod
    def cos_value(value):
        """코사인 값 반환"""
        actual_value = value.value if hasattr(value, 'value') else value
        return math.cos(actual_value)
    
    @staticmethod
    def tan_value(value):
        """탄젠트 값 반환"""
        actual_value = value.value if hasattr(value, 'value') else value
        return math.tan(actual_value)
    
    @staticmethod
    def log_value(value, base=None):
        """로그 값 반환"""
        actual_value = value.value if hasattr(value, 'value') else value
        if actual_value <= 0:
            raise ValueError("로그의 진수는 양수여야 합니다")
        
        if base is None:
            return math.log(actual_value)
        else:
            actual_base = base.value if hasattr(base, 'value') else base
            return math.log(actual_value, actual_base)
    
    @staticmethod
    def pow_value(base, exponent):
        """거듭제곱 반환"""
        actual_base = base.value if hasattr(base, 'value') else base
        actual_exp = exponent.value if hasattr(exponent, 'value') else exponent
        return pow(actual_base, actual_exp)
    
    @staticmethod
    def len_value(value):
        """길이 반환"""
        actual_value = value.value if hasattr(value, 'value') else value
        if isinstance(actual_value, (list, tuple, str)):
            return len(actual_value)
        raise TypeError("길이를 계산할 수 없는 타입입니다")
    
    @staticmethod
    def max_value(*args):
        """최댓값 반환"""
        if len(args) == 0:
            raise ValueError("최소 하나의 인수가 필요합니다")
        
        # QubeValue 객체들을 실제 값으로 변환
        actual_values = []
        for arg in args:
            if hasattr(arg, 'value'):
                if isinstance(arg.value, (list, tuple)):
                    actual_values.extend(arg.value)
                else:
                    actual_values.append(arg.value)
            else:
                actual_values.append(arg)
        
        return max(actual_values)
    
    @staticmethod
    def min_value(*args):
        """최솟값 반환"""
        if len(args) == 0:
            raise ValueError("최소 하나의 인수가 필요합니다")
        
        # QubeValue 객체들을 실제 값으로 변환
        actual_values = []
        for arg in args:
            if hasattr(arg, 'value'):
                if isinstance(arg.value, (list, tuple)):
                    actual_values.extend(arg.value)
                else:
                    actual_values.append(arg.value)
            else:
                actual_values.append(arg)
        
        return min(actual_values)
    
    @staticmethod
    def sum_value(iterable):
        """합계 반환"""
        actual_value = iterable.value if hasattr(iterable, 'value') else iterable
        if isinstance(actual_value, (list, tuple)):
            return sum(actual_value)
        raise TypeError("합계를 계산할 수 없는 타입입니다")
    
    @staticmethod
    def range_value(start, end=None, step=None):
        """범위 생성"""
        actual_start = start.value if hasattr(start, 'value') else start
        
        if end is None:
            return list(range(actual_start))
        
        actual_end = end.value if hasattr(end, 'value') else end
        
        if step is None:
            return list(range(actual_start, actual_end))
        
        actual_step = step.value if hasattr(step, 'value') else step
        return list(range(actual_start, actual_end, actual_step))
    
    @staticmethod
    def random_value():
        """0과 1 사이의 난수 반환"""
        return random.random()
    
    @staticmethod
    def random_int(start, end):
        """지정된 범위의 정수 난수 반환"""
        actual_start = start.value if hasattr(start, 'value') else start
        actual_end = end.value if hasattr(end, 'value') else end
        return random.randint(actual_start, actual_end)

# 표준 라이브러리 함수 매핑
STDLIB_FUNCTIONS = {
    # 타입 변환
    'str': QubeStdlib.str_convert,
    'toString': QubeStdlib.to_string,
    
    # 수학 함수
    'abs': QubeStdlib.abs_value,
    'sqrt': QubeStdlib.sqrt_value,
    'sin': QubeStdlib.sin_value,
    'cos': QubeStdlib.cos_value,
    'tan': QubeStdlib.tan_value,
    'log': QubeStdlib.log_value,
    'pow': QubeStdlib.pow_value,
    
    # 컬렉션 함수
    'len': QubeStdlib.len_value,
    'max': QubeStdlib.max_value,
    'min': QubeStdlib.min_value,
    'sum': QubeStdlib.sum_value,
    'range': QubeStdlib.range_value,
    
    # 랜덤 함수
    'random': QubeStdlib.random_value,
    'randomInt': QubeStdlib.random_int,
}

def get_stdlib_function(name):
    """표준 라이브러리 함수 반환"""
    return STDLIB_FUNCTIONS.get(name)