from flask import Flask, request, render_template_string, url_for, session
import math
import random
import re
import os
import uuid
import time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

# ---------- Globals ----------
GLOBAL_MESSAGE = []
ONLINE_USERS = {}
GUEST_ADMINS = set()

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

# ---------- HTML ----------
html_template = """
<!DOCTYPE html>
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
    .info { font-size:0.9em; color:#666; margin-bottom:12px; line-height:1.4; word-break: break-word; }
    #output { white-space: pre-wrap; background:#f9f9f9; border:1px solid #ddd; padding:12px; height:200px; overflow-y:auto; border-radius:6px; margin-bottom:12px; }
    .command-row { display:flex; gap:10px; align-items:center; }
    .command-row input[type=text] { padding:12px; font-size:1.05em; border:1px solid #ccc; border-radius:6px; flex:1; }
    .calc-button { margin-top:10px; width:100%; padding:12px; font-size:1em; border:none; border-radius:6px; background:#4CAF50; color:white; cursor:pointer; }
    .calc-button:hover { background:#45a049; }
    .global-message { margin-top:10px; padding:6px; border-radius:4px; font-weight:bold; }
    .gm-owner { color:green; }
    .gm-guest { color:blue; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Python Calculator</h1>
    <div class="info">
      <strong>Commands:</strong><br>
      <b>/q</b> - Quit (clears output)<br>
      <b>/f</b> - Random math fact<br>
      <b>/e</b> - Random math equation<br>
      <b>/n</b> - Random number<br>
      <br>
      <span>More commands hidden as easter eggs 👀</span><br>
      <b>Made by Giego :D</b>
    </div>
    <div id="output">{{ output|safe or "Welcome to Python Calculator!" }}</div>
    {% if global_messages %}
      {% for gm in global_messages %}
        <div class="global-message {{ gm.type }}">{{ gm.sender }}: {{ gm.text }}</div>
      {% endfor %}
    {% endif %}
    <form method="POST" class="command-area">
      <div class="command-row">
        <input type="text" name="command" autofocus autocomplete="off" placeholder="Enter command or expression" />
      </div>
      <button type="submit" class="calc-button">Calculate</button>
    </form>
    {% if audio %}
    <audio id="rickroll" autoplay>
      <source src="{{ audio }}" type="audio/mp4">
    </audio>
    <script>
      const audio = document.getElementById("rickroll");
      audio.play().catch(() => { audio.setAttribute("controls", "true"); });
    </script>
    {% endif %}
  </div>
</body>
</html>
"""

# ---------- Helpers ----------
def random_math_fact():
    return random.choice(facts)

def random_math_equation():
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    op = random.choice(["+", "-", "*", "/", "^"])
    try:
        if op == "^":
            result = a ** b
        elif op == "/":
            result = "undefined" if b == 0 else round(a / b, 6)
        elif op == "*":
            result = a * b
        elif op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        else:
            result = "undefined"
        return f"{a} {op} {b} = {result}"
    except Exception:
        return f"{a} {op} {b} = undefined"

def random_number():
    return random.randint(0, 10000)

def handle_power(expression: str) -> str:
    while "^" in expression:
        match_pow = re.search(r'(\d+(\.\d+)?|\([^()]+\))\s*\^\s*(\d+(\.\d+)?|\([^()]+\))', expression)
        if not match_pow:
            break
        base = match_pow.group(1)
        exponent = match_pow.group(3)
        replacement = f'pow({base}, {exponent})'
        expression = expression[:match_pow.start()] + replacement + expression[match_pow.end():]
    return expression

