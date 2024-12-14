import customtkinter
from tkinter import ttk  # Assuming Treeview from tkinter
from crud_operations import fetch_all_data, insert_data, update_data, delete_data
from ui_components import create_table_display
import sys

class LibraryApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("1400x800")

        # Define color constants
        self.BUTTON_NORMAL_COLOR = "#2980b9"    # Normal blue color
        self.BUTTON_SELECTED_COLOR = "#1abc9c"   # Highlighted teal color

        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar with better styling and fixed width
        self.sidebar_frame = customtkinter.CTkFrame(self, width=200, corner_radius=0, fg_color="#2c3e50")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_columnconfigure(0, weight=1)  # Center the content horizontally
        self.sidebar_frame.grid_propagate(False)

        # Create a scrollable frame for the sidebar content
        self.sidebar_content = customtkinter.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.sidebar_content.grid(row=0, column=0, sticky="n")
        self.sidebar_content.grid_columnconfigure(0, weight=1)  # Center the content horizontally

        # App title in sidebar with word wrap
        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_content, 
            text="Library\nManagement",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color="#ecf0f1"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        # Section label for tables
        self.tables_label = customtkinter.CTkLabel(
            self.sidebar_content,
            text="TABLES",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color="#95a5a6"
        )
        self.tables_label.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")

        # Sidebar buttons for switching between tables with categories
        table_categories = {
            "Users": ["Admins", "Members"],
            "Content": ["Books", "Authors", "Publishers", "Genres"],
            "Transactions": ["Loans", "Reservations", "Fines"]
        }

        current_row = 2
        self.table_buttons = {}
        
        for category, tables in table_categories.items():
            # Category label
            category_label = customtkinter.CTkLabel(
                self.sidebar_content,
                text=category.upper(),
                font=customtkinter.CTkFont(size=12),
                text_color="#7f8c8d"
            )
            category_label.grid(row=current_row, column=0, padx=20, pady=(10, 5), sticky="w")
            current_row += 1

            # Table buttons for this category
            for table in tables:
                btn = customtkinter.CTkButton(
                    self.sidebar_content,
                    text=table,
                    height=32,
                    width=160,
                    corner_radius=5,
                    command=lambda t=table: self.switch_table(t),
                    fg_color="#2980b9",
                    hover_color="#3498db",
                    anchor="center"
                )
                btn.grid(row=current_row, column=0, padx=20, pady=3)
                self.table_buttons[table] = btn
                current_row += 1

        # CRUD buttons at the bottom with a separator
        separator = customtkinter.CTkFrame(self.sidebar_content, height=2, fg_color="#34495e")
        separator.grid(row=current_row, column=0, sticky="ew", padx=20, pady=(20, 10))

        # CRUD Buttons - Stacked vertically
        self.create_btn = customtkinter.CTkButton(
            self.sidebar_content,
            text="Create",
            command=self.create_record,
            height=35,
            width=160,
            corner_radius=5,
            fg_color="#27ae60",
            hover_color="#2ecc71"
        )
        self.create_btn.grid(row=current_row + 1, column=0, padx=20, pady=5)

        self.update_btn = customtkinter.CTkButton(
            self.sidebar_content,
            text="Update",
            command=self.update_record,
            height=35,
            width=160,
            corner_radius=5,
            fg_color="#f39c12",
            hover_color="#f1c40f"
        )
        self.update_btn.grid(row=current_row + 2, column=0, padx=20, pady=5)

        self.delete_btn = customtkinter.CTkButton(
            self.sidebar_content,
            text="Delete",
            command=self.delete_record,
            height=35,
            width=160,
            corner_radius=5,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.delete_btn.grid(row=current_row + 3, column=0, padx=20, pady=5)

        # Main content frame
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Initialize current table and load default
        self.current_table = None
        self.switch_table("Books")

    def switch_table(self, table_name):
        """Loads and displays data for a specified table."""
        # Reset all buttons to normal color
        for btn in self.table_buttons.values():
            btn.configure(fg_color=self.BUTTON_NORMAL_COLOR)
        
        # Highlight the selected button
        self.table_buttons[table_name].configure(fg_color=self.BUTTON_SELECTED_COLOR)
        
        self.current_table = table_name
        columns, data = fetch_all_data(table_name)

        # Clear previous widgets
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create search bar
        self.create_search_bar()

        # Display table
        if data:
            table_frame = create_table_display(self.main_frame, data, columns)
            table_frame.pack(fill="both", expand=True)

    def create_search_bar(self):
        """Creates the search bar at the top of the main frame"""
        search_frame = customtkinter.CTkFrame(self.main_frame)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        search_entry = customtkinter.CTkEntry(
            search_frame, 
            placeholder_text="Search...",
            width=300
        )
        search_entry.pack(side="left", padx=5)
        
        search_button = customtkinter.CTkButton(
            search_frame,
            text="Search",
            width=100,
            command=lambda: self.search_records(search_entry.get())
        )
        search_button.pack(side="left", padx=5)
        
        clear_button = customtkinter.CTkButton(
            search_frame,
            text="Clear",
            width=100,
            command=lambda: self.switch_table(self.current_table)
        )
        clear_button.pack(side="left", padx=5)

    def create_record(self):
        """Opens a new form window for creating a record for the current table."""
        if not self.current_table:
            return

        form_window = customtkinter.CTkToplevel(self)
        form_window.title(f"Create New {self.current_table}")
        form_window.geometry("500x600")

        # Create main container frame with padding
        main_frame = customtkinter.CTkFrame(form_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = customtkinter.CTkLabel(
            main_frame,
            text=f"Create New {self.current_table}",
            font=customtkinter.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # Create scrollable frame
        scroll_frame = customtkinter.CTkScrollableFrame(main_frame)
        scroll_frame.pack(fill="both", expand=True)

        # Bind mouse wheel event for scrolling (platform-specific)
        if sys.platform.startswith('darwin'):  # macOS
            scroll_frame.bind('<MouseWheel>', lambda e: scroll_frame._parent_canvas.yview_scroll(-int(e.delta), "units"))
        else:  # Windows and Linux
            scroll_frame.bind_all("<MouseWheel>", lambda e: scroll_frame._parent_canvas.yview_scroll(-int(e.delta/120), "units"))
            form_window.bind("<Destroy>", lambda e: scroll_frame.unbind_all("<MouseWheel>"))

        columns, _ = fetch_all_data(self.current_table)
        entry_widgets = {}

        # Create form fields
        for column in columns:
            # Container for each field
            field_frame = customtkinter.CTkFrame(scroll_frame, fg_color="transparent")
            field_frame.pack(fill="x", pady=5)

            label = customtkinter.CTkLabel(
                field_frame,
                text=column,
                font=customtkinter.CTkFont(size=12)
            )
            label.pack(side="top", anchor="w", padx=5)

            entry = customtkinter.CTkEntry(field_frame, width=400)
            entry.pack(side="top", fill="x", padx=5)
            entry_widgets[column] = entry

        # Submit button
        submit_btn = customtkinter.CTkButton(
            main_frame,
            text="Create Record",
            command=lambda: self.submit_create_form(entry_widgets, form_window),
            fg_color="#27ae60",
            hover_color="#2ecc71",
            height=40
        )
        submit_btn.pack(pady=20)

    def update_record(self):
        """Displays a form for updating a record."""
        if not self.current_table:
            return

        selected_record = self.get_selected_record()
        if not selected_record:
            return

        update_window = customtkinter.CTkToplevel(self)
        update_window.title(f"Update {self.current_table}")
        update_window.geometry("500x600")

        # Create main container frame with padding
        main_frame = customtkinter.CTkFrame(update_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = customtkinter.CTkLabel(
            main_frame,
            text=f"Update {self.current_table}",
            font=customtkinter.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # Create scrollable frame
        scroll_frame = customtkinter.CTkScrollableFrame(main_frame)
        scroll_frame.pack(fill="both", expand=True)

        # Bind mouse wheel event for scrolling (platform-specific)
        if sys.platform.startswith('darwin'):  # macOS
            scroll_frame.bind('<MouseWheel>', lambda e: scroll_frame._parent_canvas.yview_scroll(-int(e.delta), "units"))
        else:  # Windows and Linux
            scroll_frame.bind_all("<MouseWheel>", lambda e: scroll_frame._parent_canvas.yview_scroll(-int(e.delta/120), "units"))
            update_window.bind("<Destroy>", lambda e: scroll_frame.unbind_all("<MouseWheel>"))

        columns, _ = fetch_all_data(self.current_table)
        form_entries = {}

        # Create form fields
        for i, column in enumerate(columns):
            # Container for each field
            field_frame = customtkinter.CTkFrame(scroll_frame, fg_color="transparent")
            field_frame.pack(fill="x", pady=5)

            label = customtkinter.CTkLabel(
                field_frame,
                text=column,
                font=customtkinter.CTkFont(size=12)
            )
            label.pack(side="top", anchor="w", padx=5)

            entry = customtkinter.CTkEntry(field_frame, width=400)
            entry.insert(0, selected_record[i])
            entry.pack(side="top", fill="x", padx=5)
            form_entries[column] = entry

        # Submit button
        submit_btn = customtkinter.CTkButton(
            main_frame,
            text="Update Record",
            command=lambda: self.submit_update_form(form_entries, update_window),
            fg_color="#f39c12",
            hover_color="#f1c40f",
            height=40
        )
        submit_btn.pack(pady=20)

    def show_error_message(self, window, message):
        """Displays an error message in the form window"""
        error_frame = customtkinter.CTkFrame(window, fg_color="#e74c3c")
        error_frame.pack(fill="x", padx=20, pady=5)
        
        error_label = customtkinter.CTkLabel(
            error_frame,
            text=message,
            text_color="white",
            wraplength=350
        )
        error_label.pack(pady=10)
        
        # Auto-dismiss after 3 seconds
        window.after(3000, error_frame.destroy)

    def submit_create_form(self, entry_widgets, form_window):
        """Handles form submission and data insertion."""
        try:
            values = [entry.get().strip() for entry in entry_widgets.values()]

            if any(value == "" for value in values):
                raise ValueError("All fields must be filled.")

            # Insert the data
            insert_data(self.current_table, values)
            
            # Show success message
            success_frame = customtkinter.CTkFrame(form_window)
            success_frame.pack(fill="x", padx=10, pady=5)
            success_label = customtkinter.CTkLabel(
                success_frame, 
                text="Record created successfully!", 
                text_color="green"
            )
            success_label.pack()
            form_window.after(1500, form_window.destroy)
            self.switch_table(self.current_table)

        except Exception as e:
            # Show error in a contained frame
            error_msg = str(e)
            if "foreign key constraint fails" in error_msg.lower():
                if "authorid" in error_msg.lower():
                    error_msg = "Error: The specified AuthorID does not exist in the Authors table."
                elif "genreid" in error_msg.lower():
                    error_msg = "Error: The specified GenreID does not exist in the Genres table."
                elif "publisherid" in error_msg.lower():
                    error_msg = "Error: The specified PublisherID does not exist in the Publishers table."
            
            # Show error in a contained frame
            error_frame = customtkinter.CTkFrame(form_window)
            error_frame.pack(fill="x", padx=10, pady=5)
            error_label = customtkinter.CTkLabel(
                error_frame,
                text=error_msg,
                text_color="red",
                wraplength=350
            )
            error_label.pack(pady=5)

    def submit_update_form(self, form_entries, window):
        """Submits the updated data to the database."""
        try:
            values = [entry.get() for entry in form_entries.values()]
            
            # Get the first column name (assuming it's the primary key)
            primary_key_column = list(form_entries.keys())[0]
            primary_key_value = values[0]
            
            # Create the WHERE clause using the actual column name
            condition = f"{primary_key_column} = {primary_key_value}"
            
            # Remove the primary key from the columns to update
            columns = list(form_entries.keys())[1:]
            
            # Update with all values except the primary key
            update_data(self.current_table, columns, values[1:], condition)
            
            # Show success message
            success_label = customtkinter.CTkLabel(window, text="Record updated successfully!", fg_color="green")
            success_label.grid(row=len(form_entries) + 1, column=0, columnspan=2)
            window.after(1500, window.destroy)
            self.switch_table(self.current_table)
            
        except Exception as e:
            # Show error message in the form window
            error_label = customtkinter.CTkLabel(window, text=f"Failed to update record: {e}", fg_color="red")
            error_label.grid(row=len(form_entries) + 1, column=0, columnspan=2)

    def delete_record(self):
        """Handles record deletion for the current table."""
        if not self.current_table:
            print("No table selected.")
            return

        selected_record = self.get_selected_record()
        if not selected_record:
            print("No record selected for deletion.")
            return

        try:
            # Get the columns for the current table
            columns, _ = fetch_all_data(self.current_table)
            # Use the first column as the primary key
            primary_key_column = columns[0]
            primary_key_value = selected_record[0]
            
            # Create the WHERE clause using the actual column name
            condition = f"{primary_key_column} = {primary_key_value}"
            
            # Perform the deletion
            delete_data(self.current_table, condition)
            self.switch_table(self.current_table)
            print("Record deleted successfully!")
            
        except Exception as e:
            print(f"Failed to delete record: {e}")

    def get_selected_record(self):
        """Retrieves the currently selected record from the Treeview table."""
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, customtkinter.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Treeview):
                        selected_items = child.selection()
                        if selected_items:
                            return child.item(selected_items[0], "values")
        
        # If we get here, either no selection was made or no table exists
        print("Please select a record first.")
        return None

    def search_records(self, search_term):
        """Filter table data based on search term"""
        if not self.current_table or not search_term:
            return
        
        columns, all_data = fetch_all_data(self.current_table)
        
        # Filter data based on search term (case-insensitive)
        filtered_data = []
        search_term = search_term.lower()
        for record in all_data:
            if any(str(value).lower().find(search_term) != -1 for value in record):
                filtered_data.append(record)
        
        # Clear previous widgets
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create search bar
        self.create_search_bar()
        
        # Display filtered results
        if filtered_data:
            table_frame = create_table_display(self.main_frame, filtered_data, columns)
            table_frame.pack(fill="both", expand=True)
