import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pickle
import os

# Define a helper class for tooltip functionality
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None

        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        # Create a tooltip widget as a label
        x, y, _, _ = self.widget.bbox("insert")  # Get the bounding box of the widget
        x += self.widget.winfo_rootx() + 20  # Position to the right of the widget
        y += self.widget.winfo_rooty() + 20  # Position below the widget

        self.tooltip = tk.Toplevel(self.widget)  # Create a new top-level window
        self.tooltip.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip.wm_geometry(f"+{x}+{y}")  # Set its position

        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", borderwidth=1, relief="solid")
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

# Define the main application class
class ElectricalWireCalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title('Electrical Wire Calculator')
        self.geometry('800x600')  # Set the window size

        self.active_bg_color = '#d9d9d9'  # Color for active page button

        # Initialize frames for each page and place them on top of each other
        self.frames = {}
        for F in (MainPage, CalculatePage, SavedCalculationPage, HelpPage):
            frame = F(self)
            self.frames[F] = frame
            frame.place(x=160, y=0, width=640, height=600)

        # Build the menu and associate pages with buttons
        self.menu = tk.Frame(self, bg='lightgrey')
        self.menu.pack(side='left', fill='y')
        
        self.menu_buttons = {}
        descriptions = {
            MainPage: "Go to the main page to get started.",
            CalculatePage: "Enter values to calculate electrical wire parameters.",
            SavedCalculationPage: "View, edit, or delete previously saved setups.",
            HelpPage: "View help information for using the calculator."
        }

        for F in self.frames:
            btn = tk.Button(self.menu, text=F.__name__.replace("Page", ""),
                            command=lambda f=F: self.show_frame(f))
            btn.pack(fill='x')
            self.menu_buttons[self.frames[F]] = btn
            # Add a tooltip to the button
            ToolTip(btn, descriptions[F])

        self.show_frame(MainPage)  # Start with the main page

    def show_frame(self, page_class):
        '''Show a frame for the given page class and highlight the button'''
        frame = self.frames[page_class]
        frame.tkraise()

        if page_class == SavedCalculationPage:
            frame.refresh_setups()  # Refresh the saved setups every time the page is shown

        # Highlight the active button
        for btn in self.menu_buttons.values():
            btn['bg'] = 'SystemButtonFace'  # Reset all buttons to default color
        self.menu_buttons[frame]['bg'] = self.active_bg_color  # Highlight the active button

# Define the main page
class MainPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(bg='white')  # Set background color to white or as per the UI design
        
        # Add the welcome message with proper alignment and font size
        welcome_text = (
            "WELCOME TO ELECTRICAL WIRE CALCULATOR. THIS PROGRAM WILL GIVE YOU A "
            "SIMPLE AND QUICK SOLUTION TO CALCULATE THE SIZE, ESTIMATED COST, AND "
            "IMPEDANCE OF ELECTRICAL WIRE TO USE IN CABLE DESIGN FOR HOME PROJECTS.\n\n"
            "FOR GUIDANCE, PLEASE SELECT HELP BUTTON IN DROP DOWN MENU. ELSE, GO AHEAD AND CLICK START."
        )
        
        self.welcome_label = tk.Label(self, text=welcome_text, anchor='center', justify='left', bg='white', wraplength=500)
        self.welcome_label.pack(pady=(100, 20))  # Adjust padding as needed
        
        # Add the START button with styling as per the UI design
        self.start_button = tk.Button(self, text="START", command=lambda: master.show_frame(CalculatePage))
        self.start_button.pack()
        
        # You may want to style the button (e.g., color, size) to match the UI design
        self.start_button.config(height=2, width=20)  # Example styling

        # Position the button in the center
        self.start_button.place(relx=0.5, rely=0.5, anchor='center')

