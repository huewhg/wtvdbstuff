
import os, sys, subprocess, importlib.util
for mod, pkg in [("fuzzywuzzy","fuzzywuzzy"), ("sqlalchemy","SQLAlchemy")]:
    if importlib.util.find_spec(mod) is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
from fuzzywuzzy import fuzz
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from getpass import getpass
import hashlib, os
from datetime import datetime

engine = create_engine('sqlite:///users.db', echo=False)
Base = declarative_base()
UID = 0
UNAME = ""
class User(Base):
    __tablename__ = 'Users'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String, nullable=False)
    Hash = Column(String, nullable=False)
class Item(Base):
    __tablename__ = 'Items'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String, nullable=False)
    Price = Column(Integer, nullable=True)
    Shop = Column(String, nullable=True)
    Brand = Column(String, nullable=True)
    AddedBy = Column(Integer, nullable=False)
class Done(Base):
    __tablename__ = 'Dones'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String, nullable=False)
    Price = Column(Integer, nullable=True)
    Shop = Column(String, nullable=True)
    Brand = Column(String, nullable=True)
    AddedBy = Column(Integer, nullable=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
DEBUG = False

def logon():
    while True:
        cls()
        is_int = False
        all_users = session.query(User).all()
        max = 1
        for user in all_users:
            print(f"{user.ID}) {user.Name}")
            if user.ID > max:
                max = user.ID
        if len(all_users) == 0:
            print("Please, create a user.")
            new_user()
        else:
            choice = input(f"Choose user to log in to by ID (1-{max}). If you want to create a new user, input \"n\". If you want to exit the aplication, input \"e\". ")
            if choice.lower().strip() == "n":
                new_user()
            elif choice.lower().strip() == "e":
                exit()
            else:
                try:
                    choice = int(choice.strip())
                    is_int = True
                except:
                    print("Invalid input!")
                    is_int = False
                if is_int:
                    log, user = checkPWD(choice, all_users)
                    if log:
                        print(f"Logging in {user.Name}")
                        return user.ID, user.Name

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')
def checkPWD(UID, users):
    for i in users:
        if i.ID == UID:
            while True:
                password = getpass(f"Input password for {i.Name}. Enter nothing if you want to log in to a different account.")
                if password == "":
                    return False, i
                elif hashlib.sha256(password.encode('utf-8')).hexdigest() == i.Hash:
                    print("Correct password!")
                    return True, i
                else:
                    print("Incorrect password!")
def new_user():
    name = input("Input new user username: ")
    password = "Huewhg"
    confirm = "is love"
    while password != confirm:
        password = getpass("Input password for new user.")
        confirm = getpass("Confirm password for new user.")
        if password != confirm:
            print("\nPassword doesn't match confirmation. Try again.\n")
    
    new_user = User(Name=name, Hash=hashlib.sha256(password.encode('utf-8')).hexdigest())
    password = "Huewhg"
    confirm = "is love"
    session.add(new_user)
    session.commit()
    print(f"Added {name} as a new user!")
def list_grocs(Item, session, out = True, wait = True):
    if out:
        cls()
    all_Items = session.query(Item).all()
    max = 1
    for item in all_Items:
        if out:
            print(f"{item.ID}) {item.Name} ", end = "")
            if item.Price:
                print(f"{item.Price}CZK, ", end= "")
            if item.Shop:
                print(f"From: {item.Shop}, ", end = "")
            if item.Brand:
                print(f"By: {item.Brand},", end = "")
            addedname = session.query(User) \
                    .filter(User.ID == item.AddedBy) \
                    .one()
            print(f" Added by: {addedname.Name}")
        if item.ID > max:
            max = item.ID
    if wait:
        input("Press enter to return.")
    return max
def AddItem(UID, Item, session):
    name = input("Input new item name: ").strip()
    price = None
    while True:
        price = input("Price (enter if none/unknown): ")
        if not price:
            break
        else:
            price = price.strip()
            try:
                price = int(price)
                break
            except:
                print("Invalid format!")
    shop = input("Shop (enter if none/unknown): ")
    if not shop:
        shop = None
    brand = input("Brand (enter if none/unknown): ")
    if not brand:
        brand = None
                
    new_item = Item(Name=name, Price = price, Shop = shop, Brand = brand, AddedBy = UID)
    session.add(new_item)
    session.commit()

def Mark_Done(Item, Done, session, DEBUG, list_grocs):
    list_grocs(Item, session, wait=False)
    while True:
        rem = input("Select which item has been bought (enter to return): ")
        rem = rem.strip()
        if not rem:
            return
        else:
            try:
                rem = int(rem)
                item = session.query(Item).get(rem)
                break
            except Exception as e:
                print("Invalid format!")
                if DEBUG:
                    print(e)
                
    session.add(Done(
                    Name=item.Name, Price = item.Price, Shop = item.Shop, Brand = item.Brand, AddedBy = item.AddedBy
                ))
    session.delete(item)
    session.commit()

while True:
    
    UID, UNAME = logon()
    if UID != None and UNAME != None:
        while True:
            cls()
            now_str = datetime.now().strftime("%d.%m. %Y %H:%M:%S")
            action = input(
                f"User {UNAME} — {now_str}\n"
                "Enter:\n"
                "1) Inspect grocery list\n"
                "2) Search grocery list\n"
                "3) Add to grocery list\n"
                "4) Mark as Done\n"
                "5) Look through archives \n"
                "6) Log Out\n"
            )
            action = action.lower().strip()
            if action == "1":
                list_grocs(Item, session)
            elif action == "2":
                all_Items = session.query(Item).all()
                search = input("Insert text to search: " )
                its = {}
                for i in all_Items:
                    sim = fuzz.ratio(search.lower(), i.Name.lower())
                    if DEBUG:
                        print(sim)
                    its.update({i.ID: sim})
                if DEBUG:
                    print(its)
                sorted_items = sorted(its.items(), key=lambda kv: kv[1], reverse=True)
                if DEBUG:
                    print(sorted_items)
                cls()
                for idx in range(min(3, len(sorted_items))):
                    item_id, _ = sorted_items[idx]
                    item = session.get(Item, item_id)

                    print(f"{idx + 1}) {item.Name} ", end="")
                    if item.Price:
                        print(f"{item.Price}CZK, ", end="")
                    if item.Shop:
                        print(f"From: {item.Shop}, ", end="")
                    if item.Brand:
                        print(f"By: {item.Brand},", end="")
                    addedname = session.query(User) \
                            .filter(User.ID == item.AddedBy) \
                            .one()
                    print(f" Added by: {addedname.Name}")
                input()
                    
            elif action == "3":
                AddItem(UID, Item, session)
            elif action == "4":
                Mark_Done(Item, Done, session, DEBUG, list_grocs)
            elif action == "5":
                list_grocs(Done, session)
            elif action == "6":
                UID = None
                UNAME = None
                break
#print(f"{UID} - {UNAME}")
session.close()
