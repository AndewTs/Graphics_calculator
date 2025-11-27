import sympy as sp

class AnalysisModule:
    def __init__(self):
        self.x = sp.Symbol('x')
        
    def analyze_function(self, func_text):
        try:
            # Пытаемся преобразовать строку в sympy выражение
            if '=' in func_text:
                # Если это уравнение, извлекаем левую часть
                func_text = func_text.split('=')[0].strip()
            
            expr = sp.sympify(func_text)
        except Exception as e:
            raise ValueError(f"Некорректное выражение функции: {str(e)}")
            
        result = "АНАЛИЗ ФУНКЦИИ:\n\n"
        result += f"Функция: f(x) = {expr}\n\n"
        
        # Область определения
        result += "ОБЛАСТЬ ОПРЕДЕЛЕНИЯ:\n"
        try:
            domain_issues = []
            
            # Проверяем знаменатели
            if expr.has(sp.Pow):
                for term in expr.args:
                    if term.is_Pow and term.exp.is_negative:
                        denominator = term.base
                        issues = sp.solve(denominator, self.x)
                        if issues:
                            domain_issues.extend([f"x ≠ {issue}" for issue in issues])
            
            # Проверяем логарифмы
            if expr.has(sp.log):
                for term in expr.args:
                    if term.func == sp.log:
                        arg = term.args[0]
                        # Решаем неравенство arg > 0
                        try:
                            solution = sp.solve_univariate_inequality(arg > 0, self.x, relational=False)
                            domain_issues.append(f"Для log: {solution}")
                        except:
                            domain_issues.append("Аргумент логарифма должен быть > 0")
            
            if domain_issues:
                result += f"Ограничения: {', '.join(set(domain_issues))}\n"
            else:
                result += "Функция определена для всех действительных x\n"
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
            x_intercepts = sp.solve(expr, self.x)
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
            limit_plus_inf = sp.limit(expr, self.x, sp.oo)
            limit_minus_inf = sp.limit(expr, self.x, -sp.oo)
            result += f"lim(x→+∞) = {limit_plus_inf}\n"
            result += f"lim(x→-∞) = {limit_minus_inf}\n"
        except:
            result += "Не удалось вычислить пределы на бесконечности\n"
            
        # Производная
        result += "\nПРОИЗВОДНАЯ:\n"
        try:
            derivative = sp.diff(expr, self.x)
            result += f"f'(x) = {derivative}\n"
        except:
            result += "Не удалось вычислить производную\n"
            
        # Вторая производная
        result += "\nВТОРАЯ ПРОИЗВОДНАЯ:\n"
        try:
            second_derivative = sp.diff(expr, self.x, 2)
            result += f"f''(x) = {second_derivative}\n"
        except:
            result += "Не удалось вычислить вторую производную\n"
            
        # Интеграл
        result += "\nИНТЕГРАЛ:\n"
        try:
            integral = sp.integrate(expr, self.x)
            result += f"∫f(x)dx = {integral} + C\n"
        except:
            result += "Не удалось вычислить интеграл\n"
            
        # Определенный интеграл на интервале [-5, 5] для примера
        result += "\nОПРЕДЕЛЕННЫЙ ИНТЕГРАЛ:\n"
        try:
            definite_integral = sp.integrate(expr, (self.x, -5, 5))
            result += f"∫f(x)dx от -5 до 5 = {definite_integral}\n"
        except:
            result += "Не удалось вычислить определенный интеграл\n"
            
        # Экстремумы на интервале [-10, 10]
        result += "\nЭКСТРЕМУМЫ НА ИНТЕРВАЛЕ [-10, 10]:\n"
        try:
            derivative = sp.diff(expr, self.x)
            critical_points = sp.solve(derivative, self.x)
            extremums = []
            for point in critical_points:
                if point.is_real and -10 <= float(point) <= 10:
                    y_value = expr.subs(self.x, point)
                    # Определяем тип экстремума по второй производной
                    second_deriv = sp.diff(expr, self.x, 2).subs(self.x, point)
                    if second_deriv > 0:
                        extremum_type = "минимум"
                    elif second_deriv < 0:
                        extremum_type = "максимум"
                    else:
                        extremum_type = "точка перегиба"
                    extremums.append((float(point), float(y_value), extremum_type))
            
            if extremums:
                for ext in extremums:
                    result += f"{ext[2]}: ({ext[0]:.2f}, {ext[1]:.2f})\n"
            else:
                result += "Экстремумы не найдены на заданном интервале\n"
        except:
            result += "Не удалось найти экстремумы\n"
            
        return result