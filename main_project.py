from tkinter import Tk, Label, Frame, Entry, Button, messagebox, filedialog
from tkinter.ttk import Combobox
import os
import shutil
import time
from PIL import Image, ImageTk
import random
import project_tables
import sqlite3
import project_mails


def generate_captcha():
    """Generate a CAPTCHA containing 3 uppercase letters and 3 digits."""
    captcha = []

    for _ in range(3):
        c = chr(random.randint(65, 90))
        captcha.append(c)
        n = random.randint(0, 9)
        captcha.append(str(n))

    random.shuffle(captcha)
    return " ".join(captcha)


def refresh():
    global captcha_lbl, forgot_captcha

    captcha = generate_captcha()
    captcha_lbl.configure(text=captcha)

    # Keep the expected CAPTCHA in sync on the forgot-password screen.
    if "forgot_captcha" in globals():
        forgot_captcha = captcha


root = Tk()
root.state("zoomed")
root.configure(bg="powder blue")
root.title("ABC Bank")
root.resizable(width=False, height=False)

title_lbl = Label(
    root,
    text="Banking Automation",
    bg="powder blue",
    font=("Arial", 60, "bold", "underline"),
)
title_lbl.pack()

today_lbl = Label(
    root,
    text=time.strftime("%A, %d %B %Y"),
    bg="powder blue",
    font=("Arial", 15, "bold"),
    fg="blue",
)
today_lbl.pack(pady=10)

img = Image.open("images/logo.jpg").resize((300, 150))
img_bitmap = ImageTk.PhotoImage(img, master=root)
logo_lbl = Label(root, image=img_bitmap)
logo_lbl.place(relx=0, rely=0)

footer_lbl = Label(
    root,
    text="Developed By: xxxxxx",
    bg="powder blue",
    fg="blue",
    font=("Arial", 20, "bold"),
)
footer_lbl.pack(side="bottom", pady=10)


def main_screen():
    def forgot():
        frm.destroy()
        forgot_screen()

    def login():
        uacn = acn_entry.get().strip()
        upass = pass_entry.get()
        ucap = inputcap_entry.get().strip()
        utype = user_combo.get()

        actual_cap = captcha_lbl.cget("text").replace(" ", "")

        if utype == "Admin":
            if uacn == "0" and upass == "admin":
                if ucap == actual_cap:
                    frm.destroy()
                    admin_screen()
                else:
                    messagebox.showerror("Login", "Invalid captcha")
            else:
                messagebox.showerror(
                    "Login", "Invalid ACN/PASS/TYPE"
                )

        elif utype == "User":
            if ucap == actual_cap:
                conobj = sqlite3.connect(database="bank.sqlite")
                curobj = conobj.cursor()
                query = (
                    "select * from accounts "
                    "where accounts_acno=? and accounts_pass=?"
                )
                curobj.execute(query, (uacn, upass))
                tup = curobj.fetchone()
                conobj.close()

                if tup is None:
                    messagebox.showerror(
                        "User Login", "Invalid ACN/PASS"
                    )
                else:
                    frm.destroy()
                    user_screen(uacn)
            else:
                messagebox.showerror("Login", "Invalid captcha")
        else:
            messagebox.showerror(
                "Login", "Kindly Select Valid User Type"
            )

    frm = Frame(root)
    frm.configure(bg="pink")
    frm.place(relx=0, rely=0.15, relwidth=1, relheight=0.8)

    user_lbl = Label(
        frm, text="User Type", bg="pink", font=("Arial", 20, "bold")
    )
    user_lbl.place(relx=0.3, rely=0.1)

    user_combo = Combobox(
        frm,
        values=["Admin", "User", "---Select---"],
        font=("", 20),
        state="readonly",
    )
    user_combo.current(2)
    user_combo.place(relx=0.45, rely=0.1)

    acn_lbl = Label(
        frm, text="ACN", bg="pink", font=("Arial", 20, "bold")
    )
    acn_lbl.place(relx=0.3, rely=0.2)

    acn_entry = Entry(frm, font=("Arial", 20), bd=5)
    acn_entry.place(relx=0.45, rely=0.2)
    acn_entry.focus()

    pass_lbl = Label(
        frm, text="Pass", bg="pink", font=("Arial", 20, "bold")
    )
    pass_lbl.place(relx=0.3, rely=0.3)

    pass_entry = Entry(frm, font=("Arial", 20), bd=5, show="*")
    pass_entry.place(relx=0.45, rely=0.3)

    global captcha_lbl
    captcha_lbl = Label(
        frm,
        text=generate_captcha(),
        bg="white",
        font=("Arial", 20, "bold"),
    )
    captcha_lbl.place(relx=0.45, rely=0.4)

    refresh_btn = Button(
        frm, text="refresh", fg="blue", command=refresh
    )
    refresh_btn.place(relx=0.6, rely=0.4)

    inputcap_lbl = Label(
        frm, text="Captcha", bg="pink", font=("Arial", 20, "bold")
    )
    inputcap_lbl.place(relx=0.3, rely=0.5)

    inputcap_entry = Entry(frm, font=("Arial", 20), bd=5)
    inputcap_entry.place(relx=0.45, rely=0.5)

    login_btn = Button(
        frm,
        text="login",
        bg="powder blue",
        font=("Arial", 20, "bold"),
        bd=5,
        command=login,
    )
    login_btn.place(relx=0.48, rely=0.6)

    def reset_login():
        user_combo.current(2)
        acn_entry.delete(0, "end")
        pass_entry.delete(0, "end")
        inputcap_entry.delete(0, "end")
        acn_entry.focus()
        refresh()

    reset_btn = Button(
        frm,
        text="reset",
        bg="powder blue",
        font=("Arial", 20, "bold"),
        bd=5,
        command=reset_login,
    )
    reset_btn.place(relx=0.57, rely=0.6)

    forgot_btn = Button(
        frm,
        width=18,
        text="forgot password",
        bg="powder blue",
        font=("Arial", 20, "bold"),
        bd=5,
        command=forgot,
    )
    forgot_btn.place(relx=0.45, rely=0.7)


