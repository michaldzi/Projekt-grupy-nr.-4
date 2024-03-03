from collections import UserDict
import re
import pickle
from datetime import datetime, timedelta


class Field:
    """Base class for entry fields."""

    def __init__(self, value):
        self.value = value


class Name(Field):
    """Class for first and last name."""

    pass


class Phone(Field):
    """Class for phone number with validation."""

    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Niepoprawny numer telefonu")
        super().__init__(value)

    @staticmethod
    def validate_phone(value):
        """Checks if the phone number is valid (9 digits, format 123456789)."""
        pattern = re.compile(r"^\d{9}$")
        return pattern.match(value) is not None


class Email(Field):
    """Class for email address with validation."""

    def __init__(self, value):
        if not self.validate_email(value):
            raise ValueError("Niepoprawny adres email")
        super().__init__(value)

    @staticmethod
    def validate_email(value):
        """Checks if the email is valid."""
        pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        return pattern.match(value) is not None


class Birthday(Field):
    """Class for birthday with validation."""

    def __init__(self, value):
        if not self.validate_birthday(value):
            raise ValueError("Niepoprawna data urodzenia")
        super().__init__(value)

    @staticmethod
    def validate_birthday(value):
        """Checks if the birthday is valid."""
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False


class Address(Field):
    """Class for residential address."""

    def __init__(self, street, city, postal_code, country):
        self.street = street
        self.city = city
        self.postal_code = postal_code
        self.country = country
        super().__init__(f"{street}, {city}, {postal_code}, {country}")


class Record:
    """Class for an entry in the address book."""

    def __init__(self, name: Name, birthday: Birthday = None, address: Address = None):
        self.name = name
        self.phones = []
        self.emails = []
        self.birthday = birthday
        self.address = address
        self.notes = []

    def add_phone(self, phone: Phone):
        """Adds a phone number."""
        self.phones.append(phone)

    def remove_phone(self, phone: Phone):
        """Removes a phone number."""
        self.phones.remove(phone)

    def edit_phone(self, old_phone: Phone, new_phone: Phone):
        """Changes a phone number."""
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def add_email(self, email: Email):
        """Adds an email address."""
        self.emails.append(email)

    def remove_email(self, email: Email):
        """Removes an email address."""
        self.emails.remove(email)

    def edit_email(self, old_email: Email, new_email: Email):
        """Changes an email address."""
        self.remove_email(old_email)
        self.add_email(new_email)

    def edit_name(self, new_name: Name):
        """Changes the first and last name."""
        self.name = new_name

    def days_to_birthday(self):
        """Returns the number of days to the next birthday."""
        if not self.birthday or not self.birthday.value:
            return "Brak daty urodzenia"
        today = datetime.now()
        bday = datetime.strptime(self.birthday.value, "%Y-%m-%d")
        next_birthday = bday.replace(year=today.year)
        if today > next_birthday:
            next_birthday = next_birthday.replace(year=today.year + 1)
        days = (next_birthday - today).days
        return days

    def edit_address(self, new_address: Address):
        """Changes the address."""
        self.address = new_address

    def __str__(self):
        """Returns a string representation of the entry, now including address."""
        phones = ", ".join(phone.value for phone in self.phones)
        emails = ", ".join(email.value for email in self.emails)
        birthday_str = f", Urodziny: {self.birthday.value}" if self.birthday else ""
        days_to_bday_str = (
            f", Dni do urodzin: {self.days_to_birthday()}" if self.birthday else ""
        )
        address_str = f", Adres: {self.address.value}" if self.address else ""
        return (
            f"Imię i nazwisko: {self.name.value}, "
            f"Telefony: {phones}, Email: {emails}{birthday_str}{days_to_bday_str}{address_str}"
        )

    def add_note(self, note):
        """Adds a note to the record."""
        self.notes.append(note)

    def show_notes(self):
        """Shows all notes associated with the record."""
        if not self.notes:
            print("No notes for this contact.")
        else:
            print("Notes:")
            for note in self.notes:
                print(note)


