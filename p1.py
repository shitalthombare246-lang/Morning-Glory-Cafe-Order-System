# ==========================================
# Morning Glory Cafe Order System
# Database : MorningCafe.db
# Table    : Cafe
# ==========================================

from tkinter import *
from tkinter.messagebox import showinfo, showerror, askyesno
from tkinter.scrolledtext import ScrolledText
from sqlite3 import connect
from datetime import datetime
import requests

# -----------------------------
# Database auto-create
# -----------------------------
def create_table():
    with connect("MorningCafe.db") as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS Cafe (
            orderid INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT,
            choice TEXT,
            items TEXT,
            total_price REAL,
            payment_mode TEXT
        )
        """)
        con.commit()

create_table()

# -----------------------------
# Price List
# -----------------------------
PRICE_LIST = {
    "Cold Coffee": 80,
    "Pizza": 150,
    "Ice Cream": 60,
    "Burger": 100,
    "Sandwich": 70,
    "Fries": 50
}

# -----------------------------
# Main Window
# -----------------------------
root = Tk()
root.title("Morning Glory Cafe Order System")
root.geometry("450x420+200+100")
root.configure(bg="#E6F2E6")

f_title = ("Arial", 20, "bold")
f_btn = ("Arial", 14, "bold")
f_entry = ("Arial", 12)

Label(
    root,
    text="Morning Glory Cafe\nOrder System",
    font=f_title,
    bg="#E6F2E6"
).pack(pady=15)

# -----------------------------
# Location & Temperature Label
# -----------------------------
lbl_info = Label(
    root,
    text="Location, Temperature Quote",
    font=("Arial", 15),
    bg="#E6F2E6"
)
lbl_info.pack(side=BOTTOM, pady=10)

def update_location_temp():
    try:
        r = requests.get("https://ipinfo.io")
        data = r.json()
        city = data.get("city", "Unknown")

        api_key = "21272ad74a235c2dedc8fe3c58462a1b"
        wurl = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        wdata = requests.get(wurl).json()
        temp = wdata["main"]["temp"]

        lbl_info.config(
            text=f"Location: {city} | Temperature: {temp}°C"
        )
    except:
        lbl_info.config(text="Location / Temperature not available")

# -----------------------------
# ADD ORDER
# -----------------------------
def f_add():
    aw = Toplevel(root)
    aw.title("Add Order")
    aw.geometry("600x650+200+100")
    aw.configure(bg="#FFFACD")

    Label(aw, text="Add New Order", font=f_title, bg="#FFFACD").pack(pady=10)

    Label(aw, text="Order ID", font=f_entry, bg="#FFFACD").place(x=50, y=80)
    ent_id = Entry(aw, font=f_entry)
    ent_id.place(x=250, y=80)

    Label(aw, text="Customer Name", font=f_entry, bg="#FFFACD").place(x=50, y=130)
    ent_name = Entry(aw, font=f_entry)
    ent_name.place(x=250, y=130)

    Label(aw, text="Phone", font=f_entry, bg="#FFFACD").place(x=50, y=180)
    ent_phone = Entry(aw, font=f_entry)
    ent_phone.place(x=250, y=180)

    order_type = StringVar(value="DineIn")
    Label(aw, text="Order Type", font=f_entry, bg="#FFFACD").place(x=50, y=230)
    Radiobutton(aw, text="Dine In", variable=order_type, value="DineIn", bg="#FFFACD").place(x=250, y=230)
    Radiobutton(aw, text="Takeaway", variable=order_type, value="Takeaway", bg="#FFFACD").place(x=350, y=230)

    payment = StringVar(value="Cash")
    Label(aw, text="Payment Mode", font=f_entry, bg="#FFFACD").place(x=50, y=270)
    OptionMenu(aw, payment, "Cash", "UPI", "Card").place(x=250, y=270)

    Label(aw, text="Items", font=f_entry, bg="#FFFACD").place(x=50, y=320)

    vars_items = {}
    y = 350
    for item, price in PRICE_LIST.items():
        var = IntVar()
        Checkbutton(
            aw,
            text=f"{item} (₹{price})",
            variable=var,
            bg="#FFFACD"
        ).place(x=250, y=y)
        vars_items[item] = var
        y += 30

    def save_order():
        oid = ent_id.get()
        name = ent_name.get()
        phone = ent_phone.get()

        if not oid or not name or not phone:
            showerror("Error", "All fields required")
            return

        items = []
        total = 0
        for item, var in vars_items.items():
            if var.get() == 1:
                items.append(item)
                total += PRICE_LIST[item]

        if not items:
            showerror("Error", "Select at least one item")
            return

        with connect("MorningCafe.db") as con:
            con.execute(
                "INSERT INTO Cafe VALUES (?,?,?,?,?,?,?)",
                (oid, name, phone, order_type.get(), ", ".join(items), total, payment.get())
            )
            con.commit()

        showinfo("Success", f"Order Added\nTotal Bill: ₹{total}")
        aw.destroy()

    Button(
        aw,
        text="Save Order",
        font=f_btn,
        bg="green",
        fg="white",
        command=save_order
    ).place(x=250, y=y+20)

# -----------------------------
# VIEW ORDER
# -----------------------------
def f_view():
    vw = Toplevel(root)
    vw.title("View Orders")
    vw.geometry("650x400+200+100")

    st = ScrolledText(vw, font=f_entry, width=75, height=20)
    st.pack()

    with connect("MorningCafe.db") as con:
        rows = con.execute("SELECT * FROM Cafe")
        for r in rows:
            st.insert(END, f"{r}\n")

# -----------------------------
# DELETE ORDER
# -----------------------------
def f_delete():
    dw = Toplevel(root)
    dw.title("Delete Order")
    dw.geometry("300x200+200+100")

    Label(dw, text="Order ID", font=f_entry).pack(pady=10)
    ent = Entry(dw, font=f_entry)
    ent.pack()

    def delete():
        oid = ent.get()
        if askyesno("Confirm", "Delete this order?"):
            with connect("MorningCafe.db") as con:
                con.execute("DELETE FROM Cafe WHERE orderid=?", (oid,))
                con.commit()
            showinfo("Deleted", "Order Deleted")
            dw.destroy()

    Button(dw, text="Delete", font=f_btn, bg="red", fg="white", command=delete).pack(pady=20)

# -----------------------------
# MAIN BUTTONS
# -----------------------------
Button(root, text="Add Order", font=f_btn, width=20, bg="green", fg="white", command=f_add).pack(pady=6)
Button(root, text="View Order", font=f_btn, width=20, bg="blue", fg="white", command=f_view).pack(pady=6)
Button(root, text="Delete Order", font=f_btn, width=20, bg="red", fg="white", command=f_delete).pack(pady=6)
Button(root, text="Exit", font=f_btn, width=20, command=root.destroy).pack(pady=6)

update_location_temp()
root.mainloop()
