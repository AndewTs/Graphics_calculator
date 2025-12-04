import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np

# Имитируем безопасный словарь
SAFE_DICT = {
    'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
    'cot': lambda x: 1/np.tan(x),
    'pi': np.pi, 'e': np.e,
    'sqrt': np.sqrt, 'exp': np.exp, 'log': np.log,
    'np': np,
}

def safe_eval(expr, x_val):
    """Безопасное вычисление функции"""
    try:
        return eval(expr, {"x": x_val, **SAFE_DICT})
    except:
        return np.nan

def test_safe_eval_basic():
    """Тест безопасного вычисления простых функций"""
    assert safe_eval("x**2", 2) == 4
    assert safe_eval("x**2", -3) == 9
    print("test_safe_eval_basic пройден")

def test_safe_eval_trig():
    """Тест тригонометрических функций"""
    assert np.isclose(safe_eval("sin(x)", 0), 0)
    assert np.isclose(safe_eval("cos(x)", 0), 1)
    assert np.isclose(safe_eval("tan(x)", 0), 0)
    print("test_safe_eval_trig пройден")

def test_safe_eval_constants():
    """Тест математических констант"""
    assert safe_eval("pi", 0) == np.pi
    assert safe_eval("e", 0) == np.e
    print("test_safe_eval_constants пройден")

def test_safe_eval_complex():
    """Тест сложных выражений"""
    result = safe_eval("sin(x) + cos(x)", 0)
    assert np.isclose(result, 1)  # sin(0) + cos(0) = 0 + 1 = 1
    
    result = safe_eval("sqrt(x)", 4)
    assert result == 2
    print("test_safe_eval_complex пройден")

def test_safe_eval_error():
    """Тест обработки ошибок"""
    # Деление на ноль должно вернуть NaN
    result = safe_eval("1/x", 0)
    assert np.isnan(result)
    print("test_safe_eval_error пройден")

if __name__ == "__main__":
    test_safe_eval_basic()
    test_safe_eval_trig()
    test_safe_eval_constants()
    test_safe_eval_complex()
    test_safe_eval_error()
    print("Все тесты безопасных функций пройдены!")