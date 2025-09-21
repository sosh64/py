from flask import Flask, request, render_template_string, session
import math
import random
import re
import os
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

# ---------- Global state ----------
GLOBAL_MESSAGE = ""
SUPER_ADMIN_ID = None  # Track super admin

# ---------- Facts ----------
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

# ---------- Helpers ----------
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
    if expr.strip().replace(" ", "") == "10+9":
        return "Result: 21"
    try:
        result = eval(expr, {"__builtins__": None}, {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
            "factorial": math.factorial, "pow": pow,
            "pi": math.pi, "e": math.e, "__name__": "__main__"
        })
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"

# ---------- HTML ----------
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Python Calculator</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html,body { height:100%; width:100%; font-family: monospace, monospace; background:#f5f5f5; display:flex; justify-content:center; align-items:flex-start; padding:20px; }
    .container { width:100%; max-width:600px; background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.1); position:relative; }
    h1 { text-align:center; color:#333; margin-bottom:18px; }
    .output-wrap { position:relative; margin-bottom:12px; }
    #global { white-space: pre-wrap; background:#e8ffe8; border:1px solid #88cc88; padding:8px; margin-bottom:8px; border-radius:6px; font-weight:bold; }
    #output { white-space: pre-wrap; background:#f9f9f9; border:1px solid #ddd; padding:12px; height:200px; overflow-y:auto; border-radius:6px; }
    .green { color:#006600; }
    .blue { color:#0044cc; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Python Calculator</h1>
    <div class="output-wrap">
      <div id="global">{{ global_message|safe }}</div>
      <div id="output">{{ output|safe or "Welcome to Python Calculator!" }}</div>
    </div>
    <form method="POST">
      <input type="text" name="command" autofocus autocomplete="off" placeholder="Enter command or expression" style="width:100%;padding:12px;margin-bottom:10px;" />
      <button type="submit" style="width:100%;padding:12px;background:#4CAF50;color:white;border:none;border-radius:6px;cursor:pointer;">Calculate</button>
    </form>
  </div>
</body>
</html>
"""

# ---------- Routes ----------
@app.before_request
def ensure_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

@app.route("/", methods=["GET", "POST"])
def index():
    global GLOBAL_MESSAGE, SUPER_ADMIN_ID
    output = ""

    if request.method == "POST":
        user_input = request.form.get("command", "").strip()
        cmd_lower = user_input.lower()

        # --- ADMIN AUTH ---
        if cmd_lower == "/at102588":  # Owner Admin
            session["role"] = "owner"
            SUPER_ADMIN_ID = session["session_id"]
            output = "You are now OWNER admin."
        elif cmd_lower == "/at88":  # Guest Admin
            session["role"] = "guest_admin"
            output = "You are now GUEST admin."

        # --- OWNER COMMANDS ---
        elif cmd_lower == "8$" and session.get("role") == "owner":
            GLOBAL_MESSAGE = ""
            session["role"] = None
            output = "All admins removed and global cleared."
        elif cmd_lower == "ban$" and session.get("role") == "owner":
            SUPER_ADMIN_ID = session["session_id"]
            output = "You are now the only OWNER admin. Others removed."
        elif cmd_lower == "g$" and session.get("role") == "owner":
            GLOBAL_MESSAGE = ""
            output = "Global message cleared."
        elif cmd_lower.startswith("gm ") and session.get("role") == "owner":
            if SUPER_ADMIN_ID and SUPER_ADMIN_ID != session["session_id"]:
                output = "Only the super admin can send messages now."
            else:
                text = user_input[3:].strip()
                if text:
                    GLOBAL_MESSAGE = f"<span class='green'>Giego: {text}</span>"
                    output = "Global message set."

        # --- GUEST ADMIN COMMANDS ---
        elif cmd_lower.startswith("/gb "):
            text = user_input[4:].strip()
            if text:
                GLOBAL_MESSAGE = f"<span class='blue'>Guest: {text}</span>"
                output = "Guest message set."

        # --- NORMAL COMMANDS ---
        elif cmd_lower == "/q":
            output = "Session cleared."
        elif cmd_lower == "/credit":
            output = "This website is coded, created and owned by Giego"
        elif cmd_lower == "/f":
            output = random_math_fact()
        elif cmd_lower == "/e":
            output = random_math_equation()
        elif cmd_lower == "/n":
            output = str(random_number())
        else:
            output = evaluate_expression(user_input)

    return render_template_string(html_template, output=output, global_message=GLOBAL_MESSAGE)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)