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
    FROM books b 
    INNER JOIN bookcopies bc 
    ON b.bookid=bc.bookid
	INNER JOIN loans l 
    ON bc.bookcopyid=l.bookcopyid ;""")
    bookList = connection.fetchall()
    print(bookList)
    return render_template("booklist.html", booklist=bookList)  # booklist.html


# @app.route("/loanbook")
# def loanbook():
#     todaydate = datetime.now().date()
#     connection = getCursor()
#     connection.execute("SELECT * FROM borrowers;")
#     borrowerList = connection.fetchall()
#     sql = """SELECT * FROM bookcopies
#     INNER JOIN books on books.bookid = bookcopies.bookid
#     WHERE bookcopyid not in (SELECT bookcopyid from loans where returned <> 1 or returned is NULL);"""
#     connection.execute(sql)
#     bookList = connection.fetchall()
#     return render_template("addloan.html", loandate=todaydate, borrowers=borrowerList, books=bookList)


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
    sql = """ SELECT br.borrowerid, br.firstname, br.familyname,  
                l.borrowerid, l.bookcopyid, l.loandate, l.returned, b.bookid, b.booktitle, b.author, 
                b.category, b.yearofpublication, bc.format 
                FROM books b
                INNER JOIN bookcopies bc on b.bookid = bc.bookid
                INNER JOIN loans l on bc.bookcopyid = l.bookcopyid
                INNER JOIN borrowers br on l.borrowerid = br.borrowerid
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
    sql = """SELECT b.bookid, b.booktitle, b.author, count(l.loanid) AS MostLoanBooks
    FROM books b
    LEFT JOIN bookcopies bc
    ON b.bookid = bc.bookid
    LEFT JOIN loans l
    ON l.bookcopyid = bc.bookcopyid
    GROUP BY b.bookid, b.booktitle
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
    cur.execute("""INSERT INTO borrowers (firstname, familyname, dateofbirth, housenumbername, street, town, city, postalcode) 
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s);""",
                (firstname, familyname, dateofbirth, housenumbername, street, town, city, postalcode,))
    return redirect("/listborrowers")


@app.route("/edit", methods=["POST"])
def edit():
    firstname = request.form.get("firstname")
    print(firstname)
    familyname = request.form.get("familyname")
    print(familyname)
    dateofbirth = request.form.get("dateofbirth")
    housenumbername = request.form.get("housenumbername")
    street = request.form.get("street")
    town = request.form.get("town")
    city = request.form.get("city")
    postalcode = request.form.get("postalcode")
    borrowerid = request.form.get("borrowerid")
    print(borrowerid)
    cur = getCursor()
    cur.execute("""UPDATE borrowers 
    SET firstname = %s, familyname = %s, dateofbirth = %s, housenumbername = %s,
    street= %s, town = %s, city = %s, postalcode = %s WHERE borrowerid = %s;""",
                (firstname, familyname, dateofbirth, housenumbername, street, town, city, postalcode, borrowerid))
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
    staffbookList = connection.fetchall()
    print(staffbookList)
    return render_template("staffbooklist.html", staffbooklist=staffbookList)


@app.route("/searchborrowers", methods=["POST", "GET"])
def searchborrowers():
    if request.method == "GET":
        return render_template("searchborrowers.html")
    else:
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
    SELECT br.borrowerid, concat(firstname,+ ' ',+familyname) As Name, b.booktitle, bc.format, loandate + interval 35 day as duedate, 
    timestampdiff(day, loandate + interval 35 day, now()) as overdays 
    FROM borrowers br
    INNER JOIN loans l
    ON br.borrowerid = l.borrowerid 
    INNER JOIN bookcopies bc
    ON bc.bookcopyid = l.bookcopyid
    INNER JOIN books b
    ON b.bookid=bc.bookid
    WHERE loandate + interval 35 day < now() and returned =0 
    ORDER BY br.borrowerid DESC; """)
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
    connection.execute("""UPDATE loans l 
            INNER JOIN bookcopies bc
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
    sql = """SELECT * 
    from bookcopies bc 
    INNER JOIN books b 
    ON b.bookid = bc.bookid 
    WHERE bookcopyid not in 
    (SELECT bookcopyid FROM loans 
    WHERE returned <>1 or returned is null) or format in ('eBook', 'Audio Book')"""
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
    JOIN bookcopies bc 
    ON b.bookid=bc.bookid
	JOIN loans l 
    ON bc.bookcopyid=l.bookcopyid ;""")
    staffbookList = connection.fetchall()
    print(staffbookList)
    return render_template("staffbooklist.html", staffbooklist=staffbookList)


if __name__ == "__main__":
    app.run(debug=True)