def admin_screen():
    def open_acn():
        def open_acn_db():
            uname = name_entry.get().strip()
            uemail = email_entry.get().strip()
            umob = mob_entry.get().strip()
            ugender = gender_combo.get()
            ubal = 0.0
            uopendate = time.strftime("%A, %d %B %Y")
            upass = generate_captcha().replace(" ", "")

            if not uname or not uemail or not umob or ugender == "---Select---":
                messagebox.showerror(
                    "Open Account", "Kindly fill all account details"
                )
                return

            conobj = sqlite3.connect(database="bank.sqlite")
            curobj = conobj.cursor()

            query = "insert into accounts values(null,?,?,?,?,?,?,?)"
            curobj.execute(
                query,
                (uname, upass, uemail, umob, ugender, uopendate, ubal),
            )
            conobj.commit()

            query = "select max(accounts_acno) from accounts"
            curobj.execute(query)
            uacno = curobj.fetchone()[0]
            conobj.close()

            try:
                project_mails.send_mail_for_openacn(
                    uemail, uacno, uname, upass, uopendate
                )
                msg = (
                    f"Account opened with ACN {uacno} and mail sent to "
                    f"{uemail}. Kindly check spam also"
                )
                messagebox.showinfo("Open Account", msg)
            except Exception as msg:
                messagebox.showerror("Open Account", str(msg))

        def reset():
            name_entry.delete(0, "end")
            email_entry.delete(0, "end")
            mob_entry.delete(0, "end")
            gender_combo.current(3)
            name_entry.focus()

        ifrm = Frame(
            frm, highlightthickness=2, highlightbackground="black"
        )
        ifrm.configure(bg="white")
        ifrm.place(relx=0.15, rely=0.2, relwidth=0.7, relheight=0.6)

        title_lbl = Label(
            ifrm,
            text="This is open account screen",
            bg="white",
            font=("Arial", 20, "bold"),
            fg="purple",
        )
        title_lbl.pack()

        name_lbl = Label(
            ifrm, text="Name", bg="white", font=("Arial", 20, "bold")
        )
        name_lbl.place(relx=0.1, rely=0.1)

        name_entry = Entry(ifrm, font=("Arial", 20), bd=5)
        name_entry.place(relx=0.1, rely=0.18)
        name_entry.focus()

        email_lbl = Label(
            ifrm, text="Email", bg="white", font=("Arial", 20, "bold")
        )
        email_lbl.place(relx=0.1, rely=0.4)

        email_entry = Entry(ifrm, font=("Arial", 20), bd=5)
        email_entry.place(relx=0.1, rely=0.48)

        mob_lbl = Label(
            ifrm, text="Mob", bg="white", font=("Arial", 20, "bold")
        )
        mob_lbl.place(relx=0.5, rely=0.1)

        mob_entry = Entry(ifrm, font=("Arial", 20), bd=5)
        mob_entry.place(relx=0.5, rely=0.18)

        gender_lbl = Label(
            ifrm, text="Gender", bg="white", font=("Arial", 20, "bold")
        )
        gender_lbl.place(relx=0.5, rely=0.4)

        gender_combo = Combobox(
            ifrm,
            values=["Male", "Female", "Others", "---Select---"],
            font=("", 20),
            state="readonly",
        )
        gender_combo.current(3)
        gender_combo.place(relx=0.5, rely=0.48)

        open_btn = Button(
            ifrm,
            text="open account",
            bg="powder blue",
            font=("Arial", 20, "bold"),
            bd=5,
            command=open_acn_db,
        )
        open_btn.place(relx=0.4, rely=0.7)

        reset_btn = Button(
            ifrm,
            command=reset,
            text="reset",
            bg="powder blue",
            font=("Arial", 20, "bold"),
            bd=5,
        )
        reset_btn.place(relx=0.7, rely=0.7)

    def delete_acn():
        def send_otp():
            nonlocal otp, uacn, otp_entry

            uacn = acn_entry.get().strip()
            conobj = sqlite3.connect(database="bank.sqlite")
            curobj = conobj.cursor()
            query = "select * from accounts where accounts_acno=?"
            curobj.execute(query, (uacn,))
            tup = curobj.fetchone()
            conobj.close()

            if tup is None:
                messagebox.showerror("Delete Account", "Record not found")
                return

            otp = str(random.randint(1000, 9999))
            project_mails.send_otp(tup[3], tup[1], otp)
            messagebox.showinfo(
                "Delete Account", "OTP sent to registered mail id"
            )

            otp_entry = Entry(ifrm, font=("Arial", 20), bd=5)
            otp_entry.place(relx=0.45, rely=0.6)

        def verify():
            uotp = otp_entry.get().strip()

            if otp == uotp:
                resp = messagebox.askyesno(
                    "Delete Account",
                    "Do you want to delete this account?",
                )

                if not resp:
                    return

                conobj = sqlite3.connect(database="bank.sqlite")
                curobj = conobj.cursor()
                query = "delete from accounts where accounts_acno=?"
                curobj.execute(query, (uacn,))
                conobj.commit()
                conobj.close()

                messagebox.showinfo("Delete Account", "Account Deleted")
                frm.destroy()
                admin_screen()
            else:
                messagebox.showerror("Delete Account", "Incorrect OTP")

        otp = ""
        uacn = ""
        otp_entry = None

        ifrm = Frame(
            frm, highlightthickness=2, highlightbackground="black"
        )
        ifrm.configure(bg="white")
        ifrm.place(relx=0.15, rely=0.2, relwidth=0.7, relheight=0.6)

        title_lbl = Label(
            ifrm,
            text="This is delete account screen",
            bg="white",
            font=("Arial", 20, "bold"),
            fg="purple",
        )
        title_lbl.pack()

        acn_lbl = Label(
            ifrm, text="ACN", bg="white", font=("Arial", 20, "bold")
        )
        acn_lbl.place(relx=0.3, rely=0.2)

        acn_entry = Entry(ifrm, font=("Arial", 20), bd=5)
        acn_entry.place(relx=0.45, rely=0.2)
        acn_entry.focus()

        otp_btn = Button(
            ifrm,
            command=send_otp,
            text="send OTP",
            bg="powder blue",
            font=("Arial", 20, "bold"),
            bd=5,
        )
        otp_btn.place(relx=0.45, rely=0.4)

        verify_btn = Button(
            ifrm,
            command=verify,
            text="verify",
            bg="powder blue",
            font=("Arial", 20, "bold"),
            bd=5,
        )
        verify_btn.place(relx=0.72, rely=0.6)

    def view_acn():
        def view_details():
            uacn = acn_entry.get().strip()

            conobj = sqlite3.connect(database="bank.sqlite")
            curobj = conobj.cursor()
            query = "select * from accounts where accounts_acno=?"
            curobj.execute(query, (uacn,))
            tup = curobj.fetchone()
            conobj.close()

            if tup is None:
                messagebox.showerror("View Account", "Record not found")
            else:
                details = (
                    f"User Name = {tup[1]}\n"
                    f"Aval Bal = {tup[7]}\n"
                    f"ACN Open date = {tup[6]}\n"
                    f"Email = {tup[3]}\n"
                    f"Mob = {tup[4]}"
                )
                messagebox.showinfo("View Account", details)

        ifrm = Frame(
            frm, highlightthickness=2, highlightbackground="black"
        )
        ifrm.configure(bg="white")
        ifrm.place(relx=0.15, rely=0.2, relwidth=0.7, relheight=0.6)

        title_lbl = Label(
            ifrm,
            text="This is view account screen",
            bg="white",
            font=("Arial", 20, "bold"),
            fg="purple",
        )
        title_lbl.pack()

        acn_lbl = Label(
            ifrm, text="ACN", bg="white", font=("Arial", 20, "bold")
        )
        acn_lbl.place(relx=0.3, rely=0.2)

        acn_entry = Entry(ifrm, font=("Arial", 20), bd=5)
        acn_entry.place(relx=0.45, rely=0.2)
        acn_entry.focus()

        view_btn = Button(
            ifrm,
            command=view_details,
            text="View",
            bg="powder blue",
            font=("Arial", 20, "bold"),
            bd=5,
        )
        view_btn.place(relx=0.45, rely=0.4)

    def logout():
        resp = messagebox.askyesno("logout", "Do you want to logout?")
        if resp:
            frm.destroy()
            main_screen()

    frm = Frame(root)
    frm.configure(bg="pink")
    frm.place(relx=0, rely=0.15, relwidth=1, relheight=0.8)

    wel_lbl = Label(
        frm,
        text="Welcome, Admin",
        bg="pink",
        font=("Arial", 20, "bold"),
        fg="green",
    )
    wel_lbl.place(relx=0, rely=0)

    logout_btn = Button(
        frm,
        text="logout",
        bg="powder blue",
        font=("Arial", 20, "bold"),
        bd=5,
        command=logout,
    )
    logout_btn.place(relx=0.9, rely=0)

    open_btn = Button(
        frm,
        text="open account",
        bg="green",
        font=("Arial", 20, "bold"),
        fg="white",
        bd=5,
        command=open_acn,
    )
    open_btn.place(relx=0.2, rely=0)

    delete_btn = Button(
        frm,
        text="delete account",
        bg="red",
        font=("Arial", 20, "bold"),
        fg="white",
        bd=5,
        command=delete_acn,
    )
    delete_btn.place(relx=0.4, rely=0)

    view_btn = Button(
        frm,
        text="view account",
        bg="yellow",
        font=("Arial", 20, "bold"),
        fg="black",
        bd=5,
        command=view_acn,
    )
    view_btn.place(relx=0.6, rely=0)


