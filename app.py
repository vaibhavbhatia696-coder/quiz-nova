
from flask import Flask, render_template, redirect, url_for, session, request
import sqlite3
import random
from pathlib import Path

# ==================================================
# QUIZNOVA CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
    static_url_path="/static"
)

app.secret_key = "quiznova-change-this-secret-key"
DB_PATH = BASE_DIR / "quiznova.db"

TOTAL_LEVELS = 10
QUESTIONS_PER_LEVEL = 20
POINTS_PER_QUESTION = 5
POINTS_PER_LEVEL = QUESTIONS_PER_LEVEL * POINTS_PER_QUESTION

CATEGORIES = {
    "coding": "Coding & Programming",
    "analytics": "Data Analytics",
    "cyber": "Cyber Security"
}

LEVELS = {
    level: {
        "name": f"Level {level}",
        "time": 30 if level <= 3 else 25 if level <= 7 else 20
    }
    for level in range(1, TOTAL_LEVELS + 1)
}


# ==================================================
# QUESTION HELPERS
# Every question has:
# question, options, answer, explanation
# ==================================================

def make_question(question, options, answer, explanation):
    options = list(options)
    random.Random(question).shuffle(options)

    return (
        question,
        options,
        answer,
        explanation
    )


def build_coding_questions(level):
    """Create 20 different programming problems for this level."""

    n = level
    questions = []

    # 1. Arithmetic output
    a, b = 3 + n, 7 + n
    questions.append(make_question(
        f"Python mein a = {a}, b = {b}. print(a + b) ka output kya hoga?",
        [str(a + b), str(a * b), str(b - a), str(a - b)],
        str(a + b),
        "Addition operator + dono numbers ko add karta hai."
    ))

    # 2. Multiplication
    a, b = 2 + n, 4 + n
    questions.append(make_question(
        f"Python mein print({a} * {b}) ka output kya hoga?",
        [str(a * b), str(a + b), str(a ** b), str(b - a)],
        str(a * b),
        "Python ka * operator multiplication karta hai."
    ))

    # 3. Integer division
    a = 30 + n * 3
    b = 3 + (n % 4)
    answer = a // b
    questions.append(make_question(
        f"Python mein print({a} // {b}) kya print karega?",
        [str(answer), str(a / b), str(a % b), str(a * b)],
        str(answer),
        "// floor division hai, jo quotient ka floor deta hai."
    ))

    # 4. Modulo
    a = 17 + n * 2
    b = 3 + (n % 5)
    answer = a % b
    questions.append(make_question(
        f"Python expression {a} % {b} ka result kya hoga?",
        [str(answer), str(a // b), str(a + b), str(a * b)],
        str(answer),
        "% operator division ka remainder deta hai."
    ))

    # 5. String length
    word = ["python", "developer", "programming", "variable",
            "function", "database", "software", "iteration",
            "algorithm", "computer"][n - 1]
    questions.append(make_question(
        f"Python mein len('{word}') ka result kya hoga?",
        [str(len(word)), str(len(word) + 1), str(len(word) - 1), "0"],
        str(len(word)),
        "len() string ke characters count karta hai."
    ))

    # 6. List indexing
    values = [n, n + 4, n + 8, n + 12]
    questions.append(make_question(
        f"items = {values}. Python mein items[2] ki value kya hogi?",
        [str(values[2]), str(values[1]), str(values[0]), str(values[3])],
        str(values[2]),
        "Python indexing zero se start hoti hai."
    ))

    # 7. List slicing
    values = [n, n + 1, n + 2, n + 3, n + 4]
    answer = str(values[1:4])
    questions.append(make_question(
        f"values = {values}. values[1:4] ka result kya hoga?",
        [answer, str(values[1:3]), str(values[0:4]), str(values[2:5])],
        answer,
        "Slice mein starting index include aur ending index exclude hota hai."
    ))

    # 8. Boolean comparison
    a, b = n + 5, n + 8
    questions.append(make_question(
        f"Python expression {a} < {b} ka result kya hoga?",
        ["True", "False", "None", "Error"],
        "True",
        "Left value right value se chhoti hai."
    ))

    # 9. If/else
    number = n * 3
    answer = "Even" if number % 2 == 0 else "Odd"
    questions.append(make_question(
        f"number = {number}. Agar number % 2 == 0 ho to 'Even', warna 'Odd' print hota hai. Output?",
        ["Even", "Odd", "True", "Error"],
        answer,
        "Even numbers ka remainder 2 se divide karne par zero hota hai."
    ))

    # 10. For loop sum
    end = n + 3
    answer = str(sum(range(1, end + 1)))
    questions.append(make_question(
        f"total = 0; for i in range(1, {end + 1}): total += i. Final total?",
        [answer, str(end), str(end * 2), str(end ** 2)],
        answer,
        "Loop 1 se lekar range ke ending number se ek kam tak values add karta hai."
    ))

    # 11. List append
    original = [n, n + 2]
    questions.append(make_question(
        f"items = {original}; items.append({n + 5}). List kya banegi?",
        [str(original + [n + 5]), str(original), str([n + 5] + original),
         str(original + [n + 5, n + 6])],
        str(original + [n + 5]),
        "append() list ke end mein ek item add karta hai."
    ))

    # 12. Tuple property
    questions.append(make_question(
        f"Level {n} ke Python task mein coordinates = ({n}, {n + 1}) tuple diya hai. Tuple ki key property kya hai?",
        ["Immutable", "Always sorted", "Only strings store karta hai", "Duplicates allow nahi karta"],
        "Immutable",
        "Tuple ke existing elements ko directly modify nahi kar sakte."
    ))

    # 13. Dictionary lookup
    key = f"item{n}"
    value = n * 10
    questions.append(make_question(
        f"data = {{'{key}': {value}}}. data['{key}'] ka result kya hoga?",
        [str(value), repr(key), "None", str(n)],
        str(value),
        "Dictionary key se associated value return hoti hai."
    ))

    # 14. Function return
    x = n + 2
    y = n + 6
    questions.append(make_question(
        f"def add(a, b): return a + b. add({x}, {y}) kya return karega?",
        [str(x + y), str(x * y), str(y - x), "None"],
        str(x + y),
        "Function dono arguments ka sum return karta hai."
    ))

    # 15. Default arguments
    value = n + 10
    questions.append(make_question(
        f"def greet(name='Guest'): return name. greet() ka result kya hoga? (Example {value})",
        ["Guest", str(value), "None", "Error"],
        "Guest",
        "Argument nahi diya gaya to default value use hoti hai."
    ))

    # 16. Set uniqueness
    values = [n, n + 1, n, n + 2, n + 1]
    questions.append(make_question(
        f"Python mein set({values}) mein kitne unique elements honge?",
        ["3", "5", "4", "2"],
        "3",
        "Set duplicate values ko ek hi baar rakhta hai."
    ))

    # 17. Exception handling
    questions.append(make_question(
        f"Level {n}: Python mein zero se divide karne par kaunsa exception aata hai?",
        ["ZeroDivisionError", "ValueError", "IndexError", "KeyError"],
        "ZeroDivisionError",
        "Zero divisor ke saath numeric division ZeroDivisionError raise karta hai."
    ))

    # 18. OOP
    questions.append(make_question(
        f"Level {n} ke object-oriented programming task mein class ka primary purpose kya hai?",
        ["Objects ke attributes aur methods define karna",
         "Sirf loops chalana", "Internet connection banana",
         "Python interpreter install karna"],
        "Objects ke attributes aur methods define karna",
        "Class objects banane ka blueprint hoti hai."
    ))

    # 19. Recursion
    questions.append(make_question(
        f"Level {n} ke factorial program mein function apne aap ko call karta hai. Is technique ko kya kehte hain?",
        ["Recursion", "Inheritance", "Iteration only", "Encapsulation"],
        "Recursion",
        "Recursion mein function apne aap ko call karta hai."
    ))

    # 20. Algorithm complexity
    questions.append(make_question(
        f"Level {n} ke algorithm mein n elements ko ek baar scan kiya jata hai. Time complexity kya hai?",
        ["O(n)", "O(1)", "O(n²)", "O(2ⁿ)"],
        "O(n)",
        "Single pass mein operations input size ke proportional hote hain."
    ))

    return questions


def build_analytics_questions(level):
    """Create 20 different data analytics questions for this level."""

    n = level
    questions = []

    # 1. Mean
    values = [n, n + 2, n + 4]
    answer = str(sum(values) / len(values))
    questions.append(make_question(
        f"Dataset {values} ka mean kya hai?",
        [answer, str(sum(values)), str(max(values)), str(min(values))],
        answer,
        "Mean = sum of values / number of values."
    ))

    # 2. Median
    values = [n, n + 8, n + 3, n + 5, n + 2]
    sorted_values = sorted(values)
    answer = str(sorted_values[len(sorted_values) // 2])
    questions.append(make_question(
        f"Dataset {values} ka median kya hai?",
        [answer, str(min(values)), str(max(values)), str(sum(values))],
        answer,
        "Median ke liye data sort karke middle value lete hain."
    ))

    # 3. Range
    values = [n + 2, n + 9, n + 4, n + 1]
    answer = str(max(values) - min(values))
    questions.append(make_question(
        f"Dataset {values} ka range kya hai?",
        [answer, str(max(values)), str(min(values)), str(sum(values))],
        answer,
        "Range = maximum - minimum."
    ))

    # 4. Percentage change
    old = 100 + n * 10
    new = old + 20
    answer = f"{(new - old) / old * 100:.2f}%"
    questions.append(make_question(
        f"Sales {old} se {new} ho gayi. Percentage increase kitna hai?",
        [answer, "20%", "10%", "5%"],
        answer,
        "Percentage change = (new - old) / old × 100."
    ))

    # 5. Missing data
    questions.append(make_question(
        f"Level {n} ke customer dataset mein age column ke kuch values missing hain. Inhe handle karne ka valid approach kya hai?",
        ["Context ke hisaab se impute ya remove karna",
         "Har missing value ko bina check 0 banana",
         "Poora dataset hamesha delete karna",
         "Missing values ko column names banana"],
        "Context ke hisaab se impute ya remove karna",
        "Missing values ko data aur analysis objective ke according handle karna chahiye."
    ))

    # 6. Outlier
    questions.append(make_question(
        f"Level {n} ke income dataset mein mostly values 20,000–60,000 hain aur ek value 9,000,000 hai. Is unusual value ko kya kehte hain?",
        ["Outlier", "Median", "Foreign key", "Header"],
        "Outlier",
        "Outlier baaki observations se kaafi alag hota hai."
    ))

    # 7. Standard deviation
    questions.append(make_question(
        f"Level {n} mein do classes ke average marks equal hain, lekin Class A ka standard deviation kam hai. Iska kya meaning hai?",
        ["Class A ke marks mean ke aas-paas zyada clustered hain",
         "Class A ka mean zero hai",
         "Class A mein students nahi hain",
         "Dono classes ke marks identical hain"],
        "Class A ke marks mean ke aas-paas zyada clustered hain",
        "Lower standard deviation generally less spread indicate karta hai."
    ))

    # 8. Correlation
    questions.append(make_question(
        f"Level {n} ke study-hours aur marks data mein correlation +0.85 hai. Best interpretation kya hai?",
        ["Strong positive association",
         "Strong negative association",
         "No association at all",
         "Proof of causation"],
        "Strong positive association",
        "Positive correlation mein variables generally same direction mein move karte hain."
    ))

    # 9. Correlation limitation
    questions.append(make_question(
        f"Level {n} ke report mein ice-cream sales aur swimming incidents correlated hain. Sirf correlation se kya conclude nahi kar sakte?",
        ["That one necessarily causes the other",
         "That they are associated",
         "That both values can be measured",
         "That a correlation coefficient exists"],
        "That one necessarily causes the other",
        "Correlation alone causation establish nahi karti."
    ))

    # 10. Classification
    questions.append(make_question(
        f"Level {n} ke model ko email ko spam ya not spam label dena hai. Kaunsa ML task hai?",
        ["Classification", "Regression", "Clustering only", "Sorting"],
        "Classification",
        "Classification categorical labels predict karti hai."
    ))

    # 11. Regression
    questions.append(make_question(
        f"Level {n} mein house features se house ki sale price estimate karni hai. Kaunsa task suitable hai?",
        ["Regression", "Classification only", "Deduplication", "Encryption"],
        "Regression",
        "Sale price numeric target hai, isliye regression useful ho sakti hai."
    ))

    # 12. Grouping
    questions.append(make_question(
        f"Level {n} ke sales data mein har city ki total sales chahiye. Kaunsa analysis operation useful hai?",
        ["Group by city and aggregate sales",
         "Delete the city column",
         "Sort column names only",
         "Encrypt every row"],
        "Group by city and aggregate sales",
        "Grouping aur aggregation city-wise totals calculate karte hain."
    ))

    # 13. Visualization
    questions.append(make_question(
        f"Level {n} ke report mein 12 months ki sales trend dikhani hai. Kaunsa chart generally suitable hai?",
        ["Line chart", "Pie chart with one slice per row", "Network diagram", "Word cloud"],
        "Line chart",
        "Line chart time ke saath changes dikhane ke liye useful hai."
    ))

    # 14. Categories comparison
    questions.append(make_question(
        f"Level {n} ke dashboard mein 5 product categories ki sales compare karni hain. Best basic chart?",
        ["Bar chart", "Password table", "Flowchart", "Code editor"],
        "Bar chart",
        "Bar chart categories ke values compare karne mein useful hai."
    ))

    # 15. Data leakage
    questions.append(make_question(
        f"Level {n} ka prediction model training mein aisi information use karta hai jo prediction ke baad hi available hoti hai. Is problem ko kya kehte hain?",
        ["Data leakage", "Normalization", "Sampling", "Tokenization"],
        "Data leakage",
        "Data leakage model ko unrealistic information dekar evaluation distort kar sakta hai."
    ))

    # 16. Train/test split
    questions.append(make_question(
        f"Level {n} mein model ke unseen data par performance estimate karni hai. Kaunsa approach useful hai?",
        ["Separate test dataset",
         "Test set par hi model train karna",
         "Labels ko randomly delete karna",
         "Training score ko hamesha final maan lena"],
        "Separate test dataset",
        "Test data training mein use nahi hota aur generalization assess karta hai."
    ))

    # 17. Precision
    questions.append(make_question(
        f"Level {n} ke fraud model ne 20 transactions ko fraud flag kiya, jinmein 15 actual fraud the. Precision kya hai?",
        ["75%", "25%", "15%", "95%"],
        "75%",
        "Precision = true positives / all predicted positives = 15/20."
    ))

    # 18. Recall
    questions.append(make_question(
        f"Level {n} mein 40 actual fraud transactions the aur model ne unmein se 30 detect kiye. Recall kya hai?",
        ["75%", "30%", "40%", "25%"],
        "75%",
        "Recall = detected actual positives / all actual positives = 30/40."
    ))

    # 19. Normalization
    questions.append(make_question(
        f"Level {n} mein numerical features ki scales bahut different hain. Kuch algorithms ke liye kaunsa preprocessing useful ho sakta hai?",
        ["Feature scaling", "Duplicate row creation", "Column deletion without review", "Changing every value to a filename"],
        "Feature scaling",
        "Scaling numerical features ko comparable ranges mein la sakti hai."
    ))

    # 20. SQL aggregation
    questions.append(make_question(
        f"Level {n} ke SQL report mein har department ka employee count chahiye. Kaunsa function use kar sakte ho?",
        ["COUNT()", "LOWER()", "SUBSTRING()", "REPLACE() only"],
        "COUNT()",
        "COUNT() rows ya non-null values count kar sakta hai."
    ))

    return questions


def build_cyber_questions(level):
    """Create 20 different cyber security questions for this level."""

    n = level
    questions = []

    # 1. Phishing
    questions.append(make_question(
        f"Level {n}: Bank ke naam se email aata hai aur password verify karne ke liye unknown link deta hai. Safest action kya hai?",
        ["Link par click na karke official channel se verify karna",
         "Password turant enter karna",
         "Email sab colleagues ko forward karna",
         "Email ka password sender ko bhejna"],
        "Link par click na karke official channel se verify karna",
        "Unexpected links aur credential requests ko independently verify karna chahiye."
    ))

    # 2. MFA
    questions.append(make_question(
        f"Level {n} ke work account mein password ke saath authenticator approval bhi required hai. Ye kis control ka example hai?",
        ["Multi-factor authentication", "Single sign-on only", "File compression", "Data backup"],
        "Multi-factor authentication",
        "MFA alag types ke authentication factors use karta hai."
    ))

    # 3. Least privilege
    questions.append(make_question(
        f"Level {n} mein intern ko sirf reports read karni hain. Best access policy kya hai?",
        ["Sirf required read access dena",
         "Permanent administrator access dena",
         "Sab employees ke passwords share karna",
         "Logging disable karna"],
        "Sirf required read access dena",
        "Least privilege unnecessary permissions ko limit karta hai."
    ))

    # 4. Encryption
    questions.append(make_question(
        f"Level {n} ki application sensitive data ko disk par unreadable form mein store karti hai. Ye kis technique ka example hai?",
        ["Encryption at rest", "Plain-text logging", "Screen capture", "Data sorting"],
        "Encryption at rest",
        "Encryption at rest stored data ko protect karne mein madad karti hai."
    ))

    # 5. Hashing
    questions.append(make_question(
        f"Level {n} ke login system ko password verify karna hai bina plain-text password store kiye. Recommended approach kya hai?",
        ["Suitable password-hashing algorithm with salt",
         "Plain-text password file",
         "Reversible encoding only",
         "Password ko public database mein rakhna"],
        "Suitable password-hashing algorithm with salt",
        "Passwords ko modern password-hashing algorithms se salted hash ke roop mein store karna chahiye."
    ))

    # 6. Ransomware
    questions.append(make_question(
        f"Level {n} ke office computers ki files achanak encrypt ho gayi hain aur ransom note dikh raha hai. Likely incident kya hai?",
        ["Ransomware", "Normal software update", "Data visualization", "Password reset reminder"],
        "Ransomware",
        "Ransomware files ya systems ka access block karke payment demand kar sakta hai."
    ))

    # 7. Firewall
    questions.append(make_question(
        f"Level {n} ke network mein rules ke basis par incoming aur outgoing traffic allow/block karna hai. Kaunsa control useful hai?",
        ["Firewall", "Spreadsheet", "Compiler", "Image editor"],
        "Firewall",
        "Firewall configured network rules ke mutabik traffic filter karta hai."
    ))

    # 8. Patching
    questions.append(make_question(
        f"Level {n} ke server software mein known security vulnerability hai aur vendor patch available hai. Best next step?",
        ["Test karke patch ko promptly apply karna",
         "Vulnerability ko hamesha ignore karna",
         "Logs delete karna",
         "Sab users ko same password dena"],
        "Test karke patch ko promptly apply karna",
        "Timely patch management known vulnerabilities ka risk reduce karta hai."
    ))

    # 9. HTTPS
    questions.append(make_question(
        f"Level {n} ke website connection mein HTTPS certificate validation ka primary benefit kya hai?",
        ["Server identity verify karne aur connection encrypt karne mein madad",
         "Website ko malware-proof guarantee karna",
         "Har user ko administrator banana",
         "Backups automatically create karna"],
        "Server identity verify karne aur connection encrypt karne mein madad",
        "HTTPS transport encryption aur certificate-based server authentication provide karta hai."
    ))

    # 10. Backup
    questions.append(make_question(
        f"Level {n} ke company ko ransomware ke baad recovery chahiye. Kaunsa backup approach zyada resilient hai?",
        ["Regular tested backups, including isolated or offline copies",
         "Sirf same computer par ek copy",
         "Backups ko hamesha disabled rakhna",
         "Passwords ko documents mein save karna"],
        "Regular tested backups, including isolated or offline copies",
        "Isolated backups aur recovery testing restoration mein madad karte hain."
    ))

    # 11. Social engineering
    questions.append(make_question(
        f"Level {n} mein attacker phone par IT support bankar employee se OTP maangta hai. Ye kya hai?",
        ["Social engineering", "Load balancing", "Data normalization", "Version control"],
        "Social engineering",
        "Social engineering logon ko manipulate karke sensitive information ya access hasil karti hai."
    ))

    # 12. Public Wi-Fi
    questions.append(make_question(
        f"Level {n} mein public Wi-Fi par company resources access karne hain. Kaunsa practice safer hai?",
        ["Approved secure connection/VPN use karna aur certificate warnings verify karna",
         "Har certificate warning ignore karna",
         "Passwords openly share karna",
         "Automatic file sharing enable karna"],
        "Approved secure connection/VPN use karna aur certificate warnings verify karna",
        "Trusted secure connections aur warning validation risk reduce karte hain."
    ))

    # 13. SQL injection
    questions.append(make_question(
        f"Level {n} ki web app database query mein user input directly concatenate karti hai. Isse kaunsa risk ho sakta hai?",
        ["SQL injection", "Screen burn-in", "Image compression", "CPU cooling"],
        "SQL injection",
        "Untrusted input ko query mein concatenate karna SQL injection risk create kar sakta hai."
    ))

    # 14. SQL injection mitigation
    questions.append(make_question(
        f"Level {n} ke database code mein SQL injection risk reduce karna hai. Kaunsa approach recommended hai?",
        ["Parameterized queries",
         "Input ko SQL text ke saath concatenate karna",
         "Database errors users ko expose karna",
         "Authentication remove karna"],
        "Parameterized queries",
        "Parameterized queries data aur SQL instructions ko separate rakhti hain."
    ))

    # 15. XSS
    questions.append(make_question(
        f"Level {n} ki website untrusted user input ko safely encode kiye bina page par render karti hai. Kaunsa issue ho sakta hai?",
        ["Cross-site scripting (XSS)", "Disk fragmentation", "Power failure", "Data deduplication"],
        "Cross-site scripting (XSS)",
        "Unsafe rendering injected scripts ko browser mein execute karwa sakti hai."
    ))

    # 16. Secure permissions
    questions.append(make_question(
        f"Level {n} ke server par application files ko sabhi users writable nahi hona chahiye. Best practice kya hai?",
        ["Restrictive file permissions aur required service access",
         "Har file ko world-writable banana",
         "Passwords remove karna",
         "Audit logs disable karna"],
        "Restrictive file permissions aur required service access",
        "Minimum required file permissions unauthorized changes ka risk kam karti hain."
    ))

    # 17. Incident response
    questions.append(make_question(
        f"Level {n} mein suspected compromised company laptop mila. Initial response mein kya karna chahiye?",
        ["Incident response policy follow karke security team ko report aur isolate karna",
         "Evidence delete karna",
         "Sab files social media par upload karna",
         "Alert ko ignore karna"],
        "Incident response policy follow karke security team ko report aur isolate karna",
        "Prompt reporting aur controlled isolation incident ko contain karne mein madad karte hain."
    ))

    # 18. Logs
    questions.append(make_question(
        f"Level {n} ki security team failed logins aur suspicious access investigate kar rahi hai. Kaunsa source useful hai?",
        ["Authentication aur security logs",
         "Desktop wallpaper",
         "Monitor brightness setting",
         "Keyboard language only"],
        "Authentication aur security logs",
        "Logs events aur access attempts ki investigation mein madad karte hain."
    ))

    # 19. DDoS
    questions.append(make_question(
        f"Level {n} ki public website bahut zyada malicious traffic ki wajah se unavailable ho jati hai. Ye kis attack se match karta hai?",
        ["Distributed denial of service (DDoS)",
         "Password hashing",
         "Data cleaning",
         "Code formatting"],
        "Distributed denial of service (DDoS)",
        "DDoS service ko excessive distributed traffic se overwhelm karne ki koshish karta hai."
    ))

    # 20. Vulnerability scanning
    questions.append(make_question(
        f"Level {n} ke authorized security assessment mein known weaknesses identify karni hain. Kaunsa activity useful hai?",
        ["Authorized vulnerability scanning",
         "Unknown systems par unauthorized testing",
         "Security logs erase karna",
         "Passwords publicly post karna"],
        "Authorized vulnerability scanning",
        "Authorized scanning systems ki known vulnerabilities identify karne mein madad karti hai."
    ))

    return questions


# ==================================================
# BUILD BANK: 200 QUESTIONS PER CATEGORY
# 20 questions per level x 10 levels
# ==================================================

QUESTION_BUILDERS = {
    "coding": build_coding_questions,
    "analytics": build_analytics_questions,
    "cyber": build_cyber_questions
}


def build_question_bank():
    bank = {}

    for category, builder in QUESTION_BUILDERS.items():
        category_questions = []

        for level in range(1, TOTAL_LEVELS + 1):
            level_questions = builder(level)

            if len(level_questions) != QUESTIONS_PER_LEVEL:
                raise ValueError(
                    f"{category}, Level {level}: "
                    f"{QUESTIONS_PER_LEVEL} questions required, "
                    f"got {len(level_questions)}."
                )

            # Each level's questions should be unique.
            question_texts = [q[0] for q in level_questions]
            if len(question_texts) != len(set(question_texts)):
                raise ValueError(
                    f"Duplicate question found in {category}, "
                    f"Level {level}."
                )

            category_questions.extend(level_questions)

        bank[category] = category_questions

    return bank


QUESTION_BANK = build_question_bank()


# ==================================================
# DATABASE
# ==================================================

def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                category TEXT PRIMARY KEY,
                unlocked_level INTEGER NOT NULL DEFAULT 1,
                completed_levels TEXT NOT NULL DEFAULT ''
            )
        """)

        for category in CATEGORIES:
            db.execute("""
                INSERT OR IGNORE INTO progress
                (category, unlocked_level, completed_levels)
                VALUES (?, 1, '')
            """, (category,))


def get_progress():
    with get_db() as db:
        rows = db.execute("SELECT * FROM progress").fetchall()

    progress = {}

    for row in rows:
        progress[row["category"]] = {
            "unlocked_level": row["unlocked_level"],
            "completed_levels": [
                int(value)
                for value in row["completed_levels"].split(",")
                if value.strip().isdigit()
            ]
        }

    for category in CATEGORIES:
        progress.setdefault(category, {
            "unlocked_level": 1,
            "completed_levels": []
        })

    return progress


def complete_level(category, level):
    if category not in CATEGORIES or level not in LEVELS:
        return

    with get_db() as db:
        row = db.execute(
            "SELECT * FROM progress WHERE category = ?",
            (category,)
        ).fetchone()

        if row is None:
            return

        completed = [
            int(value)
            for value in row["completed_levels"].split(",")
            if value.strip().isdigit()
        ]

        if level not in completed:
            completed.append(level)

        unlocked = min(
            TOTAL_LEVELS,
            max(row["unlocked_level"], level + 1)
        )

        db.execute("""
            UPDATE progress
            SET unlocked_level = ?, completed_levels = ?
            WHERE category = ?
        """, (
            unlocked,
            ",".join(map(str, sorted(completed))),
            category
        ))


# ==================================================
# QUIZ HELPERS
# ==================================================

def get_level_questions(category, level):
    if category not in CATEGORIES or level not in LEVELS:
        return []

    start = (level - 1) * QUESTIONS_PER_LEVEL
    end = start + QUESTIONS_PER_LEVEL

    return QUESTION_BANK[category][start:end]


def create_quiz(category, level):
    if category not in CATEGORIES or level not in LEVELS:
        return False

    progress = get_progress()[category]

    if level > progress["unlocked_level"]:
        return False

    questions = get_level_questions(category, level)

    if len(questions) != QUESTIONS_PER_LEVEL:
        return False

    selected = random.sample(questions, QUESTIONS_PER_LEVEL)

    session["quiz_questions"] = selected
    session["quiz_answers"] = [""] * QUESTIONS_PER_LEVEL
    session["current_index"] = 0
    session["quiz_category"] = category
    session["quiz_level"] = level
    session["quiz_finished"] = False

    return True


# ==================================================
# INITIALIZE
# ==================================================

init_db()


# ==================================================
# HOME PAGE
# ==================================================

@app.route("/", endpoint="home")
def home():
    progress = get_progress()

    category_counts = {
        category: len(QUESTION_BANK[category])
        for category in CATEGORIES
    }

    return render_template(
        "index.html",
        categories=CATEGORIES,
        levels=LEVELS,
        total=sum(category_counts.values()),
        progress=progress,
        category_counts=category_counts,
        questions_per_level=QUESTIONS_PER_LEVEL,
        points_per_question=POINTS_PER_QUESTION,
        points_per_level=POINTS_PER_LEVEL
    )


app.add_url_rule(
    "/home",
    endpoint="index",
    view_func=lambda: redirect(url_for("home"))
)


# ==================================================
# QUIZ PAGE
# ==================================================

@app.route("/quiz", methods=["GET", "POST"], endpoint="quiz")
def start_quiz():
    if request.method == "POST":
        questions = session.get("quiz_questions", [])

        if not questions or session.get("quiz_finished"):
            return redirect(url_for("home"))

        index = session.get("current_index", 0)

        if not 0 <= index < len(questions):
            return redirect(url_for("result"))

        answers = session.get(
            "quiz_answers",
            [""] * len(questions)
        )

        answers[index] = request.form.get("answer", "").strip()
        session["quiz_answers"] = answers

        if index + 1 >= len(questions):
            session["quiz_finished"] = True
            return redirect(url_for("result"))

        session["current_index"] = index + 1
        return redirect(url_for("quiz"))

    category = request.args.get("category")
    level_raw = request.args.get("level")

    if category and level_raw:
        try:
            level = int(level_raw)
        except (TypeError, ValueError):
            return redirect(url_for("home"))

        if not create_quiz(category, level):
            return redirect(url_for("home"))

    elif (
        not session.get("quiz_questions")
        or session.get("quiz_finished")
    ):
        return redirect(url_for("home"))

    questions = session.get("quiz_questions", [])
    index = session.get("current_index", 0)

    if not questions or not 0 <= index < len(questions):
        return redirect(url_for("home"))

    category = session["quiz_category"]
    level = session["quiz_level"]
    current = questions[index]

    question_data = {
        "question": current[0],
        "options": current[1],
        "answer": current[2],
        "explanation": current[3]
    }

    return render_template(
        "quiz.html",
        question=question_data,
        number=index + 1,
        total=len(questions),
        time_limit=LEVELS[level]["time"],
        category_name=CATEGORIES[category],
        level_name=LEVELS[level]["name"],
        points_per_question=POINTS_PER_QUESTION
    )


# ==================================================
# RESULT PAGE
# ==================================================

@app.route("/result", endpoint="result")
def result():
    questions = session.get("quiz_questions", [])

    if not questions or not session.get("quiz_finished"):
        return redirect(url_for("home"))

    answers = session.get("quiz_answers", [])
    score = 0
    review = []

    for index, question in enumerate(questions):
        selected = answers[index] if index < len(answers) else ""
        correct = question[2]
        is_correct = selected == correct

        if is_correct:
            score += 1

        review.append({
            "number": index + 1,
            "question": question[0],
            "selected": selected,
            "correct": correct,
            "is_correct": is_correct,
            "explanation": question[3]
        })

    total = len(questions)
    percentage = round(score * 100 / total) if total else 0
    points_earned = score * POINTS_PER_QUESTION
    max_points = total * POINTS_PER_QUESTION

    if percentage >= 80:
        result_icon = "🏆"
        message = "Excellent work! You really know your stuff!"
    elif percentage >= 60:
        result_icon = "🎉"
        message = "Great effort! Keep learning and improving."
    elif percentage >= 40:
        result_icon = "💪"
        message = "Good attempt! Review your answers and try again."
    else:
        result_icon = "🌱"
        message = "Keep practicing. Every attempt helps you learn!"

    complete_level(
        session.get("quiz_category"),
        session.get("quiz_level")
    )

    return render_template(
        "result.html",
        score=score,
        total=total,
        percentage=percentage,
        result_icon=result_icon,
        message=message,
        review=review,
        points_earned=points_earned,
        max_points=max_points,
        points_per_question=POINTS_PER_QUESTION,
        category_name=CATEGORIES.get(
            session.get("quiz_category"), ""
        ),
        level_name=LEVELS.get(
            session.get("quiz_level"), {}
        ).get("name", "")
    )


# ==================================================
# RESTART QUIZ
# ==================================================

@app.route("/restart", endpoint="restart")
def restart():
    for key in (
        "quiz_questions",
        "quiz_answers",
        "current_index",
        "quiz_category",
        "quiz_level",
        "quiz_finished"
    ):
        session.pop(key, None)

    return redirect(url_for("home"))


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":
    print("QuizNova starting...")
    print("Categories:", len(CATEGORIES))
    print("Levels per category:", TOTAL_LEVELS)
    print("Questions per level:", QUESTIONS_PER_LEVEL)
    print("Question records per category:", len(QUESTION_BANK["coding"]))
    print("Total question records:", sum(len(q) for q in QUESTION_BANK.values()))
    print("Points per question:", POINTS_PER_QUESTION)
    print("Maximum points per level:", POINTS_PER_LEVEL)

    app.run(debug=True)
