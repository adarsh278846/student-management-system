import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB = "students.db"

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, roll TEXT NOT NULL UNIQUE,
            class_name TEXT, age INTEGER, phone TEXT,
            math REAL DEFAULT 0, science REAL DEFAULT 0, english REAL DEFAULT 0
        )""")

def grade(avg):
    if avg >= 90: return "A+"
    if avg >= 80: return "A"
    if avg >= 70: return "B"
    if avg >= 60: return "C"
    if avg >= 50: return "D"
    return "F"

def clear_form():
    for v in (name_v, roll_v, class_v, age_v, phone_v, math_v, sci_v, eng_v):
        v.set("")
    selected_id.set("")

def load_students():
    tree.delete(*tree.get_children())
    with sqlite3.connect(DB) as con:
        rows = con.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    for r in rows:
        avg = round((r[6] + r[7] + r[8]) / 3, 1)
        tree.insert("", "end", iid=str(r[0]),
                    values=(r[1], r[2], r[3], r[4], r[5], avg, grade(avg)))

def save_student():
    if not name_v.get().strip() or not roll_v.get().strip():
        messagebox.showwarning("Missing", "Name and Roll No. are required.")
        return
    try:
        vals = (name_v.get().strip(), roll_v.get().strip(), class_v.get().strip(),
                int(age_v.get()) if age_v.get() else None, phone_v.get().strip(),
                float(math_v.get() or 0), float(sci_v.get() or 0), float(eng_v.get() or 0))
        if any(x < 0 or x > 100 for x in vals[5:]):
            raise ValueError
        with sqlite3.connect(DB) as con:
            if selected_id.get():
                con.execute("""UPDATE students SET name=?,roll=?,class_name=?,age=?,phone=?,
                    math=?,science=?,english=? WHERE id=?""", vals + (int(selected_id.get()),))
            else:
                con.execute("""INSERT INTO students
                    (name,roll,class_name,age,phone,math,science,english)
                    VALUES (?,?,?,?,?,?,?,?)""", vals)
        load_students(); clear_form()
        messagebox.showinfo("Saved", "Student record saved successfully.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Roll No. already exists.")
    except ValueError:
        messagebox.showerror("Error", "Age/marks must be valid numbers. Marks must be 0–100.")

def select_student(event=None):
    sel = tree.selection()
    if not sel: return
    sid = int(sel[0]); selected_id.set(str(sid))
    with sqlite3.connect(DB) as con:
        r = con.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
    if r:
        for var, val in zip((name_v, roll_v, class_v, age_v, phone_v, math_v, sci_v, eng_v),
                            (r[1], r[2], r[3], r[4] or "", r[5], r[6], r[7], r[8])):
            var.set(val)

def delete_student():
    sel = tree.selection()
    if not sel: return
    if messagebox.askyesno("Confirm", "Delete selected student?"):
        with sqlite3.connect(DB) as con:
            con.execute("DELETE FROM students WHERE id=?", (int(sel[0]),))
        load_students(); clear_form()

def search():
    q = search_v.get().strip()
    tree.delete(*tree.get_children())
    with sqlite3.connect(DB) as con:
        rows = con.execute("""SELECT * FROM students
            WHERE name LIKE ? OR roll LIKE ? OR class_name LIKE ?
            ORDER BY name""", (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
    for r in rows:
        avg = round((r[6]+r[7]+r[8])/3, 1)
        tree.insert("", "end", iid=str(r[0]), values=(r[1],r[2],r[3],r[4],r[5],avg,grade(avg)))

init_db()
root = tk.Tk()
root.title("Student Management System")
root.geometry("1100x650")
root.minsize(900, 550)

style = ttk.Style()
style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

name_v, roll_v, class_v, age_v = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
phone_v, math_v, sci_v, eng_v = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
search_v, selected_id = tk.StringVar(), tk.StringVar()

top = ttk.Frame(root, padding=12); top.pack(fill="x")
ttk.Label(top, text="STUDENT MANAGEMENT SYSTEM", font=("Segoe UI", 20, "bold")).pack(anchor="w")
ttk.Label(top, text="Add, edit, search and manage student records").pack(anchor="w")

form = ttk.LabelFrame(root, text="Student Details", padding=10); form.pack(fill="x", padx=12, pady=5)
fields = [("Name",name_v),("Roll No.",roll_v),("Class",class_v),("Age",age_v),("Phone",phone_v),
          ("Math",math_v),("Science",sci_v),("English",eng_v)]
for i,(label,var) in enumerate(fields):
    ttk.Label(form,text=label).grid(row=i//4*2,column=i%4*2,padx=5,pady=3,sticky="w")
    ttk.Entry(form,textvariable=var,width=22).grid(row=i//4*2+1,column=i%4*2,padx=5,pady=3,sticky="ew")
for c in range(8): form.columnconfigure(c,weight=1)

buttons=ttk.Frame(root,padding=8); buttons.pack(fill="x",padx=12)
ttk.Button(buttons,text="Save / Update",command=save_student).pack(side="left",padx=4)
ttk.Button(buttons,text="Clear",command=clear_form).pack(side="left",padx=4)
ttk.Button(buttons,text="Delete",command=delete_student).pack(side="left",padx=4)
ttk.Label(buttons,text="Search:").pack(side="left",padx=(25,5))
ttk.Entry(buttons,textvariable=search_v,width=28).pack(side="left")
ttk.Button(buttons,text="Search",command=search).pack(side="left",padx=4)
ttk.Button(buttons,text="Show All",command=load_students).pack(side="left",padx=4)

frame=ttk.Frame(root,padding=12); frame.pack(fill="both",expand=True)
cols=("Name","Roll No.","Class","Age","Phone","Average","Grade")
tree=ttk.Treeview(frame,columns=cols,show="headings")
for c in cols:
    tree.heading(c,text=c); tree.column(c,width=120,anchor="center")
tree.column("Name",width=180,anchor="w")
ys=ttk.Scrollbar(frame,orient="vertical",command=tree.yview); tree.configure(yscrollcommand=ys.set)
tree.pack(side="left",fill="both",expand=True); ys.pack(side="right",fill="y")
tree.bind("<<TreeviewSelect>>",select_student)

load_students()
root.mainloop()

