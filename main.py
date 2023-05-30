import sqlite3
import telebot

class Calculator:
    def __init__(self):
        self.database = Database()
        self.expression = Expression()

    def calculate_expression(self, expr):
        if self.expression.is_valid(expr):
            result = self.expression.evaluate(expr)
            self.database.save_expression(expr, result)
            return result
        else:
            return "Expression is invalid"

    def get_previous_expressions(self):
        return self.database.get_all_expressions()

class Expression:
    def is_valid(self, expr):
        stack = []
        for char in expr:
            if char == '(':
                stack.append(char)
            elif char == ')':
                if len(stack) == 0 or stack[-1] != '(':
                    return False
                stack.pop()
        return len(stack) == 0

    def evaluate(self, expr):
        if self.is_valid(expr):
            return self._evaluate(expr)
        else:
            raise ValueError("Expression is invalid")

    def _evaluate(self, expr):
        # Рекурсивно вычисляем выражение
        if expr.isdigit():
            return int(expr)

        # Удаляем внешние скобки
        if expr[0] == '(' and expr[-1] == ')':
            expr = expr[1:-1]

        level = 0
        for i, char in enumerate(expr):
            if char == '(':
                level += 1
            elif char == ')':
                level -= 1
            elif level == 0 and char in ['+', '-']:
                left_expr = expr[:i]
                right_expr = expr[i+1:]
                if char == '+':
                    return self._evaluate(left_expr) + self._evaluate(right_expr)
                elif char == '-':
                    return self._evaluate(left_expr) - self._evaluate(right_expr)

        level = 0
        for i, char in enumerate(expr):
            if char == '(':
                level += 1
            elif char == ')':
                level -= 1
            elif level == 0 and char in ['*', '/']:
                left_expr = expr[:i]
                right_expr = expr[i+1:]
                if char == '*':
                    return self._evaluate(left_expr) * self._evaluate(right_expr)
                elif char == '/':
                    denominator = self._evaluate(right_expr)
                    if denominator == 0:
                        raise ZeroDivisionError("Divide by zero is fail")
                    return self._evaluate(left_expr) / denominator

        return self._evaluate(expr)

class Database:
    def __init__(self):
        self.connection = sqlite3.connect('expressions.db', check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expressions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expression TEXT,
                result REAL
            )
        ''')
        self.connection.commit()

    def save_expression(self, expr, result):
        self.cursor.execute('INSERT INTO expressions (expression, result) VALUES (?, ?)', (expr, result))
        self.connection.commit()

    def get_all_expressions(self):
        self.cursor.execute('SELECT * FROM expressions')
        return self.cursor.fetchall()

class TelegramBot:
    def __init__(self, calculator_token):
        self.calculator = Calculator()
        self.bot = telebot.TeleBot(calculator_token)

        @self.bot.message_handler(commands=['calculate'])
        def handle_calculate_message(message):
            expression = message.text.split(' ', 1)[1]
            try:
                result = self.calculator.calculate_expression(expression)
                self.bot.reply_to(message, f"Result: {result}")
            except Exception as e:
                self.bot.reply_to(message, f"Error: {str(e)}")

        @self.bot.message_handler(commands=['history'])
        def handle_history_message(message):
            expressions = self.calculator.get_previous_expressions()
            response = "Previous expressions:\n"
            for expr in expressions:
                response += f"{expr[0]}. {expr[1]} = {expr[2]}\n"
            self.bot.reply_to(message, response)

    def start(self):
        self.bot.polling()

if __name__ == '__main__':
    bot_token = 'TELEGRAM_API_TOKEN'
    bot = TelegramBot(bot_token)
    bot.start()
