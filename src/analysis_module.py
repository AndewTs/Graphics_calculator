import sympy as sp
from sympy import diff, integrate, solve, limit
from sympy.calculus.util import continuous_domain

class AnalysisModule:
    def __init__(self):
        self.x = sp.Symbol('x')
        
    def analyze_function(self, func_text):
        try:
            expr = sp.sympify(func_text)
        except Exception as e:
            raise ValueError(f"Некорректное выражение функции: {str(e)}")
            
        result = "АНАЛИЗ ФУНКЦИИ:\n\n"
        result += f"Функция: f(x) = {expr}\n\n"
        
        # Область определения
        result += "ОБЛАСТЬ ОПРЕДЕЛЕНИЯ:\n"
        try:
            # Используем встроенную функцию continuous_domain для определения области определения
            domain = continuous_domain(expr, self.x, sp.S.Reals)
            
            if domain == sp.S.Reals:
                result += "Функция определена для всех действительных x\n"
            else:
                # Находим точки разрыва
                discontinuities = self.find_discontinuities(expr)
                if discontinuities:
                    result += f"Функция не определена в точках: {', '.join(discontinuities)}\n"
                    result += f"Область определения: {domain}\n"
                else:
                    result += f"Область определения: {domain}\n"
                    
        except Exception as e:
            result += f"Не удалось определить область определения: {str(e)}\n"
            
        # Точки пересечения с осями
        result += "\nТОЧКИ ПЕРЕСЕЧЕНИЯ:\n"
        
        # С осью Y (x=0)
        try:
            y_intercept = expr.subs(self.x, 0)
            if y_intercept.is_finite:
                result += f"С осью Y: (0, {y_intercept})\n"
            else:
                result += "С осью Y: функция не определена в x=0\n"
        except:
            result += "С осью Y: не определена\n"
            
        # С осью X (y=0)
        try:
            x_intercepts = solve(expr, self.x)
            real_roots = [root for root in x_intercepts if root.is_real]
            if real_roots:
                result += f"С осью X: {[f'({root}, 0)' for root in real_roots]}\n"
            else:
                result += "С осью X: нет действительных корней\n"
        except:
            result += "С осью X: не удалось найти корни\n"
            
        # Проверка на четность/нечетность
        result += "\nСВОЙСТВА СИММЕТРИИ:\n"
        try:
            f_neg_x = expr.subs(self.x, -self.x)
            
            if sp.simplify(expr - f_neg_x) == 0:
                result += "Функция четная (симметрична относительно оси Y)\n"
            elif sp.simplify(expr + f_neg_x) == 0:
                result += "Функция нечетная (симметрична относительно начала координат)\n"
            else:
                result += "Функция общего вида (ни четная, ни нечетная)\n"
        except:
            result += "Не удалось определить симметрию\n"
            
        # Пределы на бесконечности
        result += "\nПРЕДЕЛЫ НА БЕСКОНЕЧНОСТИ:\n"
        try:
            limit_plus_inf = limit(expr, self.x, sp.oo)
            limit_minus_inf = limit(expr, self.x, -sp.oo)
            result += f"lim(x→+∞) = {limit_plus_inf}\n"
            result += f"lim(x→-∞) = {limit_minus_inf}\n"
        except:
            result += "Не удалось вычислить пределы на бесконечности\n"
            
        # Пределы в точках разрыва
        result += "\nПРЕДЕЛЫ В ТОЧКАХ РАЗРЫВА:\n"
        try:
            discontinuities = self.find_discontinuities(expr)
            for point in discontinuities:
                try:
                    point_val = sp.sympify(point)
                    limit_left = limit(expr, self.x, point_val, dir='-')
                    limit_right = limit(expr, self.x, point_val, dir='+')
                    result += f"lim(x→{point}-) = {limit_left}, lim(x→{point}+) = {limit_right}\n"
                except:
                    result += f"Не удалось вычислить пределы в точке {point}\n"
        except:
            result += "Не удалось вычислить пределы в точках разрыва\n"
            
        # Производная
        result += "\nПРОИЗВОДНАЯ:\n"
        try:
            derivative = diff(expr, self.x)
            result += f"f'(x) = {derivative}\n"
        except:
            result += "Не удалось вычислить производную\n"
            
        # Вторая производная
        result += "\nВТОРАЯ ПРОИЗВОДНАЯ:\n"
        try:
            second_derivative = diff(expr, self.x, 2)
            result += f"f''(x) = {second_derivative}\n"
        except:
            result += "Не удалось вычислить вторую производную\n"
            
        # Интеграл
        result += "\nИНТЕГРАЛ:\n"
        try:
            integral = integrate(expr, self.x)
            result += f"∫f(x)dx = {integral} + C\n"
        except:
            result += "Не удалось вычислить интеграл\n"
            
        # Определенный интеграл на интервале [-5, 5]
        result += "\nОПРЕДЕЛЕННЫЙ ИНТЕГРАЛ:\n"
        try:
            definite_integral = integrate(expr, (self.x, -5, 5))
            result += f"∫f(x)dx от -5 до 5 = {definite_integral}\n"
        except:
            result += "Не удалось вычислить определенный интеграл\n"
            
        # Экстремумы на интервале [-10, 10]
        result += "\nЭКСТРЕМУМЫ НА ИНТЕРВАЛЕ [-10, 10]:\n"
        try:
            derivative = diff(expr, self.x)
            critical_points = solve(derivative, self.x)
            extremums = []
            for point in critical_points:
                if point.is_real and -10 <= float(point) <= 10:
                    y_value = expr.subs(self.x, point)
                    # Определяем тип экстремума по второй производной
                    try:
                        second_deriv = sp.diff(expr, self.x, 2).subs(self.x, point)
                        if second_deriv > 0:
                            extremum_type = "минимум"
                        elif second_deriv < 0:
                            extremum_type = "максимум"
                        else:
                            extremum_type = "точка перегиба"
                    except:
                        extremum_type = "экстремум (тип не определен)"
                    extremums.append((float(point), float(y_value), extremum_type))
            
            if extremums:
                for ext in extremums:
                    result += f"{ext[2]}: ({ext[0]:.2f}, {ext[1]:.2f})\n"
            else:
                result += "Экстремумы не найдены на заданном интервале\n"
        except:
            result += "Не удалось найти экстремумы\n"
            
        return result

    def find_discontinuities(self, expr):
        """Находит точки разрыва функции"""
        discontinuities = []
        
        # Находим точки, где знаменатель равен нулю
        try:
            # Получаем знаменатель выражения
            if expr.is_rational_function(self.x):
                denominator = expr.as_numer_denom()[1]
                denominator_roots = solve(denominator, self.x)
                for root in denominator_roots:
                    if root.is_real:
                        discontinuities.append(str(root))
        except:
            pass
        
        # Находим точки, где логарифмы не определены
        try:
            # Ищем все логарифмы в выражении
            logs = expr.atoms(sp.log)
            for log_func in logs:
                # Аргумент логарифма должен быть > 0
                arg = log_func.args[0]
                # Решаем неравенство arg <= 0
                try:
                    critical_points = solve(arg <= 0, self.x)
                    if critical_points:
                        for point in critical_points:
                            if hasattr(point, 'is_real') and point.is_real:
                                discontinuities.append(str(point))
                except:
                    pass
        except:
            pass
        
        # Находим точки, где корни четной степени не определены
        try:
            # Ищем корни четной степени
            for power in expr.atoms(sp.Pow):
                base, exp = power.as_base_exp()
                if exp.is_rational and not exp.is_integer:
                    # Для дробных степеней с четным знаменателем
                    p, q = exp.as_numer_denom()
                    if q % 2 == 0 and p % 2 != 0:  # Знаменатель четный
                        # Основание должно быть >= 0
                        try:
                            critical_points = solve(base < 0, self.x)
                            if critical_points:
                                for point in critical_points:
                                    if hasattr(point, 'is_real') and point.is_real:
                                        discontinuities.append(str(point))
                        except:
                            pass
        except:
            pass
        return list(set(discontinuities))