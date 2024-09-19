import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QGridLayout  # Ajout de QGridLayout
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from MainWindow import Window

class LoginWind(QDialog):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ops Risk Manager Connexion")
        self.setGeometry(300, 300, 400, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Création du layout principal
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Création d'un widget central avec un effet de fond
        self.central_widget = QLabel()
        self.central_widget.setPixmap(QPixmap("Sky.jpeg"))  # Assurez-vous que cette image est dans le répertoire
        self.central_widget.setStyleSheet("background-color: rgba(0, 0, 0, 150); border-radius: 10px;")
        self.central_widget.setFixedSize(400, 300)
        self.main_layout.addWidget(self.central_widget, alignment=Qt.AlignCenter)

        # Disposition en grille pour les champs de saisie et les boutons
        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)

        # Titre de l'application avec une police moderne
        self.title_label = QLabel("OPS RISK MANAGER")
        font = QFont("Arial", 24, QFont.Bold)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet("color: white; letter-spacing: 1.5px;")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label, 0, 0, 1, 2)

        # Label pour le nom d'utilisateur avec icône moderne
        self.label_user = QLabel("\U0001F464 Nom d'utilisateur:")
        self.label_user.setStyleSheet("color: #ECF0F1; font-size: 16px;")
        self.layout.addWidget(self.label_user, 1, 0)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        self.username_input.setStyleSheet("""
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #BDC3C7;
            background-color: #2C3E50;
            color: white;
        """)
        self.layout.addWidget(self.username_input, 1, 1)

        # Label pour le mot de passe avec icône moderne
        self.label_password = QLabel("\U0001F512 Mot de passe:")
        self.label_password.setStyleSheet("color: #ECF0F1; font-size: 16px;")
        self.layout.addWidget(self.label_password, 2, 0)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.setStyleSheet("""
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #BDC3C7;
            background-color: #2C3E50;
            color: white;
        """)
        self.layout.addWidget(self.password_input, 2, 1)

        # Bouton de connexion avec style moderne
        self.login_button = QPushButton("Connexion")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #2980B9;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3498DB;
            }
            QPushButton:pressed {
                background-color: #1F618D;
            }
        """)
        self.login_button.clicked.connect(self.check_login)
        self.layout.addWidget(self.login_button, 3, 0, 1, 2)

        # Bouton de fermeture avec style moderne
        self.close_button = QPushButton("Fermer")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #C0392B;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #E74C3C;
            }
            QPushButton:pressed {
                background-color: #A93226;
            }
        """)
        self.close_button.clicked.connect(self.reject)  # Ferme la boîte de dialogue sans accepter
        self.layout.addWidget(self.close_button, 4, 0, 1, 2)  # Ajout du bouton au layout

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "admin":  # Exemple simple pour tester
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", "Nom d'utilisateur ou mot de passe incorrect.")

def main():
    app = QApplication(sys.argv)
    # Appliquer un thème avec CSS
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QPushButton {
            background-color: #007BFF;
            color: white;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #0056b3;
        }
        QComboBox, QLineEdit {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
        }
        QLabel {
            font-size: 14px;
            font-weight: bold;
        }
        QDialog {
            font-family: 'Arial', sans-serif;
        }
    """)
    login_window = LoginWind() 
    if login_window.exec_() == QDialog.Accepted:
        main_window = Window()  # Assurez-vous que le nom de la classe est correct
        main_window.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()