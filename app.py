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
GLOBAL_MESSAGE = []  # list of global messages
ONLINE_USERS = {}    # session_id -> last_seen timestamp
GUEST_ADMINS = set() # track guest admin sessions

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
    .info { font-size:0.9em; color:#666; margin-bottom:12px; line-height:1.4; word-break: break-word; }
    .output-wrap { position:relative; margin-bottom:12px; }
    #output { white-space: pre-wrap; background:#f9f9f9; border:1px solid #ddd; padding:12px; height:200px; overflow-y:auto; border-radius:6px; }
    .output-pin-btn {
      position:absolute;
      right:10px;
      bottom:10px;
      background:#000;
      color:#fff;
      display:none;
      align-items:center;
      justify-content:center;
      gap:8px;
      padding:10px;
      border-radius:6px;
      text-decoration:none;
      font-size:0.95em;
      box-shadow:0 2px 6px rgba(0,0,0,0.15);
    }
    .output-pin-btn svg { stroke: white; }
    .command-area { margin-top: 0; }
    .command-row { display:flex; gap:10px; align-items:center; }
    .command-row input[type=text] { padding:12px; font-size:1.05em; border:1px solid #ccc; border-radius:6px; flex:1; }
    .link-button { background:#000; color:#fff; display:flex; align-items:center; justify-content:center; gap:8px; padding:10px 12px; border-radius:6px; text-decoration:none; font-size:0.95em; min-width:48px; }
    .link-button svg { stroke:white; }
    .link-button:hover { background:#222; }
    .calc-button { margin-top:10px; width:100%; padding:12px; font-size:1em; border:none; border-radius:6px; background:#4CAF50; color:white; cursor:pointer; }
    .calc-button:hover { background:#45a049; }
    @media (max-width:768px) {
      .command-row .link-button { display:none; }
      .output-pin-btn { display:flex; }
    }
    .small-note { display:block; margin-top:8px; color:#444; font-size:0.95em; word-break:break-word; }
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
      <b>/credit</b> - Show credits<br>
      <b>/q</b> - Quit (clears output)<br>
      <b>/f</b> - Random math fact<br>
      <b>/e</b> - Random math equation<br>
      <b>/n</b> - Random number<br>
      <b>/at102588</b> - Become Owner<br>
      <b>/at88</b> - Become Guest Admin<br>
      <span class="small-note">Check out my TikTok for easter eggs! Made by Giego :D</span>
    </div>
    <div class="output-wrap">
      <div id="output">{{ output|safe or "Welcome to Python Calculator!" }}</div>
      {% if global_messages %}
        {% for gm in global_messages %}
          <div class="global-message {{ gm.type }}">{{ gm.sender }}: {{ gm.text }}</div>
        {% endfor %}
      {% endif %}
      <a href="{{ url_for('updates') }}" class="output-pin-btn" aria-label="View update logs">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="23 4 23 10 17 10"></polyline>
          <polyline points="1 20 1 14 7 14"></polyline>
          <path d="M3.51 9a9 9 0 0114.36-3.36L23 10"></path>
          <path d="M20.49 15a9 9 0 01-14.36 3.36L1 14"></path>
        </svg>
      </a>
    </div>
    <form method="POST" class="command-area">
      <div class="command-row">
        <input type="text" name="command" autofocus autocomplete="off" placeholder="Enter command or expression" />
        <a href="{{ url_for('updates') }}" class="link-button" title="View update logs">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 4 23 10 17 10"></polyline>
            <polyline points="1 20 1 14 7 14"></polyline>
            <path d="M3.51 9a9 9 0 0114.36-3.36L23 10"></path>
            <path d="M20.49 15a9 9 0 01-14.36 3.36L1 14"></path>
          </svg>
        </a>
      </div>
      <button type="submit" class="calc-button">Calculate</button>
    </form>
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
    op = random.choice(['+', '-', '*', '/', '^'])
    equation = f"{a} {op} {b}"
    try:
        if op == '^':
            result = pow(a, b)
        else:
            result = eval(equation.replace('^', '**'))
    except Exception:
        result = "undefined"
    return f"{equation} = {result}"

def random_number():
    return random.randint(0, 10000)

def evaluate_expression(expr):
    expr = expr.replace('x', '*')
    expr = re.sub(r'(\d+(\.\d+)?)\s*%', r'(\1/100)', expr)
    if expr.strip().replace(" ", "") == "10+9":
        return "Result: 21"
    try:
        result = eval(expr, {"__builtins__": None}, {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
            "factorial": math.factorial, "pow": pow,
            "pi": math.pi, "e": math.e
        })
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"

# ---------- Routes ----------
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

@app.route("/", methods=["GET", "POST"])
def index():
    global GLOBAL_MESSAGE, GUEST_ADMINS
    output = ""
    if request.method == "POST":
        user_input = request.form.get("command", "").strip()
        cmd = user_input.lower()

        if cmd == "/q":
            output = "Session cleared."
        elif cmd == "/credit":
            output = "This website is coded, created and owned by Giego"
        elif cmd == "/f":
            output = random_math_fact()
        elif cmd == "/e":
            output = random_math_equation()
        elif cmd == "/n":
            output = str(random_number())
        elif cmd == "/at102588":
            session["role"] = "owner"
            output = "You are now Owner (Giego)."
        elif cmd == "/at88":
            session["role"] = "guest"
            GUEST_ADMINS.add(session["sid"])
            output = "You are now Guest Admin."
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
        else:
            output = evaluate_expression(user_input)

    return render_template_string(html_template, output=output, global_messages=GLOBAL_MESSAGE)

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
            if len(lines) >= 2 and lines[-1].lower().startswith("date"):
                date = lines[-1].split(":", 1)[-1].strip()
                text_lines = lines[1:-1]
            else:
                text_lines = lines[1:]
            logs.append({"title": title, "text": "\n".join(text_lines).strip(), "date": date})
    else:
        logs = [{"title": "No updates yet", "text": "There are no updates.", "date": ""}]
    template = """<!DOCTYPE html>
<html><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Update Logs</title>
<style>body{font-family:monospace;background:#f5f5f5;padding:20px}
.container{max-width:600px;margin:auto;background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}
h1{text-align:center;margin-bottom:20px}.log{border-bottom:1px solid #ddd;padding:10px 0}
.log:last-child{border-bottom:none}.title{font-weight:bold}.text{margin:5px 0;white-space:pre-wrap}.date{font-size:0.85em;color:#888}
a{display:inline-block;margin-top:15px;color:#4CAF50;text-decoration:none}</style></head>
<body><div class="container"><h1>Update Logs</h1>
{% for log in logs %}<div class="log"><div class="title">{{ log.title }}</div><div class="text">{{ log.text }}</div>{% if log.date %}<div class="date">Released: {{ log.date }}</div>{% endif %}</div>{% endfor %}
<a href="{{ url_for('index') }}">← Back</a></div></body></html>"""
    return render_template_string(template, logs=logs)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)