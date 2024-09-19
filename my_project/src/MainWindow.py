import sys
import sqlite3
import re
import os
import pandas as pd
from databases import connect_db, inserer_rapports, afficher_evenements_et_plans, generer_matrice_risques,inserer_rapports,afficher_rapports,ajouter_danger
from dialog import MatrixDialog, ReportDialog, EventDialog, KPIDialog, AddActionPlanDialog
from KPI import CabinOperationsKPI, FlightDispatchersKPI, FlightOperationsKPI
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton,
                             QListWidget, QLineEdit, QMessageBox, QDialog, QInputDialog, QTextEdit, QTableWidget, 
                             QTableWidgetItem, QGridLayout, QGraphicsDropShadowEffect, QHBoxLayout, QFrame)
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QDialog, QLineEdit, QSpinBox, QPushButton, QVBoxLayout, QLabel, QMessageBox, QFormLayout


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OPS RISQ MANAGER")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #2C3E50; color: #ECF0F1;")  # Couleurs modernes

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout principal
        main_layout = QVBoxLayout(self.central_widget)

        # Ajout du titre "Welcome to OPS RISQ MANAGER" en haut
        self.title_label = QLabel("Welcome to Ops Risk Manager")
        self.title_label.setFont(QFont("Arial", 40, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #ECF0F1; margin-top: 30px;")

        # Effet d'ombre pour le titre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 0)
        self.title_label.setGraphicsEffect(shadow)

        main_layout.addWidget(self.title_label)

        # Layout principal horizontal pour diviser les activités et les boutons
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Création de la barre latérale pour les boutons à gauche
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #34495E;")
        sidebar.setFixedWidth(250)

        # Layout pour les boutons de la barre latérale
        sidebar_layout = QVBoxLayout(sidebar)

        # Ajout des boutons à la barre latérale
        button_style = """
        QPushButton {
            background-color: #2980B9;
            color: #ECF0F1;
            font-size: 14px;
            border-radius: 5px;
            padding: 10px;
            margin: 5px;
        }
        QPushButton:hover {
            background-color: #3498DB;
        }
        QPushButton:pressed {
            background-color: #1F618D;
        }
        """

        self.button_add_danger = QPushButton("Add event")
        self.button_add_danger.setStyleSheet(button_style)
        sidebar_layout.addWidget(self.button_add_danger)

        self.button_add_action_plan = QPushButton("Add action plan")
        self.button_add_action_plan.setStyleSheet(button_style)
        sidebar_layout.addWidget(self.button_add_action_plan)

        self.button_view_matrix = QPushButton("Risk matrix")
        self.button_view_matrix.setStyleSheet(button_style)
        sidebar_layout.addWidget(self.button_view_matrix)

        self.button_view_reports = QPushButton("Rapports")
        self.button_view_reports.setStyleSheet(button_style)
        sidebar_layout.addWidget(self.button_view_reports)

        self.button_view_events = QPushButton("Show event and action plan")
        self.button_view_events.setStyleSheet(button_style)
        sidebar_layout.addWidget(self.button_view_events)

        self.button_show_kpi = QPushButton("Show KPI")
        self.button_show_kpi.setStyleSheet(button_style)
        sidebar_layout.addWidget(self.button_show_kpi)

        self.button_show_graphs = QPushButton('Show Graphs')
        self.button_show_graphs.setStyleSheet(button_style)
        sidebar_layout.addWidget(self.button_show_graphs)

        sidebar_layout.addStretch()  # Pour pousser les boutons vers le haut

        content_layout.addWidget(sidebar)

        # Section des activités au centre
        activity_layout = QVBoxLayout()

        self.label = QLabel("Sélectionnez une activité :")
        self.label.setFont(QFont("Arial", 16))
        self.label.setStyleSheet("color: #ECF0F1;")
        activity_layout.addWidget(self.label)

        self.combobox = QComboBox()
        self.combobox.setFont(QFont("Arial", 14))
        self.combobox.setStyleSheet("padding: 5px;")
        activity_layout.addWidget(self.combobox)

        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Arial", 12))
        self.list_widget.setStyleSheet("background-color: #ECF0F1; color: #2C3E50;")
        activity_layout.addWidget(self.list_widget)

        content_layout.addLayout(activity_layout)

        # Connexions des boutons
        self.combobox.currentIndexChanged.connect(self.on_combobox_changed)
        self.button_add_danger.clicked.connect(self.on_add_danger_clicked)
        self.button_add_action_plan.clicked.connect(self.on_add_action_plan_clicked)
        self.button_view_matrix.clicked.connect(self.on_view_matrix_clicked)
        self.button_view_reports.clicked.connect(self.on_view_reports_clicked)
        self.button_view_events.clicked.connect(self.on_view_events_clicked)
        self.button_show_kpi.clicked.connect(self.on_show_kpi_clicked)
        self.button_show_graphs.clicked.connect(self.on_show_graphs_clicked)

        # Initialisation de la connexion à la base de données
        try:
            self.conn = sqlite3.connect('C:/Users/COMPOS/Desktop/app/my_project/data/mydatabases.db')
            inserer_rapports(self.conn)  # Insère les rapports automatiquement lors du démarrage
            self.populate_combobox()
        except sqlite3.Error as e:
            print(f"Erreur lors de la connexion à la base de données : {e}")
            self.conn = None

    def populate_combobox(self):
        if self.conn is None:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, nom FROM activites')
            activites = cursor.fetchall()
            for activite in activites:
                self.combobox.addItem(activite[1], activite[0])
        except sqlite3.Error as e:
            print(f"Erreur lors de l'extraction des activités : {e}")

    def on_combobox_changed(self):
        if self.conn is None:
            return
        self.list_widget.clear()
        activite_id = self.combobox.currentData()
        if activite_id is None:
            return

        events = afficher_evenements_et_plans(self.conn, activite_id, self.list_widget)

        if events is None:
            return

        for event in events:
            item = QListWidgetItem(event[1])  # Description de l'événement (index 1)
            item.setData(Qt.UserRole, event[0])  # Stocker l'ID dans les données de l'élément (index 0)
            self.list_widget.addItem(item)

    def on_add_danger_clicked(self):
    # Récupérer l'ID de l'activité sélectionnée
     activite_id = self.combobox.currentData()
     if activite_id is None:
        QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une activité.")
        return

    # Obtenir la description du danger
     description, ok1 = QInputDialog.getText(self, "Description du danger", "Entrez la description du danger :")
     if not ok1 or not description:
        QMessageBox.warning(self, "Erreur", "La description du danger est requise.")
        return

    # Obtenir la probabilité du danger
     probabilite, ok2 = QInputDialog.getText(self, "Probabilité", "Entrez la probabilité (A, B, C, D, E) :")
     if not ok2 or not probabilite:
        QMessageBox.warning(self, "Erreur", "La probabilité du danger est requise.")
        return

    # Obtenir la gravité du danger
     gravite, ok3 = QInputDialog.getInt(self, "Gravité", "Entrez la gravité (1 à 5) :", min=1, max=5)
     if not ok3:
        QMessageBox.warning(self, "Erreur", "La gravité du danger est requise.")
        return

     try:
        # Ajouter le danger dans la base de données
        ajouter_danger(self.conn, activite_id, description, probabilite, gravite)

        # Afficher un message de succès
        QMessageBox.information(self, "Succès", "Le danger a été ajouté avec succès.")

        # Mettre à jour la liste des dangers
        self.on_combobox_changed()
     except Exception as e:
        # En cas d'erreur lors de l'ajout dans la base de données
        QMessageBox.critical(self, "Erreur", f"Une erreur est survenue lors de l'ajout du danger : {e}")

    def on_add_action_plan_clicked(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un évènement.")
            return

        item_text = selected_items[0].text()
        print(f"Texte de l'événement sélectionné: {item_text}")

        if "ID:" in item_text:
            try:
                danger_id = int(item_text.split("ID:")[1].strip())
                print(f"ID du danger extrait: {danger_id}")
            except ValueError:
                QMessageBox.warning(self, "Erreur", "ID du danger est mal formaté dans le texte de l'événement.")
                return
        else:
            QMessageBox.warning(self, "Erreur", "ID du danger non trouvé dans le texte de l'événement.")
            return

        # Ouvrir la boîte de dialogue pour ajouter le plan d'action
        self.add_action_plan_dialog = AddActionPlanDialog(danger_id, self)
        self.add_action_plan_dialog.exec_()

    def on_view_matrix_clicked(self):
        matrice_risques = generer_matrice_risques(self.conn)
        # Assuming generer_matrice_risques returns a DataFrame, integrate it here.
        self.matrix_dialog = MatrixDialog(matrice_risques, self)
        self.matrix_dialog.exec_()

    def on_view_reports_clicked(self):
        report_dialog = ReportDialog(self.conn, self)
        report_dialog.exec_()

    def on_view_events_clicked(self):
        event_dialog = EventDialog(self.conn, self)
        event_dialog.exec_()     
           
    def on_show_kpi_clicked(self):
     # Chemins vers les fichiers CSV
     input_folder = 'input_data'
    # Fichiers CSV pour chaque activité
     flight_ops_path = os.path.join(input_folder, 'flight_operations.csv')
     flight_dispatchers_path = os.path.join(input_folder, 'flight_dispatchers.csv')
     cabin_ops_path = os.path.join(input_folder, 'cabin_operations.csv')
    
    # Lire les fichiers CSV
     flight_ops_df = pd.read_csv(flight_ops_path)
     flight_dispatchers_df = pd.read_csv(flight_dispatchers_path)
     cabin_ops_df = pd.read_csv(cabin_ops_path)

    # Créer les objets KPI
     flight_ops_kpi = FlightOperationsKPI(flight_ops_df)
     flight_dispatchers_kpi = FlightDispatchersKPI(flight_dispatchers_df)
     cabin_ops_kpi = CabinOperationsKPI(cabin_ops_df)

    # Calculer les KPI
     flight_ops_kpi_df = flight_ops_kpi.calculate_kpi()
     flight_dispatchers_kpi_df = flight_dispatchers_kpi.calculate_kpi()
     cabin_ops_kpi_df = cabin_ops_kpi.calculate_kpi()

    # Créer une boîte de dialogue pour afficher les KPI
     kpi_dialog = QDialog(self)
     kpi_dialog.setWindowTitle("KPI Dashboard")
     layout = QVBoxLayout()

    # Afficher les KPI sous forme de tableau
     self.display_table(layout, flight_ops_kpi_df, "Flight Operations KPI")
     self.display_table(layout, flight_dispatchers_kpi_df, "Flight Dispatchers KPI")
     self.display_table(layout, cabin_ops_kpi_df, "Cabin Operations KPI")

    # Ajouter le layout à la boîte de dialogue
     kpi_dialog.setLayout(layout)
     kpi_dialog.exec_()

    def display_table(self, layout, kpi_df, title):
    # Créer un QTableWidget pour afficher les KPI
     table = QTableWidget()
     table.setRowCount(kpi_df.shape[0])
     table.setColumnCount(kpi_df.shape[1])
     table.setHorizontalHeaderLabels(kpi_df.columns)
     table.setVerticalHeaderLabels([title])
     table.setMinimumSize(1000, 300)
    # Remplir le tableau avec les données des KPI
     for row in range(kpi_df.shape[0]):
        for col in range(kpi_df.shape[1]):
            item = QTableWidgetItem(str(kpi_df.iat[row, col]))
            item.setForeground(QColor('yellow'))
            table.setItem(row, col, item)
            table.setStyleSheet("""
        QHeaderView::section {
            background-color: black;
            color: white;
            padding: 5px;
            border: 1px solid gray;
        }
    """)
    # Ajouter le tableau au layout
            table.resizeColumnsToContents()
            table.resizeRowsToContents()
     layout.addWidget(table)
    def on_show_graphs_clicked(self):
        # Chemins vers les fichiers CSV
        input_folder = 'input_data'
        flight_ops_path = os.path.join(input_folder, 'flight_operations.csv')
        flight_dispatchers_path = os.path.join(input_folder, 'flight_dispatchers.csv')
        cabin_ops_path = os.path.join(input_folder, 'cabin_operations.csv')
        # Lire les fichiers CSV
        flight_ops_df = pd.read_csv(flight_ops_path)
        flight_dispatchers_df = pd.read_csv(flight_dispatchers_path)
        cabin_ops_df = pd.read_csv(cabin_ops_path)
        # Créer une boîte de dialogue pour afficher les graphiques
        graph_dialog = QDialog(self)
        graph_dialog.setWindowTitle("KPI Graphs")
        layout = QVBoxLayout()

        # Afficher les graphiques
        layout.addWidget(self.create_graph(flight_ops_df, 'Flight Operations KPI'))
        layout.addWidget(self.create_graph(flight_dispatchers_df, 'Flight Dispatchers KPI'))
        layout.addWidget(self.create_graph(cabin_ops_df, 'Cabin Operations KPI'))

        # Ajouter le layout à la boîte de dialogue
        graph_dialog.setLayout(layout)
        graph_dialog.exec_() 
    def create_graph(self, df, title):
    # Créer une figure avec une taille personnalisée
     figure = Figure(figsize=(10, 8))  # Taille de la figure ajustée pour plus d'espace
     canvas = FigureCanvas(figure)
     ax = figure.add_subplot(111)

    # Extraire les colonnes KPI et calculer les valeurs moyennes
     kpi_columns = df.columns.tolist()
     kpi_values = df.mean()

    # Créer un graphique en ligne avec marqueurs
     ax.plot(kpi_columns, kpi_values, marker='o', color='b', linewidth=2)

    # Ajouter le titre et les labels
     ax.set_title(title, fontsize=16, fontweight='bold', color='navy')
     ax.set_xlabel('KPI', fontsize=14)
     ax.set_ylabel('Values', fontsize=14)

    # Rotation des étiquettes de l'axe des X avec des labels plus grands
     ax.tick_params(axis='x', rotation=45, labelsize=12)  # Ajuster la taille des étiquettes
     ax.tick_params(axis='y', labelsize=12)

    # Ajouter 6 cm d'espace en bas pour afficher correctement les étiquettes longues
     figure.subplots_adjust(bottom=0.35 + (3 / 25.4))  # Ajouter 6 cm d'espace (0.236 unité supplémentaire)

    # Ajouter une grille pour améliorer la lisibilité
     ax.grid(True, which='both', linestyle='--', linewidth=0.7, alpha=0.7)

    # Ajuster la taille des étiquettes pour éviter qu'elles ne se chevauchent
     ax.set_xticks(range(len(kpi_columns)))  # Assurer que chaque KPI ait son propre tick
     ax.set_xticklabels(kpi_columns, rotation=45, ha='right', fontsize=12)  # Affichage amélioré

     return canvas
        
    def closeEvent(self, event):
        if self.conn:
            self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
