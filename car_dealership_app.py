import tkinter as tk
from tkinter import ttk, messagebox
import random
from tkcalendar import Calendar
from datetime import datetime

# Fixed week view: Monday, Jan 6, 2025 to Sunday, Jan 12, 2025
WEEK_DATES = [
    ("M", "06-Jan-2025"),
    ("T", "07-Jan-2025"),
    ("W", "08-Jan-2025"),
    ("T", "09-Jan-2025"),
    ("F", "10-Jan-2025"),
    ("S", "11-Jan-2025"),
    ("S", "12-Jan-2025")
]
# Time slots from 08:00 to 18:00 (inclusive)
TIME_SLOTS = [f"{h:02d}:00" for h in range(8, 19)]


class CarDealershipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audi Dealership App")
        self.root.geometry("1200x800")

        # Audi-themed header
        header_frame = tk.Frame(root, bg="black")
        header_frame.pack(fill="x")
        header_label = tk.Label(header_frame, text="Audi Dealership App", font=("Helvetica", 20, "bold"), bg="black", fg="white")
        header_label.pack(pady=10)

        # Notebook with four tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=1, fill="both")

        self.service_tab = ttk.Frame(self.notebook)
        self.sales_tab = ttk.Frame(self.notebook)
        self.inventory_tab = ttk.Frame(self.notebook)
        self.manager_financing_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.service_tab, text="Service Scheduling")
        self.notebook.add(self.sales_tab, text="Sales Scheduling")
        self.notebook.add(self.inventory_tab, text="Inventory Management")
        self.notebook.add(self.manager_financing_tab, text="Manager Financing Options")

        # Data stores
        self.service_appointments = []   # list of dicts for service
        self.sales_appointments = []     # list of dicts for sales
        self.inventory_items = []        # list of dicts for inventory

        # Build scheduling grids (each is a weekly view)
        self.build_scheduling_grid(self.service_tab, "service")
        self.build_scheduling_grid(self.sales_tab, "sales")

        # Add "Add Appointment" buttons above each scheduling grid
        ttk.Button(self.service_tab, text="Add Service Appointment", command=self.open_service_appointment_popup)\
            .pack(pady=5)
        ttk.Button(self.sales_tab, text="Add Sales Appointment", command=self.open_sales_appointment_popup)\
            .pack(pady=5)

        # Build Inventory Management view (with search and add new inventory)
        self.build_inventory_view()

        # Build Manager Financing Options view
        self.build_manager_financing_view()

    def build_scheduling_grid(self, parent, sched_type):
        """Create a grid view with 7 columns (days) and rows for time slots."""
        grid_frame = ttk.Frame(parent)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=10)
        if sched_type == "service":
            self.service_grid_cells = {}
        else:
            self.sales_grid_cells = {}

        # Header row: blank top-left cell, then day headers.
        ttk.Label(grid_frame, text="").grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        for col, (day_letter, date_str) in enumerate(WEEK_DATES, start=1):
            header_text = f"{day_letter}\n{date_str}"
            ttk.Label(grid_frame, text=header_text, borderwidth=1, relief="solid", width=15)\
                .grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        # Left column: time slots.
        for row, time_slot in enumerate(TIME_SLOTS, start=1):
            ttk.Label(grid_frame, text=time_slot, borderwidth=1, relief="solid", width=10)\
                .grid(row=row, column=0, sticky="nsew", padx=1, pady=1)

        # Create empty cells for each (day, time)
        for row in range(1, len(TIME_SLOTS)+1):
            for col in range(1, len(WEEK_DATES)+1):
                cell = tk.Frame(grid_frame, borderwidth=1, relief="solid", width=150, height=50)
                cell.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
                if sched_type == "service":
                    self.service_grid_cells[(col, row)] = cell
                else:
                    self.sales_grid_cells[(col, row)] = cell

        # Configure grid to expand equally.
        for col in range(len(WEEK_DATES)+1):
            grid_frame.columnconfigure(col, weight=1)
        for row in range(len(TIME_SLOTS)+1):
            grid_frame.rowconfigure(row, weight=1)

    def open_service_appointment_popup(self):
        """Pop-up for adding a service appointment with a calendar and hour dropdown."""
        popup = tk.Toplevel(self.root)
        popup.title("Add Service Appointment")

        ttk.Label(popup, text="Customer Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        cust_var = tk.StringVar()
        ttk.Entry(popup, textvariable=cust_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(popup, text="VIN:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        vin_var = tk.StringVar()
        ttk.Entry(popup, textvariable=vin_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(popup, text="Select Date:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        cal = Calendar(popup, selectmode='day', year=2025, month=1, day=6)
        cal.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(popup, text="Select Hour:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        hour_var = tk.StringVar()
        hour_options = [f"{h:02d}:00" for h in range(8, 19)]
        hour_combo = ttk.Combobox(popup, textvariable=hour_var, values=hour_options, state="readonly")
        hour_combo.current(0)
        hour_combo.grid(row=3, column=1, padx=5, pady=5)

        def add_service():
            cust = cust_var.get().strip()
            vin = vin_var.get().strip()
            date_selected = cal.get_date()
            hour = hour_var.get()
            if not cust or not vin:
                messagebox.showerror("Input Error", "Please fill in all fields.")
                return
            try:
                dt = datetime.strptime(date_selected, "%m/%d/%y")
            except Exception:
                dt = datetime.strptime(date_selected, "%m/%d/%Y")
            week_start = datetime(2025, 1, 6)
            week_end = datetime(2025, 1, 12)
            if dt < week_start or dt > week_end:
                messagebox.showerror("Input Error", "Date must be within Jan 6-12, 2025 for this view.")
                return
            day_index = (dt - week_start).days  # 0 for Monday, etc.
            col = day_index + 1
            row = int(hour[:2]) - 8 + 1
            appointment = {"customer": cust, "vin": vin, "date": dt, "hour": hour}
            self.service_appointments.append(appointment)
            cell = self.service_grid_cells.get((col, row))
            if cell:
                lbl = tk.Label(cell, text=f"{cust}\nVIN: {vin}\n{hour}", bg="lightblue", wraplength=140)
                lbl.pack(expand=True, fill="both")
            popup.destroy()

        ttk.Button(popup, text="Add Appointment", command=add_service)\
            .grid(row=4, column=0, columnspan=2, pady=10)

    def open_sales_appointment_popup(self):
        """Pop-up for adding a sales appointment (VIN removed; salesman auto-assigned)."""
        popup = tk.Toplevel(self.root)
        popup.title("Add Sales Appointment")

        ttk.Label(popup, text="Customer Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        cust_var = tk.StringVar()
        ttk.Entry(popup, textvariable=cust_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(popup, text="Select Date:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        cal = Calendar(popup, selectmode='day', year=2025, month=1, day=6)
        cal.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(popup, text="Select Hour:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        hour_var = tk.StringVar()
        hour_options = [f"{h:02d}:00" for h in range(8, 19)]
        hour_combo = ttk.Combobox(popup, textvariable=hour_var, values=hour_options, state="readonly")
        hour_combo.current(0)
        hour_combo.grid(row=2, column=1, padx=5, pady=5)

        def add_sales():
            cust = cust_var.get().strip()
            date_selected = cal.get_date()
            hour = hour_var.get()
            if not cust:
                messagebox.showerror("Input Error", "Please fill in all fields.")
                return
            try:
                dt = datetime.strptime(date_selected, "%m/%d/%y")
            except Exception:
                dt = datetime.strptime(date_selected, "%m/%d/%Y")
            week_start = datetime(2025, 1, 6)
            week_end = datetime(2025, 1, 12)
            if dt < week_start or dt > week_end:
                messagebox.showerror("Input Error", "Date must be within Jan 6-12, 2025 for this view.")
                return
            day_index = (dt - week_start).days
            col = day_index + 1
            row = int(hour[:2]) - 8 + 1
            salesmen = ["Chris", "Anthony", "Tyler", "Zach"]
            salesman = random.choice(salesmen)
            appointment = {"customer": cust, "date": dt, "hour": hour, "salesman": salesman}
            self.sales_appointments.append(appointment)
            cell = self.sales_grid_cells.get((col, row))
            if cell:
                lbl = tk.Label(cell, text=f"{cust}\n{hour}\nSales: {salesman}", bg="lightgreen", wraplength=140)
                lbl.pack(expand=True, fill="both")
            popup.destroy()

        ttk.Button(popup, text="Add Appointment", command=add_sales)\
            .grid(row=3, column=0, columnspan=2, pady=10)

    def build_inventory_view(self):
        """Build the Inventory Management view with search and a grid-of-boxes display."""
        # Search bar at the top with additional Year field
        search_frame = ttk.LabelFrame(self.inventory_tab, text="Search Inventory")
        search_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(search_frame, text="Make:").grid(row=0, column=0, padx=5, pady=5)
        self.inv_search_make_var = tk.StringVar()
        make_opts = ["All", "Audi", "BMW", "Mercedes", "Lexus", "Acura"]
        ttk.Combobox(search_frame, textvariable=self.inv_search_make_var, values=make_opts, state="readonly")\
            .grid(row=0, column=1, padx=5, pady=5)
        self.inv_search_make_var.set("All")

        ttk.Label(search_frame, text="Model:").grid(row=0, column=2, padx=5, pady=5)
        self.inv_search_model_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.inv_search_model_var, width=10)\
            .grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(search_frame, text="Type:").grid(row=0, column=4, padx=5, pady=5)
        self.inv_search_type_var = tk.StringVar()
        ttk.Combobox(search_frame, textvariable=self.inv_search_type_var, values=["All", "New", "Used"], state="readonly")\
            .grid(row=0, column=5, padx=5, pady=5)
        self.inv_search_type_var.set("All")

        ttk.Label(search_frame, text="Year:").grid(row=0, column=6, padx=5, pady=5)
        self.inv_search_year_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.inv_search_year_var, width=6)\
            .grid(row=0, column=7, padx=5, pady=5)

        ttk.Button(search_frame, text="Search", command=self.search_inventory).grid(row=0, column=8, padx=5)
        ttk.Button(search_frame, text="Reset", command=self.reset_inventory_search).grid(row=0, column=9, padx=5)

        # Form for adding a new inventory item (now with Year)
        add_frame = ttk.LabelFrame(self.inventory_tab, text="Add New Inventory Item")
        add_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(add_frame, text="Type:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.inv_type_var = tk.StringVar()
        ttk.Combobox(add_frame, textvariable=self.inv_type_var, values=["New", "Used"], state="readonly")\
            .grid(row=0, column=1, padx=5, pady=5)
        self.inv_type_var.set("New")

        ttk.Label(add_frame, text="Make:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.inv_make_var = tk.StringVar()
        ttk.Combobox(add_frame, textvariable=self.inv_make_var, values=["Audi", "BMW", "Mercedes", "Lexus", "Acura"], state="readonly")\
            .grid(row=1, column=1, padx=5, pady=5)
        self.inv_make_var.set("Audi")

        ttk.Label(add_frame, text="Model:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.inv_model_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.inv_model_var)\
            .grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Year:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.inv_year_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.inv_year_var, width=6)\
            .grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="VIN:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.inv_vin_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.inv_vin_var)\
            .grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Price:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.inv_price_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.inv_price_var)\
            .grid(row=5, column=1, padx=5, pady=5)

        ttk.Button(add_frame, text="Add Inventory", command=self.add_inventory_item)\
            .grid(row=6, column=0, columnspan=2, pady=10)

        # Display inventory items as boxes (grid layout)
        self.inv_display_frame = ttk.Frame(self.inventory_tab)
        self.inv_display_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.refresh_inventory_display()

    def refresh_inventory_display(self):
        for widget in self.inv_display_frame.winfo_children():
            widget.destroy()
        cols = 3
        for i, item in enumerate(self.inventory_items):
            # Display all financing options joined by newline if available.
            fin_options = "\n".join(item.get("financing_options", [])) if item.get("financing_options") else "N/A"
            box = ttk.LabelFrame(self.inv_display_frame, text=f"{item['make']} {item['model']} ({item.get('year', 'N/A')})", relief="solid")
            box.grid(row=i // cols, column=i % cols, padx=5, pady=5, sticky="nsew")
            info = f"Type: {item['type']}\nVIN: {item['vin']}\nPrice: {item['price']}\nFinancing:\n{fin_options}"
            ttk.Label(box, text=info, wraplength=200).pack(padx=5, pady=5)
            # Add a button to add financing for this car directly
            ttk.Button(box, text="Add Financing", command=lambda vin=item['vin']: self.open_financing_options_for_item(vin))\
                .pack(padx=5, pady=5)
        for c in range(cols):
            self.inv_display_frame.columnconfigure(c, weight=1)

    def add_inventory_item(self):
        inv_item = {
            "type": self.inv_type_var.get().strip(),
            "make": self.inv_make_var.get().strip(),
            "model": self.inv_model_var.get().strip(),
            "year": self.inv_year_var.get().strip(),
            "vin": self.inv_vin_var.get().strip(),
            "price": self.inv_price_var.get().strip(),
            "financing_options": []  # initialize as empty list
        }
        if not all(inv_item.values()):
            messagebox.showerror("Input Error", "Please fill in all fields for inventory item.")
            return
        self.inventory_items.append(inv_item)
        self.refresh_inventory_display()
        # Update manager financing VIN dropdown if available.
        if hasattr(self, 'fin_vin_combo'):
            vin_opts = [item['vin'] for item in self.inventory_items]
            self.fin_vin_combo['values'] = vin_opts
            if vin_opts:
                self.fin_vin_combo.current(0)
        messagebox.showinfo("Inventory Added", "Inventory item added successfully.")
        self.inv_type_var.set("New")
        self.inv_make_var.set("Audi")
        self.inv_model_var.set("")
        self.inv_year_var.set("")
        self.inv_vin_var.set("")
        self.inv_price_var.set("")

    def search_inventory(self):
        search_make = self.inv_search_make_var.get().strip().lower()
        search_model = self.inv_search_model_var.get().strip().lower()
        search_type = self.inv_search_type_var.get().strip().lower()
        search_year = self.inv_search_year_var.get().strip().lower()
        filtered = []
        for item in self.inventory_items:
            if search_make != "all" and search_make not in item['make'].lower():
                continue
            if search_model and search_model not in item['model'].lower():
                continue
            if search_type != "all" and search_type != item['type'].lower():
                continue
            if search_year and search_year not in item.get('year', '').lower():
                continue
            filtered.append(item)
        self.inv_display_frame.destroy()
        self.inv_display_frame = ttk.Frame(self.inventory_tab)
        self.inv_display_frame.pack(fill="both", expand=True, padx=10, pady=5)
        cols = 3
        for i, item in enumerate(filtered):
            fin_options = "\n".join(item.get("financing_options", [])) if item.get("financing_options") else "N/A"
            box = ttk.LabelFrame(self.inv_display_frame, text=f"{item['make']} {item['model']} ({item.get('year', 'N/A')})", relief="solid")
            box.grid(row=i // cols, column=i % cols, padx=5, pady=5, sticky="nsew")
            info = f"Type: {item['type']}\nVIN: {item['vin']}\nPrice: {item['price']}\nFinancing:\n{fin_options}"
            ttk.Label(box, text=info, wraplength=200).pack(padx=5, pady=5)
            ttk.Button(box, text="Add Financing", command=lambda vin=item['vin']: self.open_financing_options_for_item(vin))\
                .pack(padx=5, pady=5)
        for c in range(cols):
            self.inv_display_frame.columnconfigure(c, weight=1)

    def reset_inventory_search(self):
        self.inv_search_make_var.set("All")
        self.inv_search_model_var.set("")
        self.inv_search_type_var.set("All")
        self.inv_search_year_var.set("")
        self.refresh_inventory_display()

    def build_manager_financing_view(self):
        top_frame = ttk.Frame(self.manager_financing_tab)
        top_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(top_frame, text="Select Inventory VIN:").pack(side="left", padx=5)
        self.fin_vin_var = tk.StringVar()
        vin_opts = [item['vin'] for item in self.inventory_items]
        self.fin_vin_combo = ttk.Combobox(top_frame, textvariable=self.fin_vin_var, values=vin_opts, state="readonly")
        if vin_opts:
            self.fin_vin_combo.current(0)
        self.fin_vin_combo.pack(side="left", padx=5)

        ttk.Button(top_frame, text="Set Financing Options", command=self.open_manager_financing_popup)\
            .pack(side="left", padx=5)

        self.manager_financing_tree = ttk.Treeview(self.manager_financing_tab, columns=("VIN", "Financing"), show="headings")
        self.manager_financing_tree.heading("VIN", text="VIN")
        self.manager_financing_tree.heading("Financing", text="Financing Options")
        self.manager_financing_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.refresh_manager_financing_tree()

    def open_manager_financing_popup(self):
        # Uses the VIN selected in the dropdown from the manager financing tab.
        selected_vin = self.fin_vin_var.get().strip()
        if not selected_vin:
            messagebox.showerror("Input Error", "Please select an inventory item (by VIN).")
            return
        self.open_financing_options_popup(selected_vin)

    def open_financing_options_for_item(self, vin):
        # Opens the financing popup for a given inventory item from its box button.
        self.open_financing_options_popup(vin)

    def open_financing_options_popup(self, selected_vin):
        popup = tk.Toplevel(self.root)
        popup.title("Set Financing Options")

        ttk.Label(popup, text="Lowest Price:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        lowest_price_var = tk.StringVar()
        ttk.Entry(popup, textvariable=lowest_price_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(popup, text="Money Down:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        money_down_var = tk.StringVar()
        ttk.Entry(popup, textvariable=money_down_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(popup, text="Financing Months:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        months_opts = [str(m) for m in range(36, 145, 6)]
        fin_months_var = tk.StringVar()
        ttk.Combobox(popup, textvariable=fin_months_var, values=months_opts, state="readonly")\
            .grid(row=2, column=1, padx=5, pady=5)
        fin_months_var.set(months_opts[0])

        ttk.Label(popup, text="APR Rate (%):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        apr_var = tk.StringVar(value="3.5")
        ttk.Entry(popup, textvariable=apr_var).grid(row=3, column=1, padx=5, pady=5)

        result_label = ttk.Label(popup, text="Monthly Payment: ")
        result_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        def calculate_financing():
            try:
                lowest_price = float(lowest_price_var.get().strip())
                money_down = float(money_down_var.get().strip())
                months = int(fin_months_var.get().strip())
                apr = float(apr_var.get().strip())
                principal = lowest_price - money_down
                if principal <= 0:
                    messagebox.showerror("Input Error", "Money down must be less than the lowest price.")
                    return
                monthly_rate = apr / 100 / 12
                if monthly_rate == 0:
                    payment = principal / months
                else:
                    payment = (principal * monthly_rate) / (1 - (1 + monthly_rate) ** -months)
                result = f"${payment:.2f}/month for {months} months at {apr}% APR"
                result_label.config(text=f"Monthly Payment: {result}")
                # Append the financing option to the inventory item's financing_options list.
                for item in self.inventory_items:
                    if item['vin'] == selected_vin:
                        if 'financing_options' not in item:
                            item['financing_options'] = []
                        item['financing_options'].append(result)
                        break
                self.refresh_inventory_display()
                self.refresh_manager_financing_tree()
            except Exception as e:
                messagebox.showerror("Input Error", f"Invalid input: {e}")

        ttk.Button(popup, text="Calculate & Save Financing", command=calculate_financing)\
            .grid(row=4, column=0, columnspan=2, pady=10)

    def refresh_manager_financing_tree(self):
        for child in self.manager_financing_tree.get_children():
            self.manager_financing_tree.delete(child)
        for item in self.inventory_items:
            if item.get('financing_options'):
                fin_options = "\n".join(item['financing_options'])
                self.manager_financing_tree.insert("", "end", values=(item['vin'], fin_options))


if __name__ == "__main__":
    root = tk.Tk()
    app = CarDealershipApp(root)
    root.mainloop()
