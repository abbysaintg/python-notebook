import os
import subprocess
from prettytable import PrettyTable
from datetime import datetime

notes_folder = os.path.join(os.path.dirname(__file__), 'notes')

# CLASS DEFINITIONS
class Notebook:
    def __init__(self):
        self.notes = self.load_notes()

    def print_logo(self):
        print(r"""
 _   _  ___ _____ _____ ____   ___   ___  _  __
| \ | |/ _ \_   _| ____| __ ) / _ \ / _ \| |/ /
|  \| | | | || | |  _| |  _ \| | | | | | | ' /
| |\  | |_| || | | |___| |_) | |_| | |_| | . \
|_| \_|\___/ |_| |_____|____/ \___/ \___/|_|\_\
    """)

    def home(self):
        self.reset_screen()

    def reset_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self.print_logo()
        print("\nType 'help' to see the list of commands\n")
        self.display_notes()
        print('\n')

    def load_notes(self):
        notes = []
        for note_file in os.listdir(notes_folder):
            if note_file.endswith(".txt"):
                name = os.path.splitext(note_file)[0]
                with open(os.path.join(notes_folder, note_file), "r") as f:
                    content = f.read()
                notes.append(Note(name, content))
        return notes

    def display_notes(self):
        table = PrettyTable()
        table.field_names = ["#", "Name", "Date Edited", "Content"]
        table.align = "l"
        for i, note in enumerate(self.notes, start=1):
            with open(f"notes/{note.name}.txt", mode='r') as file:
                contents = file.read()
            formatted_name = note.name.replace('_', ' ')
            formatted_time = note.edited_time.strftime('%a %b %d @ %I:%M%p')
            formatted_content = note.content[:50] + '...' if len(note.content) > 50 else note.content
            table.add_row([i, formatted_name, formatted_time, formatted_content], divider=True)
        print(table)

    def note_exists(self, name):
        return any(note.name.lower() == name.lower() for note in self.notes)

    def create_note(self, name):
        if self.note_exists(name):
            print("A note with this name already exists. Please choose a different name.")
        else:
            content = input("Enter the content of your note (press Enter to finish): ")
            note = Note(name, content)
            self.notes.append(note)
            note.save()
            self.reset_screen()

    def get_note(self, name):
        for note in self.notes:
            if note.name.lower() == name.lower():
                return note
        return None
    def rename_note(self, old_name, new_name):
        if old_name.lower() != new_name.lower() and self.note_exists(new_name):
            print("A note with this name already exists. Please choose a different name.")
        else:
            note = self.get_note(old_name)
            if note:
                old_filepath = note.filepath
                note.name = new_name
                note.filepath = os.path.join(notes_folder, f"{new_name}.txt")
                os.rename(old_filepath, note.filepath)
                note.save()
                self.reset_screen()
                print("Note renamed successfully.")
            else:
                self.reset_screen()
                print("Note not found.")

    def delete_note(self, name):
        note = self.get_note(name)
        if note:
            confirmation = input(
                f"Are you sure you want to delete the note '{name}'? (yes/no): ").lower()
            if confirmation == 'yes':
                note.delete()
                self.notes.remove(note)
                self.reset_screen()
                return True
            else:
                print("Deletion cancelled.")
                return False
        self.reset_screen()
        return False

    def display_help(self):
        help_text = """
    Available commands:
    - home: Display the list of notes.
    - create <name>: Create a new note with the specified name.
    - edit <name>: Edit the note with the specified name.
    - delete <name>: Delete the note with the specified name.
    - rename <old_name> <new_name>: Rename a note.
    - help: Display this help message.
    - exit | quit | q: Exit the program.
    """
        print(help_text)


class Note:
    def __init__(self, name, content=None):
        self.name = name
        self.content = content if content is not None else ""
        self.edited_time = datetime.now()
        self.filepath = os.path.join(notes_folder, f"{self.name}.txt")

    def edit(self):
        if not os.path.exists(self.filepath):
            print("The note file does not exist. Creating a new file.")
            self.save()

        try:
            subprocess.run(["open", "-t", self.filepath])
            print(
                "Note is opened in the text editor. Please save your changes and close the editor.")
            input("Press Enter when you are done editing...")
            self.load_content()
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def load_content(self):
        with open(self.filepath, "r") as f:
            self.content = f.read()

    def save(self):
        with open(self.filepath, "w") as f:
            f.write(self.content)
        self.edited_time = datetime.now()

    def display(self):
        print(self.content)


class CommandProcessor:
    def __init__(self, notebook):
        self.notebook = notebook
        self.commands = {
            "home": self.home,
            "create": self.create,
            "edit": self.edit,
            "delete": self.delete,
            "rename": self.rename,
            "help": self.help,
            "exit": self.exit,
            "quit": self.exit,
            "q": self.exit
        }

    def process(self, command):
        tokens = command.split()
        if not tokens:
            return

        action = tokens[0].lower()
        if action in self.commands:
            self.commands[action](tokens[1:])
        else:
            print("Invalid command")

    def home(self, args):
        self.notebook.home()

    def create(self, args):
        if args:
            name = "_".join(args)
            self.notebook.create_note(name)
        else:
            print("Please provide a note name.")

    def edit(self, args):
        if len(args) > 0:
            name = "_".join(args)
            note = self.notebook.get_note(name)
            if note:
                note.edit()
                note.save()
                self.notebook.reset_screen()
            else:
                print("Note not found.")
        else:
            print("Please provide a note name.")

    def delete(self, args):
        if len(args) > 0:
            if self.notebook.delete_note(args[0]):
                print("Note deleted successfully.")
            else:
                print("Note not found.")
        else:
            print("Please provide a note name.")

    def rename(self, args):
        if len(args) > 1:
            old_name, new_name = args[0], "_".join(args[1:])
            self.notebook.rename_note(old_name, new_name)
        else:
            print("Please provide the old and new note names.")

    def help(self, args):
        self.notebook.display_help()

    def exit(self, args):
        exit()

# MAIN FUNCTION
def main():
    notebook = Notebook()
    command_processor = CommandProcessor(notebook)

    notebook.reset_screen()
    while True:
        command = input("Notebook> ")
        command_processor.process(command)


# SCRIPT ENTRY POINT
if __name__ == "__main__":
    if not os.path.exists(notes_folder):
        os.makedirs(notes_folder)
    main()