def forgot_screen():
    def back():
        frm.destroy()
        main_screen()

    def send_otp():
        nonlocal forgot_captcha

        uacn = acn_entry.get().strip()
        uemail = email_entry.get().strip()
        ucaptcha = inputcap_entry.get().strip()

        if ucaptcha != forgot_captcha.replace(" ", ""):
            messagebox.showerror("Forgot Password", "Invalid captcha")
            return

        conobj = sqlite3.connect(database="bank.sqlite")
        curobj = conobj.cursor()
        query = (
            "select * from accounts "
            "where accounts_acno=? and accounts_email=?"
        )
        curobj.execute(query, (uacn, uemail))
        tup = curobj.fetchone()
        conobj.close()

        if tup is None:
            messagebox.showerror("Forgot Password", "Record not found")
            return

        otp = str(random.randint(1000, 9999))
        project_mails.send_otp(uemail, tup[1], otp)
        messagebox.showinfo(
            "Forgot Pass", "OTP sent to given/registered mail id"
        )

        otp_entry = Entry(frm, font=("Arial", 20), bd=5)
        otp_entry.place(relx=0.45, rely=0.7)

        def verify():
            uotp = otp_entry.get().strip()
            if otp == uotp:
                messagebox.showinfo(
                    "Forgot Password", f"Your Pass = {tup[2]}"
                )
            else:
                messagebox.showerror(
                    "Forgot Password", "Incorrect OTP"
                )

        verify_btn = Button(
            frm,
            command=verify,
            text="verify",
            bg="powder blue",
            font=("Arial", 20, "bold"),
            bd=5,
        )
        verify_btn.place(relx=0.7, rely=0.7)

    frm = Frame(root)
    frm.configure(bg="pink")
    frm.place(relx=0, rely=0.15, relwidth=1, relheight=0.8)

    back_btn = Button(
        frm,
        text="back",
        bg="powder blue",
        font=("Arial", 20, "bold"),
        bd=5,
        command=back,
    )
    back_btn.place(relx=0, rely=0)

    acn_lbl = Label(
        frm, text="ACN", bg="pink", font=("Arial", 20, "bold")
    )
    acn_lbl.place(relx=0.3, rely=0.2)

    acn_entry = Entry(frm, font=("Arial", 20), bd=5)
    acn_entry.place(relx=0.45, rely=0.2)
    acn_entry.focus()

    email_lbl = Label(
        frm, text="Email", bg="pink", font=("Arial", 20, "bold")
    )
    email_lbl.place(relx=0.3, rely=0.3)

    email_entry = Entry(frm, font=("Arial", 20), bd=5)
    email_entry.place(relx=0.45, rely=0.3)

    forgot_captcha = generate_captcha()

    global captcha_lbl
    captcha_lbl = Label(
        frm,
        text=forgot_captcha,
        bg="white",
        font=("Arial", 20, "bold"),
    )
    captcha_lbl.place(relx=0.45, rely=0.4)

    refresh_btn = Button(
        frm, text="refresh", fg="blue", command=refresh
    )
    refresh_btn.place(relx=0.6, rely=0.4)

    inputcap_entry = Entry(frm, font=("Arial", 20), bd=5)
    inputcap_entry.place(relx=0.45, rely=0.5)

    otp_btn = Button(
        frm,
        command=send_otp,
        text="send OTP",
        bg="powder blue",
        font=("Arial", 20, "bold"),
        bd=5,
    )
    otp_btn.place(relx=0.45, rely=0.6)

    def reset():
        acn_entry.delete(0, "end")
        email_entry.delete(0, "end")
        inputcap_entry.delete(0, "end")
        acn_entry.focus()
        refresh()

    reset_btn = Button(
        frm,
        text="reset",
        bg="powder blue",
        font=("Arial", 20, "bold"),
        bd=5,
        command=reset,
    )
    reset_btn.place(relx=0.57, rely=0.6)


