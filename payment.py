
loic=5000
aime=8000
amount=1550
ask=int(input("pay your ticket: "))
while (ask<amount):
    ask=int(input("pay your ticket: "))
    if (ask>amount):
        names=input("what is your name:")
        if(names=="loic"):
            loic=loic-amount
            print(f"your balance is {names}:{loic}")
if (ask == amount):
    names=input("your name please: ")
    if(names=="aime"):
        aime=aime-amount
        print(f"your balance is {names}:{aime}")
