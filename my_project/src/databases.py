import sys
import sqlite3
import re
import os
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton,
                             QListWidget,
                             QLineEdit, QMessageBox, QDialog, QInputDialog, QTextEdit, QTableWidget, QTableWidgetItem,
                             QGridLayout, QGraphicsDropShadowEffect, QHBoxLayout, QFrame)
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtCore import Qt
from tabulate import tabulate
from PyQt5.QtWidgets import QListWidgetItem

# Connexion à la base de données
def connect_db(db_name='mydatabases.db'):
    return sqlite3.connect(db_name)
conn = connect_db()

# Création des tables
def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS activites
                    (id INTEGER PRIMARY KEY, nom TEXT UNIQUE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS dangers
                    (id INTEGER PRIMARY KEY,
                    activite_id INTEGER,
                    description TEXT,
                    probabilite TEXT,
                    gravite INTEGER,
                    FOREIGN KEY(activite_id) REFERENCES activites(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS plans_action
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    danger_id INTEGER,
                    objectif TEXT,
                    actions_specifiques TEXT,
                    responsables TEXT,
                    ressources_necessaires TEXT,
                    calendrier TEXT,
                    efficacite TEXT,
                    FOREIGN KEY(danger_id) REFERENCES dangers(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS rapports
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titre TEXT,
                    contenu TEXT,
                    date TEXT)''')
    conn.commit()
    create_tables(conn)

# Insertion des données initiales
def insert_initial_data(conn):
    activites_et_dangers = [
        (1017, 'Flight Operations', [
            ('Abusive use of reverse', 'A', 4),
            ('Cooling time not respected', 'B', 3),
            ('Cross Wind T/O/LDG', 'A', 5),
            ('Dépassement d’amplitude de service de vol', 'C', 2),
            ('Documents/Manuels de bord erroné, non à jour,incomplets,détériorés ou format inadapté', 'C', 2),
            ('Erreur d’insertion des données FMC', 'B', 4),
            ('Déviation Mineure de la Route de Vol', 'D', 1),
            ('Perte Totale de Propulsion en Vol', 'A', 1),
            ('Turbulences Modérées à Sévères', 'B', 5),
            ('Flight Crew Incapacitation', 'D', 5),
            ('Hard Landing', 'C', 4),
            ('Overweight at Landing', 'E', 4),
            ('Speed exceedance MMO/VMO/clackers alarm', 'C', 3),
            ('Unstabilized Approach', 'A', 4)
        ]),
        (2200, 'Dispatcher', [
            ('Absence or lack of flight tracking', 'A', 4),
            ('Déroutement (météo, NOTAM, Perfo...)', 'A', 3),
            ('Dossier MTO incomplet, incorrect ou obsolète', 'B', 2),
            ('Erreur plan de vol ATC', 'C', 3),
            ('Changement de Dernière Minute dans les Autorisations de Vol', 'E', 5),
            ('Erreur dans les Calculs de Performance', 'E', 1),
            ('Communication Incorrecte avec l\'Équipage de Vol', 'C', 1),
            ('Erreur de Planification de Vol', 'D', 3),
            ('Erreur plan de vol OFP (Route, rubrique fuel...)', 'C', 2),
            ('Non réalisation d\'une étude de faisabilité d\'un vol (type d\'A/C, moyens d\'assistance...)', 'A', 3),
            ('NOTAM incorrect et/ou incomplet', 'C', 2),
            ('Obstacle dans la trouée d\'envol', 'C', 4),
            ('Erreur masse et centrage', 'C', 4)
        ]),
        (2021, 'Cabine', [
            ('Cabin Fire/ Fumes/Smoke', 'D', 5),
            ('Cabin lavatory smoke', 'D', 4),
            ('Chargement CATERING non conforme', 'A', 2),
            ('Event involving Portable Electronic Device (Lithium Battery)', 'B', 4),
            ('Passager malade/ blessé', 'A', 3),
            ('Un incendie dans la cabine','B' ,1),
            ('Trolley non conforme', 'A', 2),
            ('Une lumière de lecture qui ne fonctionne pas', 'E', 3),
            ('Des turbulences légères provoquant des secousses régulières dans la cabine', 'C', 5),
            ('Dysfonctionnement de l\'Éclairage de la Cabine', 'D', 1),
            ('Une légère égratignure sur un siège', 'E', 2),
            ('Passagers indisciplinés', 'A', 2)
        ])
    ]

    cursor = conn.cursor()
    for activite_id, activite, dangers in activites_et_dangers:
        cursor.execute('INSERT OR IGNORE INTO activites (id, nom) VALUES (?, ?)', (activite_id, activite))
        cursor.executemany('INSERT INTO dangers (activite_id, description, probabilite, gravite) VALUES (:activite_id, :description, :probabilite, :gravite)',
                           [{'activite_id': activite_id, 'description': danger[0], 'probabilite': danger[1], 'gravite': danger[2]} for danger in dangers])
    conn.commit()
    insert_initial_data(conn)

# Ajout de nouveaux dangers
def ajouter_danger(conn, activite_id, description, probabilite, gravite):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO dangers (activite_id, description, probabilite, gravite) VALUES (?, ?, ?, ?)',
                   (activite_id, description, probabilite, gravite))
    conn.commit()

# Insertion automatique des rapports
def inserer_rapports(conn, dossier_rapports='C:/Users/COMPOS/Desktop/app/my_project/Rapport'):
    cursor = conn.cursor()
    for fichier in os.listdir(dossier_rapports):
        if fichier.endswith('.txt'):
            chemin_fichier = os.path.join(dossier_rapports, fichier)
            with open(chemin_fichier, 'r', encoding='utf-8') as f:
                contenu = f.read()
                titre = os.path.splitext(fichier)[0]
                date = '2024-01-01'  # Remplacer par une méthode pour extraire la date si disponible
                cursor.execute('INSERT INTO rapports (titre, contenu, date) VALUES (?, ?, ?)', (titre, contenu, date))
    conn.commit()

# Fonction pour afficher les rapports
def afficher_rapports(conn, widget):
    cursor = conn.cursor()
    cursor.execute('SELECT titre, contenu FROM rapports')
    rapports = cursor.fetchall()
    widget.clear()
    for titre, contenu in rapports:
        widget.addItem(f"{titre}: {contenu[:100]}...")  # Affiche un aperçu du contenu

def afficher_evenements_et_plans(conn, activite_id, list_widget):
    cursor = conn.cursor()

    # Sélectionner les événements pour l'activité spécifiée
    cursor.execute('SELECT id, description FROM events WHERE activite_id = ?', (activite_id,))
    events = cursor.fetchall()

    list_widget.clear()

    for event in events:
        # Ajouter l'événement à la liste
        item_text = f"Événement: {event[1]}\nID: {event[0]}"
        item = QListWidgetItem(item_text)
        list_widget.addItem(item)
        
        # Sélectionner les plans d'action associés à cet événement
        cursor.execute('SELECT objectif, actions_specifiques, responsables, ressources_necessaires, calendrier, efficacite FROM plans_action WHERE danger_id = ?', (event[0],))
        plans = cursor.fetchall()
        
        if plans:
            for plan in plans:
                plan_text = (f"  Objectif: {plan[0]}\n"
                             f"  Actions spécifiques: {plan[1]}\n"
                             f"  Responsables: {plan[2]}\n"
                             f"  Ressources nécessaires: {plan[3]}\n"
                             f"  Calendrier: {plan[4]}\n"
                             f"  Efficacité: {plan[5]}")
                plan_item = QListWidgetItem(plan_text)
                plan_item.setForeground(Qt.gray)  # Optionnel: changer la couleur du texte des plans d'action
                list_widget.addItem(plan_item)



#génirer la matrice des risque

def generer_matrice_risques(conn):
    # Création d'un dictionnaire pour convertir les lettres en valeurs numériques
    probabilité_mapping = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1}

    cursor = conn.cursor()
    cursor.execute('SELECT nom FROM activites')
    activites = cursor.fetchall()
    
    data = []
    
    for activite in activites:
        activite_nom = activite[0]
        cursor.execute('SELECT description, probabilite, gravite FROM dangers WHERE activite_id IN (SELECT id FROM activites WHERE nom = ?)', (activite_nom,))
        dangers = cursor.fetchall()
        
        for danger in dangers:
            description, probabilité, gravité = danger
            # Convertir probabilité en valeur numérique
            probabilité_numérique = probabilité_mapping.get(probabilité, 0)
            # Calculer grave_proba
            grave_proba = probabilité_numérique * gravité
            # Ajouter les données dans la liste
            data.append({
                'Activité': activite_nom,
                'Danger': description,
                'Probabilité': probabilité,
                'Gravité': gravité,
                'grave_proba': grave_proba
            })
    
    # Convertir la liste de dictionnaires en DataFrame
    df = pd.DataFrame(data)
    return df
