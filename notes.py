import pickle
from datetime import datetime

class Note:
    def __init__(self, content):
        self.content = content
        self.created_at = datetime.now()

    def __str__(self):
        return f"{self.created_at}: {self.content}"

class Notebook:
    def __init__(self):
        self.notes = []  # A list for storing notes, each note can be a dictionary or a class instance

    def add_note(self, title, content):
        # Adding a note as a dictionary
        note = {"title": title, "content": content}
        self.notes.append(note)

    def show_notes(self):
        if not self.notes:
            print("Nie ma notatek do wyświetlenia.")
            return
        for note in self.notes:
            print("--------")
            print(f"Tytuł: {note['title']}")
            print(f"Treść: {note['content']}")
            print("--------")

    def delete_note(self, note_id):
        # Deleting a note
        if 0 <= note_id < len(self.notes):
            del self.notes[note_id]
        else:
            print("Nie ma notatki o podanym ID.")

    def save_notes(self, filename='notes.pkl'):
        try:
            with open(filename, 'wb') as file:
                pickle.dump(self.notes, file)
        except Exception as e:
            print(f"Wystąpił błąd podczas zapisu notatek: {e}")

    def load_notes(self, filename='notes.pkl'):
        try:
            with open(filename, 'rb') as file:
                self.notes = pickle.load(file)
        except FileNotFoundError:
            print("Plik z notatkami nie istnieje. Tworzenie nowego pliku.")
            self.notes = []
        except Exception as e:
            print(f"Wystąpił błąd podczas wczytywania notatek: {e}")