# Define the calculate page
class CalculatePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.grid_columnconfigure(1, weight=1)

        # Create variables for entries and dropdowns
        self.voltage_type_var = tk.StringVar()
        self.wire_material_var = tk.StringVar()
        self.phases_var = tk.StringVar()
        self.unit_var = tk.StringVar()

        # Create variables for output labels
        self.wire_size_var = tk.StringVar(value="AWG")
        self.estimated_cost_var = tk.StringVar(value="$ / UNIT")
        self.impedance_var = tk.StringVar(value="OHMS")

        # Create input widgets
        self.voltage_type_dropdown = self.create_dropdown('Voltage Type', ['DC', 'AC'], self.voltage_type_var, 0)
        self.wire_material_dropdown = self.create_dropdown('Wire Material', ['COPPER', 'ALUMIUM', 'SILVER', 'GOLD', 'NICKEL', 'ALLOY'], self.wire_material_var, 1)
        self.phases_dropdown = self.create_dropdown('Phases', ['1', '3'], self.phases_var, 2)

        # Entries
        self.voltage_entry = self.create_entry('Voltage (V)', 3)
        self.current_entry = self.create_entry('Current (A)', 4)
        self.wire_length_entry = self.create_entry('Wire Length', 5)
        self.unit_dropdown = self.create_dropdown('', ['CM', 'INCH'], self.unit_var, 5, 2)
        self.voltage_drop_entry = self.create_entry('Voltage Drop (%)', 6)

        # Output labels
        self.create_output_label('Wire Size', self.wire_size_var, 0, suffix="(AWG)")
        self.create_output_label('Estimated Cost', self.estimated_cost_var, 1, suffix="$ / UNIT")
        self.create_output_label('Impedance', self.impedance_var, 2, suffix="(OHMS)")

        # Action buttons
        ttk.Button(self, text='CALCULATE', command=self.perform_calculation).grid(row=7, column=0, pady=10, sticky='ew')
        ttk.Button(self, text='CLEAR', command=self.clear_inputs).grid(row=7, column=1, pady=10, sticky='ew')
        ttk.Button(self, text='SAVE', command=self.save_current_setup).grid(row=7, column=2, pady=10, sticky='ew')

    def create_dropdown(self, label, options, variable, row, column=0):
        ttk.Label(self, text=label).grid(row=row, column=column, sticky='ew')
        dropdown = ttk.Combobox(self, textvariable=variable, values=options, state='readonly')
        dropdown.grid(row=row, column=column+1, padx=5, pady=5, sticky='ew')
        return dropdown
    
    def create_entry(self, label, row, column=0):
        ttk.Label(self, text=label).grid(row=row, column=column, sticky='ew')
        entry = ttk.Entry(self)
        entry.grid(row=row, column=column+1, padx=5, pady=5, sticky='ew')
        return entry

    def create_output_label(self, label, variable, row, column=3, suffix=""):
        ttk.Label(self, text=label).grid(row=row, column=column, sticky='ew')
        
        # Create the Entry widget for the value, separate from the label with the unit/suffix
        output_value_entry = ttk.Entry(self, textvariable=variable, state='readonly')
        output_value_entry.grid(row=row, column=column+1, padx=5, pady=5, sticky='ew')

        # Create a separate label for the suffix/unit
        ttk.Label(self, text=suffix).grid(row=row, column=column+2, sticky='w')

    def perform_calculation(self):
        try:
            # Convert inputs to the correct data types
            voltage = float(self.voltage_entry.get())
            current = float(self.current_entry.get())
            wire_length = float(self.wire_length_entry.get())
            voltage_drop = float(self.voltage_drop_entry.get())

            # Mapping the dropdown choices to their corresponding values
            voltage_type_values = {'DC': 1, 'AC': 2}
            wire_material_values = {'COPPER': 1, 'ALUMIUM': 3, 'SILVER': 4, 'GOLD': 5, 'NICKEL': 6, 'ALLOY': 7}
            phase_values = {'1': 1, '3': 3}

            # Get the selected dropdown choices
            voltage_type = voltage_type_values[self.voltage_type_var.get()]
            wire_material = wire_material_values[self.wire_material_var.get()]
            phases = phase_values[self.phases_var.get()]
            unit = self.unit_var.get()

            # Adjust wire length based on the unit
            if unit == 'INCH':
                wire_length *= 3

            # Calculate the output values
            wire_size = (voltage * current) / (voltage_type + phases + wire_length + voltage_drop)
            estimated_cost = wire_length * wire_material
            impedance = wire_length * (5 * wire_material)

            # Update the output variables
            self.wire_size_var.set(f"{wire_size:.2f}")  # Format to 2 decimal places
            self.estimated_cost_var.set(f"${estimated_cost:.2f} / UNIT")
            self.impedance_var.set(f"{impedance:.2f} OHMS")

        except ValueError:
            # In case of invalid input, show an error message
            messagebox.showerror("Invalid input", "Please enter valid numerical values for voltage, current, wire length, and voltage drop.")

    def clear_inputs(self):
        # Clear all input fields
        self.voltage_type_var.set('')
        self.wire_material_var.set('')
        self.phases_var.set('')
        self.unit_var.set('')

        # Clear the entry widgets
        self.voltage_entry.delete(0, 'end')
        self.current_entry.delete(0, 'end')
        self.wire_length_entry.delete(0, 'end')
        self.voltage_drop_entry.delete(0, 'end')
        
        # Clear output labels
        self.wire_size_var.set('')
        self.estimated_cost_var.set('')
        self.impedance_var.set('')

    def save_current_setup(self):
        # Function to save the current setup
        setup_name = simpledialog.askstring("Save Setup", "Enter a name for this setup:")
        if setup_name:
            current_setup = {
                'voltage_type': self.voltage_type_var.get(),
                'wire_material': self.wire_material_var.get(),
                'phases': self.phases_var.get(),
                'voltage': self.voltage_entry.get(),
                'current': self.current_entry.get(),
                'wire_length': self.wire_length_entry.get(),
                'unit': self.unit_var.get(),
                'voltage_drop': self.voltage_drop_entry.get()
            }
            # Access the setups from the SavedCalculationPage directly and update
            saved_page = self.master.frames[SavedCalculationPage]
            saved_page.setups.append((setup_name, current_setup))
            saved_page.save_setups_to_file()  # Update this call
            messagebox.showinfo('Saved', f'Setup "{setup_name}" has been saved.')
            saved_page.refresh_setups()  # Refresh the SavedCalculationPage

            
    def load_setup_data(self, setup_data):
        # Load the setup data into the CalculatePage fields
        self.voltage_type_var.set(setup_data['voltage_type'])
        self.wire_material_var.set(setup_data['wire_material'])
        self.phases_var.set(setup_data['phases'])
        self.voltage_entry.insert(0, setup_data['voltage'])
        self.current_entry.insert(0, setup_data['current'])
        self.wire_length_entry.insert(0, setup_data['wire_length'])
        self.unit_var.set(setup_data['unit'])
        self.voltage_drop_entry.insert(0, setup_data['voltage_drop'])
        # You might need to call perform_calculation or update the output fields accordingly