class AddressBook(UserDict):
    """Class for the address book."""

    def add_record(self, record: Record):
        """Adds an entry to the address book."""
        self.data[record.name.value] = record
        print("Dodano wpis.")

    def show_all_records(self):
        if not self.data:
            print("Brak kontaktów")
        else:
            print("Kontakty: ")
            for i, (name, record) in enumerate(self.data.items(), start=1):
                print(f"{i}. {name}: {record}")

    def find_record(self, search_term):
        """Finds entries containing the exact phrase provided."""
        found_records = []
        for record in self.data.values():
            if search_term.lower() in record.name.value.lower():
                found_records.append(record)
                continue
            for phone in record.phones:
                if search_term in phone.value:
                    found_records.append(record)
                    break
            for email in record.emails:
                if search_term in email.value:
                    found_records.append(record)
                    break
        return found_records

    def upcoming_birthdays(self, days):
        today = datetime.now().date()
        days = int(days)
        print(today)
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:

                bday = datetime.strptime(record.birthday.value, "%Y-%m-%d").date()
                print(bday)
                next_birthday = bday.replace(year=today.year)
                if today > next_birthday:
                    next_birthday = next_birthday.replace(year=today.year + 1)

                days_to = (next_birthday - today).days
                print(days_to)
                if (next_birthday - today).days <= days:
                    upcoming_birthdays.append(record.name.value)

        element = ", ".join(upcoming_birthdays)
        print(f"W ciągu najblizszych {days} dni, urodziny mają: \n{element}")

    def delete_record(self, name):
        """Deletes a record by name."""
        if name in self.data:
            del self.data[name]
            print(f"Usunięto wpis: {name}.")
        else:
            print(f"Wpis o nazwie {name} nie istnieje.")

    def __iter__(self):
        """Returns an iterator over the address book records."""
        self.current = 0
        return self

    def __next__(self):
        if self.current < len(self.data):
            records = list(self.data.values())[self.current : self.current + 5]
            self.current += 5
            return records
        else:
            raise StopIteration

    def find_by_birthday_range(self, days):
        """Finds contacts with birthdays within the specified range of days."""
        found_contacts = []
        for record in self.data.values():
            days_to_birthday = record.days_to_birthday()
            if (
                days_to_birthday != "Brak daty urodzenia"
                and 0 <= days_to_birthday <= days
            ):
                found_contacts.append(record)
        return found_contacts


def edit_record(book):
    """Edits an existing record in the address book."""
    name_to_edit = input("Wprowadź imię i nazwisko które chcesz edytować: ")
    if name_to_edit in book.data:
        record = book.data[name_to_edit]
        print(f"Edytowanie: {name_to_edit}.")

        new_name_input = input(
            "Podaj imię i nazwisko (wciśnij Enter żeby zachować obecne): "
        )
        if new_name_input.strip():
            record.edit_name(Name(new_name_input))
            print("Zaktualizowano imię i nazwisko.")

        if record.phones:
            print("Obecne numery telefonów: ")
            for idx, phone in enumerate(record.phones, start=1):
                print(f"{idx}. {phone.value}")
            phone_to_edit = input(
                "Wprowadź indeks numeru telefonu który chcesz edytować "
                "(wciśnij Enter żeby zachować obecny): "
            )
            if phone_to_edit.isdigit():
                idx = int(phone_to_edit) - 1
                if 0 <= idx < len(record.phones):
                    new_phone_number = input("Podaj nowy numer telefonu: ")
                    if new_phone_number.strip():
                        record.edit_phone(record.phones[idx], Phone(new_phone_number))
                        print("Numer telefonu zaktualizowany.")
                    else:
                        print("Nie dokonano zmian.")
                else:
                    print("Niepoprawny indeks numeru.")
            else:
                print("Pomięto edycję numeru.")
        else:
            print("Brak numerów telefonu.")

        print("Wpis zaktualizowany.")
    else:
        print("Wpisu nie znaleziono.")


def save_address_book(book, filename="address_book.pkl"):
    try:
        with open(filename, "wb") as file:
            pickle.dump(book.data, file)
        print("Zapisano liste adresową.")
    except Exception as e:
        print(f"Błąd przy zapisie liście kontaktów: {e}")


def load_address_book(filename="address_book.pkl"):
    try:
        with open(filename, "rb") as file:
            data = pickle.load(file)
        book = AddressBook()
        book.data = data
        print("Witam w Osobistym asystencie.")
        return book
    except FileNotFoundError:
        print("Plik nie istnieje, tworzenie nowej listy kontaktów.")
        return AddressBook()
    except Exception as e:
        print(f"Błąd przy ładowaniu listy kontaktów: {e}")
        return AddressBook()


def input_phone():
    """Asks the user to enter a phone number."""
    while True:
        try:
            number = input(
                "Podaj numer telefonu w formacie '123456789' (naciśnij Enter, aby pominąć): "
            )
            if not number:
                return None
            return Phone(number)
        except ValueError as e:
            print(e)