def evaluate_expression(expr: str) -> str:
    expr = expr.strip().lower()

    # Easter eggs
    if expr == "potato":
        return "🥔 You've unlocked the secret potato! May your calculations be crispy and golden."
    if expr.replace(" ", "") == "10+9":
        return "Result: 21"

    expr = expr.replace("x", "*")
    expr = re.sub(r'(\d+(\.\d+)?)\s*%', r'(\1/100)', expr)
    expr = handle_power(expr)

    try:
        result = eval(expr, {"__builtins__": None}, {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
            "factorial": math.factorial, "pow": pow,
            "pi": math.pi, "e": math.e
        })
        if isinstance(result, float):
            result = round(result, 6)
        return f"Result: {result}"
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception:
        return "Error: Invalid expression"

def simulate_lag():
    fake_data = [
        "[ERROR] Unauthorized access from 127.0.0.1",
        "[WARNING] Math core breached!",
        "[INFO] Rebooting π-module...",
        "[CRITICAL] Fibonacci sequence looping infinitely!",
        "[TRACE] Injecting golden ratio... █▒▒▒▒▒▒▒▒▒▒",
        "[MATRIX] 0101010101010101 💥",
        "[HACK] Deploying potato virus 🥔...",
    ]
    return "\n".join(fake_data + ["💀 System compromised... Just kidding. Back to math!"])

# ---------- Track Users ----------
@app.before_request
def track_users():
    sid = session.get("sid")
    if not sid:
        sid = str(uuid.uuid4())
        session["sid"] = sid
    ONLINE_USERS[sid] = time.time()
    cutoff = time.time() - 300
    for k in list(ONLINE_USERS.keys()):
        if ONLINE_USERS[k] < cutoff:
            del ONLINE_USERS[k]

# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def index():
    global GLOBAL_MESSAGE, GUEST_ADMINS
    output, audio = "", None

    if request.method == "POST":
        user_input = request.form.get("command", "").strip()
        cmd = user_input.lower()

        # --- Public Commands ---
        if cmd == "/q":
            output = "Session cleared."
        elif cmd == "/f":
            output = random_math_fact()
        elif cmd == "/e":
            output = random_math_equation()
        elif cmd == "/n":
            output = str(random_number())

        # --- Hidden Admin Commands ---
        elif cmd == "/at102588":
            session["role"] = "owner"
            output = "You are now Owner (Giego)."
        elif cmd == "/at88":
            session["role"] = "guest"
            GUEST_ADMINS.add(session["sid"])
            output = "You are now Guest Admin."
        elif cmd == ")&":
            if session.get("role") == "owner":
                session.pop("role", None)
                output = "Your Owner role has been removed."
            elif session.get("role") == "guest":
                session.pop("role", None)
                GUEST_ADMINS.discard(session["sid"])
                output = "Your Guest Admin role has been removed."
            else:
                output = "You have no role to remove."
        elif cmd.startswith("gm ") and session.get("role") == "owner":
            GLOBAL_MESSAGE.append({"sender": "Giego", "text": user_input[3:].strip(), "type": "gm-owner"})
            output = "Global message set by Owner."
        elif cmd.startswith("/gb ") and session.get("sid") in GUEST_ADMINS:
            GLOBAL_MESSAGE.append({"sender": "Guest", "text": user_input[4:].strip(), "type": "gm-guest"})
            output = "Global message set by Guest."
        elif cmd == "g$" and session.get("role") == "owner":
            GLOBAL_MESSAGE.clear()
            output = "All global messages cleared."
        elif cmd == "?pc" and session.get("role") == "owner":
            output = f"{len(ONLINE_USERS)} players online"
        elif cmd == "ban$" and session.get("role") == "owner":
            GUEST_ADMINS.clear()
            output = "All Guest Admins have been banned. They must re-enter /at88."

        # --- Hidden Fun Easter Eggs ---
        elif cmd == "lag":
            output = simulate_lag()
        elif user_input == "67":
            output = "🎶 Never gonna give you up..."
            audio = url_for("static", filename="rickroll.mp3.m4a")

        # --- Math Eval ---
        else:
            output = evaluate_expression(user_input)

    return render_template_string(html_template, output=output, audio=audio, global_messages=GLOBAL_MESSAGE)

# ---------- Main ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)