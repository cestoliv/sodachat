import sqlite3
import uuid
import datetime
import os
import sys
import inspect
from colorama import Fore, Back, Style
import traceback

# Changed the directory to /sources, to make it easier to import locally
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

# Delete database to start from 0
if os.path.exists(f"{parentdir}/db/sodachat.db"):
    os.remove(f"{parentdir}/db/sodachat.db")

import fonctions.users as users
import fonctions.messages as messages

#######
# USERS
#######
print(Fore.YELLOW + "USERS")
print("\tsignup")
"""
    signup
"""
# Créer l'utilisateur Olivier
print(Style.RESET_ALL) 
print("\t\tCréation de l'utilisateur Olivier (cestoliv)")
try:
    olivier = users.signup("Olivier Cartier", "cestoliv", "azerty")
    if olivier["status"] == "success":
        print(Fore.GREEN + "\t\t\tRéussi !")
    else:
        print(Fore.RED + "\t\t\tRaté... " + olivier["code"])
except Exception as e:
    print(Fore.RED + "\t\t\tErreur... " + traceback.print_exc())

# Créer l'utilisateur Dorian
print(Style.RESET_ALL) 
print("\t\tCréation de l'utilisateur Dorian (dgrandfils)")
try:
    dorian = users.signup("Dorian Grandfils", "dgrandfils", "azerty")
    if dorian["status"] == "success":
        print(Fore.GREEN + "\t\t\tRéussi !")
    else:
        print(Fore.RED + "\t\t\tRaté... " + dorian["code"])
except Exception as e:
    print(Fore.RED + "\t\t\tErreur... " + traceback.print_exc())

# Créer l'utilisateur Olivia
print(Style.RESET_ALL) 
print("\t\tCréation de l'utilisateur Olivia (cestoliv) avec un identifiants déjà utilisé")
try:
    olivia = users.signup("\t\t\tOlivia ...", "cestoliv", "azerty")
    if olivia["status"] == "success":
        print(Fore.RED + "\t\t\tRaté... Censé retourner l'erreur 0001 car le nom d'utilisateur est déjà attribué.")
    else:
        if olivia["code"] == "0001":
            print(Fore.GREEN + "\t\t\tRéussi !")
        else:
            print(Fore.RED + "\t\t\tRaté... " + olivia["code"])
except Exception as e:
    print(Fore.RED + "\t\t\tErreur... " + traceback.print_exc())

"""
    signin
"""
print(Fore.YELLOW + "\tsignin")

# Connection à l'utilisateur Olivier
print(Style.RESET_ALL) 
print("\t\tConnection à l'utilisateur Olivier (cestoliv)")
try:
    olivier = users.signin("cestoliv", "azerty")
    if olivier["status"] == "success":
        print(Fore.GREEN + "\t\t\tRéussi !")
    else:
        print(Fore.RED + "\t\t\tRaté... " + olivier["code"])
except Exception as e:
    print(Fore.RED + "\t\t\tErreur... " + traceback.print_exc())

# Connection à l'utilisateur Dorian
print(Style.RESET_ALL) 
print("\t\tConnection à l'utilisateur Dorian (dgrandfils) avec un mauvais mot de passe")
try:
    dorian = users.signin("dgrandfils", "uiopqs")
    if dorian["status"] == "success":
        print(Fore.RED + "\t\t\tRaté... Censé retourner l'erreur 0001 car le mot de passe est incorrect.")
    else:
        if dorian["code"] == "0001":
            print(Fore.GREEN + "\t\t\tRéussi !")
        else:
            print(Fore.RED + "\t\t\tRaté... " + dorian["code"])
except Exception as e:
    print(Fore.RED + "\t\t\tErreur... " + traceback.print_exc())

# Connection à l'utilisateur Olivia
print(Style.RESET_ALL) 
print("\t\tConnection à l'utilisateur Olivia (olivia) qui n'existe pas")
try:
    olivia = users.signin("olivia", "azerty")
    if olivia["status"] == "success":
        print(Fore.RED + "\t\t\tRaté... Censé retourner l'erreur 0001 car le nom d'utilisateur est incorrect")
    else:
        if olivia["code"] == "0001":
            print(Fore.GREEN + "\t\t\tRéussi !")
        else:
            print(Fore.RED + "\t\t\tRaté... " + olivia["code"])
