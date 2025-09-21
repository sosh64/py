from flask import Flask, request, render_template_string, url_for, session
import math
import random
import re
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")

# ---------- Global messages ----------
OWNER_MESSAGE = ""
GUEST_MESSAGE = ""

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

    .global-box { margin-top:12px; padding:10px; border-radius:6px; }
    .owner-msg { color:green; font-weight:bold; }
    .guest-msg { color:blue; font-weight:bold; }

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
    .command-row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
    .command-row input[type=text] { flex:1; min-width:150px; padding:12px; font-size:1.05em; border:1px solid #ccc; border-radius:6px; }
    .link-button { background:#000; color:#fff; display:flex; align-items:center; justify-content:center; gap:8px; padding:10px 12px; border-radius:6px; text-decoration:none; font-size:0.95em; min-width:48px; }
    .link-button svg { stroke:white; }
    .link-button:hover { background:#222; }

    .calc-button { margin-top:10px; width:100%; padding:12px; font-size:1em; border:none; border-radius:6px; background:#4CAF50; color:white; cursor:pointer; }
    .calc-button:hover { background:#45a049; }

    @media (max-width:768px) {
      .command-row { flex-direction:column; align-items:stretch; }
      .command-row .link-button { align-self:flex-end; }
      .output-pin-btn { display:flex; }
    }

    .small-note { display:block; margin-top:8px; color:#444; font-size:0.95em; word-break:break-word; }
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
      <span class="small-note">Check out my TikTok for easter eggs! Made by Giego :D</span>
    </div>

    <div class="output-wrap">
      <div id="output">{{ output|safe or "Welcome to Python Calculator!" }}</div>
      {% if owner_message %}
        <div class="global-box owner-msg">{{ owner_message }}</div>
      {% endif %}
      {% if guest_message %}
        <div class="global-box guest-msg">{{ guest_message }}</div>
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
        <a href="{{ url_for('updates') }}" class="link-button" title="View update logs" aria-label="View update logs">
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

    {% if audio %}
      <audio id="rickroll">
        <source src="{{ audio }}" type="audio/mp4">
      </audio>
      <script>
        function playRickroll(){ const audio = document.getElementById("rickroll"); audio.play().catch(()=>{alert("Click play to hear it!")}); }
      </script>
    {% endif %}
  </div>
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
        if op == '^':
            result = pow(a, b)
        elif op == '/' and b == 0:
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
        if not match_pow: break
        base, exponent = match_pow.group(1), match_pow.group(3)
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
            "pi": math.pi, "e": math.e
        })
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    global OWNER_MESSAGE, GUEST_MESSAGE
    output, audio = "", None

    if request.method == "POST":
        user_input = request.form.get("command", "").strip()
        cmd_lower = user_input.lower()

        if cmd_lower == "/q":
            output = "Session cleared."
        elif cmd_lower == "/credit":
            output = "This website is coded, created and owned by Giego"
        elif cmd_lower == "/f":
            output = random_math_fact()
        elif cmd_lower == "/e":
            output = random_math_equation()
        elif cmd_lower == "/n":
            output = str(random_number())
        elif cmd_lower == "potato":
            output = "🥔 Secret potato unlocked."
        elif cmd_lower == "lag":
            output = "[FAKE LAG SIMULATION]"
        elif cmd_lower == "67":
            audio = url_for('static', filename='rickroll.mp3.m4a')
            output = '<button onclick="playRickroll()" style="background:#ffbb00; color:black; padding:10px; border:none; border-radius:5px; cursor:pointer;">click here for mango 67 mustard phonk 😈</button>'
        elif cmd_lower == "/at102588":
            session["role"] = "owner"
            output = "You are now OWNER (Giego)."
        elif cmd_lower == "/at88":
            session["role"] = "guest"
            output = "You are now Guest Admin."
        elif user_input.startswith("gm ") and session.get("role") == "owner":
            OWNER_MESSAGE = f"Giego: {user_input[3:].strip()}"
            output = "Global message set (Owner)."
        elif user_input.startswith("/gb "):
            GUEST_MESSAGE = f"Guest: {user_input[4:].strip()}"
            output = "Global message set (Guest)."
        elif cmd_lower == "g$" and session.get("role") == "owner":
            OWNER_MESSAGE, GUEST_MESSAGE = "", ""
            output = "Global messages cleared."
        else:
            output = evaluate_expression(user_input)

    return render_template_string(
        html_template,
        output=output,
        audio=audio,
        owner_message=OWNER_MESSAGE,
        guest_message=GUEST_MESSAGE,
    )

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
            title, date, text_lines = lines[0], "", []
            if len(lines) >= 2 and lines[-1].lower().startswith("date"):
                date = lines[-1].split(":", 1)[1].strip() if ":" in lines[-1] else lines[-1]
                text_lines = lines[1:-1]
            else:
                text_lines = lines[1:]
            logs.append({"title": title, "text": "\n".join(text_lines).strip(), "date": date})
    else:
        logs = [{"title": "No updates yet", "text": "Create updates.txt in the app folder.", "date": ""}]

    template = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Update Logs</title>
<style>body{font-family:monospace;background:#f5f5f5;padding:20px}.container{max-width:600px;margin:auto;background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}h1{text-align:center;margin-bottom:20px}.log{border-bottom:1px solid #ddd;padding:10px 0}.log:last-child{border-bottom:none}.title{font-weight:bold;color:#333}.text{margin:5px 0;color:#555;white-space:pre-wrap}.date{font-size:0.85em;color:#888}a{display:inline-block;margin-top:15px;text-decoration:none;color:#4CAF50}</style>
</head><body><div class="container"><h1>Update Logs</h1>
{% for log in logs %}<div class="log"><div class="title">{{ log.title }}</div><div class="text">{{ log.text }}</div>{% if log.date %}<div class="date">Released: {{ log.date }}</div>{% endif %}</div>{% endfor %}
<a href="{{ url_for('index') }}">← Back to Calculator</a></div></body></html>"""
    return render_template_string(template, logs=logs)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)