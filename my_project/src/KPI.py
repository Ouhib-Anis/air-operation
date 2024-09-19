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

# Classes KPI
class FlightOperationsKPI:
    def __init__(self, df):
        self.df = df
    def calculate_kpi(self):
        kpis = {
            "Taux d'incidents": (self.df['incidents'] / self.df['flight_hours']) * 100000,
            "Taux d'accidents": (self.df['accidents'] / self.df['total_flights']) * 1000000,
            "Pourcentage de conformité": (self.df['compliance_checks'] / self.df['total_regulations']) * 100,
            "Nombre de rapports soumis": self.df['safety_reports'].sum(),
            "Taux de résolution des problèmes": (self.df['resolved_issues'] / self.df['safety_reports']) * 100,
            "Taux de maintenance non planifiée": (self.df['unplanned_maintenance'] / self.df['flight_hours']) * 1000,
            "Temps moyen de résolution": self.df['total_maintenance_hours'] / self.df['total_pannes'],
            "Pourcentage de l'équipage formé": (self.df['trained_crew'] / self.df['total_crew']) * 100,
            "Taux de réussite aux tests": (self.df['passed_tests'] / self.df['total_tests']) * 100,
            "Nombre de rapports de fatigue": self.df['fatigue_reports'].sum(),
            "Heures moyennes de repos": self.df['total_rest_hours'] / self.df['rest_periods'],
            "Taux de défaillance des systèmes": (self.df['system_failures'] / self.df['total_systems']) * 100,
            "Efficacité des systèmes de détection et d'alerte": (self.df['valid_alerts'] / self.df['total_alerts']) * 100,
            "Nombre de risques évalués": self.df['identified_risks'].sum(),
            "Pourcentage de risques avec plans d'action": (self.df['planed_risks'] / self.df['total_risks']) * 100,
            "Taux de violation": (self.df['total_violations'] / self.df['total_hours']) * 10000,
            "Nombre de leçons apprises": self.df['learned_lessons'].sum(),
            "Pourcentage de recommandations mises en œuvre": (self.df['implemented_recommendations'] / self.df['total_recommendations']) * 100,
        }
        return pd.DataFrame([kpis])   
    
    def to_string(self):
        return self.calculate_kpi().to_string(index=False)

class FlightDispatchersKPI:
    def __init__(self, df):
        self.df = df

    def calculate_kpi(self):
        kpis = {
            "Taux de ponctualité des départs": (self.df['on_time_departures'] / self.df['total_flights']) * 100,
            "Taux de ponctualité des arrivées": (self.df['on_time_arrivals'] / self.df['total_flights']) * 100,
            "Temps moyen de préparation des plans de vol": self.df['preparation_time'] / self.df['total_preparations'],
            "Taux d'erreurs dans les plans de vol": (self.df['flight_plan_errors'] / self.df['total_flight_plans']) * 100,
            "Réduction des coûts": ((self.df['pre_optimization_costs'] - self.df['post_optimization_costs']) / self.df['pre_optimization_costs']) * 100,
            "Taux de retards imputables à la préparation": (self.df['preparation_delays'] / self.df['total_flights']) * 100,
            "Taux de changements de dernière minute": (self.df['last_minute_changes'] / self.df['total_flight_plans']) * 100,
            "Temps moyen de réponse": self.df['total_responses'] / self.df['emergency_responses'],
            "Satisfaction de l'équipage": (self.df['satisfaction_scores'] / self.df['total_responses_scores']) * 100,
            "Taux de conformité": (self.df['regulatory_compliance'] / self.df['total_compliances']) * 100,
            "Taux d'annulations dues à la planification": (self.df['planning_cancellations'] / self.df['total_cancelations']) * 100,
            "Taux de communications manquées ou retardées": (self.df['missed_communications'] / self.df['total_communications']) * 100,
            "Efficacité de la gestion du carburant": (self.df['fuel_saved'] / self.df['total_fuel']) * 100,
        }
        return pd.DataFrame([kpis])
    
    def to_string(self):
        return self.calculate_kpi().to_string(index=False)
class CabinOperationsKPI:
    def __init__(self, df):
        self.df = df

    def calculate_kpi(self):
        kpis = {
            "Taux de satisfaction des passagers": (self.df['passenger_satisfaction_score'] / self.df['total_responses']) * 100,
            "Temps moyen de réponse": self.df['response_time'] / self.df['total_requests'],
            "Taux de plaintes des passagers": (self.df['passenger_complaints'] / self.df['total_passengers']) * 100,
            "Taux de conformité": (self.df['compliance_checks'] / self.df['total_compliances']) * 100,
            "Temps moyen d'embarquement": self.df['boarding_time'] / self.df['total_boardings'],
            "Temps moyen de débarquement": self.df['deboarding_time'] / self.df['total_deboardings'],
            "Taux d'incidents en cabine": (self.df['cabin_incidents'] / self.df['total_flights']) * 100,
            "Taux de satisfaction des repas et boissons": (self.df['meal_satisfaction_score'] / self.df['total_meal_responses']) * 100,
            "Taux de disponibilité des produits": (self.df['product_availability'] / self.df['total_products']) * 100,
            "Score de performance de l'équipage": (self.df['crew_performance_score'] / self.df['total_performance_responses']) * 100,
            "Taux de retards causés par la cabine": (self.df['delay_caused_cabin'] / self.df['total_delays']) * 100,
            "Taux de conformité de la gestion des bagages à main": (self.df['hand_baggage_compliance'] / self.df['total_hand_baggage']) * 100,
            "Pourcentage de l'équipage formé": (self.df['trained_crew'] / self.df['total_crew']) * 100,
            "Nombre de premiers secours administrés": self.df['first_aid_cases'].sum(),
        }
        return pd.DataFrame([kpis])
    
    
    def to_string(self):
        return self.calculate_kpi().to_string(index=False)