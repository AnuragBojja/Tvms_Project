from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime
import random

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'U-UxfWC8WccUwKeCNNxVbMHr1z4sXT5TPoSyJPnlVnY'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Anurag'
app.config['MYSQL_DB'] = 'TVMS'



# Initialize MySQL
mysql = MySQL(app)

# Home Route
@app.route('/')
def home():
    if 'loggedin' in session:
        # Redirect based on user type
        if session['user_type'] == 'officer':
            return redirect(url_for('officer_dashboard'))
        elif session['user_type'] == 'violator':
            return redirect(url_for('violator_dashboard'))
        elif session['user_type'] == 'superuser':
            return redirect(url_for('super_user_dashboard'))
    return redirect(url_for('login'))


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']  # officer, violator, or superuser

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check the user type and query the appropriate table
        if user_type == 'officer':
            cursor.execute("SELECT * FROM Officers WHERE email = %s AND password = %s", (email, password))
        elif user_type == 'violator':
            cursor.execute("SELECT * FROM Violators WHERE email = %s AND password = %s", (email, password))
        elif user_type == 'superuser':
            cursor.execute("SELECT * FROM Super_Users WHERE email = %s AND password = %s", (email, password))
        else:
            flash('Invalid user type selected!', 'danger')
            return render_template('login.html')

        user = cursor.fetchone()

        if user:
            session['loggedin'] = True
            session['user_id'] = user.get('officer_id') or user.get('violator_id') or user.get('super_user_id')

            if user_type == 'superuser':
                session['name'] = user['name']  # Set the `name` from Super_Users table
                session['role'] = user['role']  # Set the `role` from Super_Users table
            else:
                session['username'] = f"{user['first_name']} {user['last_name']}"

            session['user_type'] = user_type

            flash('Login successful!', 'success')

            # Redirect to respective dashboards based on user type
            if user_type == 'officer':
                return redirect(url_for('officer_dashboard'))
            elif user_type == 'violator':
                return redirect(url_for('violator_dashboard'))
            elif user_type == 'superuser':
                return redirect(url_for('super_user_dashboard'))
        else:
            flash('No user found with the provided credentials.', 'danger')
    return render_template('login.html')


