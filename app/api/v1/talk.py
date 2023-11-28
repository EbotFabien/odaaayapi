#Object Oriented Programming
#Banking Scenario Withdrawal Function

class  BankAccount:
    def __init__(self):
        self.balance = 0

    def deposit(self,amount):
        self.balance +=amount
        return self.balance
    
    def withdraw(self,amount):
        if self.balance >=amount:
            self.balance -= amount
        
        else:
            print("Insufficient balance")
        
        return self.balance
    
account =BankAccount()
account.deposit(100)
print(account.withdraw(200))
