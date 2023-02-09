from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None


def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser,
                                         password=connect.dbpass, host=connect.dbhost,
                                         database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

# blank web for public


@app.route("/shareintern")
def shareintern():
    return render_template("shareintern.html")

# blank web for staff


@app.route("/shareextern")
def shareextern():
    return render_template("shareextern.html")


@app.route("/")
def home():
    return render_template("base.html")


@app.route("/listbooks")
def listbooks():
    connection = getCursor()
    connection.execute("""SELECT b.bookid, b.booktitle,b.author,b.category,b.description,l.returned,l.loandate 
    FROM books b JOIN bookcopies bc ON b.bookid=bc.bookid
	JOIN loans l ON bc.bookcopyid=l.bookcopyid;""")
    bookList = connection.fetchall()
    print(bookList)
    return render_template("booklist.html", booklist=bookList)


@app.route("/loanbook")
def loanbook():
    todaydate = datetime.now().date()
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers;")
    borrowerList = connection.fetchall()
    sql = """SELECT * FROM bookcopies
inner join books on books.bookid = bookcopies.bookid
 WHERE bookcopyid not in (SELECT bookcopyid from loans where returned <> 1 or returned is NULL);"""
    connection.execute(sql)
    bookList = connection.fetchall()
    return render_template("addloan.html", loandate=todaydate, borrowers=borrowerList, books=bookList)


@app.route("/loan/add", methods=["POST"])
def addloan():
    borrowerid = request.form.get('borrower')
    bookid = request.form.get('book')
    loandate = request.form.get('loandate')
    cur = getCursor()
    cur.execute("INSERT INTO loans (borrowerid, bookcopyid, loandate, returned) VALUES(%s,%s,%s,0);",
                (borrowerid, bookid, str(loandate),))
    return redirect("/currentloans")


@app.route("/currentloans")
def currentloans():
    connection = getCursor()
    sql = """ select br.borrowerid, br.firstname, br.familyname,  
                l.borrowerid, l.bookcopyid, l.loandate, l.returned, b.bookid, b.booktitle, b.author, 
                b.category, b.yearofpublication, bc.format 
            from books b
                inner join bookcopies bc on b.bookid = bc.bookid
                    inner join loans l on bc.bookcopyid = l.bookcopyid
                        inner join borrowers br on l.borrowerid = br.borrowerid
            order by br.familyname, br.firstname, l.loandate;"""
    connection.execute(sql)
    loanList = connection.fetchall()
    return render_template("currentloans.html", loanlist=loanList)


@app.route("/search")
def search():
    return render_template("searchpublic.html")


@app.route("/searchpublic", methods=["POST"])
def searchpublic():
    booktitle = request.form.get("search")
    author = request.form.get("search")
    booktitle = "%" + booktitle + "%"
    author = "%" + author + "%"
    connection = getCursor()
    connection.execute(
        """SELECT * FROM books
                       WHERE booktitle LIKE %s OR author LIKE %s""", (booktitle, author,))
    bookList = connection.fetchall()
    print(bookList)
    return render_template("booklist.html", booklist=bookList)


@app.route("/staff")
def staff():
    return render_template("staff.html")


@app.route("/loansummary")
def loansummary():
    connection = getCursor()
    sql = """SELECT bookid, booktitle, author, count(loanid) AS MostLoanBooks
    FROM books
    LEFT JOIN bookcopies
    ON books.bookid = bookcopies.bookid
    LEFT JOIN loans
    ON loans.bookcopyid = bookcopies.bookcopyid
    GROUP BY books.bookid,books.booktitle
    ORDER BY MostLoanBooks DESC;"""
    connection.execute(sql)
    loansummary = connection.fetchall()
    return render_template("loansummary.html", loanSummary=loansummary)


@app.route("/addborrower")
def addborrower():
    return render_template("addborrower.html")


@app.route("/add", methods=["POST"])
def add():
    firstname = request.form.get("firstname")
    familyname = request.form.get("familyname")
    dateofbirth = request.form.get("dateofbirth")
    housenumbername = request.form.get("housenumbername")
    street = request.form.get("street")
    town = request.form.get("town")
    city = request.form.get("city")
    postalcode = request.form.get("postalcode")
    cur = getCursor()
    cur.execute("INSERT INTO borrowers (firstname, familyname, dateofbirth, housenumbername, street, town, city, postalcode) VALUES(%s,%s,%s,%s,%s,%s,%s,%s);",
                (firstname, familyname, dateofbirth, housenumbername, street, town, city, postalcode,))
    return redirect("/listborrowers")


@app.route("/editborrower")
def editborrower():
    return render_template("editborrower.html")

# 如何将一些columns为空还可以继续进行，borrowerid required


@app.route("/edit", methods=["POST"])
def edit():
    first_name = request.form.get("firstname")
    family_name = request.form.get("familyname")
    date_of_birth = request.form.get("dateofbirth")
    house_number_name = request.form.get("housenumbername")
    street_edit = request.form.get("street")
    town_edit = request.form.get("town")
    city_edit = request.form.get("city")
    postalcode_edit = request.form.get("postalcode")
    borrowerid_edit = request.form.get("borrowerid")
    cur = getCursor()
    cur.execute("""Update borrowers 
    SET firstname = %s, familyname = %s, dateofbirth = %s, housenumbername = %s, street = %s, town = %s, city = %s, postalcode = %s
    WHERE borrowerid = %s;""",
                (first_name, family_name, date_of_birth, house_number_name, street_edit, town_edit, city_edit, postalcode_edit, borrowerid_edit))
    return redirect("/listborrowers")


