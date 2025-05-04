# -*- coding: utf-8 -*-
# Fahrradwerkstatt App für ERPNext - Bicycle Repair DocType
# 
# Erstellt: 04.05.2025
# Änderungen:
# - Initiale Erstellung des Bicycle Repair DocType für die Fahrradwerkstatt-App
#
# Diese Datei definiert die Logik für das Fahrradreparatur-Datenmodell.

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_days

class BicycleRepair(Document):
    def validate(self):
        """
        Validiere das Reparatur-Dokument vor dem Speichern
        """
        self.validate_dates()
        self.update_status()
        self.calculate_total()
    
    def validate_dates(self):
        """
        Stelle sicher, dass die Termine logisch sind
        """
        if self.completion_date and getdate(self.completion_date) < getdate(self.repair_date):
            frappe.throw(_("Das Fertigstellungsdatum kann nicht vor dem Reparaturdatum liegen."))
        
        if not self.estimated_completion_date:
            # Setze ein geschätztes Fertigstellungsdatum (3 Arbeitstage)
            self.estimated_completion_date = add_days(getdate(self.repair_date), 3)
    
    def update_status(self):
        """
        Aktualisiert den Status basierend auf den Daten
        """
        today = getdate(nowdate())
        
        if self.status == "Abgeschlossen":
            return
            
        if not self.completion_date:
            if getdate(self.repair_date) > today:
                self.status = "Geplant"
            elif self.status == "Geplant":
                self.status = "Eingegangen"
        else:
            self.status = "Abgeschlossen"
    
    def calculate_total(self):
        """
        Berechnet die Gesamtkosten der Reparatur
        """
        total = 0
        if self.parts:
            for part in self.parts:
                part.amount = part.rate * part.quantity
                total += part.amount
        
        # Arbeitskosten hinzufügen
        if self.labor_cost:
            total += self.labor_cost
            
        self.total_cost = total
    
    def on_submit(self):
        """
        Aktionen bei Einreichung des Dokuments
        """
        self.update_bicycle()
        self.create_invoice()
    
    def update_bicycle(self):
        """
        Aktualisiere das Fahrraddokument
        """
        if self.bicycle:
            bicycle = frappe.get_doc("Bicycle", self.bicycle)
            
            # Wenn dies eine Wartung ist, aktualisiere das letzte Servicedatum
            if self.is_maintenance:
                bicycle.last_service_date = self.completion_date or self.repair_date
                
            # Status aktualisieren
            if self.status == "Abgeschlossen":
                bicycle.status = "Einsatzbereit"
            else:
                bicycle.status = "In Reparatur"
                
            bicycle.save()
    
    def create_invoice(self):
        """
        Erstelle eine Rechnung, wenn die Reparatur abgeschlossen ist
        """
        if self.status == "Abgeschlossen" and not self.invoice:
            # Nur erstellen, wenn noch keine Rechnung existiert
            if not self.customer:
                return
                
            # Rechnungsposten vorbereiten
            items = []
            
            # Teile zur Rechnung hinzufügen
            if self.parts:
                for part in self.parts:
                    items.append({
                        "item_code": part.item_code,
                        "item_name": part.item_name,
                        "description": part.description or part.item_name,
                        "qty": part.quantity,
                        "rate": part.rate
                    })
            
            # Arbeitskosten zur Rechnung hinzufügen
            if self.labor_cost:
                items.append({
                    "item_name": _("Arbeitskosten für {0}").format(self.bicycle_name or "Fahrrad"),
                    "description": self.description or _("Arbeitskosten für Reparatur"),
                    "qty": 1,
                    "rate": self.labor_cost
                })
            
            if items:
                # Rechnung erstellen
                invoice = frappe.get_doc({
                    "doctype": "Sales Invoice",
                    "customer": self.customer,
                    "due_date": add_days(nowdate(), 14),
                    "items": items,
                    "bicycle_repair": self.name
                })
                
                invoice.insert()
                
                # Referenz auf die erstellte Rechnung speichern
                self.invoice = invoice.name
                self.db.set_value("Bicycle Repair", self.name, "invoice", invoice.name)
                
                frappe.msgprint(_("Rechnung {0} für diese Reparatur wurde erstellt").format(invoice.name))