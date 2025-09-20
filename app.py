from flask import Flask, request, render_template_string
import math
import random
import re
import sys
import time

app = Flask(__name__)

facts = [
    "Zero is the only number that can't be represented in Roman numerals.",
    "A circle has infinite lines of symmetry.",
    "Pi has been calculated to over 62 trillion digits.",
    "A googol is 10 to the power of 100.",
    "The Fibonacci sequence appears in nature, like in pinecones and sunflowers.",
    "An icosagon is a shape with 20 sides.",
    "There are infinitely many prime numbers.",
    "The number e is approximately 2.718 and is the base of natural logarithms.",
    "A perfect number is a number equal to the sum of its proper divisors (e.g., 28).",
    "The Pythagorean theorem only works in right-angled triangles.",
    "A palindrome number reads the same backward and forward (e.g., 121, 1331).",
    "The square root of 2 is irrational and cannot be written as a simple fraction.",
    "In base 2 (binary), only 1s and 0s are used to represent numbers.",
    "The golden ratio is approximately 1.618 and appears in art, architecture, and nature.",
    "A Möbius strip has only one surface and one edge.",
    "There are more real numbers between 0 and 1 than all whole numbers combined.",
    "The number 9 is known as a 'magic number' in many multiplication tricks.",
    "Euler’s identity combines five fundamental constants: e^(iπ) + 1 = 0.",
    "Kaprekar’s constant (6174) always appears in a specific subtraction trick.",
    "A prime number has exactly two distinct factors: 1 and itself.",
    "The sum of all angles in a triangle is always 180 degrees (in Euclidean geometry).",
    "You can tile a plane using only three regular polygons: triangles, squares, and hexagons.",
    "Infinity is not a number — it’s a concept representing something without end.",
    "The factorial of a number n (n!) is the product of all positive integers ≤ n.",
    "Magic squares are grids where the numbers in each row, column, and diagonal add up to the same total.",
    "An ellipse is the set of points where the sum of distances to two foci is constant."
]

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Calculator</title>
    <style>
        body { font-family: monospace, monospace; background: #f5f5f5; padding: 20px; max-width: 600px; margin: auto; }
        h1 { text-align: center; color: #333; }
        #output { white-space: pre-wrap; background: #fff; border: 1px solid #ddd; padding: 10px; height: 300px; overflow-y: auto; margin-bottom: 10px; }
        input[type=text] { width: 100%; padding: 10px; font-size: 1.1em; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
        .info { color: #666; font-size: 0.9em; margin-bottom: 10px; }
        button { margin-top: 10px; padding: 10px 20px; font-size: 1em; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Python Calculator</h1>
    <div class="info">
        Commands:<br>
        <b>/q</b> - Quit (clears output)<br>
        <b>/f</b> - Random math fact<br>
        <b>/e</b> - Random math equation<br>
        <b>/n</b> - Random number<br>
        <q> check out my tiktok for easter eggs!<q>
        <b>this was made by Giego :D</b>
    </div>
    <div id="output">{{ output }}</div>
    <form method="POST">
        <input type="text" name="command" autofocus autocomplete="off" placeholder="Enter command or expression" />
        <button type="submit">Calculate</button>
    </form>
</body>
</html>
"""

def random_math_fact():
    return random.choice(facts)

def random_math_equation():
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    op = random.choice(['+', '-', '*', '/', '^'])
    equation = f"{a} {op} {b}"

    try:
        if '^' in equation:
            base, exponent = map(float, equation.split('^'))
            result = pow(base, exponent)
        else:
            # For division, handle zero division gracefully
            if op == '/' and b == 0:
                result = "undefined"
            else:
                result = eval(equation.replace('^', '**'))
    except Exception:
        result = "undefined"
    return f"{equation} = {result}"

def random_number():
    return random.randint(0, 10000)

def handle_power(expression):
    while '^' in expression:
        match_pow = re.search(r'(\d+(\.\d+)?|\([^()]+\))\s*\^\s*(\d+(\.\d+)?|\([^()]+\))', expression)
        if not match_pow:
            break
        base = match_pow.group(1)
        exponent = match_pow.group(3)
        replacement = f'pow({base}, {exponent})'
        expression = expression[:match_pow.start()] + replacement + expression[match_pow.end():]
    return expression

def evaluate_expression(expr):
    expr = expr.replace('x', '*')
    expr = re.sub(r'(\d+(\.\d+)?)\s*%', r'(\1/100)', expr)
    expr = handle_power(expr)

    try:
        result = eval(expr, {"__builtins__": None}, {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "sqrt": math.sqrt,
            "log": math.log,
            "log10": math.log10,
            "factorial": math.factorial,
            "pow": pow,
            "pi": math.pi,
            "e": math.e,
            "__name__": "__main__"
        })
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"

def simulate_lag():
    # simulate lag and fake data output (as text)
    fake_data = [
        "[ERROR] Unauthorized access from 127.0.0.1",
        "[WARNING] Math core breached!",
        "[INFO] Rebooting π-module...",
        "[CRITICAL] Fibonacci sequence looping infinitely!",
        "[TRACE] Injecting golden ratio... █▒▒▒▒▒▒▒▒▒▒",
        "[MATRIX] 0101010101010101 💥",
        "[HACK] Deploying potato virus 🥔...",
    ]
    lines = []
    for line in fake_data:
        lines.append(line)
    lines.append("💀 System compromised... Just kidding. Back to math! ")
    return "\n".join(lines)

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
        user_input = request.form.get("command", "").strip().lower()
        if user_input == "/q":
            output = "Session cleared."
        elif user_input == "/f":
            output = random_math_fact()
        elif user_input == "/e":
            output = random_math_equation()
        elif user_input == "/n":
            output = str(random_number())
        elif user_input == "potato":
            output = "🥔 You've unlocked the secret potato! May your calculations be crispy and golden."
        elif user_input == "lag":
            output = simulate_lag()
        else:
            # Support for x= or x = assignment expressions (from your original)
            if user_input.startswith('x=') or user_input.startswith('x ='):
                try:
                    rhs = user_input.split('=')[1].strip()
                    x_val = eval(rhs, {"__builtins__": None}, {
                        "sin": math.sin,
                        "cos": math.cos,
                        "tan": math.tan,
                        "sqrt": math.sqrt,
                        "log": math.log,
                        "log10": math.log10,
                        "factorial": math.factorial,
                        "pow": pow,
                        "pi": math.pi,
                        "e": math.e,
                        "__name__": "__main__"
                    })
                    output = f"x = {x_val}"
                except Exception as e:
                    output = f"Error: {e}"
            elif user_input.startswith('x -'):
                parts = user_input.split('=')
                if len(parts) == 2:
                    left, right = parts[0].strip(), parts[1].strip()
                    try:
                        sub_val = left[3:].strip()
                        sub_val_eval = eval(sub_val, {"__builtins__": None}, {
                            "sin": math.sin,
                            "cos": math.cos,
                            "tan": math.tan,
                            "sqrt": math.sqrt,
                            "log": math.log,
                            "log10": math.log10,
                            "factorial": math.factorial,
                            "pow": pow,
                            "pi": math.pi,
                            "e": math.e,
                            "__name__": "__main__"
                        })
                        right_val = eval(right, {"__builtins__": None}, {
                            "sin": math.sin,
                            "cos": math.cos,
                            "tan": math.tan,
                            "sqrt": math.sqrt,
                            "log": math.log,
                            "log10": math.log10,
                            "factorial": math.factorial,
                            "pow": pow,
                            "pi": math.pi,
                            "e": math.e,
                            "__name__": "__main__"
                        })
                        x_val = right_val + sub_val_eval
                        output = f"x = {x_val}"
                    except Exception as e:
                        output = f"Error: {e}"
                else:
                    output = "Invalid input."
            else:
                output = evaluate_expression(user_input)

    return render_template_string(html_template, output=output)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