# Define the saved calculations page
class SavedCalculationPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(bg='white')

        self.load_setups()

    def load_setups(self):
        # Load the setups from the storage
        self.setups = self.load_setups_from_file()

        # Create the list of setups with their corresponding buttons
        self.setup_widgets = []  # Keep track of the widgets so we can destroy them later
        for i, (setup_name, setup_data) in enumerate(self.setups):
            widgets = self.create_setup_row(setup_name, setup_data, i)
            self.setup_widgets.extend(widgets)

        # Add 'Delete All' button
        self.create_delete_all_button()  # Pass the row index for the button

    def create_setup_row(self, setup_name, setup_data, row):
        widgets = []

        setup_label = tk.Label(self, text=setup_name)
        setup_label.grid(row=row, column=0, sticky='ew')
        widgets.append(setup_label)

        edit_button = tk.Button(self, text='EDIT NAME', command=lambda r=row: self.edit_setup_name(r))
        edit_button.grid(row=row, column=1)
        widgets.append(edit_button)

        delete_button = tk.Button(self, text='DELETE', command=lambda r=row: self.delete_setup(r))
        delete_button.grid(row=row, column=2)
        widgets.append(delete_button)

        load_button = tk.Button(self, text='LOAD', command=lambda: self.load_setup(setup_data))
        load_button.grid(row=row, column=3)
        widgets.append(load_button)

        return widgets

    def edit_setup_name(self, setup_index):
        # This function allows the user to edit the name of the setup
        new_name = simpledialog.askstring("Edit Setup Name", "Enter the new setup name:")
        if new_name:
            self.setups[setup_index] = (new_name, self.setups[setup_index][1])
            self.save_setups_to_file()
            self.refresh_setups()

    def delete_setup(self, setup_index):
        try:
            # This function deletes a setup
            if messagebox.askyesno("Delete Setup", "Are you sure you want to delete this setup?"):
                del self.setups[setup_index]
                self.save_setups_to_file()
                self.refresh_setups()
        except IndexError:
            messagebox.showerror("Error", "Failed to delete setup: Index out of range")


    def delete_all_setups(self):
        # This function deletes all setups
        if messagebox.askyesno("Delete All Setups", "Are you sure you want to delete all setups?"):
            self.setups.clear()
            self.save_setups_to_file()
            self.refresh_setups()

    def load_setup(self, setup_data):
        # This function loads the setup values into the CalculatePage
        self.master.frames[CalculatePage].load_setup_data(setup_data)
        self.master.show_frame(CalculatePage)

    def refresh_setups(self):
        # Clear existing setups
        for widget in self.setup_widgets:
            widget.grid_forget()  # This removes the widget from the grid
            widget.destroy()
        self.setup_widgets.clear()

        # Reload and display the setups
        self.load_setups()

        # Re-create the Delete All button to ensure it is placed correctly in the grid
        self.create_delete_all_button()

    def create_delete_all_button(self):
        # Destroy the existing Delete All button if it exists
        if hasattr(self, 'delete_all_button'):
            self.delete_all_button.destroy()

        # Now create a new Delete All button using grid
        self.delete_all_button = tk.Button(self, text='DELETE ALL', command=self.delete_all_setups)
        next_row = len(self.setups) + 1  # This assumes setups are in consecutive rows
        self.delete_all_button.grid(row=next_row, column=0, columnspan=4, pady=10, sticky='ew')


    def load_setups_from_file(self):
        # Load setups from file (implement the actual loading logic)
        if os.path.isfile('setups.pkl'):
            with open('setups.pkl', 'rb') as input_file:
                return pickle.load(input_file)
        else:
            return []

    def save_setups_to_file(self):
        # Save setups to file
        with open('setups.pkl', 'wb') as output_file:
            pickle.dump(self.setups, output_file)

