from flask import Flask, request, render_template_string, url_for, session
import ast
import operator as op
import math
import random
import re
import os
import time
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

# ---------- Globals ----------
GLOBAL_MESSAGE = []       # list of {"sender","text","type"}
ONLINE_USERS = {}         # sid -> last_seen
GUEST_ADMINS = set()      # session sid set

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

# ---------- HTML (with locked Update Logs button) ----------
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Python Calculator</title>
  <style>
    * { box-sizing: border-box; margin:0; padding:0; }
    html,body { font-family:monospace,monospace; background:#f5f5f5;
                display:flex; justify-content:center; align-items:flex-start; padding:20px; height:100%; }
    .container { width:100%; max-width:650px; background:#fff; padding:20px;
                 border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.1); position:relative; }
    h1 { text-align:center; color:#333; margin-bottom:18px; }
    .info { font-size:0.9em; color:#444; margin-bottom:12px; line-height:1.5; }
    #output { white-space:pre-wrap; background:#f9f9f9; border:1px solid #ddd;
              padding:12px; height:200px; overflow-y:auto; border-radius:6px; margin-bottom:12px; }
    input[type=text] { width:100%; padding:12px; font-size:1.05em;
                       border:1px solid #ccc; border-radius:6px; }
    button { margin-top:10px; width:100%; padding:12px; font-size:1em; border:none;
             border-radius:6px; background:#4CAF50; color:white; cursor:pointer; }
    button:hover { background:#45a049; }
    .global-message { margin-top:6px; padding:6px; border-radius:4px; font-weight:bold; }
    .gm-owner { color:green; }
    .gm-guest { color:blue; }

    /* LOCKED update logs button: always visible inside container, bottom-right */
    .update-logs-btn {
      position: absolute;
      right: 16px;
      bottom: 16px;
      background:#000;
      color:#fff;
      display:flex;
      align-items:center;
      justify-content:center;
      gap:8px;
      padding:8px 12px;
      border-radius:6px;
      text-decoration:none;
      font-size:0.95em;
      box-shadow:0 2px 8px rgba(0,0,0,0.12);
    }
    .update-logs-btn svg { stroke: white; }
    .update-logs-btn:hover { background:#222; }

    /* small note */
    .small-note { display:block; margin-top:8px; color:#444; font-size:0.95em; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Python Calculator</h1>

    <div class="info">
      <strong>Commands:</strong><br>
      <b>/q</b> - Quit (clear output)<br>
      <b>/f</b> - Random math fact<br>
      <b>/e</b> - Random math equation<br>
      <b>/n</b> - Random number<br>
      <b>/at102588</b> - Become Owner<br>
      <b>/at88</b> - Become Guest Admin<br>
      <b>)&</b> - Remove your role<br>
      <b>gm ...</b> - Global message (Owner)<br>
      <b>/gb ...</b> - Global message (Guest Admin)<br>
      <b>g$</b> - Clear global messages (Owner)<br>
      <b>?pc</b> - Show online users (Owner)<br>
      <b>ban$</b> - Ban all Guest Admins (Owner)<br>
      <br>
      <span class="small-note">More commands are hidden as easter eggs (potato, lag, 10+9, 67). Made by Giego :D</span>
    </div>

    <div id="output">{{ output|safe or "Welcome to Python Calculator!" }}</div>

    {% if global_messages %}
      {% for gm in global_messages %}
        <div class="global-message {{ gm.type }}">{{ gm.sender }}: {{ gm.text }}</div>
      {% endfor %}
    {% endif %}

    <form method="POST" autocomplete="off">
      <input type="text" name="command" autofocus autocomplete="off" placeholder="Enter command or expression" />
      <button type="submit">Calculate</button>
    </form>

    <!-- locked update logs button: always visible bottom-right inside container -->
    <a href="{{ url_for('updates') }}" class="update-logs-btn" aria-label="View update logs">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
           stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <polyline points="23 4 23 10 17 10"></polyline>
        <polyline points="1 20 1 14 7 14"></polyline>
        <path d="M3.51 9a9 9 0 0114.36-3.36L23 10"></path>
        <path d="M20.49 15a9 9 0 01-14.36 3.36L1 14"></path>
      </svg>
      Update Logs
    </a>

    {% if audio %}
      <audio id="rickroll" preload="none">
        <source src="{{ audio }}" type="audio/mp4">
      </audio>
      <script>
        function playRickroll(){
          const a = document.getElementById("rickroll");
          if(!a) return;
          a.play().catch(()=> a.setAttribute("controls","true"));
        }
      </script>
    {% endif %}
  </div>
</body>
</html>
"""

# ---------- Safe math evaluator (AST-based) ----------
# Allowed binary operators mapping
ALLOWED_BINOPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.FloorDiv: op.floordiv,
}

ALLOWED_UNARYOPS = {
    ast.UAdd: lambda x: +x,
    ast.USub: lambda x: -x,
}

# Allowed functions (lowercase keys)
ALLOWED_FUNCS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "factorial": math.factorial,
    "pow": pow,
    "abs": abs,
    "round": round,
}

ALLOWED_NAMES = {
    "pi": math.pi,
    "e": math.e
}


def _convert_percent(expr: str) -> str:
    return re.sub(r'(\d+(\.\d+)?)\s*%', r'(\1/100)', expr)


def _normalize_power(expr: str) -> str:
    return expr.replace("^", "**")


def _eval_ast(node):
    if isinstance(node, ast.Constant):  # Python 3.8+
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Unsupported constant")
    if isinstance(node, ast.Num):  # older nodes
        return node.n

    if isinstance(node, ast.BinOp):
        left = _eval_ast(node.left)
        right = _eval_ast(node.right)
        op_type = type(node.op)
        if op_type not in ALLOWED_BINOPS:
            raise ValueError("Operator not allowed")
        # protect pow/large exponents
        if isinstance(node.op, ast.Pow):
            if isinstance(right, (int, float)) and abs(right) > 1000:
                raise ValueError("Exponent too large")
        return ALLOWED_BINOPS[op_type](left, right)

    if isinstance(node, ast.UnaryOp):
        op_t = type(node.op)
        if op_t not in ALLOWED_UNARYOPS:
            raise ValueError("Unary operator not allowed")
        val = _eval_ast(node.operand)
        return ALLOWED_UNARYOPS[op_t](val)

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls allowed")
        func_name = node.func.id.lower()
        if func_name not in ALLOWED_FUNCS:
            raise ValueError(f"Function '{func_name}' not allowed")
        func = ALLOWED_FUNCS[func_name]
        args = [_eval_ast(a) for a in node.args]
        # Factorial safety
        if func_name == "factorial":
            if len(args) != 1 or not isinstance(args[0], int) or args[0] < 0 or args[0] > 1000:
                raise ValueError("factorial requires integer 0..1000")
        return func(*args)

    if isinstance(node, ast.Name):
        name = node.id.lower()
        if name in ALLOWED_NAMES:
            return ALLOWED_NAMES[name]
        raise ValueError(f"Name '{node.id}' not allowed")

    raise ValueError("Unsupported expression element")


def safe_eval(expr: str):
    if not expr or not expr.strip():
        raise ValueError("Empty expression")
    expr = _convert_percent(expr)
    expr = _normalize_power(expr)

    try:
        parsed = ast.parse(expr, mode="eval")
    except SyntaxError:
        raise ValueError("Syntax error")

    # Small whitelist of allowed node types
    allowed_nodes = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
                     ast.Call, ast.Name, ast.Load, ast.Add, ast.Sub, ast.Mult,
                     ast.Div, ast.Mod, ast.Pow, ast.FloorDiv, ast.UAdd, ast.USub)
    for node in ast.walk(parsed):
        if not isinstance(node, allowed_nodes):
            raise ValueError("Unsupported expression element")

    return _eval_ast(parsed.body)


def format_result(res):
    if isinstance(res, float):
        r = round(res, 8)
        if r.is_integer():
            return str(int(r))
        else:
            # strip trailing zeros
            s = ("{:.8f}".format(r)).rstrip("0").rstrip(".")
            return s
    return str(res)


# ---------- Utility helpers ----------
def random_math_fact():
    return random.choice(facts)


def random_math_equation():
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    op = random.choice(["+", "-", "*", "/", "^"])
    if op == "^":
        if b > 10:
            result = "big"
        else:
            result = pow(a, b)
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


def random_number():
    return random.randint(0, 10000)


def simulate_lag():
    lines = [
        "[ERROR] Unauthorized access from 127.0.0.1",
        "[WARNING] Math core breached!",
        "[INFO] Rebooting π-module...",
        "[CRITICAL] Fibonacci sequence looping infinitely!",
        "[TRACE] Injecting golden ratio... █▒▒▒▒▒▒▒▒▒▒",
        "[MATRIX] 0101010101010101 💥",
        "[HACK] Deploying potato virus 🥔...",
        "💀 System compromised... Just kidding. Back to math!"
    ]
    return "\n".join(lines)


# ---------- Tracking ----------
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
    output = ""
    audio = None

    if request.method == "POST":
        user_input = request.form.get("command", "").strip()
        cmd_lower = user_input.lower()

        # Public commands
        if cmd_lower == "/q":
            output = "Session cleared."
        elif cmd_lower == "/f":
            output = random_math_fact()
        elif cmd_lower == "/e":
            output = random_math_equation()
        elif cmd_lower == "/n":
            output = str(random_number())

        # Admin commands (hidden)
        elif cmd_lower == "/at102588":
            session["role"] = "owner"
            output = "You are now Owner."
        elif cmd_lower == "/at88":
            session["role"] = "guest"
            GUEST_ADMINS.add(session["sid"])
            output = "You are now Guest Admin."
        elif cmd_lower == ")&":
            role = session.pop("role", None)
            if role == "owner":
                output = "Your Owner role has been removed."
            elif role == "guest":
                GUEST_ADMINS.discard(session["sid"])
                output = "Your Guest Admin role has been removed."
            else:
                output = "You have no role."
        elif cmd_lower.startswith("gm ") and session.get("role") == "owner":
            GLOBAL_MESSAGE.append({"sender": "Owner", "text": user_input[3:].strip(), "type": "gm-owner"})
            output = "Global message set by Owner."
        elif cmd_lower.startswith("/gb ") and session.get("sid") in GUEST_ADMINS:
            GLOBAL_MESSAGE.append({"sender": "Guest", "text": user_input[4:].strip(), "type": "gm-guest"})
            output = "Global message set by Guest."
        elif cmd_lower == "g$" and session.get("role") == "owner":
            GLOBAL_MESSAGE.clear()
            output = "All global messages cleared."
        elif cmd_lower == "?pc" and session.get("role") == "owner":
            output = f"{len(ONLINE_USERS)} players online"
        elif cmd_lower == "ban$" and session.get("role") == "owner":
            GUEST_ADMINS.clear()
            output = "All Guest Admins banned."

        # Easter eggs (hidden)
        elif cmd_lower == "potato":
            output = "🥔 You've unlocked the secret potato! May your calculations be crispy and golden."
        elif cmd_lower == "lag":
            output = simulate_lag()
        elif cmd_lower == "67":
            audio = url_for("static", filename="rickroll.mp3.m4a")
            output = (
                '<button onclick="playRickroll()" style="background:#ffbb00;color:black;padding:10px 15px;'
                'border:none;border-radius:5px;cursor:pointer;font-size:16px;">'
                'click here for mango 67 mustard phonk 😈</button>'
            )

        # Math expression (safe)
        else:
            # special easter egg exact match (ignore whitespace)
            if user_input.replace(" ", "") == "10+9":
                output = "Result: 21"
            else:
                try:
                    value = safe_eval(user_input)
                    output = "Result: " + format_result(value)
                except ValueError as e:
                    output = "Error: " + str(e)
                except Exception as e:
                    output = "Error: Invalid expression"

    return render_template_string(html_template, output=output, audio=audio, global_messages=GLOBAL_MESSAGE)


@app.route("/updates")
def updates():
    updates_file = os.path.join(os.path.dirname(__file__), "updates.txt")
    logs = []
    try:
        with open(updates_file, "r", encoding="utf-8") as f:
            raw = f.read().strip()
    except FileNotFoundError:
        raw = ""

    if raw:
        blocks = [b.strip() for b in raw.split("\n\n") if b.strip()]
        for b in blocks:
            lines = [ln.rstrip() for ln in b.splitlines() if ln.strip()]
            title = lines[0] if lines else ""
            date = ""
            text_lines = []
            if len(lines) >= 2:
                last = lines[-1]
                if last.lower().startswith("date"):
                    if ":" in last:
                        date = last.split(":", 1)[1].strip()
                    else:
                        date = last
                    text_lines = lines[1:-1]
                else:
                    text_lines = lines[1:]
            logs.append({"title": title, "text": "\n".join(text_lines).strip(), "date": date})
    else:
        logs = [{"title": "No updates yet", "text": "There are no update entries. Create updates.txt in the app folder.", "date": ""}]

    template = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Update Logs</title>
<style>body{font-family:monospace;background:#f5f5f5;padding:20px}
.container{max-width:600px;margin:auto;background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}
h1{text-align:center;margin-bottom:20px}.log{border-bottom:1px solid #ddd;padding:10px 0}
.log:last-child{border-bottom:none}.title{font-weight:bold;color:#333}
.text{margin:5px 0;color:#555;white-space:pre-wrap}.date{font-size:0.85em;color:#888}
a{display:inline-block;margin-top:15px;text-decoration:none;color:#4CAF50}</style></head>
<body><div class="container"><h1>Update Logs</h1>
{% for log in logs %}<div class="log"><div class="title">{{log.title}}</div>
<div class="text">{{log.text}}</div>{% if log.date %}<div class="date">Released: {{log.date}}</div>{% endif %}</div>{% endfor %}
<a href="{{ url_for('index') }}">← Back to Calculator</a></div></body></html>"""
    return render_template_string(template, logs=logs)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)