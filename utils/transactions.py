# app.py ou utils/transactions.py

from datetime import datetime
from sqlalchemy import desc

def get_recent_transactions(limit=15):
    """
    Récupère les dernières transactions unifiées (cotisations, aides, dons, événements)
    Gère correctement les dates NULL et les relations manquantes
    """
    transactions = []

    # 1️⃣ Cotisations
    for c in Cotisation.query.join(Membre, isouter=True)\
                             .order_by(desc(Cotisation.date_paiement))\
                             .limit(limit).all():
        transactions.append({
            'id': c.id,
            'type': 'cotisation',
            'subtype': c.type_cotisation or 'Cotisation',
            'membre': f"{c.membre.nom} {c.membre.prenom}" if c.membre else 'Membre inconnu',
            'date': c.date_paiement,
            'montant': float(c.montant) if c.montant else 0.0,
            'signe': '+',
            'statut': c.statut or 'En attente',
            'color': 'success' if c.statut == 'Paye' else 'warning',
            'icon': 'fa-money-bill-wave'
        })

    # 2️⃣ Aides
    for a in Aide.query.join(Membre, isouter=True)\
                       .order_by(desc(Aide.date_attribution))\
                       .limit(limit).all():
        transactions.append({
            'id': a.id,
            'type': 'aide',
            'subtype': a.type_aide or 'Aide sociale',
            'membre': f"{a.beneficiaire.nom} {a.beneficiaire.prenom}" if a.beneficiaire else 'Bénéficiaire inconnu',
            'date': a.date_attribution,
            'montant': float(a.montant) if a.montant else 0.0,
            'signe': '-',
            'statut': 'Versé',
            'color': 'danger',
            'icon': 'fa-hand-holding-heart'
        })

    # 3️⃣ Dons
    for d in Don.query.order_by(desc(Don.date)).limit(limit).all():
        transactions.append({
            'id': d.id,
            'type': 'don',
            'subtype': 'Don',
            'membre': d.donateur_nom or 'Donateur anonyme',
            'date': d.date,
            'montant': float(d.montant) if d.montant else 0.0,
            'signe': '+',
            'statut': 'Reçu',
            'color': 'info',
            'icon': 'fa-gift'
        })

    # 4️⃣ Événements (dépenses)
    for e in Evenement.query.order_by(desc(Evenement.date)).limit(limit).all():
        transactions.append({
            'id': e.id,
            'type': 'evenement',
            'subtype': e.nom or 'Événement',
            'membre': 'Mutuelle',
            'date': e.date,
            'montant': float(e.depenses_reelles or 0.0),
            'signe': '-',
            'statut': 'Validé',
            'color': 'secondary',
            'icon': 'fa-calendar-check'
        })

    # 🔽 Trier par date (les dates NULL vont en fin de liste)
    transactions.sort(key=lambda x: x['date'] or datetime.min, reverse=True)
    
    # Retourner uniquement les `limit` plus récentes
    return transactions[:limit]