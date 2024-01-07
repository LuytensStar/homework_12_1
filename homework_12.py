import os.path
import sys
from collections import UserDict
from datetime import datetime
import pickle

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return 'Give me a name and phone please'
        except TypeError:
            return "Give me name and phone please"
        except ValueError:
            return "Enter user name"
        except NameError:
            return "Give me name and phone please"
    return wrapper


class Field:
    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value


class Phone(Field):

    def __init__(self, phone):
        self.value = phone
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, phone):
        print(f'setter phone{phone}')
        try:
            if not (phone.isdigit() and len(phone) == 10):
                raise ValueError('Phone is not digit or 10 symbols long')
            self.__value = phone
        except ValueError as e:
            print(e)
            raise

class Name(Field):
    pass

class Birthday(Field):
    def __init__(self, birthday):
        self.__value = birthday

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        try:
            datetime.strptime(value, '%d-%m-%Y')
            self.__value = value

        except ValueError:
            raise ValueError('Not that format')


class Record:
    def __init__(self, name, birthday = None):
        self.name = Name(name)
        self.birthday = Birthday(birthday) if Birthday else None
        self.phones = []

    def add_phone(self, phone):
        print(phone)
        phone_obj = Phone(phone)
        if phone_obj.value is not None:
            self.phones.append(phone_obj)
        else:
            print('Invalid phone number')
        # self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                break

    def edit_phone(self, old_phone, new_phone):
        for i,p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return

        raise ValueError('No such phone')

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None


    def days_to_birtday(self):
        if self.birthday:
            time_now = datetime.now()
            birthday_date = datetime.strptime(self.birthday.value, '%d-%m-%Y')
            next_birthday = datetime(time_now.year, birthday_date.month, birthday_date.day)
            if time_now > next_birthday:  # Compare with next_birthday, not birthday_date
                next_birthday = datetime(time_now.year + 1, birthday_date.month, birthday_date.day)
            return (next_birthday - time_now).days
        else:
            return None

    def __str__(self):
        phones = "; ".join([str(phone.value) for phone in self.phones])
        return f"Contact name: {self.name.value}, phones: {phones}"

class AddressBook(UserDict):

    def add_record(self, record, phone = None):
        if record.name.value in self.data:
            self.data[record.name.value].add_phone(phone)
        else:
            self.data[record.name.value] = record
    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def iterator(self,n):
        records = list(self.data.values())
        for i in range(0, len(records), n):
         yield records[i:i+n]

    def save_to_file(self, filename):
        with open(filename, 'wb') as fp:
            pickle.dump(self.data, fp)

    def load_from_file(self, filename):
        if os.path.getsize(filename) >0:
            with open(filename, 'rb') as fp:
                self.data = pickle.load(fp)
        else:
            self.data = {}

    def match(self, symblos):
        result = []
        for name, record in self.data.items():
            if symblos.lower() in name.lower():
                result.append(record)
            else:
                for phone in record.phones:
                    if symblos in phone.value:
                        result.append(record)
                        break
        return result


book = AddressBook()

def hello():
    return f"Hello how can i help you?"


@input_error
def add(name, phone):
    record = book.find(name)
    if record:
        record.add_phone(phone)
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
    if record.phones[0].value:
        print('Телефон додано')
    # record = Record(name)
    # record.add_phone(phone)
    # book.add_record(record)
    # if record.phones[0].value:
    #     print('Телефон додано')


@input_error
def change(name, phone):
    record = book.find(name)
    if record:
        record.edit_phone(record.phones[0].value, phone)
        return f"Номер телефону змінено на {phone}"
    else:
        return f"контакту з іменем {name} не існує"



def phone(name):
    record = book.find(name)
    if record:
        phones = ", ".join([phone.value for phone in record.phones])
        return f"телефон контакту {name} це {phones}"
    else:
        return f"No user with such name"


def match(symbols):
    results = book.match(symbols)
    return "\n".join(str(record) for record in results)

def add_birthday(name, birthday):
    record = book.find(name)
    if record:
        record.birthday = Birthday(birthday)
    else:
        return f"No user with such name"

def days_to_birthday(name):
    record = book.find(name)
    return record.days_to_birtday()



carry = {'phone': phone, 'change': change, 'add': add, 'hello': hello(), 'match' : match, 'add_birthday': add_birthday, 'days_to_birthday': days_to_birthday}

def parse_command(command):
    parts = command.split(' ')
    if '' in parts:
        parts.remove('')
    if parts[0] in carry and len(parts) == 3:
        return carry[str(parts[0])](parts[1], parts[2])
    elif parts[0] in carry and len(parts) == 2:
        return carry[parts[0]](parts[1])
    elif parts[0] in carry and len(parts) == 1:
        return carry[parts[0]]


def main():
    filename = 'new_file.pkl'
    if not os.path.isfile(filename):
        with open(filename, 'w') as fp:
            pass
    book.load_from_file('new_file.pkl')
    while True:
        command = input('Enter a command: ').lower()
        if command == 'show all':
            print('\n'.join([f"{name} : {str(record)}" for name, record in book.data.items()] ))
        elif command in ['exit', 'close', 'good bye']:
            print('Good bye')
            break
        print(parse_command(command))

    book.save_to_file('new_file.pkl')



if __name__ == '__main__':

    main()


#
# record = Record('artem')
# record.add_phone('3856712345')
# book.add_record(record)
# record1 = book.find('artem')
#
# record1.edit_phone('3856712345', '3856712346')
#
# record1 = book.save_fo_file(filename='new_file.pickle')
# print(record1)
