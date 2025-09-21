from flask import Flask, request, render_template_string, url_for, session
import math, random, re, os, time, uuid

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

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
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Python Calculator</title>
  <style>
    * { box-sizing: border-box; margin:0; padding:0; }
    html,body { font-family:monospace,monospace; background:#f5f5f5;
                display:flex; justify-content:center; align-items:flex-start; padding:20px; }
    .container { width:100%; max-width:650px; background:#fff; padding:20px;
                 border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.1); }
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
      <q>made by Giego :D</q>
      <a href="{{ url_for('updates') }}">View Update Logs</a>
    </div>
    <div id="output">{{ output|safe or "Welcome to Python Calculator!" }}</div>
    {% if global_messages %}
      {% for gm in global_messages %}
        <div class="global-message {{ gm.type }}">{{ gm.sender }}: {{ gm.text }}</div>
      {% endfor %}
    {% endif %}
    <form method="POST">
      <input type="text" name="command" autofocus autocomplete="off"
             placeholder="Enter command or expression" />
      <button type="submit">Calculate</button>
    </form>
    {% if audio %}
    <audio id="rickroll" autoplay>
      <source src="{{ audio }}" type="audio/mp4">
    </audio>
    <script>
      function playRickroll(){ 
        const a=document.getElementById("rickroll");
        a.play().catch(()=>a.setAttribute("controls","true"));
      }
    </script>
    {% endif %}
  </div>
