import json
import os

# Definice třídy Account
class Account:
    def __init__(self, acc_number, uid, balance):
        self.acc_number = acc_number
        self.uid = uid
        self.balance = balance

    def get_balance(self):
        return self.balance

    def send_between_accounts(self, to_account, value):
        if self.balance >= value:
            self.balance -= value
            to_account.balance += value
            return True
        else:
            return False

# Definice třídy ClassicAccount
class ClassicAccount(Account):
    def __init__(self, acc_number, uid, balance):
        super().__init__(acc_number, uid, balance + bonus) #prakticky inicializace __init__ parenta (Account)

# Definice třídy SavingsAccount
class SavingsAccount(Account):
    def __init__(self, acc_number, uid, balance, apy):
        super().__init__(acc_number, uid, balance) #prakticky inicializace __init__ parenta (Account)
        self.apy = apy

# Definice třídy User
class User:
    def __init__(self, uid):
        self.uid = uid
        self.accounts = []

    def create_account(self, acc_type, bank):
        new_acc_number = bank.generate_account_number()  # Použijeme metodu generate_account_number
        if acc_type == "classic":
            new_account = ClassicAccount(new_acc_number, self.uid, 0)
        elif acc_type == "savings":
            new_account = SavingsAccount(new_acc_number, self.uid, 0, 0.01)
        else:
            return None
        self.accounts.append(new_acc_number)
        bank.all_accounts[new_acc_number] = new_account
        return new_account

# Definice třídy Bank
class Bank:
    def __init__(self):
        self.all_accounts = {}
        self.next_account_number = 1  # Jednoduché generování čísel účtů

    def generate_account_number(self):
        if self.all_accounts:
            max_acc_num = max(int(acc_num) for acc_num in self.all_accounts.keys())
            acc_num = str(max_acc_num + 1).zfill(6)
        else:
            acc_num = str(self.next_account_number).zfill(6)
        self.next_account_number += 1
        return acc_num

    def save_accounts_to_file(self, users, filename='accounts.json'):
        accounts_data = {}
        for user in users:
            for account_number in user.accounts:
                account = self.all_accounts[account_number]
                account_data = {
                    'acc_number': account.acc_number,
                    'uid': user.uid,
                    'balance': account.balance
                }
                if isinstance(account, SavingsAccount):
                    account_data['apy'] = account.apy
                accounts_data[account.acc_number] = account_data
        with open(filename, 'w') as file:
            json.dump(accounts_data, file, indent=4)

    def load_accounts_from_file(self, filename='accounts.json'):
        if not os.path.exists(filename):
            return {}
        with open(filename, 'r') as file:
            accounts_data = json.load(file)
        users = {}
        for acc_num, acc_data in accounts_data.items():
            uid = acc_data['uid']
            if uid not in users:
                users[uid] = User(uid=uid)  # Vytvoří uživatele s UID
            if 'apy' in acc_data:
                account = SavingsAccount(acc_data['acc_number'], acc_data['uid'], acc_data['balance'], acc_data['apy'])
            else:
                account = ClassicAccount(acc_data['acc_number'], acc_data['uid'], acc_data['balance'])
            users[uid].accounts.append(account.acc_number)
            self.all_accounts[acc_num] = account
        return users

    def add_user_and_save(self, user, filename='accounts.json'):
        # Načte existující uživatele a účty ze souboru
        existing_users = self.load_accounts_from_file(filename)
        # Přidá nového uživatele do seznamu
        existing_users[user.uid] = user
        # Uloží aktualizovaný seznam uživatelů zpět do souboru
        self.save_accounts_to_file(existing_users.values(), filename)

    def cancel_account(self, user, account_number):
        if account_number in user.accounts and account_number in self.all_accounts:
            del self.all_accounts[account_number]
            user.accounts.remove(account_number)
            return True
        else:
            return False

    def transfer(self, from_account_number, to_account_number, value):
        if from_account_number in self.all_accounts and to_account_number in self.all_accounts:
            from_account = self.all_accounts[from_account_number]
            to_account = self.all_accounts[to_account_number]
            return from_account.send_between_accounts(to_account, value)
        else:
            return False

    def find_latest_json_file(self, directory):
        json_files = []
        # Prochází všechny soubory a podadresáře v daném adresáři
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.json') and file.startswith('20'): #pokud to je json a začíná to 20 (tedy rok) a je json
                    json_files.append(os.path.join(root, file)) #prida to do seznamu
        json_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        if json_files == []:
            print("No JSON files found.")
            return None
        else:
            print(json_files)
            return json_files[0] if json_files else None #vrátí první - nejnovější - z listu

# Příklad použití
bonus = 0
bank = Bank()


while True:
    # Načtení uživatelů ze souboru při spuštění programu
    loaded_users = bank.load_accounts_from_file('accounts.json')



    print("1. Nový účet\n2. Smazat účet\n3. Převod mezi účty")
    choice = input("Zadejte číslo: ")
    if choice == "1":
        new_user = User(input("UID: "))
        new_account = new_user.create_account("classic", bank)
        bank.add_user_and_save(new_user)
    elif choice == "2":
        uid = input("Zadejte UID uživatele: ")
        if uid in loaded_users:
            if bank.cancel_account(loaded_users[uid], input("Číslo účtu k zrušení: ")):
                print("Účet byl zrušen.")
                bank.save_accounts_to_file(loaded_users.values())
            else:
                print("Účet nebyl zrušen.")
        else:
            print("Uživatel s tímto UID neexistuje.")
    elif choice == "3":
        if bank.transfer(input("Odesílatel(acc_num): "), input("Příjemce(acc_num): "), int(input("Částka: "))):
            print("Převod proběhl úspěšně.")
            bank.save_accounts_to_file(loaded_users.values())
        else:
            print("Převod se nezdařil.")