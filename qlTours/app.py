from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
import datetime

app = Flask(__name__)

# Secret key to sign session cookies
app.secret_key = '123456789'
# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="tms"
)

cursor = db.cursor()

# Home Route
@app.route('/')
def index():
    cursor.execute("SELECT * from tbltourpackages order by rand() limit 4")
    t1_result = cursor.fetchall()
    return render_template('index.html', t1_result=t1_result)

@app.route('/details/', methods=['GET'])
def details():
    callid = request.args.get('id')
    query = "SELECT * from tbltourpackages where PackageId = %s"
    cursor.execute(query, (callid,))
    t1_result = cursor.fetchall()
    return render_template('package_details.html', t1_result=t1_result)

@app.route("/package_list")
def package_list():
    cursor.execute("SELECT * from tbltourpackages")
    t1_result = cursor.fetchall()
    return render_template('package-list.html', t1_result = t1_result)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/enquiry")
def enquiry():
    return render_template("enquiry.html")

@app.route("/login")
def login_Cus():
    return render_template("login_Cus.html")

@app.route("/home", methods=['POST'])
def Check_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        query = "SELECT * FROM tblusers WHERE EmailId = %s and Password = %s"
        cursor.execute(query, (username, password,))
        account = cursor.fetchone()
        
        if account:
            session['loggedin'] = True
            session['mail'] = account[3]
            session['id'] = account[0]

            return redirect(url_for('index'))
        else:
            Note = 'Incorrect username or password!'
            return render_template("login_Cus.html", Note = Note)

@app.route("/logout")
def logout():
    session['loggedin'] = False
    session['mail'] = ""
    session['id'] = ""
    return redirect(url_for('index'))

@app.route("/profile")
def profile():
    id = session.get('id')
    query = "SELECT * FROM tblusers WHERE id = %s"
    cursor.execute(query, (id,))
    t1_result = cursor.fetchall()
    return render_template('profile.html', t1_result = t1_result)

@app.route("/profile_update", methods=['POST'])
def profile_update():
    id = session.get('id')
    name = request.form['name']
    mobileno = request.form['mobileno']
    query = "UPDATE tblusers SET FullName = %s, MobileNumber = %s WHERE id = %s"
    cursor.execute(query, (name, mobileno, id))
    db.commit()
    return redirect(url_for('profile'))

@app.route('/password_update')
def password_update1():
    return render_template('change_password.html')

@app.route('/password_update', methods=['POST'])
def password_update():
    id = session.get('id')
    new_password = request.form['Newpassword']
    re_password = request.form['Repassword']
    older_password = request.form['olderpassword']

    if new_password != re_password:
        return redirect(url_for('password_update1'))

    # Fetch the current password hash from the database
    query = "SELECT Password FROM tblusers WHERE id = %s"
    cursor.execute(query, (id,))
    result = cursor.fetchone()
    pass1 = result[0]

    if pass1 == older_password:
        # Update the password in the database
        update_query = "UPDATE tblusers SET Password = %s WHERE id = %s"
        cursor.execute(update_query, (new_password, id))
        db.commit()
        return redirect(url_for('profile'))
    else: return redirect(url_for('password_update1'))

@app.route("/tour_history")
def tour_history():
    email = session.get('mail')
    query = "SELECT * FROM tblbooking WHERE UserEmail = %s"
    cursor.execute(query, (email,))
    t1_result = cursor.fetchall()  # Lấy tất cả các kết quả khớp
    return render_template('tour_history.html', t1_result=t1_result)

@app.route('/cancel/', methods=['GET'])
def cancel():
    callid = request.args.get('id')
    query = "DELETE FROM tblbooking WHERE BookingId = %s"
    cursor.execute(query, (callid,))
    db.commit()
    return redirect(url_for('tour_history'))

