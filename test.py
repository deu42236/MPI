import json #načítání a ukladání do jsónu
import time #pojmenovávaní souboru
import os #na hledání nejnovějšího ledgeru (jsón)
"""
https://streamable.com/8mek3u?t=45
"""
#bonus za založení účtu:
bonus = 500 
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

class ClassicAccount(Account):
    def __init__(self, acc_number, uid, balance):
        super().__init__(acc_number, uid, balance+bonus) #prakticky inicializace __init__ parenta (Account)

class SavingsAccount(Account):
    def __init__(self, acc_number, uid, balance, apy):
        super().__init__(acc_number, uid, balance) #prakticky inicializace __init__ parenta (Account)
        self.apy = apy

class User:
    def __init__(self, name, uid, password):
        self.name = name
        self.uid = uid
        self.password = password
        self.accounts = []

    def create_account(self, account_type, bank):
        new_acc_number = bank.generate_account_number() # Bank handles account number generation
        if account_type == "classic":
            new_account = ClassicAccount(new_acc_number, self.uid, 0)
        elif account_type == "savings":
            new_account = SavingsAccount(new_acc_number, self.uid, 0, 0.01) # random APY (Annual percentage yield), třeba 0.01, tedy 1%
        else:
            return "Invalid account type"
        
        self.accounts.append(new_account.acc_number)
        bank.all_accounts[new_acc_number] = new_account
        return new_account
    
    def get_balance(self, account_number):
        for acc_num in self.accounts:
            if acc_num == account_number:
                return bank.all_accounts[acc_num].get_balance()
        return "Account not found for this user."

class Bank:
    def __init__(self):
        self.all_accounts = {}
        self.next_account_number = 1  # Simple account number generation

    def generate_account_number(self):
        acc_num = str(self.next_account_number).zfill(6) # nahazi nuly na zacatku aby to melo X (tady 6) cifer
        self.next_account_number += 1
        return acc_num

    def create_account(self, user, account_type):
        new_acc_number = self.generate_account_number()
        if account_type == "classic":
            new_account = ClassicAccount(new_acc_number, user.uid, 0)
        elif account_type == "savings":
            new_account = SavingsAccount(new_acc_number, user.uid, 0, 0.01) # random APY (Annual percentage yield), třeba 0.01, tedy 1%
        else:
            return "Invalid account type"
        self.all_accounts[new_acc_number] = new_account
        user.accounts.append(new_acc_number)
        return new_account

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

    def save_accounts_to_file(self):
    #by default to pojmenuje podle aktualniho casu, pokud neni definovano jinak (je to prostě nepovinej argument)
    #(je to hnusný ale nevim jak to jinak udělat :D)
        with open("accounts.json", 'w') as file:
            json.dump(self.all_accounts, file, default=lambda o: o.__dict__, indent=4) #zapíše output self.all_accounts (bank.all_accounts) do souboru, indent 4 je jen pro přehlednost 
            
    def load_accounts_from_file(self):
        with open("accounts.json", 'r') as file:
            accounts_data = json.load(file)
            for acc_num, acc_data in accounts_data.items():
                if 'apy' in acc_data:
                    account = SavingsAccount(acc_data['acc_number'], acc_data['uid'], acc_data['balance'], acc_data['apy'])
                else:
                    account = ClassicAccount(acc_data['acc_number'], acc_data['uid'], acc_data['balance'] - bonus)
                self.all_accounts[acc_num] = account





##### TEST HERE
bank = Bank()
user1 = User("Alice", "A123", "heslo")
user2 = User("Bob", "B456", "hovnoKleslo")
classic_acc1 = user1.create_account("classic", bank)
savings_acc1 = user1.create_account("savings", bank)
classic_acc2 = bank.create_account(user2, "classic")

# print(f"Classic account 1 ({user1.name}) number: {classic_acc1.acc_number}")
# print(f"Savings account 1 ({user1.name}) number: {savings_acc1.acc_number}")
# print(f"Classic account 2 ({user2.name}) number: {classic_acc2.acc_number}")

# bank.transfer(classic_acc1.acc_number, savings_acc1.acc_number, 50)
# print(f"Classic account 1 balance: {bank.all_accounts[classic_acc1.acc_number].get_balance()}")
# print(f"Savings account 1 balance: {bank.all_accounts[savings_acc1.acc_number].get_balance()}")

# print(user1.get_balance(classic_acc1.acc_number))

bank.save_accounts_to_file()
bank.cancel_account(user1, classic_acc1.acc_number)
# print(user1.accounts)
# print(bank.all_accounts)
bank.save_accounts_to_file()
print(bank.all_accounts)


directory = '.'  # Aktuální adresář







#ADMIN PANEL ZAČÁTEK
print("Seznam úkonů: \n1. Vytvořit účet\n2. Zrušit účet\n3. Převod mezi účty\n4. Uložit účty do souboru")
user_input = input("input:")
if user_input == "1":
    print("Vytvoření účtu: \n1. Classic\n2. Savings")
    if input("input:") == "1":
        print("Vytvoření účtu Classic")
        print(user1.create_account("classic", bank))
        bank.save_accounts_to_file()
        print("ok")
    else:
        print("Vytvoření účtu Savings")
        print(user1.create_account("savings", bank))
        bank.save_accounts_to_file()
elif user_input == "2":
    print("Zrušení účtu: ")
    print(bank.cancel_account(user1, input("Zadejte číslo účtu: ")))
elif user_input == "3":
    print("Převod mezi účty: ")
    print(bank.transfer(input("Zadejte číslo účtu odesílatele: "), input("Zadejte číslo účtu příjemce: "), input("Zadejte částku: ")))
elif user_input == "4":
    print("Uložení účtů do souboru: ")
    bank.save_accounts_to_file()


print(bank.all_accounts)