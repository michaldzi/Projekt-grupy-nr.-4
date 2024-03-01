from collections import UserDict
import re
import pickle
from datetime import datetime, timedelta
from notes import Notebook


class Field:
    """Base class for entry fields."""
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class PhoneNumber(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Niepoprawny numer telefonu")
        super().__init__(value)

    @staticmethod
    def validate_phone(value):
        pattern = re.compile(r"^\d{9}$")
        return pattern.match(value) is not None

class EmailAddress(Field):
    def __init__(self, value):
        if not self.validate_email(value):
            raise ValueError("Niepoprawny adres email")
        super().__init__(value)

    @staticmethod
    def validate_email(value):
        pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        return pattern.match(value) is not None

class BirthDate(Field):
    def __init__(self, value):
        if not self.validate_birthdate(value):
            raise ValueError("Niepoprawna data urodzenia")
        super().__init__(value)

    @staticmethod
    def validate_birthdate(value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

class Address(Field):
    def __init__(self, street, city, postal_code, country):
        self.street = street
        self.city = city
        self.postal_code = postal_code
        self.country = country
        super().__init__(value=f"{street}, {city}, {postal_code}, {country}")

class Record:
    def __init__(self, name: Name, birthdate: BirthDate = None):
        self.id = None  # The ID will be assigned by AddressBook
        self.name = name
        self.phone_numbers = []
        self.email_addresses = []
        self.birthdate = birthdate
        self.address = None  # Add a new property to store the address

    def add_address(self, address: Address):
        """Adds an address."""
        self.address = address

    def add_phone_number(self, phone_number: PhoneNumber):
        """Adds a phone number."""
        self.phone_numbers.append(phone_number)

    def remove_phone_number(self, phone_number: PhoneNumber):
        """Removes a phone number."""
        self.phone_numbers.remove(phone_number)

    def edit_phone_number(self, old_phone_number: PhoneNumber, new_phone_number: PhoneNumber):
        """Changes a phone number."""
        self.remove_phone_number(old_phone_number)
        self.add_phone_number(new_phone_number)

    def add_email_address(self, email_address: EmailAddress):
        """Adds an email address."""
        self.email_addresses.append(email_address)

    def remove_email_address(self, email_address: EmailAddress):
        """Removes an email address."""
        self.email_addresses.remove(email_address)

    def edit_email_address(self, old_email_address: EmailAddress, new_email_address: EmailAddress):
        """Changes an email address."""
        self.remove_email_address(old_email_address)
        self.add_email_address(new_email_address)

    def edit_name(self, new_name: Name):
        """Changes the first and last name."""
        self.name = new_name

    def days_to_birthdate(self):
        """Returns the number of days to the next birthdate."""
        if not self.birthdate or not self.birthdate.value:
            return "Brak daty urodzenia"
        today = datetime.now()
        bday = datetime.strptime(self.birthdate.value, "%Y-%m-%d")
        next_birthday = bday.replace(year=today.year)
        if today > next_birthday:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        """Returns a string representation of the entry, including the ID."""
        phone_numbers = ', '.join(phone_number.value for phone_number in self.phone_numbers)
        email_addresses = ', '.join(email_address.value for email_address in self.email_addresses)
        birthdate_str = f", Urodziny: {self.birthdate.value}" if self.birthdate else ""
        days_to_birthdate_str = f", Dni do urodzin: {self.days_to_birthdate()}" if self.birthdate else ""
        address_str = f"\nAdres: {self.address.value}" if self.address else ""
        return f"ID: {self.id}, Imię i nazwisko: {self.name.value}, " \
               f"Numery telefonów: {phone_numbers}, Adresy email: {email_addresses}{birthdate_str}{days_to_birthdate_str}{address_str}"


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.next_id = 1
        self.free_ids = set()

    def add_record(self, record: Record):
        """Adds an entry to the address book with ID management."""
        while self.next_id in self.data or self.next_id in self.free_ids:
            self.next_id += 1
        if self.free_ids:
            record.id = min(self.free_ids)
            self.free_ids.remove(record.id)
        else:
            record.id = self.next_id
            self.next_id += 1
        self.data[record.id] = record
        print(f"Dodano wpis z ID: {record.id}.")

    def delete_record_by_id(self):
        """Deletes a record based on ID."""
        user_input = input("Podaj ID rekordu, który chcesz usunąć: ").strip()
        record_id_str = user_input.replace("ID: ", "").strip()

        try:
            record_id = int(record_id_str)
            if record_id in self.data:
                del self.data[record_id]
                self.free_ids.add(record_id)
                print(f"Usunięto rekord o ID: {record_id}.")
            else:
                print("Nie znaleziono rekordu o podanym ID.")
        except ValueError:
            print("Nieprawidłowe ID. Proszę podać liczbę.")

    def find_record(self, search_term):
        """Finds entries containing the exact phrase provided."""
        found_records = []
        for record in self.data.values():
            if search_term.lower() in record.name.value.lower():
                found_records.append(record)
                continue
            for phone_number in record.phone_numbers:
                if search_term in phone_number.value:
                    found_records.append(record)
                    break
            for email_address in record.email_addresses:
                if search_term in email_address.value:
                    found_records.append(record)
                    break
        return found_records

    def find_records_by_name(self, name):
        """Finds records that match the given name and surname."""
        matching_records = []
        for record_id, record in self.data.items():
            if name.lower() in record.name.value.lower():
                matching_records.append((record_id, record))
        return matching_records


    def delete_record(self):
        """Deletes the record based on the selected ID after searching by name."""
        name_to_delete = input("Podaj imię i nazwisko osoby, którą chcesz usunąć: ")
        matching_records = self.find_records_by_name(name_to_delete)

        if not matching_records:
            print("Nie znaleziono pasujących rekordów.")
            return

        print("Znaleziono następujące pasujące rekordy:")
        for record_id, record in matching_records:
            print(f"ID: {record_id}, Rekord: {record}")

        try:
            record_id_to_delete = int(input("Podaj ID rekordu, który chcesz usunąć: "))
            if record_id_to_delete in self.data:
                del self.data[record_id_to_delete]
                self.free_ids.add(record_id_to_delete)  # Add the ID back to the free ID pool
                print(f"Usunięto rekord o ID: {record_id_to_delete}.")
            else:
                print("Nie znaleziono rekordu o podanym ID.")
        except ValueError:
            print("Nieprawidłowe ID. Proszę podać liczbę.")


    def show_all_records(self):
        """Displays all entries in the address book."""
        if not self.data:
            print("Książka adresowa jest pusta.")
            return
        for name, record in self.data.items():
            print(record)

    def __iter__(self):
        """Returns an iterator over the address book records."""
        self.current = 0
        return self

    def __next__(self):
        if self.current < len(self.data):
            records = list(self.data.values())[self.current:self.current+5]
            self.current += 5
            return records
        else:
            raise StopIteration


def edit_record(book):
    """Edits an existing record in the address book."""
    name_to_edit = input("Wprowadź imię i nazwisko które chcesz edytować: ")
    if name_to_edit in book.data:
        record = book.data[name_to_edit]
        print(f"Edytowanie: {name_to_edit}.")

        # Name and surname edit
        new_name_input = input("Podaj imię i nazwisko (wciśnij Enter żeby zachować obecne): ")
        if new_name_input.strip():
            record.edit_name(Name(new_name_input))
            print("Zaktualizowano imię i nazwisko.")

        # Phone number edit
        if record.phone_numbers:
            print("Obecne numery telefonów: ")
            for idx, phone_number in enumerate(record.phone_numbers, start=1):
                print(f"{idx}. {phone_number.value}")
            phone_to_edit = input("Wprowadź indeks numeru telefonu który chcesz edytować "
                                  "(wciśnij Enter żeby zachować obecny): ")
            if phone_to_edit.isdigit():
                idx = int(phone_to_edit) - 1
                if 0 <= idx < len(record.phone_numbers):
                    new_phone_number = input("Podaj nowy numer telefonu: ")
                    if new_phone_number.strip():
                        record.edit_phone_number(record.phone_numbers[idx], PhoneNumber(new_phone_number))
                        print("Numer telefonu zaktualizowany.")
                    else:
                        print("Nie dokonano zmian.")
                else:
                    print("Niepoprawny indeks numeru.")
            else:
                print("Pomięto edycję numeru.")
        else:
            print("Brak numerów telefonu.")

        # E-mail edit
        if record.email_addresses:
            print("Obecne adresy e-mail: ")
            for idx, email_address in enumerate(record.email_addresses, start=1):
                print(f"{idx}. {email_address.value}")
            email_to_edit = input("Wprowadź indeks adresu e-mail, który chcesz edytować "
                                  "(wciśnij Enter, aby zachować obecny): ")
            if email_to_edit.isdigit():
                idx = int(email_to_edit) - 1
                if 0 <= idx < len(record.email_addresses):
                    new_email = input("Podaj nowy adres e-mail: ")
                    if new_email.strip():
                        record.edit_email_address(record.email_addresses[idx], EmailAddress(new_email))
                        print("Adres e-mail zaktualizowany.")
                    else:
                        print("Nie dokonano zmian.")
                else:
                    print("Niepoprawny indeks adresu e-mail.")
            else:
                print("Pomięto edycję adresu e-mail.")
        else:
            print("Brak adresów e-mail.")

        print("Wpis zaktualizowany.")
    else:
        print("Wpisu nie znaleziono.")

def save_address_book(book, filename='address_book.pkl'):
    try:
        with open(filename, 'wb') as file:
            pickle.dump(book.data, file)
    except Exception as e:
        print(f"Błąd przy zapisie książki adresowej: {e}")

def load_address_book(filename='address_book.pkl'):
    try:
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        book = AddressBook()
        book.data = data
        return book
    except FileNotFoundError:
        print("Plik nie istnieje, tworzenie nowej książki adresowej.")
        return AddressBook()
    except Exception as e:
        print(f"Błąd przy ładowaniu książki adresowej: {e}")
        return AddressBook()

def input_phone_number():
    """Asks the user to enter a phone number."""
    while True:
        try:
            number = input("Podaj numer telefonu w formacie '123456789' (naciśnij Enter, aby pominąć): ")
            if not number:
                return None
            return PhoneNumber(number)
        except ValueError as e:
            print(e)

def input_email_address():
    """Asks the user to enter an email address."""
    while True:
        try:
            address = input("Podaj adres email (naciśnij Enter, aby pominąć): ")
            if not address:
                return None
            return EmailAddress(address)
        except ValueError as e:
            print(e)


def create_record():
    """Creates an entry in the address book based on user input."""
    name_input = input("Podaj imię i nazwisko: ")
    name = Name(name_input)

    birthdate = None
    while True:
        birthdate_input = input("Podaj datę urodzenia (YYYY-MM-DD) lub wciśnij Enter, aby pominąć: ")
        if not birthdate_input:
            break
        try:
            birthdate = BirthDate(birthdate_input)
            break
        except ValueError as e:
            print(e)

    record = Record(name, birthdate)

    while True:
        try:
            phone_number_input = input("Podaj numer telefonu (lub wciśnij Enter, aby zakończyć dodawanie numerów): ")
            if not phone_number_input:
                break
            phone_number = PhoneNumber(phone_number_input)
            record.add_phone_number(phone_number)
        except ValueError as e:
            print(e)

    while True:
        try:
            email_address_input = input("Podaj adres email (lub wciśnij Enter, aby zakończyć dodawanie adresów email): ")
            if not email_address_input:
                break
            email_address = EmailAddress(email_address_input)
            record.add_email_address(email_address)
        except ValueError as e:
            print(e)

    # New functionality: Adding an address
    add_address = input("Czy chcesz dodać adres? (t/n): ").lower().strip()
    if add_address in ['t']:
        street = input("Podaj ulicę: ")
        city = input("Podaj miasto: ")
        postal_code = input("Podaj kod pocztowy: ")
        country = input("Podaj nazwę państwa: ")
        address = Address(street, city, postal_code, country)
        record.add_address(address)

    return record

def main():
    notebook = Notebook()
    notebook.load_notes()
    book = load_address_book()

    while True:
        action = input("Witaj w Osobistym Asystencie proszę wybrać akcje :"
                       "\n Aby wybrać kontatkty wciśnij (1),"
                       "\n Aby wybrać notatki (2), "
                       "\n Wyjście (3): ")
        if action == '1':
            while True:
                contact_action = input(
                    "Wybierz działanie: \nDodaj kontakt (1), Znajdź kontakt (2), "
                    "Usuń kontakt (3), Edytuj kontakt (4), Pokaż wszystkie (5), Wróć (6): ")
                if contact_action == '1':
                    record = create_record()
                    book.add_record(record)
                    print("Dodano kontakt.")
                elif contact_action == '2':
                    search_term = input("Wpisz szukaną frazę: ")
                    found = book.find_record(search_term)
                    for record in found:
                        print(record)
                elif contact_action == '3':
                    book.delete_record_by_id()
                    print("Usunięto kontakt.")
                elif contact_action == '4':
                    edit_record(book)
                    print("Zaktualizowano kontakt.")
                elif contact_action == '5':
                    book.show_all_records()
                elif contact_action == '6':
                    break
                else:
                    print("Nie ma takiego polecenia, wybierz jeszcze raz.")
        elif action == '2':
            while True:
                note_action = input(
                    "Wybierz działanie dla notatek: \nDodaj notatkę (1), Pokaż notatki (2), "
                    "Usuń notatkę (3), Wróć (4): ")
                if note_action == '1':
                    title = input("Podaj tytuł notatki: ")
                    content = input("Podaj treść notatki: ")
                    notebook.add_note(title, content)
                    print("Dodano notatkę.")
                elif note_action == '2':
                    notebook.show_notes()
                elif note_action == '3':
                    note_id = input("Podaj ID notatki do usunięcia: ")
                    notebook.delete_note(note_id)
                    print("Usunięto notatkę.")
                elif note_action == '4':
                    break
                else:
                    print("Nie ma takiego polecenia, wybierz jeszcze raz")
        elif action == '3':
            print("Wyjście z programu.")
            break
        else:
            print("Nie ma takiego polecenia, wybierz jeszcze raz")

    save_address_book(book)
    notebook.save_notes()

if __name__ == "__main__":
    main()
