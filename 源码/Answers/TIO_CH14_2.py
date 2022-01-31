# TIO_CH14_2.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Answer to Try It Out Question 2 in Chapter 14


class BankAccount:
    def __init__(self, acct_number, acct_name):
        self.acct_number = acct_number
        self.acct_name = acct_name
        self.balance = 0.0

    def displayBalance(self):
        print "The account balance is:", self.balance

    def deposit(self, amount):
        self.balance = self.balance + amount
        print "You deposited", amount
        print "The new balance is:", self.balance
        
    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance = self.balance - amount
            print "You withdrew", amount
            print "The new balance is:", self.balance
        else:
            print "You tried to withdraw", amount
            print "The account balance is:", self.balance
            print "Withdrawl denied.  Not enough funds."

class InterestAccount(BankAccount):
    def addInterest(self, rate):
        interest = self.balance * rate
        print "adding interest to the account,",rate * 100,"percent"
        self.deposit (interest)
        
myAccount = InterestAccount(234567, "Warren Sande")
print "Account name:", myAccount.acct_name
print "Account number:", myAccount.acct_number
myAccount.displayBalance()
myAccount.deposit(34.52)
myAccount.addInterest(0.11)


    
