from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
from datetime import datetime
import os

def _fmt_date(d, fallback='N/A'):
    """Formate une date ou retourne fallback si None."""
    if d is None:
        return fallback
    if hasattr(d, 'strftime'):
        return d.strftime('%d/%m/%Y')
    return str(d)

def generer_recu_cotisation(membre, cotisation, chemin_sortie):
    """Génère un reçu PDF pour une cotisation"""
    
    doc = SimpleDocTemplate(chemin_sortie, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Titre
    titre_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1
    )
    
    elements.append(Paragraph("REÇU DE COTISATION", titre_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Informations Mutuelle
    mutuelle_info = [
        ["Mutuelle Solidaire", ""],
        ["Adresse : 123 Rue de la Solidarité", ""],
        ["Email : contact@mutuelle.com", ""],
        ["Téléphone : +33 1 23 45 67 89", ""]
    ]
    
    table_mutuelle = Table(mutuelle_info, colWidths=[7*cm, 7*cm])
    table_mutuelle.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),
    ]))
    elements.append(table_mutuelle)
    elements.append(Spacer(1, 1*cm))
    
    # Informations Membre
    elements.append(Paragraph("INFORMATIONS DU MEMBRE", styles['Heading2']))
    membre_info = [
        ["Nom :",      f"{membre.nom or ''} {membre.prenom or ''}".strip() or 'N/A'],
        ["Email :",    membre.email or 'N/A'],
        ["Téléphone :", membre.telephone or "N/A"],
        ["ID Membre :", f"#{membre.id}"]
    ]
    
    table_membre = Table(membre_info, colWidths=[3*cm, 6*cm])
    table_membre.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table_membre)
    elements.append(Spacer(1, 1*cm))
    
    # Informations Cotisation
    elements.append(Paragraph("DÉTAILS DE LA COTISATION", styles['Heading2']))
    cotisation_info = [
        ["Type :",             cotisation.type_cotisation or 'N/A'],
        ["Montant :",          f"{cotisation.montant:.2f} FCFA" if cotisation.montant is not None else 'N/A'],
        ["Date de Paiement :", _fmt_date(cotisation.date_paiement)],
        ["Statut :",           cotisation.statut or 'N/A'],
        ["Numéro de Reçu :",   f"REC-{cotisation.id}-{datetime.now().strftime('%Y%m%d')}"]
    ]
    
    table_cotisation = Table(cotisation_info, colWidths=[4*cm, 5*cm])
    table_cotisation.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table_cotisation)
    elements.append(Spacer(1, 2*cm))
    
    # Pied de page
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=1
    )
    elements.append(Paragraph("Merci pour votre contribution à la mutuelle !", footer_style))
    elements.append(Paragraph("Ce document sert de preuve de paiement.", footer_style))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", footer_style))
    
    doc.build(elements)
    return chemin_sortie