def input_email():
    """Asks the user to enter an email address."""
    while True:
        try:
            address = input("Podaj adres email (naciśnij Enter, aby pominąć): ")
            if not address:
                return None
            return Email(address)
        except ValueError as e:
            print(e)


def create_record():
    """Creates an entry in the address book based on user input."""
    name_input = input("Podaj imię i nazwisko: ")
    name = Name(name_input)

    birthday = None
    while True:
        birthday_input = input(
            "Podaj datę urodzenia (YYYY-MM-DD) lub wciśnij Enter, aby pominąć: "
        )
        if not birthday_input:
            break
        try:
            birthday = Birthday(birthday_input)
            break
        except ValueError as e:
            print(e)

    record = Record(name, birthday)

    while True:
        try:
            phone_input = input(
                "Podaj numer telefonu (lub wciśnij Enter, aby zakończyć dodawanie numerów): "
            )
            if not phone_input:
                break
            phone = Phone(phone_input)
            record.add_phone(phone)
        except ValueError as e:
            print(e)

    while True:
        try:
            email_input = input(
                "Podaj adres email (lub wciśnij Enter, aby zakończyć dodawanie adresów email): "
            )
            if not email_input:
                break
            email = Email(email_input)
            record.add_email(email)
        except ValueError as e:
            print(e)

    add_address = input("Czy chcesz dodać adres? (t/n): ").lower()
    if add_address == "t":
        street = input("Podaj ulicę: ")
        city = input("Podaj miasto: ")
        postal_code = input("Podaj kod pocztowy: ")
        country = input("Podaj kraj: ")
        if street and city and postal_code and country:
            address = Address(street, city, postal_code, country)
            record.address = address
        else:
            print(
                "Nie wszystkie informacje o adresie zostały podane. Adres nie zostanie dodany."
            )

    add_note = input("Czy chcesz dodać notatkę? (t/n): ").lower()
    if add_note == "t":
        note_content = input("Podaj treść notatki: ")
        if note_content.strip():
            note = Note(note_content)
            record.notes.append(note)
            print("Notatka dodana.")
        else:
            print("Notatka nie może być pusta.")

    return record


class Note:
    def __init__(self, content):
        self.content = content
        self.created_at = datetime.now()
        self.tags = []

    def add_tag(self, tag):
        self.tags.append(tag)

    def __str__(self):
        return f"Data dodania: {self.created_at},\nNotatka: {self.content}"


class Notebook:
    def __init__(self):
        self.notes = []
        # A list for storing notes, each note can be a dictionary or a class instance

    def add_note(self, note_content):
        note = Note(note_content)
        self.notes.append(note)
        print("Notatka dodana.")

    def show_notes(self):
        if not self.notes:
            print("Nie ma notatek do wyświetlenia.")
        else:
            print("Twoje notatki:")
            for i, note in enumerate(self.notes, start=1):
                print(f"{i}. {note},\nTagi: {', '.join(note.tags)}")

    def delete_note(self, note_id):
        # Deleting a note
        if 1 <= note_id <= len(self.notes):
            del self.notes[note_id - 1]
            print(f"Usunięto notatkę: {note_id}")
        else:
            print("Nie ma notatki o podanym ID.")

    def save_notes(self, filename="notes.pkl"):
        try:
            with open(filename, "wb") as file:
                pickle.dump(self.notes, file)
        except Exception as e:
            print(f"Wystąpił błąd podczas zapisu notatek: {e}")

    def load_notes(self, filename="notes.pkl"):
        try:
            with open(filename, "rb") as file:
                self.notes = pickle.load(file)
        except FileNotFoundError:
            print("Plik z notatkami nie istnieje. Tworzenie nowego pliku.")
            self.notes = []
        except Exception as e:
            print(f"Wystąpił błąd podczas wczytywania notatek: {e}")


class Tag:
    def __init__(self, notes):
        self.notes = notes

    def add_tag(self, note_index, tag):
        if 1 <= note_index <= len(self.notes.notes):
            note = self.notes.notes[note_index - 1]
            note.add_tag(tag)
            print(f"Do notatki dodano tag: {tag}")
        else:
            print("Nieprawidłowy numer notatki.")

    def search_tag(self, tag):
        notes_with_tag = []
        for note in self.notes.notes:
            if tag in note.tags:
                notes_with_tag.append(note)
        return notes_with_tag

    def sort_tags(self):
        sorted_dict = {}
        all_tags = set(tag for note in self.notes.notes for tag in note.tags)

        for tag in sorted(all_tags):
            sorted_dict[tag] = [note for note in self.notes.notes if tag in note.tags]

        return sorted_dict


