import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np

# Имитируем метод из mpl_widget.py
def _split_into_segments(x_vals, y_vals):
    """Разбивает данные на непрерывные сегменты, разделяя в точках разрыва"""
    segments = []
    current_segment_x = []
    current_segment_y = []
    
    for i in range(len(x_vals)):
        if not np.isnan(y_vals[i]):
            current_segment_x.append(x_vals[i])
            current_segment_y.append(y_vals[i])
        else:
            if current_segment_x:
                segments.append((current_segment_x, current_segment_y))
                current_segment_x = []
                current_segment_y = []
    
    if current_segment_x:
        segments.append((current_segment_x, current_segment_y))
        
    return segments

def test_split_continuous():
    """Тест для непрерывной функции"""
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]  # x**2
    
    segments = _split_into_segments(x, y)
    
    assert len(segments) == 1
    assert segments[0][0] == x
    assert segments[0][1] == y
    print("test_split_continuous пройден")

def test_split_with_gap():
    """Тест для функции с разрывом"""
    x = [0, 1, 2, 3, 4]
    y = [0, 1, np.nan, 9, 16]  # Разрыв в x=2
    
    segments = _split_into_segments(x, y)
    
    assert len(segments) == 2
    assert segments[0][0] == [0, 1]  # Первый сегмент
    assert segments[0][1] == [0, 1]
    assert segments[1][0] == [3, 4]  # Второй сегмент
    assert segments[1][1] == [9, 16]
    print("test_split_with_gap пройден")

def test_split_multiple_gaps():
    """Тест для функции с несколькими разрывами"""
    x = [0, 1, 2, 3, 4, 5, 6]
    y = [0, 1, np.nan, 3, np.nan, 5, 6]  # Разрывы в x=2 и x=4
    
    segments = _split_into_segments(x, y)
    
    assert len(segments) == 3
    print("test_split_multiple_gaps пройден")

def test_split_all_nan():
    """Тест для функции, которая везде NaN"""
    x = [0, 1, 2, 3]
    y = [np.nan, np.nan, np.nan, np.nan]
    
    segments = _split_into_segments(x, y)
    
    assert len(segments) == 0
    print("test_split_all_nan пройден")

if __name__ == "__main__":
    test_split_continuous()
    test_split_with_gap()
    test_split_multiple_gaps()
    test_split_all_nan()
    print("Все тесты сегментации пройдены!")