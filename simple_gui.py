import tkinter as tk
from tkinter import messagebox, IntVar
import random
import datetime
import os
import xml.etree.ElementTree as ET
from questions_data import questions_data

class QuizApp:
    OPTIONS_PER_QUESTION = 4
    entry_counter = 1

    def __init__(self, root):
        self.root = root
        self.root.title("INQBIZ Arcade")

        # Add header title at the bottom
        header_label = tk.Label(
            text="INQBIZ ARCADE",
            font=("Arial", 72, "bold"),
            fg="black",
        )
        header_label.pack(side="bottom", pady=(0, 72))

        # Bind hover event to change transparency
        header_label.bind("<Enter>", lambda event: root.attributes('-alpha', 0.6))
        header_label.bind("<Leave>", lambda event: root.attributes('-alpha', 1.0))

        # Function to change color alternately
        def change_color():
            current_color = header_label.cget("fg")
            next_color = "blue" if current_color == "black" else "black"
            header_label.config(fg=next_color)
            root.after(500, change_color)  # Schedule the function after 500 milliseconds

        # Schedule the initial call to the function
        root.after(500, change_color)

        # Initialize other attributes
        self.user_name = ""
        self.matrix_number = ""
        self.current_question = 0

        # Use the imported questions_data
        self.questions = questions_data

        # Shuffle questions to select 10 at random
        random.shuffle(self.questions)
        self.selected_questions = self.questions[:10]

        self.user_answer = IntVar(value=-1)
        self.score = 0

        # Create user registration interface
        self.create_user_registration()

        # Don't call mainloop here, let it be called in __main__

    def create_user_registration(self):
        registration_frame = tk.Frame(self.root)
        registration_frame.pack(pady=10)

        tk.Label(registration_frame, text="Name:", font=("Arial", 14)).grid(row=0, column=0, pady=5)
        self.name_entry = tk.Entry(registration_frame, font=("Arial", 14))
        self.name_entry.grid(row=0, column=1, pady=5)

        tk.Label(registration_frame, text="Matrix Number:", font=("Arial", 14)).grid(row=1, column=0, pady=5)
        self.matrix_entry = tk.Entry(registration_frame, font=("Arial", 14))
        self.matrix_entry.grid(row=1, column=1, pady=5)

        registration_button = tk.Button(registration_frame, text="Start Quiz", command=self.start_quiz, font=("Arial", 14))
        registration_button.grid(row=2, columnspan=2, pady=10)

    def create_quiz(self):
        self.quiz_frame = tk.Frame(self.root)
        self.quiz_frame.pack(pady=10)

        self.question_label = tk.Label(self.quiz_frame, text="", font=("Arial", 16))
        self.question_label.pack(pady=5)

        # Initialize IntVar values to unique negative numbers
        self.option_vars = [IntVar(value=-(i + 1)) for i in range(self.OPTIONS_PER_QUESTION)]

        for i in range(self.OPTIONS_PER_QUESTION):
            option_radio = tk.Radiobutton(
                self.quiz_frame,
                text="",
                variable=self.user_answer,
                value=-(i + 1),
                font=("Arial", 14)
            )
            option_radio.pack(pady=3)

        submit_button = tk.Button(
            self.quiz_frame,
            text="Submit Answer",
            command=self.show_next_question,
            font=("Arial", 14)
        )
        submit_button.pack(pady=10)

    def start_quiz(self):
        self.user_name = self.name_entry.get()
        self.matrix_number = self.matrix_entry.get()

        if self.user_name and self.matrix_number:
            self.entry_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.current_question = 0
            self.create_quiz()  # Move the creation of quiz interface here
            self.show_question()  # Add this line to display the initial question
            # Hide the registration frame and show the quiz frame
            self.quiz_frame.pack()
            self.root.geometry("400x300")  # Adjust the window size as needed
        else:
            messagebox.showerror("Error", "Please enter both Name and Matrix Number.")

    def show_question(self):
        current_question = self.selected_questions[self.current_question]
        question_text = current_question['question']
        self.question_label.config(text=question_text)

        for i in range(self.OPTIONS_PER_QUESTION):
            option_text = current_question['options'][i]
            option_radio = self.quiz_frame.winfo_children()[1 + i]
            option_radio.config(text=option_text)

    def show_next_question(self):
        selected_option = abs(self.user_answer.get())
        current_question = self.selected_questions[self.current_question]

        if selected_option == 0:
            messagebox.showwarning("Warning", "Please select an answer.")
        elif current_question['options'][selected_option - 1] == current_question['correct_option']:
            self.score += 1

        # Move to the next question or end the quiz if all questions are completed
        self.current_question += 1
        if self.current_question == len(self.selected_questions):
            self.end_quiz()
        else:
            self.show_question()

    def end_quiz(self):
        minutes_earned = self.score * 6
        messagebox.showinfo("Quiz Completed", "Congratulations, {}! You have completed the quiz.\n"
                            "You earned {} points, which is {} minutes.".format(self.user_name, self.score, minutes_earned))
        self.quiz_frame.pack_forget()
        self.root.geometry("300x150")  # Adjust the window size as needed

        # Terminate the program
        self.root.destroy()

        # Export user information to XML
        self.export_to_xml(minutes_earned)

    def export_to_xml(self, minutes_earned):
        xml_file = "quiz_results.xml"

        # Check if the file exists
        if os.path.exists(xml_file):
            # Load existing XML file
            tree = ET.parse(xml_file)
            root = tree.getroot()
        else:
            # Create a new XML file if it doesn't exist
            root = ET.Element("quiz_results")
            tree = ET.ElementTree(root)

        # Find the last entry number in the existing XML file
        entry_number = len(root) + 1

        # Create new entry
        entry = ET.SubElement(root, "entry")

        # Add entry number to the new entry
        entry_no_element = ET.SubElement(entry, "EntryNo")
        entry_no_element.text = str(entry_number)

        name = ET.SubElement(entry, "Name")
        name.text = self.user_name

        matrix_no = ET.SubElement(entry, "MatrixNo")
        matrix_no.text = self.matrix_number

        entry_time = ET.SubElement(entry, "EntryTime")
        entry_time.text = self.entry_time

        points = ET.SubElement(entry, "Points")
        points.text = str(self.score)

        playtime_minutes = ET.SubElement(entry, "PlaytimeMinutes")
        playtime_minutes.text = str(minutes_earned)

        # Save the updated XML file
        tree = ET.ElementTree(root)  # This line is necessary to update the tree after adding the new entry
        tree.write(xml_file, encoding="utf-8")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.attributes('-fullscreen', True)
    
    def on_escape(event):
        root.destroy()
    
    root.bind("<Escape>", on_escape)
    
    root.mainloop()
