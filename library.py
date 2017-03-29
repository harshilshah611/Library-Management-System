from datetime import date
from Tkinter import *
import tkMessageBox
import ttk
import mysql.connector

cnx=mysql.connector.connect(user='root', password='MyNewPass',database='lib')
cur=cnx.cursor(buffered=True)
cur2=cnx.cursor(buffered=True)
cur3=cnx.cursor(buffered=True)

total_users=("SELECT card_no "
                 "FROM borrower ")

print total_users
cur.execute(total_users)
card_no_count=0
for (count) in cur:
    x=count[0][2:]
    if card_no_count<x:
        card_no_count=int(x)

card_no_count+=1

def onClickSearchMenuButton():
    for child in frame2.winfo_children():
        child.destroy()
    for child in frame3.winfo_children():
        child.destroy()
    for child in frame4.winfo_children():
        child.destroy()
    searchLabel=Label(frame2,text='Search Book')
    searchLabel.pack(side=LEFT)
    searchTextField = Entry(frame2, bd =5)
    searchTextField.pack(side = LEFT)
    searchButton=Button(frame2, text="Search", command = lambda: onClickSearch(searchTextField.get()))
    searchButton.pack(side=LEFT)

def onClickSearch(text):
    for child in frame3.winfo_children():
        child.destroy()
    for child in frame4.winfo_children():
        child.destroy()
        
    tree = ttk.Treeview(frame3)
    ysb = ttk.Scrollbar(frame3, orient='vertical', command=tree.yview)
    xsb = ttk.Scrollbar(frame3, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        
    tree["columns"]=("one","two","three","four","five","six","seven")
    tree.column("#0", width=0)
    tree.column("one", width=70)
    tree.column("two", width=250)
    tree.column("three", width=200)
    tree.column("four", width=100)
    tree.column("five", width=100)
    tree.column("six", width=100)
    tree.column("seven", width=100)
    
    tree.heading("one", text="ISBN")
    tree.heading("two", text="TITLE")
    tree.heading("three", text="Author's Name")
    tree.heading("four", text="Branch id")
    tree.heading("five", text="Branch Name")
    tree.heading("six", text="Inventory")
    tree.heading("seven", text="Copies Left")

    if "'" in text:
        text=text[:text.index("'")]+"'"+text[text.index("'"):]
    print text
    temp=""
    x=text.split(' ')
    for t in x:
        temp+="AND (b.isbn LIKE '%"+t+"%' OR b.title LIKE '%"+t+"%' OR a.fullname LIKE '%"+t+"%')"
        
    query=("SELECT b.isbn,b.title,GROUP_CONCAT(distinct a.fullname), bc.branch_id, lb.branch_name, bc.no_of_copies, bc.inventory "
           "FROM book b, authors a, book_authors ba, books_copies bc, library_branch lb "
           "WHERE b.isbn=ba.isbn AND ba.author_id=a.author_id AND  bc.book_id=b.isbn AND bc.branch_id=lb.branch_id "+temp+"GROUP BY b.isbn, bc.branch_id")

    print query
    i=1
    cur.execute(query);
    for (isbn, title, fullname,branch_id,branch_name,no_of_copies,inventory) in cur:
        tree.insert("",i,text=("Line"+str(i)), values=(isbn, title, fullname,branch_id,branch_name,inventory,no_of_copies))
        i+=1

    tree.grid(row=0, column=0)
    ysb.grid(row=0, column=1, sticky='ns')
    xsb.grid(row=1, column=0, sticky='ew')

    cardnoLabel=Label(frame4,text='Enter card_no')
    cardnoLabel.pack(side=LEFT)
    cardNoTextField = Entry(frame4, bd =5)
    cardNoTextField.pack(side = LEFT)
    checkoutButton=Button(frame4,text="Check Out", command = lambda :onClickCheckout(tree,cardNoTextField.get()))
    checkoutButton.pack(side=LEFT)

def onClickCheckout(tree,cardno):
    
    curItem=tree.selection()
    isbn=tree.item(curItem).values()[2][0]
    branch_id=tree.item(curItem).values()[2][3]
    no_of_copies=tree.item(curItem).values()[2][6]

    isbn=str(isbn).zfill(10)
    
    query=("SELECT COUNT(*) "
            "FROM borrower "
            "WHERE card_no='"+cardno+"'")
    print query
    cur.execute(query)
    for (count)in cur:
        print ''
    if count[0]==0:
        tkMessageBox.showinfo("Error Message", "enter a valid card_no")
        return
        
    check_borrower_limit=("SELECT COUNT(*) "
                          "FROM book_loans "
                          "WHERE card_no='"+cardno+"' AND date_in is NULL")

    print check_borrower_limit
    cur.execute(check_borrower_limit)

    for (count) in cur:
        print ''

    if count[0]>=3:
        tkMessageBox.showinfo("Error Message", "book limit execeded")
        return
    
    if no_of_copies==0:
        tkMessageBox.showinfo("Error Message", "no book copies available for checkout")
        return
    
    insert_book_loans=("INSERT INTO BOOK_LOANS (isbn,branch_id,card_no,date_out,due_date,date_in) "
                       "VALUES ('"+isbn+"','"+str(branch_id)+"','"+str(cardno)+"',curdate(),DATE_ADD(curdate(),INTERVAL 14 DAY),NULL)")

    print insert_book_loans
    cur.execute(insert_book_loans)
    cnx.commit()

    get_no_of_copies=("SELECT no_of_copies "
                      "FROM books_copies "
                      "WHERE book_id='"+str(isbn)+"' AND branch_id='"+str(branch_id)+"'")

    print get_no_of_copies
    cur.execute(get_no_of_copies)
    for (x) in cur:
        print ""
    
    update_no_of_copies=("UPDATE books_copies "
                         "SET no_of_copies='"+str(int(x[0])-1)+"' "
                         "WHERE book_id='"+str(isbn)+"' AND branch_id='"+str(branch_id)+"'")

    print update_no_of_copies
    cur.execute(update_no_of_copies)
    cnx.commit()                
    print "added successfully"
        
    
def onClickAddBorrower():
    for child in frame2.winfo_children():
        child.destroy()
    for child in frame3.winfo_children():
        child.destroy()
    for child in frame4.winfo_children():
        child.destroy()
     
    ssnLabel=Label(frame2,text='ENTER SSN')
    ssnLabel.pack(side=TOP)
    ssnTextField = Entry(frame2, bd =7)
    ssnTextField.pack(side = TOP)
    fnameLabel=Label(frame2,text='ENTER First Name')
    fnameLabel.pack(side=TOP)
    fnameTextField = Entry(frame2, bd =7)
    fnameTextField.pack(side = TOP)
    lnameLabel=Label(frame2,text='ENTER Last Name')
    lnameLabel.pack(side=TOP)
    lnameTextField = Entry(frame2, bd =7)
    lnameTextField.pack(side = TOP)
    emailLabel=Label(frame2,text='ENTER Email')
    emailLabel.pack(side=TOP)
    emailTextField = Entry(frame2, bd =7)
    emailTextField.pack(side = TOP)
    addressLabel=Label(frame2,text='ENTER Address')
    addressLabel.pack(side=TOP)
    addressTextField = Entry(frame2, bd =7)
    addressTextField.pack(side = TOP)
    cityLabel=Label(frame2,text='ENTER City')
    cityLabel.pack(side=TOP)
    cityTextField = Entry(frame2, bd =7)
    cityTextField.pack(side = TOP)
    stateLabel=Label(frame2,text='ENTER State')
    stateLabel.pack(side=TOP)
    stateTextField = Entry(frame2, bd =7)
    stateTextField.pack(side = TOP)
    phoneLabel=Label(frame2,text='ENTER Phone')
    phoneLabel.pack(side=TOP)
    phoneTextField = Entry(frame2, bd =7)
    phoneTextField.pack(side = TOP)

    submitButton=Button(frame3,text="Submit", command = lambda :onClickSubmit(ssnTextField.get(),fnameTextField.get(),lnameTextField.get(),emailTextField.get(),addressTextField.get(),cityTextField.get(),stateTextField.get(),phoneTextField.get()))
    submitButton.pack(side=LEFT)
    
def onClickSubmit(ssn,fname,lname,email,address,city,state,phone):
    if ssn=='' or fname=='' or lname=='' or email=='' or address=='' or city =='' or state=='' or phone=='':
        tkMessageBox.showinfo("Error Message", "enter all fields")
        return
    
    if len(ssn)!=9 or not ssn.isdigit():
        tkMessageBox.showinfo("Error Message", "Enter a valid 9 digit numerical ssn")
        print "Enter a valid 9 digit numerical ssn"
        return

    check_ssn=("SELECT COUNT(*) "
               "FROM borrower " 
               "WHERE ssn='"+ssn+"'")

    print check_ssn 
    cur.execute(check_ssn)

    for (count) in cur:
        if count[0]>0:
            tkMessageBox.showinfo("Message", "You are already a user")
            return

    card_no='ID'
    global card_no_count
    x=str(card_no_count).zfill(6)
    card_no+=x
    card_no_count+=1

    insert_borrower=("INSERT INTO borrower (card_no,ssn,fname,lname,email,address,city,state,phone) "
                     "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)")

    print insert_borrower
    cur.execute(insert_borrower,(card_no,ssn,fname,lname,email,address,city,state,phone))
    cnx.commit()

    print "added successfully" 


def onClickCheckIn():
    for child in frame2.winfo_children():
        child.destroy()
    for child in frame3.winfo_children():
        child.destroy()
    for child in frame4.winfo_children():
        child.destroy()

    searchCheckInLabel=Label(frame2,text='Search Book for CheckIn')
    searchCheckInLabel.pack(side=LEFT)
    searchCheckInTextField = Entry(frame2, bd =7)
    searchCheckInTextField.pack(side = LEFT)
    searchCheckInButton=Button(frame2, text="Search", command = lambda: onClickCheckInSearch(searchCheckInTextField.get()))
    searchCheckInButton.pack(side=LEFT)

def onClickCheckInSearch(text):
    for child in frame3.winfo_children():
        child.destroy()
    for child in frame4.winfo_children():
        child.destroy()

    tree = ttk.Treeview(frame3)
    ysb = ttk.Scrollbar(frame3, orient='vertical', command=tree.yview)
    xsb = ttk.Scrollbar(frame3, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)

    tree["columns"]=("one","two","three","four","five","six","seven","eight","nine")
    tree.column("#0", width=0)
    tree.column("one", width=70)
    tree.column("two", width=70)
    tree.column("three", width=70)
    tree.column("four", width=100)
    tree.column("five", width=100)
    tree.column("six", width=100)
    tree.column("seven", width=100)
    tree.column("eight", width=100)
    tree.column("nine", width=100)
    
    tree.heading("one", text="Loan Id")
    tree.heading("two", text="Isbn")
    tree.heading("three", text="Branch Id")
    tree.heading("four", text="Card No")
    tree.heading("five", text="fname")
    tree.heading("six", text="lname")
    tree.heading("seven", text="Date Out")
    tree.heading("eight", text="Due Date")
    tree.heading("nine", text="Date In")

    if "'" in text:
        text=text[:text.index("'")]+"'"+text[text.index("'"):]
        
    print text
    temp=""
    x=text.split(' ')
    for t in x:
        temp+="AND (bl.isbn LIKE '%"+t+"%' OR bl.card_no LIKE '%"+t+"%' OR b.fname LIKE '%"+t+"%' OR b.lname LIKE '%"+t+"%')"

    query=("SELECT bl.loan_id, bl.isbn, bl.branch_id, bl.card_no, b.fname, b.lname, bl.date_out, bl.due_date, bl.date_in "
           "FROM book_loans bl, borrower b "
           "WHERE bl.card_no=b.card_no AND date_in is NULL "+temp)

    print query
    cur.execute(query);
    i=1
    for (loan_id,isbn,branch_id,card_no,fname,lname,date_out,due_date,date_in) in cur:
        tree.insert("",i,text=("Line"+str(i)), values=(loan_id,isbn,branch_id,card_no,fname,lname,date_out,due_date,date_in))
        i+=1

    tree.grid(row=0, column=0)
    ysb.grid(row=0, column=1, sticky='ns')
    xsb.grid(row=1, column=0, sticky='ew')

    dateInLabel=Label(frame4,text='Enter date_in as number of days from date_out')
    dateInLabel.pack(side=LEFT)
    dateInTextField = Entry(frame4, bd =5)
    dateInTextField.pack(side = LEFT)
    checkInBookButton=Button(frame4,text="Check In Book", command = lambda :onClickCheckInBook(tree,dateInTextField.get()))
    checkInBookButton.pack(side=LEFT)

def onClickCheckInBook(tree,text):

    curItem=tree.selection()
    loan_id=tree.item(curItem).values()[2][0]
    isbn=tree.item(curItem).values()[2][1]
    isbn=str(isbn).zfill(10)
    branch_id=tree.item(curItem).values()[2][2]
    if loan_id=='':
        tkMessageBox.showinfo("Message", "SELECT a Tuple first")
        return

    update_book_loans=("UPDATE book_loans "
                       "SET date_in=DATE_ADD(date_out,INTERVAL "+text+" DAY) "
                       "WHERE loan_id='"+str(loan_id)+"'")

    print update_book_loans
    cur.execute(update_book_loans)
    cnx.commit()

    get_no_of_copies=("SELECT no_of_copies "
                      "FROM books_copies "
                      "WHERE book_id='"+str(isbn)+"' AND branch_id='"+str(branch_id)+"'")

    print get_no_of_copies
    cur.execute(get_no_of_copies)
    for (x) in cur:
        print x[0]
    
    update_no_of_copies=("UPDATE books_copies "
                         "SET no_of_copies='"+str(int(x[0])+1)+"' "
                         "WHERE book_id='"+str(isbn)+"' AND branch_id='"+str(branch_id)+"'")

    print update_no_of_copies
    cur.execute(update_no_of_copies)
    cnx.commit()                
    
    print "updated successfully"

    print text
    if int(text)>14:
        insert_query=("INSERT INTO fines "
                      "values ('"+str(loan_id)+"','"+str((int(text)-14)*0.25)+"','"+str(0)+"')")
        print insert_query
        cur.execute(insert_query)
        cnx.commit()

        print "fine added"

def onClickFines():
    for child in frame2.winfo_children():
        child.destroy()
    for child in frame3.winfo_children():
        child.destroy()
    for child in frame4.winfo_children():
        child.destroy()
        
    tree = ttk.Treeview(frame2)
    ysb = ttk.Scrollbar(frame2, orient='vertical', command=tree.yview)
    xsb = ttk.Scrollbar(frame2, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)

    tree["columns"]=("one","two","three")
    tree.column("#0", width=0)
    tree.column("one", width=70)
    tree.column("two", width=70)
    tree.column("three", width=70)
    
    tree.heading("one", text="Loan Id")
    tree.heading("two", text="Fine Amt")
    tree.heading("three", text="Paid")

    query=("SELECT * "
           "FROM fines "
           "WHERE paid='0'")

    print query
    cur.execute(query);
    i=1
    for (loan_id,fine_amt,paid) in cur:
        tree.insert("",i, values=(loan_id,fine_amt,paid))
        i+=1

    query=("SELECT loan_id,due_date "
           "FROM book_loans "
           "WHERE date_in is NULL")

    cur.execute(query)

    for (loan_id,due_date) in cur:
        if int((date.today() - due_date).days)>0:

            check_already_present=("SELECT COUNT(*) "
                                   "FROM fines "
                                   "WHERE loan_id='"+str(loan_id)+"'")

            print check_already_present
            cur2.execute(check_already_present)
            
            for (count) in cur2:
                if count[0]==1:
                    
                    print date.today(),due_date,(date.today() - due_date).days, int((date.today() - due_date).days)*0.25
                    update_query=("UPDATE fines "
                                  "SET fine_amt='"+str(int((date.today() - due_date).days)*0.25)+"' "
                                  "WHERE loan_id='"+str(loan_id)+"'")
                    
                    print update_query
                    cur3.execute(update_query)
                    cnx.commit()
                else:
                    insert_query=("INSERT INTO fines "
                                  "values ('"+str(loan_id)+"','"+str(int((date.today() - due_date).days)*0.25)+"','"+str(0)+"')")
                    print insert_query
                    cur3.execute(insert_query)
                    cnx.commit()
            print "fine added"
        
    tree.grid(row=0, column=0)
    ysb.grid(row=0, column=1, sticky='ns')
    xsb.grid(row=1, column=0, sticky='ew')

    print "userwisefine"
    userWiseFineBookButton=Button(frame4,text="User Wise Fine", command = lambda :onClickUserWiseFine())
    userWiseFineBookButton.pack(side=LEFT)
    print "userwisefine2"
    
def onClickUserWiseFine():
    for child in frame2.winfo_children():
        child.destroy()
    for child in frame3.winfo_children():
        child.destroy()
    for child in frame4.winfo_children():
        child.destroy()
        
    tree = ttk.Treeview(frame2)
    ysb = ttk.Scrollbar(frame2, orient='vertical', command=tree.yview)
    xsb = ttk.Scrollbar(frame2, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)

    tree["columns"]=("one","two")
    tree.column("#0", width=0)
    tree.column("one", width=70)
    tree.column("two", width=120)
    
    tree.heading("one", text="card_no")
    tree.heading("two", text="Total Fine Amt")

    query=("SELECT bl.card_no, SUM(f.fine_amt) "
           "FROM book_loans bl,fines f "
           "WHERE bl.loan_id=f.loan_id AND f.paid='0' "
           "GROUP BY bl.card_no")

    print query
    cur.execute(query);
    i=1
    for (card_no, total_fine) in cur:
        tree.insert("",i, values=(card_no,total_fine))
        i+=1

    tree.grid(row=0, column=0)
    ysb.grid(row=0, column=1, sticky='ns')
    xsb.grid(row=1, column=0, sticky='ew')

    loanIdWiseFineBookButton=Button(frame4,text="LoanId Wise Fine", command = lambda :onClickFines())
    loanIdWiseFineBookButton.pack(side=LEFT)

    acceptPaymentButton=Button(frame4,text="Accept Payment", command = lambda :onClickAcceptPayment(tree))
    acceptPaymentButton.pack(side=LEFT)

def onClickAcceptPayment(tree):

    curItem=tree.selection()
    card_no=tree.item(curItem).values()[2][0]

    get_loanid=("SELECT loan_id "
                "FROM book_loans "
                "WHERE card_no='"+card_no+"'")

    print get_loanid
    cur.execute(get_loanid)
    
    for (loan_id) in cur:
        check_date_in=("SELECT date_in "
                       "FROM book_loans "
                       "WHERE loan_id='"+str(loan_id[0])+"'")

        print check_date_in
        cur2.execute(check_date_in)
        
        for (date_in) in cur2:
            if date_in[0] is not None:
                update_fine_paid=("UPDATE fines "
                                   "SET paid='1' "
                                   "WHERE loan_id='"+str(loan_id[0])+"'")
            
                print update_fine_paid
                cur3.execute(update_fine_paid)
            else:
                tkMessageBox.showinfo("Message", "Book to be checkin first")
    cnx.commit()
    
root=Tk()
root.wm_title("LIBRARY MANAGEMENT SYSTEM")
root.geometry("1100x600")
##menu frame
frame1=Frame(root)
frame1.pack()
searchMenuButton = Button(frame1, text="Search Book", command=onClickSearchMenuButton)
searchMenuButton.pack(side=LEFT)
addBorrowerButton = Button(frame1, text="Add Borrower", command=onClickAddBorrower)
addBorrowerButton.pack(side=LEFT)
checkInButton= Button(frame1, text="Check In", command=onClickCheckIn)
checkInButton.pack(side=LEFT)
finesButton= Button(frame1, text="Fines/RefreshFines", command=onClickFines)
finesButton.pack(side=LEFT)
##individual menu work
frame2=Frame(root)
frame2.pack()
frame3=Frame(root)
frame3.pack()
frame4=Frame(root)
frame4.pack()



root.mainloop()

cur.close()
cnx.close()