</body>
</html>"""

# ---------- Helpers ----------
def random_math_fact(): return random.choice(facts)

def random_math_equation():
    a, b = random.randint(1,20), random.randint(1,20)
    op = random.choice(['+','-','*','/','^'])
    expr = f"{a} {op} {b}"
    try:
        res = pow(a,b) if op=="^" else eval(expr.replace("^","**"))
    except: res="undefined"
    return f"{expr} = {res}"

def random_number(): return random.randint(0,10000)

def handle_power(expression):
    while '^' in expression:
        match = re.search(r'(\d+(\.\d+)?|\([^()]+\))\s*\^\s*(\d+(\.\d+)?|\([^()]+\))', expression)
        if not match: break
        base, exp = match.group(1), match.group(3)
        expression = expression[:match.start()] + f"pow({base},{exp})" + expression[match.end():]
    return expression

def evaluate_expression(expr):
    expr = expr.replace("x","*")
    expr = re.sub(r'(\d+(\.\d+)?)\s*%', r'(\1/100)', expr)
    expr = handle_power(expr)
    if expr.replace(" ","")=="10+9": return "Result: 21"
    try:
        res = eval(expr, {"__builtins__":None},{
            "sin":math.sin,"cos":math.cos,"tan":math.tan,"sqrt":math.sqrt,
            "log":math.log,"log10":math.log10,"factorial":math.factorial,
            "pow":pow,"pi":math.pi,"e":math.e
        })
        return f"Result: {res}"
    except Exception as e: return f"Error: {e}"

def simulate_lag():
    fake = [
      "[ERROR] Unauthorized access from 127.0.0.1",
      "[WARNING] Math core breached!",
      "[INFO] Rebooting π-module...",
      "[CRITICAL] Fibonacci sequence looping infinitely!",
      "[TRACE] Injecting golden ratio... █▒▒▒▒▒▒▒▒▒▒",
      "[MATRIX] 0101010101010101 💥",
      "[HACK] Deploying potato virus 🥔...",
      "💀 System compromised... Just kidding. Back to math!"
    ]
    return "\n".join(fake)

# ---------- Tracking ----------
@app.before_request
def track_users():
    sid = session.get("sid")
    if not sid:
        sid = str(uuid.uuid4()); session["sid"]=sid
    ONLINE_USERS[sid]=time.time()
    cutoff=time.time()-300
    for k in list(ONLINE_USERS.keys()):
        if ONLINE_USERS[k]<cutoff: del ONLINE_USERS[k]

# ---------- Routes ----------
@app.route("/", methods=["GET","POST"])
def index():
    global GLOBAL_MESSAGE, GUEST_ADMINS
    output, audio = "", None
    if request.method=="POST":
        user_input=request.form.get("command","").strip()
        cmd_lower=user_input.lower()

        if cmd_lower=="/q": output="Session cleared."
        elif cmd_lower=="/f": output=random_math_fact()
        elif cmd_lower=="/e": output=random_math_equation()
        elif cmd_lower=="/n": output=str(random_number())
        elif cmd_lower=="/at102588": session["role"]="owner"; output="You are now Owner."
        elif cmd_lower=="/at88": session["role"]="guest"; GUEST_ADMINS.add(session["sid"]); output="You are now Guest Admin."
        elif cmd_lower==")&":
            role=session.pop("role",None)
            if role=="owner": output="Your Owner role has been removed."
            elif role=="guest": GUEST_ADMINS.discard(session["sid"]); output="Your Guest Admin role has been removed."
            else: output="You have no role."
        elif cmd_lower.startswith("gm ") and session.get("role")=="owner":
            GLOBAL_MESSAGE.append({"sender":"Owner","text":user_input[3:].strip(),"type":"gm-owner"})
            output="Global message set by Owner."
        elif cmd_lower.startswith("/gb ") and session.get("sid") in GUEST_ADMINS:
            GLOBAL_MESSAGE.append({"sender":"Guest","text":user_input[4:].strip(),"type":"gm-guest"})
            output="Global message set by Guest."
        elif cmd_lower=="g$" and session.get("role")=="owner":
            GLOBAL_MESSAGE.clear(); output="All global messages cleared."
        elif cmd_lower=="?pc" and session.get("role")=="owner":
            output=f"{len(ONLINE_USERS)} players online"
        elif cmd_lower=="ban$" and session.get("role")=="owner":
            GUEST_ADMINS.clear(); output="All Guest Admins banned."
        elif cmd_lower=="potato":
            output="🥔 You've unlocked the secret potato! May your calculations be crispy and golden."
        elif cmd_lower=="lag":
            output=simulate_lag()
        elif cmd_lower=="67":
            audio=url_for("static",filename="rickroll.mp3.m4a")
            output="""<button onclick="playRickroll()" 
            style="background:#ffbb00;color:black;padding:10px 15px;
                   border:none;border-radius:5px;cursor:pointer;font-size:16px;">
                   click here for mango 67 mustard phonk 😈</button>"""
        else:
            output=evaluate_expression(user_input)

    return render_template_string(html_template, output=output,
                                  global_messages=GLOBAL_MESSAGE, audio=audio)

@app.route("/updates")
def updates():
    updates_file=os.path.join(os.path.dirname(__file__),"updates.txt")
    logs=[]
    try:
        with open(updates_file,"r",encoding="utf-8") as f: raw=f.read().strip()
    except FileNotFoundError: raw=""
    if raw:
        blocks=[b.strip() for b in raw.split("\n\n") if b.strip()]
        for b in blocks:
            lines=[ln.rstrip() for ln in b.splitlines() if ln.strip()]
            title=lines[0] if lines else ""; date=""; text_lines=[]
            if len(lines)>=2 and lines[-1].lower().startswith("date"):
                date=lines[-1].split(":",1)[-1].strip() if ":" in lines[-1] else lines[-1]
                text_lines=lines[1:-1]
            else: text_lines=lines[1:]
            logs.append({"title":title,"text":"\n".join(text_lines).strip(),"date":date})
    else:
        logs=[{"title":"No updates yet","text":"There are no update entries. Create updates.txt in the app folder.","date":""}]

    template="""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>Update Logs</title>
    <style>body{font-family:monospace;background:#f5f5f5;padding:20px}
    .container{max-width:600px;margin:auto;background:#fff;padding:20px;border-radius:8px;
               box-shadow:0 2px 10px rgba(0,0,0,0.1)}
    h1{text-align:center;margin-bottom:20px}.log{border-bottom:1px solid #ddd;padding:10px 0}
    .log:last-child{border-bottom:none}.title{font-weight:bold;color:#333}
    .text{margin:5px 0;color:#555;white-space:pre-wrap}
    .date{font-size:0.85em;color:#888}
    a{display:inline-block;margin-top:15px;text-decoration:none;color:#4CAF50}
    </style></head><body><div class="container"><h1>Update Logs</h1>
    {% for log in logs %}<div class="log"><div class="title">{{log.title}}</div>
    <div class="text">{{log.text}}</div>{% if log.date %}<div class="date">Released: {{log.date}}</div>{% endif %}</div>
    {% endfor %}<a href="{{ url_for('index') }}">← Back to Calculator</a></div></body></html>"""
    return render_template_string(template, logs=logs)

if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)