# Define the help page
class HelpPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(bg='white')  # Assuming a white background

        # Set the help text as shown in the design
        help_text = (
            "BELOW IS THE HINT TO ENTER WIRE REQUIREMENT INPUT\n\n"
            "- VOLTAGE TYPE: DIRECT CURRENT (DC) OR ALTERNATE CURRENT (AC)\n"
            "- WIRE MATERIAL: COPPER, ALUMIUM, SILVER, GOLD, NICKEL ALLOY\n"
            "- PHASES: 1 OR 3 PHASES\n"
            "- VOLTAGE: THE MOST COMMON AND NOMINAL VALUES.\n"
            "- CURRENT: THE NUMBER OF AMPERES DRAWN BY THE LOAD\n"
            "- WIRE LENGTH: DISTANCE FROM TWO ENDS OF THE CONNECTION\n"
            "- VOLTAGE DROP: PERCENTAGE OF FOR ENTIRE LENGTH"
        )

        # Create a label for the help text with appropriate styling
        self.help_label = tk.Label(self, text=help_text, anchor='w', justify='left', bg='white', font=('Arial', 12), wraplength=550)
        self.help_label.place(relx=0.5, rely=0.5, anchor='center')

        # Adjust the font and layout as necessary to match the design

# Create and run the application
app = ElectricalWireCalculatorApp()
app.mainloop()
