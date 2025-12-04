import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from analysis_module import AnalysisModule

def test_basic_function():
    """Тест базовой квадратичной функции"""
    analyzer = AnalysisModule()
    result = analyzer.analyze_function("x**2")
    
    assert "Функция: f(x) = x**2" in result
    assert "четная" in result
    assert "f'(x) = 2*x" in result

def test_trigonometric_function():
    """Тест тригонометрической функции"""
    analyzer = AnalysisModule()
    result = analyzer.analyze_function("sin(x)")
    
    assert "Функция: f(x) = sin(x)" in result
    assert "нечетная" in result
    assert "f'(x) = cos(x)" in result

def test_invalid_function():
    """Тест ошибки при некорректной функции"""
    analyzer = AnalysisModule()
    
    with pytest.raises(ValueError):
        analyzer.analyze_function("this_is_not_a_function")

def test_rational_function():
    """Тест рациональной функции с разрывом"""
    analyzer = AnalysisModule()
    result = analyzer.analyze_function("1/x")
    
    assert "x ≠ 0" in result or "не определена" in result
    assert "Функция: f(x) = 1/x" in result

def test_function_with_log():
    """Тест функции с логарифмом"""
    analyzer = AnalysisModule()
    result = analyzer.analyze_function("log(x)")
    
    assert "log" in result
    assert "Аргумент логарифма" in result or "не определена" in result

if __name__ == "__main__":
    # Простой запуск без pytest
    test_basic_function()
    print("test_basic_function пройден")
    
    test_trigonometric_function()
    print("test_trigonometric_function пройден")
    
    test_rational_function()
    print("test_rational_function пройден")
    
    print("Все тесты пройдены успешно!")