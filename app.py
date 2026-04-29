from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Akshata@123",
    database="patient_monitoring"
)

cursor = db.cursor()

# HOME (LOGIN)
@app.route('/')
def home():
    return render_template("login.html")


#  LOGIN
@app.route('/login', methods=['POST'])
def login_check():
    username = request.form.get('username')
    password = request.form.get('password')

    query = "SELECT * FROM users WHERE username=%s AND password=%s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    if user:
        return redirect('/dashboard')
    else:
        return render_template("login.html", error="Invalid Username or Password ❌")


# SIGNUP
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')

    try:
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, password))
        db.commit()
        return render_template("login.html", success="Account Created ✅ Please Login")
    except:
        return render_template("login.html", error="Username already exists ❌")


#  DASHBOARD
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


#  ADD PATIENT
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():

    if request.method == "POST":

        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        bp = request.form['bp']
        hr = request.form['hr']
        temp = request.form['temp']

        try:
            bp_val = int(bp)
            hr_val = int(hr)
            temp_val = float(temp)

            if bp_val >= 140 or hr_val > 120 or temp_val > 100:
                alert = "HIGH RISK"
            elif bp_val >= 120 or hr_val > 100 or temp_val > 99:
                alert = "LOW RISK"
            else:
                alert = "NORMAL"

        except:
            alert = "INVALID"
            bp_val = 0
            hr_val = 0
            temp_val = 0

        query = """
        INSERT INTO patients (name, age, gender, bp, heart_rate, temperature, alert)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (name, age, gender, bp_val, hr_val, temp_val, alert)

        cursor.execute(query, values)
        db.commit()

        return redirect('/view_patients')

    return render_template("add_patient.html")


#  VIEW PATIENTS
@app.route('/view_patients')
def view_patients():

    cursor.execute("SELECT * FROM patients")
    data = cursor.fetchall()

    patients = []

    for row in data:
        patients.append({
            "id": row[0],   
            "name": row[1],
            "age": row[2],
            "gender": row[3],
            "bp": row[4],
            "hr": row[5],
            "temp": row[6],
            "alert": row[7] if row[7] else ""
        })

    return render_template("view_patients.html", patients=patients)


# PATIENT GRAPH

@app.route('/patient_graph/<int:id>')
def patient_graph(id):

    query = "SELECT * FROM patients WHERE id=%s"
    cursor.execute(query, (id,))
    patient = cursor.fetchone()

    if not patient:
        return "Invalid Patient ID"

    return render_template("patient_graph.html",
                           name=patient[1],
                           bp=patient[4],
                           hr=int(patient[5]),
                           temp=float(patient[6]),
                           id=id)


# SUGGESTION
@app.route('/suggest/<int:id>')
def suggest(id):

    query = "SELECT * FROM patients WHERE id=%s"
    cursor.execute(query, (id,))
    patient = cursor.fetchone()

    if not patient:
        return "Invalid ID"

    bp = int(patient[4])
    hr = int(patient[5])
    temp = float(patient[6])

    if bp >= 140 or hr > 120 or temp > 100:
        msg = "HIGH RISK - Consult Doctor"
        sym = "🔴"
    elif bp >= 120 or hr > 100 or temp > 99:
        msg = "LOW RISK - Take Care"
        sym = "🟡"
    else:
        msg = "NORMAL - Healthy"
        sym = "🟢"

    return render_template("suggest.html", msg=msg, sym=sym)


#  DELETE
@app.route('/delete/<int:id>')
def delete_patient(id):

    cursor.execute("DELETE FROM patients WHERE id=%s", (id,))
    db.commit()

    return redirect('/view_patients')


# UPDATE
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):

    cursor.execute("SELECT * FROM patients WHERE id=%s", (id,))
    patient = cursor.fetchone()

    if not patient:
        return "Invalid ID"

    if request.method == "POST":

        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        bp = request.form['bp']
        hr = request.form['hr']
        temp = request.form['temp']

        try:
            bp_val = int(bp)
            hr_val = int(hr)
            temp_val = float(temp)

            if bp_val >= 140 or hr_val > 120 or temp_val > 100:
                alert = "HIGH RISK"
            elif bp_val >= 120 or hr_val > 100 or temp_val > 99:
                alert = "LOW RISK"
            else:
                alert = "NORMAL"

        except:
            alert = "INVALID"
            bp_val = 0
            hr_val = 0
            temp_val = 0

        query = """
        UPDATE patients 
        SET name=%s, age=%s, gender=%s, bp=%s, heart_rate=%s, temperature=%s, alert=%s
        WHERE id=%s
        """

        values = (name, age, gender, bp_val, hr_val, temp_val, alert, id)

        cursor.execute(query, values)
        db.commit()

        return redirect('/view_patients')

    return render_template("update.html", p=patient)


#  RUN
if __name__ == "__main__":
    app.run(debug=True, port=5001)