# Route: Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form['user_type']  # officer, violator, or superuser
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        name = f"{first_name} {last_name}"  # Combine first and last names for Super User
        phone = request.form['phone_number']
        email = request.form['email']
        password = request.form['password']

        # Validate inputs
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!', 'danger')
            return render_template('register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'danger')
            return render_template('register.html')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check for duplicate email
        if user_type == 'officer':
            cursor.execute("SELECT * FROM Officers WHERE email = %s", (email,))
        elif user_type == 'violator':
            cursor.execute("SELECT * FROM Violators WHERE email = %s", (email,))
        elif user_type == 'superuser':
            cursor.execute("SELECT * FROM Super_Users WHERE email = %s", (email,))
        else:
            flash('Invalid user type selected!', 'danger')
            return render_template('register.html')

        account = cursor.fetchone()
        if account:
            flash('Email is already registered!', 'warning')
            return render_template('register.html')

        # Insert into the appropriate table
        if user_type == 'officer':
            badge_number = request.form['badge_number']
            precinct = request.form['precinct']
            contact_info = request.form['contact_info']
            cursor.execute("""
                INSERT INTO Officers (first_name, last_name, badge_number, precinct, email, password, phone_number, contact_info)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, badge_number, precinct, email, password, phone, contact_info))
        elif user_type == 'violator':
            license_number = request.form['license_number']
            address = request.form['address']
            cursor.execute("""
                INSERT INTO Violators (first_name, last_name, license_number, address, email, password, phone_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, license_number, address, email, password, phone))
        elif user_type == 'superuser':
            role = request.form['role']
            contact_info = request.form['contact_info']
            cursor.execute("""
                INSERT INTO Super_Users (name, email, password, phone_number, role, contact_info)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, email, password, phone, role, contact_info))
        else:
            flash('Invalid user type selected!', 'danger')
            return render_template('register.html')

        mysql.connection.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/officer/dashboard')
def officer_dashboard():
    if 'loggedin' in session and session['user_type'] == 'officer':
        officer_id = session['user_id']
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT badge_number FROM Officers WHERE officer_id = %s", (officer_id,))
        officer = cursor.fetchone()

        return render_template('officer_dashboard.html', 
                               username=session['username'], 
                               badge_number=officer['badge_number'], 
                               current_time=current_time)
    else:
        flash('Access denied. Please log in as an officer.', 'danger')
        return redirect(url_for('login'))
@app.route('/officer/log', methods=['GET', 'POST'])
def log_incident_fine():
    if 'loggedin' in session and session['user_type'] == 'officer':
        if request.method == 'POST':
            officer_id = session['user_id']
            violator_first_name = request.form.get('violator_first_name')
            violator_middle_name = request.form.get('violator_middle_name')
            violator_last_name = request.form.get('violator_last_name')
            driver_license = request.form.get('driver_license')
            license_plate = request.form.get('license_plate')
            violation_category = request.form.get('violation_category')
            violation_type = request.form.get('violation_type')
            location = request.form.get('location')
            date_time = request.form.get('date_time')
            description = request.form.get('description')

            make = request.form.get('make')
            model = request.form.get('model')
            color = request.form.get('color')

            determined_amount = request.form.get('determined_amount')
            due_date = request.form.get('due_date')

            # Check if it's an edit action
            incident_id = request.form.get('incident_id')
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            if incident_id:
                # Update existing incident
                cursor.execute("""
                    UPDATE Incidents
                    SET officer_id = %s, violation_category = %s, violation_type = %s,
                        location = %s, date_time = %s, violator_first_name = %s, 
                        violator_middle_name = %s, violator_last_name = %s, 
                        driver_license = %s, description = %s
                    WHERE incident_id = %s
                """, (officer_id, violation_category, violation_type, location, date_time,
                      violator_first_name, violator_middle_name, violator_last_name,
                      driver_license, description, incident_id))
                mysql.connection.commit()

                cursor.execute("""
                    UPDATE Vehicle_Records
                    SET make = %s, model = %s, color = %s, license_plate = %s
                    WHERE incident_id = %s
                """, (make, model, color, license_plate, incident_id))
                mysql.connection.commit()

                cursor.execute("""
                    UPDATE Fines
                    SET officer_determined_amount = %s, due_date = %s
                    WHERE incident_id = %s
                """, (determined_amount, due_date, incident_id))
                mysql.connection.commit()

                flash('Incident updated successfully!', 'success')
                return redirect(url_for('review_log', incident_id=incident_id))

            # Generate unique ticket number
            ticket_number = f"T{random.randint(10000, 99999)}"

            # If no incident_id, create a new incident
            cursor.execute("""
                INSERT INTO Incidents (
                    officer_id, violation_category, violation_type, location, date_time, 
                    violator_first_name, violator_middle_name, violator_last_name, 
                    driver_license, description
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (officer_id, violation_category, violation_type, location, date_time,
                  violator_first_name, violator_middle_name, violator_last_name,
                  driver_license, description))
            mysql.connection.commit()
            incident_id = cursor.lastrowid

            # Log vehicle records
            cursor.execute("""
                INSERT INTO Vehicle_Records (incident_id, make, model, color, license_plate)
                VALUES (%s, %s, %s, %s, %s)
            """, (incident_id, make, model, color, license_plate))
            mysql.connection.commit()

            # Log fine with ticket number
            cursor.execute("""
                INSERT INTO Fines (incident_id, officer_determined_amount, due_date, ticket_number)
                VALUES (%s, %s, %s, %s)
            """, (incident_id, determined_amount, due_date, ticket_number))
            mysql.connection.commit()

            flash(f'Incident and fine logged successfully! Ticket Number: {ticket_number}', 'success')
            return redirect(url_for('review_log', incident_id=incident_id))

        # Handle GET request for editing an incident
        incident_id = request.args.get('incident_id')
        if incident_id:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("""
                SELECT * FROM Incidents
                JOIN Vehicle_Records ON Incidents.incident_id = Vehicle_Records.incident_id
                JOIN Fines ON Incidents.incident_id = Fines.incident_id
                WHERE Incidents.incident_id = %s
            """, (incident_id,))
            record = cursor.fetchone()
            return render_template('log_incident.html', record=record)

        return render_template('log_incident.html', record=None)
    else:
        flash('Access denied. Please log in as an officer.', 'danger')
        return redirect(url_for('login'))


# Review Incident
@app.route('/officer/review/<int:incident_id>')
def review_log(incident_id):
    if 'loggedin' in session and session['user_type'] == 'officer':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT * FROM Incidents 
            JOIN Vehicle_Records ON Incidents.incident_id = Vehicle_Records.incident_id
            JOIN Fines ON Incidents.incident_id = Fines.incident_id
            WHERE Incidents.incident_id = %s
        """, (incident_id,))
        record = cursor.fetchone()
        return render_template('review_log.html', record=record)
    else:
        flash('Access denied. Please log in as an officer.', 'danger')
        return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('officer_dashboard.html', username=session['username'], user_type=session['user_type'])
    else:
        flash('Access denied. Please log in first.', 'danger')
        return redirect(url_for('login'))
    
@app.route('/officer/logs', methods=['GET', 'POST'])
def officer_logs():
    if 'loggedin' in session and session['user_type'] == 'officer':
        officer_id = session['user_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch all logs for the logged-in officer
        if request.method == 'POST':
            # Handle search queries
            search_term = request.form['search']
            query = f"""
                SELECT * FROM Incidents i
                join vehicle_records v on  i.incident_id = v.incident_id
                WHERE officer_id = %s AND (
                    i.violator_first_name LIKE %s OR 
                    i.violator_last_name LIKE %s OR 
                    i.driver_license LIKE %s OR 
                    v.license_plate LIKE %s OR 
                    i.location LIKE %s
                )
            """
            cursor.execute(query, (officer_id, f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        else:
            # Default fetch for all logs
            cursor.execute("SELECT * FROM Incidents WHERE officer_id = %s", (officer_id,))

        logs = cursor.fetchall()

        return render_template('officer_logs.html', logs=logs)
    else:
        flash('Access denied. Please log in as an officer.', 'danger')
        return redirect(url_for('login'))
    
@app.route('/violator/ticket/<int:incident_id>')
@app.route('/violator/ticket/<int:incident_id>')
def ticket_details(incident_id):
    if 'loggedin' in session and session['user_type'] == 'violator':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch ticket details
        cursor.execute("""
            SELECT Incidents.*, Vehicle_Records.make, Vehicle_Records.model, Vehicle_Records.color, 
                   Fines.officer_determined_amount, Fines.due_date, Fines.paid_status
            FROM Incidents
            LEFT JOIN Vehicle_Records ON Incidents.incident_id = Vehicle_Records.incident_id
            JOIN Fines ON Incidents.incident_id = Fines.incident_id
            WHERE Incidents.incident_id = %s
        """, (incident_id,))
        ticket = cursor.fetchone()

        if not ticket:
            flash('Ticket not found.', 'danger')
            return redirect(url_for('violator_dashboard'))

        return render_template('ticket_details.html', ticket=ticket)
    else:
        flash('Access denied. Please log in as a violator.', 'danger')
        return redirect(url_for('login'))


@app.route('/violator/pay_ticket/<int:incident_id>', methods=['GET', 'POST'])
def pay_ticket(incident_id):
    if 'loggedin' in session and session['user_type'] == 'violator':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch fine details
        cursor.execute("""
            SELECT Fines.*, Incidents.violation_type
            FROM Fines
            JOIN Incidents ON Fines.incident_id = Incidents.incident_id
            WHERE Fines.incident_id = %s
        """, (incident_id,))
        fine = cursor.fetchone()

        if request.method == 'POST':
            card_type = request.form.get('card_type')
            card_number = request.form.get('card_number')
            expiry_date = request.form.get('expiry_date')
            cvv = request.form.get('cvv')
            card_holder_name = request.form.get('card_holder_name')
            billing_address = request.form.get('billing_address')
            payment_method = f"{card_type} Card"
            amount_paid = fine['officer_determined_amount']
            payment_date = datetime.now()

            # Log payment
            cursor.execute("""
                INSERT INTO Payments (fine_id, amount_paid, payment_date, payment_method, 
                                      card_type, card_number, expiry_date, cvv, 
                                      card_holder_name, billing_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (fine['fine_id'], amount_paid, payment_date, payment_method, 
                  card_type, card_number, expiry_date, cvv, 
                  card_holder_name, billing_address))
            mysql.connection.commit()

            # Update fine status
            cursor.execute("""
                UPDATE Fines
                SET paid_status = 'Paid'
                WHERE fine_id = %s
            """, (fine['fine_id'],))
            mysql.connection.commit()

            flash('Payment successful! Fine status updated to Paid.', 'success')
            return redirect(url_for('violator_dashboard'))

        return render_template('pay_ticket.html', fine=fine)
    else:
        flash('Access denied. Please log in as a violator.', 'danger')
        return redirect(url_for('login'))


@app.route('/violator/court_schedule/<int:incident_id>')
def court_schedule(incident_id):
    flash('Court scheduling functionality is under development.', 'info')
    return redirect(url_for('ticket_details', incident_id=incident_id))


@app.route('/violator/lookup_ticket', methods=['POST'])
def lookup_ticket():
    if 'loggedin' in session and session['user_type'] == 'violator':
        ticket_number = request.form.get('ticket_number')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch ticket details based on the ticket number
        cursor.execute("""
            SELECT Fines.fine_id, Fines.incident_id, Fines.officer_determined_amount, Fines.due_date, 
                   Incidents.violation_type, Incidents.location, Vehicle_Records.make, 
                   Vehicle_Records.model, Vehicle_Records.color
            FROM Fines
            JOIN Incidents ON Fines.incident_id = Incidents.incident_id
            LEFT JOIN Vehicle_Records ON Incidents.incident_id = Vehicle_Records.incident_id
            WHERE Fines.ticket_number = %s
        """, (ticket_number,))
        ticket = cursor.fetchone()

        if not ticket:
            flash('Invalid ticket number. Please check and try again.', 'danger')
            return redirect(url_for('violator_dashboard'))

        # Render the ticket confirmation page
        return render_template('confirm_ticket.html', ticket=ticket)
    else:
        flash('Access denied. Please log in as a violator.', 'danger')
        return redirect(url_for('login'))


@app.route('/violator/add_confirmed_ticket', methods=['POST'])
def add_confirmed_ticket():
    if 'loggedin' in session and session['user_type'] == 'violator':
        incident_id = request.form.get('incident_id')
        violator_id = session['user_id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check if the ticket is already associated
        cursor.execute("""
            SELECT violator_id FROM Incidents WHERE incident_id = %s
        """, (incident_id,))
        ticket = cursor.fetchone()

        if ticket['violator_id']:
            flash('This ticket is already associated with another account.', 'danger')
            return redirect(url_for('violator_dashboard'))

        # Associate the ticket with the current violator
        cursor.execute("""
            UPDATE Incidents
            SET violator_id = %s
            WHERE incident_id = %s
        """, (violator_id, incident_id))
        mysql.connection.commit()

        flash('Ticket successfully added to your account.', 'success')
        return redirect(url_for('violator_dashboard'))
    else:
        flash('Access denied. Please log in as a violator.', 'danger')
        return redirect(url_for('login'))


@app.route('/violator/dashboard')
def violator_dashboard():
    if 'loggedin' in session and session['user_type'] == 'violator':
        violator_id = session['user_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch violator details
        cursor.execute("SELECT * FROM Violators WHERE violator_id = %s", (violator_id,))
        violator = cursor.fetchone()

        if not violator:
            flash('Violator details not found. Please log in again.', 'danger')
            return redirect(url_for('login'))

        # Fetch unpaid tickets associated with violator's driver's license or violator ID
        cursor.execute("""
            SELECT Incidents.incident_id, Incidents.violation_type, Incidents.date_time, 
                   Fines.officer_determined_amount, Fines.due_date, Fines.paid_status
            FROM Incidents
            JOIN Fines ON Incidents.incident_id = Fines.incident_id
            WHERE (Incidents.violator_id = %s OR Incidents.driver_license = %s) 
                  AND Fines.paid_status != 'Paid'
        """, (violator_id, violator['license_number']))
        tickets = cursor.fetchall()

        # Fetch unpaid parking violations added by the violator
        cursor.execute("""
            SELECT Incidents.incident_id, Incidents.violation_type, Incidents.date_time, 
                   Fines.officer_determined_amount, Fines.due_date, Vehicle_Records.license_plate
            FROM Incidents
            JOIN Fines ON Incidents.incident_id = Fines.incident_id
            LEFT JOIN Vehicle_Records ON Incidents.incident_id = Vehicle_Records.incident_id
            WHERE Incidents.violator_id = %s AND Fines.paid_status != 'Paid'
        """, (violator_id,))
        parking_violations = cursor.fetchall()

        # Fetch tickets with paid status
        cursor.execute("""
            SELECT Incidents.incident_id, Incidents.violation_type, Incidents.date_time, 
                   Fines.officer_determined_amount, Fines.due_date, Fines.paid_status
            FROM Incidents
            JOIN Fines ON Incidents.incident_id = Fines.incident_id
            WHERE (Incidents.violator_id = %s OR Incidents.driver_license = %s) 
                  AND Fines.paid_status = 'Paid'
        """, (violator_id, violator['license_number']))
        paid_tickets = cursor.fetchall()

        return render_template(
            'violator_dashboard.html', 
            violator=violator, 
            tickets=tickets, 
            parking_violations=parking_violations, 
            paid_tickets=paid_tickets
        )
    else:
        flash('Access denied. Please log in as a violator.', 'danger')
        return redirect(url_for('login'))


# Route: Super User Dashboard
@app.route('/super_user/dashboard')
def super_user_dashboard():
    if 'loggedin' in session and session['user_type'] == 'superuser':
        return render_template(
            'super_user_dashboard.html',
            name=session['name'],
            role=session['role']
        )
    else:
        flash('Access denied. Please log in as a Super User.', 'danger')
        return redirect(url_for('login'))

# Route: View All Incidents
@app.route('/super_user/incidents')
def view_incidents():
    if 'loggedin' in session and session['user_type'] == 'superuser':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT i.incident_id, i.violation_type, i.violation_category, i.location, i.date_time,
                   o.first_name AS officer_first_name, o.last_name AS officer_last_name, f.officer_determined_amount ,f.paid_status
            FROM incidents i
            LEFT JOIN officers o ON i.officer_id = o.officer_id
            LEFT JOIN fines f ON i.incident_id = f.incident_id
            ORDER BY i.date_time DESC
        """)
        incidents = cursor.fetchall()
        return render_template('super_user_incidents.html', incidents=incidents)
    else:
        flash('Access denied. Please log in as a Super User.', 'danger')
        return redirect(url_for('login'))

# Route: View Incident Details
@app.route('/super_user/incident/<int:incident_id>')
def view_incident_details(incident_id):
    if 'loggedin' in session and session['user_type'] == 'superuser':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT i.*, 
                   o.first_name AS officer_first_name, o.last_name AS officer_last_name, o.badge_number, o.precinct,
                   f.officer_determined_amount, f.due_date, f.paid_status,
                   v.make, v.model, v.color, v.license_plate
            FROM incidents i
            LEFT JOIN officers o ON i.officer_id = o.officer_id
            LEFT JOIN fines f ON i.incident_id = f.incident_id
            LEFT JOIN vehicle_records v ON i.incident_id = v.incident_id
            WHERE i.incident_id = %s
        """, (incident_id,))
        incident = cursor.fetchone()
        if not incident:
            flash('Incident not found.', 'danger')
            return redirect(url_for('view_incidents'))
        return render_template('super_user_incident_details.html', incident=incident)
    else:
        flash('Access denied. Please log in as a Super User.', 'danger')
        return redirect(url_for('login'))

# Route: Edit Incident
@app.route('/super_user/incident/edit/<int:incident_id>', methods=['GET', 'POST'])
def edit_incident(incident_id):
    if 'loggedin' in session and session['user_type'] == 'superuser':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            # Get updated details
            violation_type = request.form['violation_type']
            violation_category = request.form['violation_category']
            location = request.form['location']
            description = request.form['description']

            # Update incident details in database
            cursor.execute("""
                UPDATE incidents
                SET violation_type = %s, violation_category = %s, location = %s, description = %s, updated_at = %s
                WHERE incident_id = %s
            """, (violation_type, violation_category, location, description, datetime.now(), incident_id))
            mysql.connection.commit()

            flash('Incident details updated successfully.', 'success')
            return redirect(url_for('view_incident_details', incident_id=incident_id))

        # Fetch current incident details for editing
        cursor.execute("SELECT * FROM incidents WHERE incident_id = %s", (incident_id,))
        incident = cursor.fetchone()
        if not incident:
            flash('Incident not found.', 'danger')
            return redirect(url_for('view_incidents'))
        return render_template('edit_incident.html', incident=incident)
    else:
        flash('Access denied. Please log in as a Super User.', 'danger')
        return redirect(url_for('login'))

    
@app.route('/super_user/audit_logs/<int:incident_id>')
def audit_logs(incident_id):
    if 'loggedin' in session and session['user_type'] == 'superuser':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch logs for the incident
        cursor.execute("""
            SELECT * FROM audit_logs WHERE record_id = %s AND table_name = 'incidents'
        """, (incident_id,))
        logs = cursor.fetchall()

        return render_template('audit_logs.html', logs=logs, incident_id=incident_id)
    else:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))



# Logout Route
@app.route('/super_user/logout')
def super_user_logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Route: Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)