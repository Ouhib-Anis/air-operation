import sys
import sqlite3
import re
import os
import pandas as pd
from databases  import afficher_rapports
from databases  import afficher_evenements_et_plans
from KPI import CabinOperationsKPI, FlightDispatchersKPI, FlightOperationsKPI
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton,
                             QListWidget,
                             QLineEdit, QMessageBox, QDialog, QInputDialog, QTextEdit, QTableWidget, QTableWidgetItem,
                             QGridLayout, QGraphicsDropShadowEffect, QHBoxLayout, QFrame)
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtCore import Qt
from tabulate import tabulate

class MatrixDialog(QDialog):
    def __init__(self, dataframe, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Matrice des Risques")
        self.setGeometry(200, 200, 800, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.table = QTableWidget()
        self.table.setRowCount(len(dataframe))
        self.table.setColumnCount(len(dataframe.columns))
        self.table.setHorizontalHeaderLabels(dataframe.columns)

        
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: black;
                color: white;
            }
        """)

        self.layout.addWidget(self.table)

        # Remplir la table avec les données et appliquer la coloration conditionnelle
        for row in range(len(dataframe)):
            for col in range(len(dataframe.columns)):
                value = dataframe.iloc[row, col]
                item = QTableWidgetItem(str(value))

                # Si la colonne est 'grave_proba', appliquer la coloration conditionnelle
                if dataframe.columns[col] == 'grave_proba':
                    if value <= 5:
                        item.setBackground(QColor('green'))
                    elif 5 < value <= 12:
                        item.setBackground(QColor('yellow'))
                    elif 12 < value <= 18:
                        item.setBackground(QColor('orange'))
                    elif 18 < value <= 25:
                        item.setBackground(QColor('red'))

                self.table.setItem(row, col, item)

class ReportDialog(QDialog):
    def __init__(self, conn=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rapports")
        self.setGeometry(150, 150, 600, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.list_widget)

        self.conn = conn
        if self.conn is not None:
            afficher_rapports(self.conn, self.list_widget)
        else:
            print("Aucune connexion fournie.")
class EventDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Événements et Plans d'Action")
        self.setGeometry(150, 150, 800, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.list_widget)

        self.combobox = QComboBox()
        self.combobox.setFont(QFont("Arial", 14))
        self.layout.addWidget(self.combobox)
        self.combobox.currentIndexChanged.connect(self.on_combobox_changed)

        self.conn = conn  # Stockez la connexion passée
        self.load_activites()  # Chargez les activités

    def load_activites(self):
        # Utilisez self.conn directement au lieu de self.parent().conn
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, nom FROM activites')
        activites = cursor.fetchall()
        for activite in activites:
            self.combobox.addItem(activite[1], activite[0])

    def on_combobox_changed(self):
        activite_id = self.combobox.currentData()
        afficher_evenements_et_plans(self.conn, activite_id, self.list_widget)

class KPIDialog(QDialog):
    def __init__(self, flight_ops_kpi, flight_dispatchers_kpi, cabin_ops_kpi, parent=None):
        super().__init__(parent)
        self.setWindowTitle('KPIs')
        layout = QVBoxLayout()

        # Ajouter des labels pour chaque KPI
        layout.addWidget(QLabel("KPIs pour les Opérations de Vol :"))
        layout.addWidget(QLabel(flight_ops_kpi.to_string()))

        layout.addWidget(QLabel("KPIs pour les Dispatchers de Vol :"))
        layout.addWidget(QLabel(flight_dispatchers_kpi.to_string()))

        layout.addWidget(QLabel("KPIs pour les Opérations de Cabine :"))
        layout.addWidget(QLabel(cabin_ops_kpi.to_string()))

        # Ajouter un bouton pour fermer la boîte de dialogue
        close_button = QPushButton('Close')
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)
        
class AddActionPlanDialog(QDialog):
    def __init__(self, danger_id, parent=None):
        super().__init__(parent)
        self.danger_id = danger_id
        self.setWindowTitle("Ajouter un Plan d'Action")
        self.setGeometry(150, 150, 600, 400)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Ajoutez les widgets de la boîte de dialogue
        self.objectif_edit = QLineEdit()
        self.objectif_edit.setPlaceholderText("Objectif du plan d'action")
        self.layout.addWidget(self.objectif_edit)

        self.actions_specifiques_edit = QLineEdit()
        self.actions_specifiques_edit.setPlaceholderText("Actions spécifiques")
        self.layout.addWidget(self.actions_specifiques_edit)

        self.responsables_edit = QLineEdit()
        self.responsables_edit.setPlaceholderText("Responsables")
        self.layout.addWidget(self.responsables_edit)

        self.ressources_necessaires_edit = QLineEdit()
        self.ressources_necessaires_edit.setPlaceholderText("Ressources nécessaires")
        self.layout.addWidget(self.ressources_necessaires_edit)

        self.calendrier_edit = QLineEdit()
        self.calendrier_edit.setPlaceholderText("Calendrier")
        self.layout.addWidget(self.calendrier_edit)

        self.efficacite_edit = QLineEdit()
        self.efficacite_edit.setPlaceholderText("Efficacité")
        self.layout.addWidget(self.efficacite_edit)

        self.submit_button = QPushButton("Ajouter")
        self.submit_button.clicked.connect(self.on_submit)
        self.layout.addWidget(self.submit_button)

    def on_submit(self):
    # Récupération des valeurs des champs
        objectif = self.objectif_edit.text()
        actions_specifiques = self.actions_specifiques_edit.text()
        responsables = self.responsables_edit.text()
        ressources_necessaires = self.ressources_necessaires_edit.text()
        calendrier = self.calendrier_edit.text()
        efficacite = self.efficacite_edit.text()

        # Validation des champs
        if not all([objectif, actions_specifiques, responsables, ressources_necessaires, calendrier, efficacite]):
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis.")
            return
        try:
        # Insertion dans la base de données
            cursor = self.parent().conn.cursor()
            query = '''
            INSERT INTO plans_action 
            (danger_id, objectif, actions_specifiques, responsables, ressources_necessaires, calendrier, efficacite)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            values = (
            self.danger_id, objectif, actions_specifiques, responsables,
            ressources_necessaires, calendrier, efficacite
            )
            cursor.execute(query, values)
            self.parent().conn.commit()

            # Message de confirmation
            QMessageBox.information(self, "Succès", "Plan d'action ajouté avec succès.")
            self.accept()
        except Exception as e:
        # Gestion des erreurs
            QMessageBox.warning(self, "Erreur", f"Erreur lors de l'ajout du plan d'action : {str(e)}")