def user_screen(uacn=None):
    def logout():
        resp = messagebox.askyesno("logout", "Do you want to logout?")
        if resp:
            frm.destroy()
            main_screen()

    def update_btn_screen():
        def update_db():
            uname = name_entry.get().strip()
            upass = pass_entry.get()
            uemail = email_entry.get().strip()
            umob = mob_entry.get().strip()

            if not uname or not upass or not uemail or not umob:
                messagebox.showerror(
                    "Update Details", "Kindly fill all details"
                )
                return

            conobj = sqlite3.connect(database="bank.sqlite")
            curobj = conobj.cursor()
            query = (
                "update accounts set accounts_name=?, accounts_pass=?, "
                "accounts_email=?, accounts_mob=? "
                "where accounts_acno=?"
            )
            curobj.execute(
                query, (uname, upass, uemail, umob, uacn)
            )
            conobj.commit()
            conobj.close()

            messagebox.showinfo("Update Details", "Profile Updated")
            frm.destroy()
            user_screen(uacn)

        ifrm = Frame(
            frm, highlightthickness=2, highlightbackground="black"
        )
        ifrm.configure(bg="white")
        ifrm.place(relx=0.2, rely=0.2, relwidth=0.7, relheight=0.6)

        title_lbl = Label(
            ifrm,
            text="This is update screen",
            bg="white",
            font=("Arial", 20, "bold"),
            fg="purple",
        )
        title_lbl.pack()

        conobj = sqlite3.connect(database="bank.sqlite")
        curobj = conobj.cursor()
        curobj.execute(
            "select * from accounts where accounts_acno=?",
            (uacn,),
        )
        tup = curobj.fetchone()
        conobj.close()

        if tup is None:
            messagebox.showerror("Update Details", "Record not found")
            return

        name_lbl = Label(
            ifrm, text="Name", bg="white", font=("Arial", 20, "bold")
        )
        name_lbl.place(relx=0.1, rely=0.1)

        name_entry = Entry(ifrm, font=("Arial", 20), bd=5)
        name_entry.place(relx=0.1, rely=0.18)
        name_entry.insert(0, tup[1])
        name_entry.focus()

        email_lbl = Label(
            ifrm, text="Email", bg="white", font=("Arial", 20, "bold")
        )
        email_lbl.place(relx=0.1, rely=0.4)

        email_entry = Entry(ifrm, font=("Arial", 20), bd=5)
        email_entry.place(relx=0.1, rely=0.48)
        email_entry.insert(0, tup[3])

        mob_lbl = Label(
            ifrm, text="Mob", bg="white", font=("Arial", 20, "bold")
        )
        mob_lbl.place(relx=0.5, rely=0.1)

        mob_entry = Entry(ifrm, font=("Arial", 20), bd=5)
        mob_entry.place(relx=0.5, rely=0.18)
        mob_entry.insert(0, tup[4])

        pass_lbl = Label(
            ifrm, text="Pass", bg="white", font=("Arial", 20, "bold")
        )
        pass_lbl.place(relx=0.5, rely=0.4)

        pass_entry = Entry(ifrm, font=("Arial", 20), bd=5)
        pass_entry.place(relx=0.5, rely=0.48)
        pass_entry.insert(0, tup[2])

        update_btn = Button(
            ifrm,
            text="update",
            bg="powder blue",
            font=("Arial", 20, "bold"),
            bd=5,
            command=update_db,
        )
        update_btn.place(relx=0.4, rely=0.7)

    def deposit_btn_screen():
        def deposit():
            try:
                uamt = float(amt_entry.get())
            except ValueError:
                messagebox.showerror("Deposit", "Enter a valid amount")
                return

            if uamt <= 0:
                messagebox.showerror(
                    "Deposit", "Amount must be greater than 0"
                )
                return

            conobj = sqlite3.connect(database="bank.sqlite")
            curobj = conobj.cursor()

            query = (
                "update accounts set accounts_bal=accounts_bal+? "
                "where accounts_acno=?"
            )
            curobj.execute(query, (uamt, uacn))

            query = (
                "select accounts_bal from accounts "
                "where accounts_acno=?"
            )
            curobj.execute(query, (uacn,))
            ubal = curobj.fetchone()[0]

            t = str(time.time())
            utxnid = "txn" + t[: t.index(".")]

            query = "insert into stmts values(?,?,?,?,?,?)"
            curobj.execute(
                query,
                (
                    uacn,
                    uamt,
                    "CR.",
                    time.strftime("%d-%m-%Y %r"),
                    ubal,
                    utxnid,
                ),
            )

            conobj.commit()
            conobj.close()

            messagebox.showinfo(
                "Deposit", f"{uamt} Amount Deposited"
            )
            frm.destroy()
            user_screen(uacn)

        ifrm = Frame(
            frm, highlightthickness=2, highlightbackground="black"
        )
        ifrm.configure(bg="white")
        ifrm.place(relx=0.2, rely=0.2, relwidth=0.7, relheight=0.6)

        title_lbl = Label(
            ifrm,
            text="This is deposit screen",
            bg="white",
            font=("Arial", 20, "bold"),
            fg="purple",
        )
        title_lbl.pack()

        amt_lbl = Label(
            ifrm, text="Amount", bg="white", font=("Arial", 20, "bold")
        )
        amt_lbl.place(relx=0.3, rely=0.2)

        amt_entry = Entry(ifrm, font=("Arial", 20), bd=5)
        amt_entry.place(relx=0.45, rely=0.2)
        amt_entry.focus()

        dep_btn = Button(
            ifrm,
            command=deposit,
            text="deposit",
            bg="powder blue",
            font=("Arial", 20, "bold"),
            bd=5,
        )
        dep_btn.place(relx=0.45, rely=0.4)

    def withdraw_btn_screen():
        def withdraw():
            try:
                uamt = float(amt_entry.get())
            except ValueError:
                messagebox.showerror("Withdraw", "Enter a valid amount")
                return

            if uamt <= 0:
                messagebox.showerror(
                    "Withdraw", "Amount must be greater than 0"
                )
                return

            conobj = sqlite3.connect(database="bank.sqlite")
            curobj = conobj.cursor()

            query = (
                "select accounts_bal from accounts "
                "where accounts_acno=?"
            )
            curobj.execute(query, (uacn,))
            row = curobj.fetchone()

            if row is None:
                conobj.close()
                messagebox.showerror("Withdraw", "Account not found")
                return

            ubal = row[0]

            if ubal >= uamt:
                query = (
                    "update accounts set accounts_bal=accounts_bal-? "
                    "where accounts_acno=?"
                )
                curobj.execute(query, (uamt, uacn))
                new_bal = ubal - uamt

                t = str(time.time())
                utxnid = "txn" + t[: t.index(".")]

                query = "insert into stmts values(?,?,?,?,?,?)"
                curobj.execute(
                    query,
                    (
                        uacn,
                        uamt,
                        "DB.",
                        time.strftime("%d-%m-%Y %r"),
                        new_bal,
                        utxnid,
                    ),
                )

                conobj.commit()
                conobj.close()

                messagebox.showinfo(
                    "Withdraw", f"{uamt} Amount Withdrawn"
                )
                frm.destroy()
                user_screen(uacn)
            else:
                conobj.close()
                messagebox.showerror(
                    "Withdraw", f"Insufficient Bal {ubal}"
                )

        ifrm = Frame(
            frm, highlightthickness=2, highlightbackground="black"
        )
        ifrm.configure(bg="white")
        ifrm.place(relx=0.2, rely=0.2, relwidth=0.7, relheight=0.6)

        title_lbl = Label(
            ifrm,
            text="This is withdraw screen",
            bg="white",
            font=("Arial", 20, "bold"),
            fg="purple",
        )
        title_lbl.pack()

        amt_lbl = Label(
            ifrm, text="Amount", bg="white", font=("Arial", 20, "bold")
        )
        amt_lbl.place(relx=0.3, rely=0.2)

        amt_entry = Entry(ifrm, font=("Arial", 20), bd=5)
        amt_entry.place(relx=0.45, rely=0.2)
        amt_entry.focus()

        withdraw_btn = Button(
            ifrm,
            command=withdraw,
            text="withdraw",
            bg="powder blue",
            font=("Arial", 20, "bold"),
            bd=5,
        )
        withdraw_btn.place(relx=0.45, rely=0.4)

    def check_btn_screen():
        ifrm = Frame(
            frm, highlightthickness=2, highlightbackground="black"
        )
        ifrm.configure(bg="white")
        ifrm.place(relx=0.2, rely=0.2, relwidth=0.7, relheight=0.6)

        title_lbl = Label(
            ifrm,
            text="This is details screen",
            bg="white",
            font=("Arial", 20, "bold"),
            fg="purple",
        )
        title_lbl.pack()

        conobj = sqlite3.connect(database="bank.sqlite")
        curobj = conobj.cursor()
        curobj.execute(
            "select * from accounts where accounts_acno=?",
            (uacn,),
        )
        tup = curobj.fetchone()
        conobj.close()

        if tup is None:
            messagebox.showerror("Details", "Account not found")
            return

        details = (
            f"Account No. = {tup[0]}\n"
            f"Opening Date = {tup[6]}\n"
            f"Available Bal = {tup[7]}\n"
            f"Email Id = {tup[3]}\n"
            f"Mob No. = {tup[4]}"
        )

        details_lbl = Label(
            ifrm,
            text=details,
            bg="white",
            fg="purple",
            font=("arial", 20, "bold"),
        )
        details_lbl.place(relx=0.2, rely=0.2)

    def transfer_btn_screen():
        def transfer():
            toacn = to_entry.get().strip()

            try:
                uamt = float(amt_entry.get())
            except ValueError:
                messagebox.showerror("Transfer", "Enter a valid amount")
                return

            if uamt <= 0:
                messagebox.showerror(
                    "Transfer", "Amount must be greater than 0"
                )
                return

            if toacn == str(uacn):
                messagebox.showerror(
                    "Transfer",
                    "Source and destination accounts must be different",
                )
                return

            conobj = sqlite3.connect(database="bank.sqlite")
            curobj = conobj.cursor()

            query = "select * from accounts where accounts_acno=?"
            curobj.execute(query, (toacn,))
            to_tup = curobj.fetchone()

            if to_tup is None:
                conobj.close()
                messagebox.showerror(
                    "Transfer", "To ACN does not exist"
                )
                return

            query = (
                "select accounts_bal from accounts "
                "where accounts_acno=?"
            )
            curobj.execute(query, (uacn,))
            from_row = curobj.fetchone()

            if from_row is None:
                conobj.close()
                messagebox.showerror(
                    "Transfer", "Source account not found"
                )
                return

            ubal = from_row[0]

            if ubal >= uamt:
                query = (
                    "select accounts_bal from accounts "
                    "where accounts_acno=?"
                )
                curobj.execute(query, (toacn,))
                to_bal = curobj.fetchone()[0]

                query_deduct = (
                    "update accounts set accounts_bal=accounts_bal-? "
                    "where accounts_acno=?"
                )
                query_credit = (
                    "update accounts set accounts_bal=accounts_bal+? "
                    "where accounts_acno=?"
                )

                curobj.execute(query_deduct, (uamt, uacn))
                curobj.execute(query_credit, (uamt, toacn))

                t = str(time.time())
                txn_time = time.strftime("%d-%m-%Y %r")
                utxnid1 = "txn_db" + t[: t.index(".")]
                utxnid2 = "txn_cr" + t[: t.index(".")]

                query = "insert into stmts values(?,?,?,?,?,?)"
                curobj.execute(
                    query,
                    (
                        uacn,
                        uamt,
                        "DB.",
                        txn_time,
                        ubal - uamt,
                        utxnid1,
                    ),
                )
                curobj.execute(
                    query,
                    (
                        toacn,
                        uamt,
                        "CR.",
                        txn_time,
                        to_bal + uamt,
                        utxnid2,
                    ),
                )

                conobj.commit()
                conobj.close()

                messagebox.showinfo(
                    "Transfer", f"{uamt} Amount Transferred"
                )
                frm.destroy()
                user_screen(uacn)
            else:
                conobj.close()
                messagebox.showerror(
                    "Transfer", f"Insufficient Bal {ubal}"
                )

        ifrm = Frame(
            frm, highlightthickness=2, highlightbackground="black"
        )
        ifrm.configure(bg="white")
        ifrm.place(relx=0.2, rely=0.2, relwidth=0.7, relheight=0.6)

        title_lbl = Label(
            ifrm,
            text="This is transfer screen",
            bg="white",
            font=("Arial", 20, "bold"),
            fg="purple",
        )
        title_lbl.pack()

        to_lbl = Label(
            ifrm, text="TO ACN", bg="white", font=("Arial", 20, "bold")
        )
        to_lbl.place(relx=0.3, rely=0.2)

        to_entry = Entry(ifrm, font=("Arial", 20), bd=5)
        to_entry.place(relx=0.45, rely=0.2)
        to_entry.focus()

        amt_lbl = Label(
            ifrm, text="Amount", bg="white", font=("Arial", 20, "bold")
        )
        amt_lbl.place(relx=0.3, rely=0.4)

        amt_entry = Entry(ifrm, font=("Arial", 20), bd=5)
        amt_entry.place(relx=0.45, rely=0.4)

        tr_btn = Button(
            ifrm,
            command=transfer,
            text="transfer",
            bg="powder blue",
            font=("Arial", 20, "bold"),
            bd=5,
        )
        tr_btn.place(relx=0.55, rely=0.6)

    def history_btn_screen():
        ifrm = Frame(
            frm, highlightthickness=2, highlightbackground="black"
        )
        ifrm.configure(bg="white")
        ifrm.place(relx=0.2, rely=0.2, relwidth=0.7, relheight=0.6)

        title_lbl = Label(
            ifrm,
            text="This is txn history screen",
            bg="white",
            font=("Arial", 20, "bold"),
            fg="purple",
        )
        title_lbl.pack()

        import tktable

        table_headers = (
            "Txn ID",
            "Amount",
            "Txn Type",
            "Updated Bal",
            "Date",
        )
        mytable = tktable.Table(
            ifrm,
            table_headers,
            col_width=150,
            headings_bold=True,
        )
        mytable.pack(pady=10)

        conobj = sqlite3.connect(database="bank.sqlite")
        curobj = conobj.cursor()
        query = (
            "select stmts_txnid, stmts_amt, stmts_type, "
            "stmts_update_bal, stmts_date from stmts "
            "where stmts_acn=?"
        )
        curobj.execute(query, (uacn,))

        for tup in curobj:
            mytable.insert_row(tup)

        conobj.close()

        import sys
        del sys.modules["tktable"]

    def getdetail():
        conobj = sqlite3.connect(database="bank.sqlite")
        curobj = conobj.cursor()
        query = "select * from accounts where accounts_acno=?"
        curobj.execute(query, (uacn,))
        tup = curobj.fetchone()
        conobj.close()
        return tup

    def update_picture():
        path = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif"),
                ("All files", "*.*"),
            ],
        )

        if not path:
            return

        destination = f"images/{uacn}.png"
        shutil.copy(path, destination)

        profile_img = Image.open(destination).resize((210, 180))
        bitmap_profile_img = ImageTk.PhotoImage(
            profile_img, master=root
        )
        profile_img_lbl.image = bitmap_profile_img
        profile_img_lbl.configure(image=bitmap_profile_img)

    frm = Frame(root)
    frm.configure(bg="pink")
    frm.place(relx=0, rely=0.15, relwidth=1, relheight=0.8)

    wel_lbl = Label(
        frm,
        text=f"Welcome, {getdetail()[1]}",
        bg="pink",
        font=("Arial", 20, "bold"),
        fg="green",
    )
    wel_lbl.place(relx=0, rely=0)

    logout_btn = Button(
        frm,
        text="logout",
        bg="powder blue",
        font=("Arial", 20, "bold"),
        bd=5,
        command=logout,
    )
    logout_btn.place(relx=0.92, rely=0)

    if os.path.exists(f"images/{uacn}.png"):
        path = f"images/{uacn}.png"
    else:
        path = "images/default_pic.jpg"

    profile_img = Image.open(path).resize((210, 180))
    bitmap_profile_img = ImageTk.PhotoImage(profile_img, master=root)

    profile_img_lbl = Label(frm, image=bitmap_profile_img)
    profile_img_lbl.image = bitmap_profile_img
    profile_img_lbl.place(relx=0.005, rely=0.08)

    update_pic_btn = Button(
        frm,
        command=update_picture,
        text="update picture",
        width=12,
        bg="yellow",
        font=("Arial", 20, "bold"),
        bd=5,
    )
    update_pic_btn.place(relx=0.005, rely=0.3)

    check_btn = Button(
        frm,
        text="check details",
        width=12,
        bg="yellow",
        font=("Arial", 20, "bold"),
        bd=5,
        command=check_btn_screen,
    )
    check_btn.place(relx=0.005, rely=0.4)

    deposit_btn = Button(
        frm,
        text="deposit",
        width=12,
        bg="green",
        font=("Arial", 20, "bold"),
        bd=5,
        fg="white",
        command=deposit_btn_screen,
    )
    deposit_btn.place(relx=0.005, rely=0.5)

    withdraw_btn = Button(
        frm,
        text="withdraw",
        width=12,
        bg="red",
        font=("Arial", 20, "bold"),
        bd=5,
        fg="white",
        command=withdraw_btn_screen,
    )
    withdraw_btn.place(relx=0.005, rely=0.6)

    update_btn = Button(
        frm,
        text="update",
        width=12,
        bg="powder blue",
        font=("Arial", 20, "bold"),
        bd=5,
        command=update_btn_screen,
    )
    update_btn.place(relx=0.005, rely=0.7)

    transfer_btn = Button(
        frm,
        text="transfer",
        width=12,
        bg="red",
        font=("Arial", 20, "bold"),
        bd=5,
        fg="white",
        command=transfer_btn_screen,
    )
    transfer_btn.place(relx=0.005, rely=0.8)

    history_btn = Button(
        frm,
        text="history",
        width=12,
        bg="powder blue",
        font=("Arial", 20, "bold"),
        bd=5,
        command=history_btn_screen,
    )
    history_btn.place(relx=0.005, rely=0.9)


main_screen()
root.mainloop()