class AssistantBot:
    def __init__(self):
        self.notebook = Notebook()
        self.notebook.load_notes()
        self.book = load_address_book()
        self.tag_manager = Tag(self.notebook)

    def main(self):
        while True:
            action = input(
                "Witaj w Osobistym Asystencie proszę wybrać akcje :"
                "\n Aby wybrać kontakty wciśnij (1),"
                "\n Aby wybrać notatki (2), "
                "\n Wyjście (3): "
            )
            if action == "1":
                while True:
                    contact_action = input(
                        "Wybierz działanie: \nDodaj kontakt (1), \nZnajdź kontakt (2), "
                        "\nUsuń kontakt (3), \nEdytuj kontakt (4), \nPokaż wszystkie (5), \nWyświetl kontakty które mają najblizsze urodziny(6):  \nWróć (7): "
                    )
                    if contact_action == "1":
                        record = create_record()
                        self.book.add_record(record)
                        print("Dodano kontakt.")
                    elif contact_action == "2":
                        search_term = input("Wpisz szukaną frazę: ")
                        found = self.book.find_record(search_term)
                        for record in found:
                            print(record)
                    elif contact_action == "3":
                        self.book.delete_record_by_id()
                        print("Usunięto kontakt.")
                    elif contact_action == "4":
                        edit_record(self.book)
                        print("Zaktualizowano kontakt.")
                    elif contact_action == "5":
                        self.book.show_all_records()

                    elif contact_action == "6":
                        date = int(input("Wpisz liczbe dni w której należy wyszukać:"))
                        self.book.upcoming_birthdays(date)

                    elif contact_action == "7":
                        break
                    else:
                        print("Nie ma takiego polecenia, wybierz jeszcze raz.")
            elif action == "2":
                while True:
                    notes_action = input(
                        "Wybierz działanie: \nDodaj notatkę (1), \nWyświetl notatki (2), \nEdytuj notatkę (3),"
                        "\nUsuń notatkę (4), \nZapisz notatki (5), \nWczytaj notatki (6),"
                        "\nDodaj tag do notatki (7), \nZnajdź notatkę po tagu (8), \nPosortuj notatki według tagów (9),"
                        "\nWróć (0)"
                    )

                    if notes_action == "1":
                        note_content = input("Wprowadź treść notatki: ")
                        self.notebook.add_note(note_content)
                    elif notes_action == "2":
                        self.notebook.show_notes()
                    elif notes_action == "3":
                        pass
                    elif notes_action == "4":
                        self.notebook.show_notes()
                        note_id = int(input("Podaj numer notatki do usunięcia: "))
                        self.notebook.delete_note(note_id)
                    elif notes_action == "5":
                        self.notebook.save_notes()
                        print("Notatki zostały zapisane")
                    elif notes_action == "6":
                        self.notebook.load_notes()
                        print("Notatki zaostały wczytane")
                    elif notes_action == "7":
                        self.notebook.show_notes()
                        note_index = int(
                            input("Podaj numer notatki, do której chcesz dodać tag: ")
                        )
                        tag_content = input("Wprowadź tag: ")
                        self.tag_manager.add_tag(note_index, tag_content)
                    elif notes_action == "8":
                        tag_to_search = input("Wprowadź tag do wyszukania: ")
                        notes_with_tag = self.tag_manager.search_tag(tag_to_search)
                        print(f"Notatki z tagiem '{tag_to_search}':")
                        for i, note in enumerate(notes_with_tag, start=1):
                            print(f"{i}. {note}")
                    elif notes_action == "9":
                        sorted_tags = self.tag_manager.sort_tags()
                        for tag, notes in sorted_tags.items():
                            print(f"Tag: {tag}, Notatki:")
                            for i, note in enumerate(notes, start=1):
                                print(f"  {i}. {note}")
                    elif notes_action == "0":
                        break
                    else:
                        print("Nieprawidłowy wybór. Spróbuj ponownie.")

            elif action == "3":
                print("Wyjście z programu.")
                break
            else:
                print("Nie ma takiego polecenia, wybierz jeszcze raz")
        save_address_book(self.book)
        self.notebook.save_notes()


if __name__ == "__main__":
    assistant_bot = AssistantBot()
    assistant_bot.main()
