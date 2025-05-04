# -*- coding: utf-8 -*-
# Fahrradwerkstatt App für ERPNext - Bicycle DocType
# 
# Erstellt: 04.05.2025
# Änderungen:
# - Initiale Erstellung des Bicycle DocType für die Fahrradwerkstatt-App
#
# Diese Datei definiert die Logik für das Fahrrad-Datenmodell.

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class Bicycle(Document):
    def validate(self):
        """
        Validiere das Fahrrad-Dokument vor dem Speichern
        """
        self.validate_serial_number()
        self.set_bicycle_status()
    
    def validate_serial_number(self):
        """
        Überprüfe, ob die Seriennummer eindeutig ist
        """
        if self.serial_number:
            existing = frappe.db.get_value("Bicycle", 
                {"serial_number": self.serial_number, "name": ["!=", self.name]}, "name")
            if existing:
                frappe.throw(_("Seriennummer {0} ist bereits für das Fahrrad {1} registriert").format(
                    self.serial_number, existing))
    
    def set_bicycle_status(self):
        """
        Setze den Status des Fahrrads basierend auf aktuellen Reparaturen
        """
        # Prüfe, ob es aktive Reparaturen gibt
        active_repairs = frappe.get_all("Bicycle Repair", 
            filters={"bicycle": self.name, "status": ["in", ["Eingegangen", "In Arbeit"]]})
        
        if active_repairs:
            self.status = "In Reparatur"
        elif self.status == "In Reparatur":
            # Wenn keine aktiven Reparaturen mehr vorliegen, setze auf "Einsatzbereit"
            self.status = "Einsatzbereit"
    
    def on_update(self):
        """
        Aktualisiere verknüpfte Dokumente nach der Aktualisierung
        """
        self.update_customer_details()
    
    def update_customer_details(self):
        """
        Aktualisiere Kundendetails für dieses Fahrrad
        """
        if self.customer:
            # Markiere den Kunden als Fahrradbesitzer
            frappe.db.set_value("Customer", self.customer, "bicycle_owner", 1)
            
    def get_repair_history(self):
        """
        Hole die Reparaturhistorie für dieses Fahrrad
        """
        repairs = frappe.get_all("Bicycle Repair", 
            filters={"bicycle": self.name},
            fields=["name", "repair_date", "description", "status", "cost"],
            order_by="repair_date desc")
        
        return repairs
        
    def get_maintenance_reminder(self):
        """
        Erzeuge eine Erinnerung für die nächste Wartung
        """
        # Logik für Wartungserinnerungen basierend auf dem Fahrradtyp und -alter
        last_service = frappe.get_all("Bicycle Repair", 
            filters={"bicycle": self.name, "is_maintenance": 1},
            fields=["repair_date"],
            order_by="repair_date desc",
            limit=1)
        
        if not last_service:
            return _("Dieses Fahrrad wurde noch nie gewartet. Eine erste Inspektion wird empfohlen.")
        
        # Hier weitere Logik basierend auf dem Fahrradtyp und der Zeit seit der letzten Wartung