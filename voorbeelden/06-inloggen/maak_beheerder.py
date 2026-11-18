import getpass

import bcrypt

import database

database.start()

naam = input("Naam: ")
email = input("E-mail: ")
wachtwoord = getpass.getpass("Wachtwoord: ")
if len(wachtwoord) < 8:
    print("Kies een wachtwoord van minstens 8 tekens.")
else:
    wachtwoord_hash = bcrypt.hashpw(wachtwoord.encode(), bcrypt.gensalt()).decode()
    if database.voeg_beheerder_toe(naam, email, wachtwoord_hash) is None:
        print("Dit e-mailadres bestaat al.")
    else:
        print("Beheerder bewaard.")
