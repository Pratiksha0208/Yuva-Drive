import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def init_db():
    conn = sqlite3.connect("yuva_drive.db")
    c = conn.cursor()

    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                )''')

  
    c.execute('''CREATE TABLE IF NOT EXISTS drives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company TEXT NOT NULL,
                    date TEXT NOT NULL,
                    eligibility TEXT NOT NULL,
                    venue TEXT NOT NULL,
                    details TEXT
                )''')

   
    c.execute('''CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    drive_id INTEGER,
                    FOREIGN KEY(student_id) REFERENCES users(id),
                    FOREIGN KEY(drive_id) REFERENCES drives(id)
                )''')

    
    c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
    c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('student1', 'password123', 'student')")

    conn.commit()
    conn.close()


#  APP CLASS 
class YuvaDrivePortal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🎓 Yuva Drive Portal")
        self.geometry("1000x650")

        ctk.set_default_color_theme("blue")
        ctk.set_appearance_mode("light")

        self.logo_color = "#1976D2"
        self.user_id = None
        self.user_role = None

        self.show_login_page()

 
    def show_login_page(self):
        for w in self.winfo_children():
            w.destroy()

        frame = ctk.CTkFrame(self, corner_radius=20)
        frame.pack(expand=True, padx=120, pady=80, fill="both")

        ctk.CTkLabel(frame, text="🎓 YUVA DRIVE PORTAL", font=("Helvetica", 32, "bold"), text_color=self.logo_color).pack(pady=20)
        ctk.CTkLabel(frame, text="Campus Drive Management System", font=("Helvetica", 15)).pack(pady=5)

        self.username = ctk.CTkEntry(frame, placeholder_text="Username", width=260)
        self.username.pack(pady=10)
        self.password = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=260)
        self.password.pack(pady=10)

        ctk.CTkButton(frame, text="Login", command=self.login, width=200, fg_color=self.logo_color).pack(pady=10)
        ctk.CTkButton(frame, text="Register as Student", command=self.show_register_page, fg_color="green").pack(pady=10)

        self.mode_var = ctk.StringVar(value="light")
        ctk.CTkSwitch(frame, text="🌗 Dark Mode", variable=self.mode_var,
                      onvalue="dark", offvalue="light", command=self.toggle_mode).pack(pady=10)

    def toggle_mode(self):
        ctk.set_appearance_mode(self.mode_var.get())

    def login(self):
        uname = self.username.get()
        pwd = self.password.get()

        conn = sqlite3.connect("yuva_drive.db")
        c = conn.cursor()
        c.execute("SELECT id, role FROM users WHERE username=? AND password=?", (uname, pwd))
        user = c.fetchone()
        conn.close()

        if user:
            self.user_id, self.user_role = user
            if self.user_role == "admin":
                self.show_admin_dashboard()
            else:
                self.show_student_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password!")


    def show_register_page(self):
        for w in self.winfo_children():
            w.destroy()

        frame = ctk.CTkFrame(self, corner_radius=20)
        frame.pack(expand=True, padx=120, pady=80, fill="both")

        ctk.CTkLabel(frame, text="📝 Student Registration", font=("Helvetica", 28, "bold"), text_color="green").pack(pady=20)

        username = ctk.CTkEntry(frame, placeholder_text="Create Username", width=260)
        username.pack(pady=10)
        password = ctk.CTkEntry(frame, placeholder_text="Create Password", show="*", width=260)
        password.pack(pady=10)

        def register():
            uname = username.get()
            pwd = password.get()
            if not uname or not pwd:
                messagebox.showwarning("Error", "All fields required")
                return

            conn = sqlite3.connect("yuva_drive.db")
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'student')", (uname, pwd))
                conn.commit()
                messagebox.showinfo("Success", "Registration successful! You can now log in.")
                self.show_login_page()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists!")
            finally:
                conn.close()

        ctk.CTkButton(frame, text="Register", command=register, fg_color="green").pack(pady=10)
        ctk.CTkButton(frame, text="⬅ Back to Login", command=self.show_login_page).pack(pady=10)


    def show_student_dashboard(self):
        for w in self.winfo_children():
            w.destroy()

        top = self.make_topbar("🎓 Student Dashboard")

        drives_frame = ctk.CTkScrollableFrame(self, label_text="📢 Available Campus Drives")
        drives_frame.pack(fill="both", expand=True, padx=20, pady=10)

        conn = sqlite3.connect("yuva_drive.db")
        c = conn.cursor()
        c.execute("SELECT id, company, date, eligibility, venue, details FROM drives")
        rows = c.fetchall()
        conn.close()

        for d in rows:
            f = ctk.CTkFrame(drives_frame, corner_radius=12)
            f.pack(pady=8, padx=15, fill="x")

            ctk.CTkLabel(f, text=f"🏢 {d[1]}", font=("Helvetica", 18, "bold")).pack(anchor="w", padx=10)
            ctk.CTkLabel(f, text=f"📅 {d[2]} | 🎓 {d[3]} | 📍 {d[4]}", font=("Helvetica", 13)).pack(anchor="w", padx=10)
            ctk.CTkLabel(f, text=f"📝 {d[5]}", font=("Helvetica", 12)).pack(anchor="w", padx=10)

            ctk.CTkButton(f, text="Apply", fg_color=self.logo_color,
                          command=lambda did=d[0]: self.apply_drive(did)).pack(anchor="e", padx=10, pady=5)

    def apply_drive(self, drive_id):
        conn = sqlite3.connect("yuva_drive.db")
        c = conn.cursor()

        c.execute("SELECT * FROM applications WHERE student_id=? AND drive_id=?", (self.user_id, drive_id))
        exists = c.fetchone()

        if exists:
            messagebox.showinfo("Already Applied", "You have already applied for this drive.")
        else:
            c.execute("INSERT INTO applications (student_id, drive_id) VALUES (?, ?)", (self.user_id, drive_id))
            conn.commit()
            messagebox.showinfo("Success", "You have successfully applied!")
        conn.close()

    def show_admin_dashboard(self):
        for w in self.winfo_children():
            w.destroy()

        top = self.make_topbar("🧑‍💼 Admin Dashboard", show_admin=True)
        drives_frame = ctk.CTkScrollableFrame(self, label_text="Campus Drives")
        drives_frame.pack(fill="both", expand=True, padx=20, pady=10)

        conn = sqlite3.connect("yuva_drive.db")
        c = conn.cursor()
        c.execute("SELECT id, company, date, eligibility, venue, details FROM drives")
        rows = c.fetchall()
        conn.close()

        for d in rows:
            f = ctk.CTkFrame(drives_frame, corner_radius=12)
            f.pack(pady=8, padx=15, fill="x")

            ctk.CTkLabel(f, text=f"🏢 {d[1]}", font=("Helvetica", 18, "bold")).pack(anchor="w", padx=10)
            ctk.CTkLabel(f, text=f"📅 {d[2]} | 🎓 {d[3]} | 📍 {d[4]}", font=("Helvetica", 13)).pack(anchor="w", padx=10)
            ctk.CTkLabel(f, text=f"📝 {d[5]}", font=("Helvetica", 12)).pack(anchor="w", padx=10)
            ctk.CTkButton(f, text="👥 View Applicants", command=lambda did=d[0]: self.show_applicants(did)).pack(side="right", padx=10, pady=5)
            ctk.CTkButton(f, text="🗑 Delete", fg_color="red", command=lambda did=d[0]: self.delete_drive(did)).pack(side="right", padx=10, pady=5)

    def make_topbar(self, title, show_admin=False):
        top = ctk.CTkFrame(self, corner_radius=10)
        top.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top, text=title, font=("Helvetica", 24, "bold")).pack(side="left", padx=20)

        if show_admin:
            ctk.CTkButton(top, text="➕ Add Drive", command=self.add_drive_popup, fg_color=self.logo_color).pack(side="left", padx=10)
            ctk.CTkButton(top, text="📊 Stats", command=self.show_chart_popup).pack(side="left", padx=10)

        ctk.CTkButton(top, text="Logout", fg_color="red", command=self.show_login_page).pack(side="right", padx=20)
        return top

    def add_drive_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Add New Drive")
        popup.geometry("400x480")

        ctk.CTkLabel(popup, text="➕ Add Drive", font=("Helvetica", 22, "bold")).pack(pady=20)

        company = ctk.CTkEntry(popup, placeholder_text="Company Name", width=300)
        company.pack(pady=8)
        date = ctk.CTkEntry(popup, placeholder_text="Date (e.g., 20 Oct 2025)", width=300)
        date.pack(pady=8)
        eligibility = ctk.CTkEntry(popup, placeholder_text="Eligibility (e.g., BE-CSE)", width=300)
        eligibility.pack(pady=8)
        venue = ctk.CTkEntry(popup, placeholder_text="Venue", width=300)
        venue.pack(pady=8)
        details = ctk.CTkTextbox(popup, width=300, height=100)
        details.insert("0.0", "Drive details...")
        details.pack(pady=8)

        def save_drive():
            conn = sqlite3.connect("yuva_drive.db")
            c = conn.cursor()
            c.execute("INSERT INTO drives (company, date, eligibility, venue, details) VALUES (?, ?, ?, ?, ?)",
                      (company.get(), date.get(), eligibility.get(), venue.get(), details.get("0.0", "end").strip()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Drive added successfully!")
            popup.destroy()
            self.show_admin_dashboard()

        ctk.CTkButton(popup, text="Save Drive", command=save_drive, width=200, fg_color=self.logo_color).pack(pady=15)

    def delete_drive(self, drive_id):
        conn = sqlite3.connect("yuva_drive.db")
        c = conn.cursor()
        c.execute("DELETE FROM drives WHERE id=?", (drive_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Deleted", "Drive deleted successfully!")
        self.show_admin_dashboard()

    def show_applicants(self, drive_id):
        popup = ctk.CTkToplevel(self)
        popup.title("Applicants")
        popup.geometry("400x400")

        ctk.CTkLabel(popup, text="👥 Applicants", font=("Helvetica", 20, "bold")).pack(pady=10)

        frame = ctk.CTkScrollableFrame(popup)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        conn = sqlite3.connect("yuva_drive.db")
        c = conn.cursor()
        c.execute("""SELECT username FROM users 
                     JOIN applications ON users.id = applications.student_id
                     WHERE drive_id=?""", (drive_id,))
        rows = c.fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(frame, text="No applicants yet.").pack(pady=20)
        else:
            for r in rows:
                ctk.CTkLabel(frame, text=f"🎓 {r[0]}", font=("Helvetica", 14)).pack(anchor="w", padx=20, pady=5)

    def show_chart_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("📊 Placement Stats")
        popup.geometry("500x400")

        companies = ["TCS", "Infosys", "Wipro", "Accenture"]
        selected = [30, 25, 15, 20]

        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(companies, selected, color="#1976D2")
        ax.set_title("Students Selected per Company")
        ax.set_ylabel("Students")
        ax.set_xlabel("Company")

        canvas = FigureCanvasTkAgg(fig, popup)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()



if __name__ == "__main__":
    init_db()
    app = YuvaDrivePortal()
    app.mainloop()
