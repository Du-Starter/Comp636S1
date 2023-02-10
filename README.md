# Comp636S1 Web App

### Introduction

This Flask web app is for building a library website to provide services for the public customers and internal staff. It has divided into two main parts, one part is for the public to provide web information for them, where they can search for the book information from the search engine and the other part is built for the internal staff to allow them to add/modify the borrower's information. Staff can view information such as issued books, overdue books, and return loaned books to find what they need.
This report has two main parts for discussion: the public (/) route and the staff (/staff) route. Each part will indicate the routes and templates related to each other, and the data being passed. Two empty routes (shareintern.html for internal staff and shareextern.html for the public) have been created to avoid the messy pages when writing jinja templates. Either staff or the public can click each button with the required result on a blank page.

##### Public (/)
On the public page, there are three buttons have been provided for customers to click, including home, booklist, and search. The home button is a standalone route, it does not connect with any database or rely on some other routes. Its purpose is to allow customers to return to the main page as well as to Waikirikiri Library. Both of them have the function of returning to the main page as they have been written in both shareextern.html and base.html in the Visual Studio Code (VS Code). 
Furthermore, two htmls have been used here since base.html is just a web to show the basic interface with library images animation while shareextern.html is an empty interface to represent the information from customers’ operation. Below are two snapshots to show the differences.  (Images)
Then the next button is the book list, it is to display the availability of all copies of a book, including the due date. The general method is the same: create a route (/list books) in app.py, write an SQL query and allow it to represent the table when click on it.
Lastly, the search button allows the public to partially search for book titles and/or authors. A POST method has been used in the back end, as it will submit data to the designated SQL quote for processing, then transfer the results including book title, author, category, and loan status, etc. to booklist.html to present to the public.

##### Staff(/Staff):
In the staff page, it has many inquiry functions, such as return loaned book, loan summary showing the total number of times each book has been loaned, borrower summary showing all borrowers and the total number of loans each borrower has had, etc.
Before discussing the functions of them, it is necessary to understand the HTTP protocol, which is designed for smooth communication between the client and the server. Some of these functions are used only with POST because POST is sent to the server along with the HTTP request. Some of them will use both POST and GET together because when the user submits information, they also need feedback. For example, the internal staff plans to search one of the borrower’s info, it is the condition, so GET will search the result from the back end and POST to show to the customers the staff. 
In here, the search borrower and have been chosen as the good examples to display the POST and GET
On the other hand, for example, public and staff searching button, add and update the borrower and return loanbook are those that I only use method POST to return the result to represent on the interface. 

### Debugging processes: 
Throughout the process, there are a considerable number of problems, such as confusion of logic at the beginning due to too many routes, and well organised the various routes to add in jinja templates. 
For me as an example, there are 11 htmls and 24 routes have been created. Borrowerlist as the example, the aim of this task is searching by either borrowerid or name to gather the whole information from the borrower, then staff can decide if this borrower has any infmation that need to be updated, such as house number, street or so (borrowerid set as read-only, I tried to set it as disable, the result is coming out, however, the server did not update it for some reason, then read-only is only choice). From the content above, one route created to used for search borrower and transfer to edit borrower interface to decide if he/she needed to be updated.
In the last assignment, I have only encountered POST, and I did not know that POST and GET could be used at the same time, so I also spent some time researching and testing. Fortunately, the result was good (what page display). 
Furthermore, an example given by Stuart is a SQL statement with one variable while multiple variables have been appeared in the tasks, such as partial searches based on author and book title in the public and staff pages. Author and booktitle are two variables, and the problem is how to combine the example within this task. Here is the work: 




### Conclusion
The process of uploading from local to GitHub was relatively smooth, but there was a problem when uploading from GitHub to PythonAnywhere. In this process, an error occurred that the server could not find the schema, and I couldn't figure out where the problem was for a long time, and finally found that the problem was that my local SQL statements were all library.books, but this is not used for PA, because the environment is not certain.
The next content is discussing returned books on the web, I need an interface to enter bookcopyid, then another path jumps to the original page, these two first pages need to be connected to the second route to execute SQL statements.