@app.route('/book', methods=['POST'])
def book():
    # Kiểm tra xem người dùng đã đăng nhập chưa
    user_email = session.get('mail')
    # Lấy dữ liệu từ form
    package_id = request.form.get('package_id')
    from_date = request.form.get('fromdate')
    to_date = request.form.get('todate')
    comment = request.form.get('comment')
    
    # Lấy ngày hiện tại để lưu RegDate
    reg_date = datetime.datetime.now()

    # Chèn dữ liệu vào bảng tblbooking
    query = """
    INSERT INTO tblbooking (PackageId, UserEmail, FromDate, ToDate, Comment, RegDate, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (package_id, user_email, from_date, to_date, comment, reg_date, 'Pending'))
    db.commit()

    flash('Tour booked successfully!')
    return redirect(url_for('tour_history'))

@app.route("/admin/login")
def adminlogin():
    return render_template('admin/login.html')

@app.route("/admin/home", methods=['POST'])
def adminCheck_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        query = "SELECT * FROM admin WHERE UserName = %s and Password = %s"
        cursor.execute(query, (username, password,))
        account = cursor.fetchone()
        
        if account:
            session['Adloggedin'] = True
            session['Admail'] = account[3]
            session['Adid'] = account[0]
            return render_template("admin/dashboad.html")

        else:
            Note = 'Incorrect username or password!'
            return render_template("admin/login.html", Note = Note)

@app.route("/admin/dashboard")
def Admin_dashboard():
    # Query 1
    query = "SELECT COUNT(id) FROM tblusers"
    cursor.execute(query)
    result = cursor.fetchone()
    count = result[0] if result else 0

    # Query 2
    query = "SELECT COUNT(id) FROM tblissues"
    cursor.execute(query)
    result = cursor.fetchone()
    count1 = result[0] if result else 0

    # Query 3
    query = "SELECT COUNT(PackageId) FROM tbltourpackages"
    cursor.execute(query)
    result = cursor.fetchone()
    count2 = result[0] if result else 0

    # Query 4
    query = "SELECT COUNT(id) FROM tblenquiry"
    cursor.execute(query)
    result = cursor.fetchone()
    count3 = result[0] if result else 0

    # Query 5
    query = "SELECT COUNT(id) FROM tblenquiry WHERE Status = '1'"
    cursor.execute(query)
    result = cursor.fetchone()
    count4 = result[0] if result else 0

    # Query 6
    query = "SELECT COUNT(BookingId) FROM tblbooking"
    cursor.execute(query)
    result = cursor.fetchone()
    count5 = result[0] if result else 0

    # Query 7
    query = "SELECT COUNT(BookingId) FROM tblbooking WHERE status IS NULL OR status = ''"
    cursor.execute(query)
    result = cursor.fetchone()
    count6 = result[0] if result else 0

    # Query 8
    query = "SELECT COUNT(BookingId) FROM tblbooking WHERE status = '2'"
    cursor.execute(query)
    result = cursor.fetchone()
    count7 = result[0] if result else 0

    # Query 9
    query = "SELECT COUNT(BookingId) FROM tblbooking WHERE status = '1'"
    cursor.execute(query)
    result = cursor.fetchone()
    count8 = result[0] if result else 0

    return render_template("admin/dashboad.html", count=count, count1=count1, count2=count2, count3=count3, count4=count4, count5=count5, count6=count6, count7=count7, count8=count8)

@app.route('/admin/create-package')
def create_package():
    cursor.execute("SELECT * FROM `tbltourpackages`")
    t2_result = cursor.fetchall()
    return render_template('admin/create-package.html',t2_result=t2_result)

@app.route('/admin/manage-users')
def adminprofile():
    cursor.execute("SELECT * FROM `tblusers`")
    t1_result = cursor.fetchall()
    return render_template('admin/manage-users.html', t1_result=t1_result)

@app.route('/admin/manage-packages')
def manage_packages():
    cursor.execute("SELECT * from tblTourPackages")
    t2_result = cursor.fetchall()
    return render_template('admin/manage-packages.html', t2_result=t2_result)

@app.route('/admin/manage-bookings')
def manage_bookings():
    cursor.execute("""
        SELECT 
            tblbooking.BookingId AS bookid,
            tblusers.FullName AS fname,
            tblusers.MobileNumber AS mnumber,
            tblusers.EmailId AS email,
            tbltourpackages.PackageName AS pckname,
            tblbooking.PackageId AS pid,
            tblbooking.FromDate AS fdate,
            tblbooking.ToDate AS tdate,
            tblbooking.Comment AS comment,
            tblbooking.status AS status,
            tblbooking.CancelledBy AS cancelby,
            tblbooking.UpdationDate AS upddate
        FROM tblbooking
        LEFT JOIN tblusers ON tblusers.EmailId = tblbooking.UserEmail
        LEFT JOIN tbltourpackages ON tbltourpackages.PackageId = tblbooking.PackageId
    """)
    t1_result = cursor.fetchall()
    return render_template('admin/manage-bookings.html', t1_result=t1_result)

@app.route('/admin/manageissues')
def manage_issues():
    cursor.execute("""
        SELECT * FROM `tblenquiry`
    """)
    issues_result = cursor.fetchall()
    return render_template('admin/manageissues.html', issues_result=issues_result)

@app.route("/update_package/", methods=["GET"])
def update_package1():
    id = request.args.get('id')
    cursor.execute("SELECT * FROM TblTourPackages WHERE PackageId = %s", (id,))
    result = cursor.fetchall()
    
    package = {
        'id' : result[0][0],
        'name': result[0][1],
        'type': result[0][2],
        'location': result[0][3],
        'price': result[0][4],
        'features': result[0][5],
        'details': result[0][6],
        'image': result[0][7],
        'last_update': result[0][8]
    }
    return render_template("admin/update-package.html", package=package)

@app.route("/bookking_user/", methods=["GET"])
def bookking_user():
    id = request.args.get('id')
    if id:
        cursor.execute("""
            SELECT tblbooking.BookingId as bookid, tblusers.FullName as fname, tblusers.MobileNumber as mnumber, 
                   tblusers.EmailId as email, tbltourpackages.PackageName as pckname, tblbooking.PackageId as pid, 
                   tblbooking.FromDate as fdate, tblbooking.ToDate as tdate, tblbooking.Comment as comment, 
                   tblbooking.status as status, tblbooking.CancelledBy as cancelby, tblbooking.UpdationDate as upddate 
            FROM tblbooking
            LEFT JOIN tblusers ON tblbooking.UserEmail = tblusers.EmailId
            LEFT JOIN tbltourpackages ON tbltourpackages.PackageId = tblbooking.PackageId
            WHERE tblbooking.UserEmail = %s
        """, (id,))
        result = cursor.fetchall()
        
        return render_template("admin/user-bookings.html", result=result, id=id)

@app.route("/admin/update-package", methods=["POST"])
def update_package():
    if request.method == "POST":
        # Nhận dữ liệu từ form
        package_id = request.form.get('id')
        package_name = request.form.get('packagename')
        package_type = request.form.get('packagetype')
        package_location = request.form.get('packagelocation')
        package_price = request.form.get('packageprice')
        package_features = request.form.get('packagefeatures')
        package_details = request.form.get('packagedetails')

        # Xử lý cập nhật dữ liệu trong cơ sở dữ liệu
        cursor.execute("""
            UPDATE TblTourPackages
            SET PackageName = %s,
                PackageType = %s,
                PackageLocation = %s,
                PackagePrice = %s,
                PackageFetures = %s,
                PackageDetails = %s,
                UpdationDate = NOW()
            WHERE PackageId = %s
        """, (package_name, package_type, package_location, package_price, package_features, package_details, package_id))
        db.commit()
        return redirect(url_for('update_package1', id=package_id))

@app.route('/bookking_user/manage_bookings_action/', methods=['GET'])
def manage_bookings_action():
    id1 = request.args.get('id')
    id2 = request.args.get('idk')
    if id1:
        cursor.execute("UPDATE tblbooking SET status=2 WHERE BookingId=%s", (id1,))
        db.commit()
    if id2:
        cursor.execute("UPDATE tblbooking SET status=1 WHERE BookingId=%s", (id2,))
        db.commit()
    return redirect(url_for('adminprofile'))

@app.route('/manageissues_delete/', methods=['GET'])
def manageissues_delete():
    id = request.args.get('id')
    cursor.execute('DELETE FROM tblenquiry WHERE id = %s', (id,))
    db.commit()
    return redirect(url_for('manage_issues'))

import os

@app.route('/admin/create-package', methods=['GET', 'POST'])
def create_package1():
    if request.method == 'POST':
        packagename = request.form['packagename']
        packagetype = request.form['packagetype']
        packagelocation = request.form['packagelocation']
        packageprice = request.form['packageprice']
        packagefeatures = request.form['packagefeatures']
        packagedetails = request.form['packagedetails']
        packageimage = request.files['packageimage']

        # Đường dẫn để lưu file ảnh
        image_folder = 'qlTours/static/images/packageimages/'
        os.makedirs(image_folder, exist_ok=True)
        image_path = os.path.join(image_folder, packageimage.filename)
        packageimage.save(image_path)

        # Insert the data into the database
        cursor.execute('''
            INSERT INTO tbltourpackages (PackageName, PackageType, PackageLocation, PackagePrice, PackageFetures, PackageDetails, PackageImage)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (packagename, packagetype, packagelocation, packageprice, packagefeatures, packagedetails, packageimage.filename))
        db.commit()

        return redirect(url_for('create_package'))

@app.route('/admin/delete-package/', methods=['GET'])
def delete_package():
    id = request.args.get('id')
    cursor.execute('DELETE FROM tbltourpackages WHERE PackageId = %s', (id,))
    db.commit()
    return redirect(url_for('manage_packages'))

@app.route('/enquiry', methods=['POST'])
def enquiry1():
    if request.method == 'POST':
        fname = request.form['fname']
        email = request.form['email']
        mobileno = request.form['mobileno']
        subject = request.form['subject']
        description = request.form['description']
        
        # Chèn dữ liệu vào database
        cursor.execute('''
            INSERT INTO tblenquiry (FullName, EmailId, MobileNumber, Subject, Description)
            VALUES (%s, %s, %s, %s, %s)
        ''', (fname, email, mobileno, subject, description))
        db.commit()
        
        return redirect(url_for('enquiry'))


if __name__ == '__main__':
    app.run(debug=True)