except Exception as e:
    print(Fore.RED + "\t\t\tRaté... Censé retourner l'erreur 0001 car le nom d'utilisateur est incorrect")
    print(traceback.print_exc())

# TODO :
# - get_profile
# - update_user

#######
# MESSAGES
#######
olivier = users.signin("cestoliv", "azerty")
dorian = users.signin("dgrandfils", "azerty")

print(Fore.YELLOW + "MESSAGES")
print("\tsend_message")
"""
    send_message
"""
# TODO : Erreur les utilisateurs ne sont pas en contact

# Envoi d'un message de Dorian à Olivier
print(Style.RESET_ALL) 
print("\t\tEnvoi d'un message de Dorian (dgrandfils) à Olivier (cestoliv)")
try:
    message = messages.send_message(dorian["uid"], olivier["uid"], "Yo mec, t'a pris grave de muscle la non ?")
    if message["status"] == "success":
        print(Fore.GREEN + "\t\t\tRéussi !")
    else:
        print(Fore.RED + "\t\t\tRaté... " + message["code"])
except Exception as e:
    print(Fore.RED + "\t\t\tRaté... Censé retourner un succès")
    print(traceback.print_exc())

# Envoi d'un message d'Olivier à Dorian
print(Style.RESET_ALL) 
print("\t\tEnvoi d'un message d'Olivier (cestoliv) à Dorian (dgrandfils) ")
try:
    message = messages.send_message(olivier["uid"], dorian["uid"], "Ouais je sais mec merci")
    if message["status"] == "success":
        print(Fore.GREEN + "\t\t\tRéussi !")
    else:
        print(Fore.RED + "\t\t\tRaté... " + message["code"])
except Exception as e:
    print(Fore.RED + "\t\t\tRaté... Censé retourner un succès")
    print(traceback.print_exc())


print(Fore.YELLOW + "\tget_messages")
"""
    get_messages
"""

# Récupération de la conversation entre Dorian et Olivier
print(Style.RESET_ALL) 
print("\t\tRécupération de la conversation entre Olivier (cestoliv) et Dorian (dgrandfils), les 5 dernier messages")
try:
    conv = messages.get_messages(olivier["uid"], dorian["uid"], 5, 0)
    if message["status"] == "success":
        print(Fore.GREEN + "\t\t\tRéussi !")
        print("\t\t\t" + str(conv))
    else:
        print(Fore.RED + "\t\t\tRaté... " + message["code"])
except Exception as e:
    print(Fore.RED + "\t\t\tRaté... Censé retourner un succès")
    print(traceback.print_exc())


print(Fore.YELLOW + "\tset_messages_seen")
"""
    set_messages_seen
"""

# Mettre le dernier message de la conversation Olivier - Dorian en vu
print(Style.RESET_ALL) 
print("\t\tMise du dernier message de la conversation entre Olivier (cestoliv) et Dorian (dgrandfils) en vu")
try:
    conv = messages.get_messages(dorian["uid"], olivier["uid"], 1, 0)
    if message["status"] == "success":
        if len(conv["messages"]) == 1:
            message_to_see = conv["messages"][0]
            if(message_to_see["seen"] == 1):
                print(Fore.RED + "\t\t\tRaté... Le dernier message est déjà en vu")
            else:
                seen = messages.set_messages_seen([message_to_see["id"]])

                if seen["status"] == "success":
                    print(Fore.GREEN + "\t\t\t Réussi !")
                else:
                    print(Fore.RED + "\t\t\tRaté... " + seen["code"])
        else:
            print(Fore.RED + "\t\t\tRaté... Aucun message dans la conversation")
    else:
        print(Fore.RED + "\t\t\tRaté... (lors de la récupération des messages) " + message["code"])
except Exception as e:
    print(Fore.RED + "\t\t\tRaté... Censé retourner un succès")
    print(traceback.print_exc())