import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import speech_recognition as sr

class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-Powered File Manager")
        self.root.geometry("700x650")

        # Initially set the current directory to the user's home directory
        self.current_directory = os.path.expanduser("~")
        self.create_widgets()
        self.update_directory()

    def create_widgets(self):
        # Directory selection frame
        dir_frame = tk.Frame(self.root)
        dir_frame.pack(pady=10, padx=10, fill="x")

        self.current_dir_label = tk.Label(dir_frame, text="Current Directory:", font=("Arial", 12))
        self.current_dir_label.pack(side="left")

        self.current_dir_entry = tk.Entry(dir_frame, width=50, font=("Arial", 12))
        self.current_dir_entry.pack(side="left", padx=10)

        tk.Button(dir_frame, text="Change Directory", command=self.change_directory, font=("Arial", 10)).pack(side="left")

        # File list frame with scrollbar
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10)

        self.file_listbox = tk.Listbox(list_frame, width=70, height=15, font=("Arial", 12))
        self.file_listbox.pack(side="left")

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # Operation buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        self.create_button(button_frame, "Open File", self.open_file, 0, 0)
        self.create_button(button_frame, "Delete File", self.delete_file, 0, 1)
        self.create_button(button_frame, "New Folder", self.create_new_folder, 1, 0)
        self.create_button(button_frame, "New File", self.create_new_file, 1, 1)

        # AI features
        ai_frame = tk.Frame(self.root)
        ai_frame.pack(pady=10)

        self.create_button(ai_frame, "Categorize Files", self.categorize_files, 1, 0)
        self.create_button(ai_frame, "Recent Files", self.suggest_recent_files, 2, 0)
        self.create_button(ai_frame, "Voice Command", self.listen_command, 3, 0)

    def create_button(self, parent, text, command, row, column):
        tk.Button(parent, text=text, command=command, font=("Arial", 12), width=20).grid(row=row, column=column, padx=5, pady=5)

    def update_directory(self):
        self.current_dir_entry.delete(0, tk.END)
        self.current_dir_entry.insert(0, self.current_directory)
        self.file_listbox.delete(0, tk.END)

        try:
            for item in os.listdir(self.current_directory):
                self.file_listbox.insert(tk.END, item)
        except PermissionError:
            messagebox.showerror("Error", "You don't have permission to access this directory.")

    def get_selected_file_path(self):
        selected_file = self.file_listbox.get(tk.ACTIVE)
        return os.path.join(self.current_directory, selected_file)

    # File Operations
    def change_directory(self):
        new_directory = filedialog.askdirectory()
        if new_directory:
            self.current_directory = new_directory
            self.update_directory()

    def open_file(self):
        file_path = self.get_selected_file_path()
        if os.path.isfile(file_path):
            os.system(f'"{file_path}"')
        else:
            messagebox.showerror("Error", "Selected item is not a file.")

    def delete_file(self):
        file_path = self.get_selected_file_path()
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                self.update_directory()
                messagebox.showinfo("Success", "File deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showerror("Error", "Selected item is not a file.")

    def create_new_folder(self):
        folder_name = simpledialog.askstring("New Folder", "Enter folder name:")
        if folder_name:
            new_folder_path = os.path.join(self.current_directory, folder_name)
            try:
                os.mkdir(new_folder_path)
                self.update_directory()
                messagebox.showinfo("Success", f"Folder '{folder_name}' created successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def create_new_file(self):
        file_name = simpledialog.askstring("New File", "Enter file name (with extension):")
        if file_name:
            new_file_path = os.path.join(self.current_directory, file_name)
            try:
                with open(new_file_path, 'w') as new_file:
                    new_file.write("")  # Create an empty file
                self.update_directory()
                messagebox.showinfo("Success", f"File '{file_name}' created successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # AI Features
    def categorize_files(self):
        categories = {
            'Documents': ['.pdf', '.docx', '.txt'],
            'Images': ['.jpg', '.jpeg', '.png', '.gif'],
            'Videos': ['.mp4', '.mkv', '.avi'],
            'Audio': ['.mp3', '.wav', '.m4a'],
            'Others': []
        }

        categorized_files = {key: [] for key in categories}

        for file_name in os.listdir(self.current_directory):
            file_extension = os.path.splitext(file_name)[1].lower()
            for category, extensions in categories.items():
                if file_extension in extensions:
                    categorized_files[category].append(file_name)
                    break
            else:
                categorized_files['Others'].append(file_name)

        messagebox.showinfo("Categorized Files", "\n".join([f"{category}: {', '.join(files)}" for category, files in categorized_files.items()]))

    def suggest_recent_files(self):
        files = [(file, os.path.getmtime(os.path.join(self.current_directory, file))) for file in os.listdir(self.current_directory)]
        files.sort(key=lambda x: x[1], reverse=True)
        recent_files = [file for file, _ in files[:5]]  # Get top 5 recent files
        messagebox.showinfo("Recent Files", "\n".join(recent_files))

    def listen_command(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            messagebox.showinfo("Voice Command", "Listening...")
            audio = recognizer.listen(source)

            try:
                command = recognizer.recognize_google(audio).lower()
                messagebox.showinfo("Command Recognized", f"You said: {command}")
                self.execute_voice_command(command)
            except sr.UnknownValueError:
                messagebox.showerror("Error", "Could not understand the audio.")
            except sr.RequestError as e:
                messagebox.showerror("Error", f"Could not request results: {e}")

    def execute_voice_command(self, command):
        if "open recent file" in command:
            self.suggest_recent_files()
        elif "delete file" in command:
            self.delete_file()
        elif "search file" in command:
            self.search_files()
        elif "open file" in command:
            file_name = command.replace("open file", "").strip()
            file_name = file_name.replace(" dot ", ".")
            self.open_file_by_name(file_name)
        else:
            messagebox.showerror("Error", "Command not recognized.")

    def search_files(self):
        search_term = simpledialog.askstring("Search Files", "Enter the search term:")
        if search_term:
            matching_files = [f for f in os.listdir(self.current_directory) if search_term.lower() in f.lower()]
            if matching_files:
                messagebox.showinfo("Search Results", "\n".join(matching_files))
            else:
                messagebox.showinfo("Search Results", "No files found.")

    def open_file_by_name(self, file_name):
        # Search for the file in the current directory
        matching_files = [f for f in os.listdir(self.current_directory) if file_name.lower() in f.lower()]
        
        if matching_files:
            exact_file = matching_files[0]  # Take the first matched file
            file_path = os.path.join(self.current_directory, exact_file)
            
            if os.path.isfile(file_path):
                try:
                    os.system(f'"{file_path}"')
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open file: {e}")
            else:
                messagebox.showerror("Error", "Matched item is not a file.")
        else:
            messagebox.showerror("Error", f"File '{file_name}' not found.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileManagerApp(root)
    root.mainloop()