@app.route("/searchinternal")
def searchinternal():
    return render_template("searchstaff.html")


@app.route("/searchstaff", methods=["POST"])
def searchstaff():
    booktitle = request.form.get("search")
    author = request.form.get("search")
    booktitle = "%" + booktitle + "%"
    author = "%" + author + "%"
    connection = getCursor()
    connection.execute(
        """SELECT * FROM books
                       WHERE booktitle LIKE %s OR author LIKE %s""", (booktitle, author,))
    bookList = connection.fetchall()
    print(bookList)
    return render_template("booklist.html", booklist=bookList)


@app.route("/searchborrower")
def searchborrower():
    return render_template("searchborrowers.html")


@app.route("/searchborrowers", methods=["POST"])
def searchborrowers():
    borrower_firstname = request.form.get("search")
    borrower_familyname = request.form.get("search")
    borrower_borrowerid = request.form.get("search")
    borrower_firstname = "%" + borrower_firstname + "%"
    borrower_familyname = "%" + borrower_familyname + "%"
    borrower_borrowerid = "%" + borrower_borrowerid + "%"
    connection = getCursor()
    connection.execute(
        """SELECT * FROM borrowers
        WHERE firstname LIKE %s OR familyname LIKE %s OR borrowerid LIKE %s
                       """, (borrower_firstname, borrower_familyname, borrower_borrowerid,))
    borrowerList = connection.fetchall()
    print(borrowerList)
    return render_template("borrowerlist.html", borrowerlist=borrowerList)


@app.route("/listborrowers")
def listborrowers():
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers;")
    borrowerList = connection.fetchall()
    return render_template("borrowerlist.html", borrowerlist=borrowerList)


@app.route("/overdue")
def overdue():
    connection = getCursor()
    connection.execute("""
    SELECT (datediff(curdate(),loandate) -28) AS OverDue, concat( br.firstname,+ " " ,+br.familyname ) AS Name, 
    l.loandate AS LoanDate,  DATE_ADD(l.loandate, INTERVAL 28 DAY) AS DueDate, b.booktitle, bc.format 
    FROM loans l
    LEFT JOIN bookcopies  bc ON BC.bookcopyid = l.bookcopyid
    INNER JOIN books  b ON b.bookid = bc.bookid
    INNER JOIN borrowers br ON br.borrowerid = l.borrowerid
    WHERE ((bc.format NOT IN ('eBook', 'Audio Book')) AND (l.returned = 0) AND (datediff(curdate(),l.loandate) > 35)); """)
    overdue = connection.fetchall()
    return render_template("overdue.html", overDue=overdue)


@app.route("/borrowersummary")
def borrowersummary():
    connection = getCursor()
    connection.execute("""
    SELECT br.borrowerid, concat(br.firstname,+' ',+br.familyname ) AS Name, count(l.loanid) AS LoanNumbers
    FROM loans l
    INNER JOIN borrowers br ON br.borrowerid = l.borrowerid
    GROUP BY l.borrowerid
    ORDER BY br.borrowerid; """)
    borrowersummary = connection.fetchall()
    return render_template("borrowersummary.html", borrowerSummary=borrowersummary)


@app.route("/returnbook")
def returnbook():
    bookcopyid = request.form.get("bookcopyid")
    print(bookcopyid)
    return render_template("returnloanbook.html")


@app.route("/returnloanbook", methods=["POST"])
def returnloanbook():
    bookcopyid = request.form.get("bookcopyid")
    connection = getCursor()
    connection.execute("""UPDATE loans l INNER JOIN bookcopies bc
            ON l.bookcopyid=bc.bookcopyid
            SET returned = 1 WHERE bc.bookcopyid = %s;""", (bookcopyid,))
    print(bookcopyid)
    return redirect("staff")


@app.route("/issuebook")
def issuebook():
    todaydate = datetime.now().date()
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers;")
    borrowerList = connection.fetchall()
    sql = """SELECT * FROM bookcopies
    inner join books on books.bookid = bookcopies.bookid
    WHERE bookcopyid not in (SELECT bookcopyid from loans where returned <> 1 or returned is NULL);"""
    connection.execute(sql)
    bookList = connection.fetchall()
    return render_template("addloan.html", loandate=todaydate, borrowers=borrowerList, books=bookList)


@app.route("/borrowerbook")
def borrowerbook():
    return redirect("staff")


@app.route("/staff/listbooks")
def stafflistbooks():
    connection = getCursor()
    connection.execute("""SELECT b.bookid, b.booktitle,b.author,b.category,b.description,l.returned,l.loandate 
    FROM books b 
    JOIN bookcopies bc ON b.bookid=bc.bookid
	JOIN loans l ON bc.bookcopyid=l.bookcopyid ;""")
    staffbookList = connection.fetchall()
    print(staffbookList)
    return render_template("staffbooklist.html", staffbooklist=staffbookList)
