# Exemples de requêtes — Données Québec MCP

Tous les exemples ci-dessous ont été testés avec Claude Desktop connecté au serveur MCP. Les réponses sont générées automatiquement par l'agent IA à partir des données ouvertes en temps réel.

[Retour au README](README.md)

---

## SQL et analyse de données

### 1. Top 10 des postes de quartier — actes criminels

**Requête :**
> « Quels sont les 10 postes de quartier avec le plus d'actes criminels à Montréal ? Fais une requête SQL avec le total par PDQ. »

**Outils utilisés :** `search_montreal_datasets` > `query_montreal_sql`

**Réponse :**

Le dataset « Actes criminels » du SPVM ne contient pas de colonne ARRONDISSEMENT mais PDQ (poste de quartier de police).

| Rang | PDQ | Total actes |
|------|-----|-------------|
| 1 | 38 (Centre-Sud) | 24 942 |
| 2 | 21 (Plateau-Mont-Royal) | 23 041 |
| 3 | 20 (Ville-Marie Est) | 20 135 |
| 4 | 48 (Saint-Laurent) | 16 163 |
| 5 | 26 (Côte-des-Neiges) | 15 955 |
| 6 | 7 (Rosemont) | 15 559 |
| 7 | 39 (LaSalle) | 15 400 |
| 8 | 15 (Verdun) | 13 899 |
| 9 | 44 (Saint-Léonard) | 13 395 |
| 10 | 23 (Outremont/CDN) | 13 234 |

---

### 2. Introductions par effraction vs vols de véhicules

**Requête :**
> « Compare le nombre d'introductions par effraction vs les vols de véhicules par PDQ à Montréal. »

**Outils utilisés :** `query_montreal_sql` (2 requêtes SQL)

**Réponse :**

| PDQ | Introductions | Vols véhicules |
|-----|---------------|----------------|
| 38 (Centre-Sud) | 8 208 | 3 982 |
| 23 (Outremont/CDN) | 4 185 | 1 784 |
| 26 (Côte-des-Neiges) | 4 143 | 3 454 |
| 15 (Verdun) | 4 044 | 2 096 |
| 21 (Plateau) | 3 783 | 2 467 |
| 48 (Saint-Laurent) | 3 703 | 3 815 |
| 44 (Saint-Léonard) | 3 694 | 2 616 |
| 39 (LaSalle) | 3 281 | 4 090 |
| 7 (Rosemont) | 3 059 | 5 302 |

**Observation :** Le PDQ 7 (Rosemont) se distingue par un très haut ratio de vols de véhicules par rapport aux introductions.

---

### 3. Tendance mensuelle des actes criminels

**Requête :**
> « Quelle est la tendance mensuelle des actes criminels à Montréal pour les 12 derniers mois ? »

**Outils utilisés :** `query_montreal_sql`

**Réponse :**

| Mois | Actes criminels |
|------|-----------------|
| Mars 2025 | 1 751 |
| Avril 2025 | 2 736 |
| Mai 2025 | 2 665 |
| Juin 2025 | 2 711 |
| Juillet 2025 | 2 555 |
| Août 2025 | 2 680 |
| Septembre 2025 | 2 592 |
| Octobre 2025 | 2 615 |
| Novembre 2025 | 2 419 |
| Décembre 2025 | 2 129 |
| Janvier 2026 | 1 959 |
| Février 2026 | 1 741 |

**Tendance :** Pic au printemps/été (~2 700/mois), baisse en hiver (~1 700-2 000/mois).

---

## Exploration multi-outils (chaînage)

### 4. Qualité de l'eau à Montréal

**Requête :**
> « Trouve les données sur la qualité de l'eau à Montréal, montre-moi les colonnes disponibles, puis donne-moi les 20 dernières mesures triées par date. »

**Outils utilisés :** `search_montreal_datasets` > `query_montreal_data` > `query_montreal_sql`

**Réponse :**

Dataset : **RSMA QUALO** — programme de suivi de la qualité de l'eau en rive, 2 060 mesures en 2025.

**Colonnes :** `point_echantillonnage`, `plan_eau`, `administration`, `nom`, `date_heure`, `temperature`, `pH`, `coliformes_fecaux`, `conductivite`, `precipitations`, `meteo`, `latitude`, `longitude`

**Dernières mesures (octobre 2025) :**

| Station | Plan d'eau | Date | Temp. | pH | Colif. fécaux |
|---------|-----------|------|-------|----|---------------|
| IBIZ-15 | Île Bizard | 2025-10-02 | 17°C | 7.4 | 13 |
| IBIZ-14 | Île Bizard | 2025-10-02 | 16°C | 7.1 | 8 |
| IBIZ-13 | Île Bizard | 2025-10-02 | 16°C | 7.3 | 36 |
| RDP-20 | Rivière des Prairies | 2025-10-01 | 22°C | 8.5 | 2 500 |
| RDP-100 | Rivière des Prairies | 2025-10-01 | 18°C | 7.4 | 250 |

**Alerte :** Coliformes fécaux à 2 500 à la station RDP-20 (Pointe aux Moutons) — nettement au-dessus des seuils de baignade (~200 UFC/100 mL).

---

### 5. Jeux de données de la Ville de Laval

**Requête :**
> « Quels jeux de données la Ville de Laval publie sur Données Québec ? Montre-moi les plus récents avec leurs ressources. »

**Outils utilisés :** `search_datasets` (filtré par organisation) > `list_dataset_resources`

**Réponse :**

La Ville de Laval publie **133 jeux de données**. Les 10 plus récemment mis à jour (décembre 2025) :

| Jeu de données | Mise à jour |
|---------------|-------------|
| Délimitation approximative des carrières | 2025-12-17 |
| Liste des élus | 2025-12-17 |
| Pistes cyclables et piétonnières | 2025-12-17 |
| Analyses des substances de l'eau distribuée | 2025-12-17 |
| Limites des districts électoraux | 2025-12-17 |
| Localisation des cours d'eau verbalisés | 2025-12-17 |
| Localisation des cours d'eau intérieur | 2025-12-17 |
| Géolocalisation des adresses | 2025-12-17 |
| Grandes affectations du territoire | 2025-12-17 |
| Tronçons de calcul des contraintes sonores | 2025-12-17 |

---

### 6. Arbres publics de Montréal par arrondissement

**Requête :**
> « Trouve un dataset sur les arbres publics de Montréal, explore sa structure, puis dis-moi combien d'arbres il y a par arrondissement. »

**Outils utilisés :** `search_montreal_datasets` > `query_montreal_data` > `query_montreal_sql`

**Réponse :**

**333 556 arbres** dans la base. Colonnes clés : `ARROND_NOM`, `Essence_fr`, `Essence_latin`, `DHP` (diamètre), `Date_Plantation`, `Arbre_remarquable`, `NOM_PARC`, `Longitude`, `Latitude`.

| Arrondissement | Nb arbres |
|---------------|-----------|
| Mercier – Hochelaga-Maisonneuve | 37 871 |
| Rosemont – La Petite-Patrie | 37 136 |
| Ahuntsic – Cartierville | 36 741 |
| Rivière-des-Prairies – PAT | 34 539 |
| Côte-des-Neiges – NDG | 29 130 |
| Villeray – Saint-Michel – PE | 27 332 |
| Saint-Léonard | 23 458 |
| Le Sud-Ouest | 22 682 |
| Ville-Marie | 20 202 |
| Le Plateau-Mont-Royal | 19 455 |
| Verdun | 19 149 |
| Pierrefonds – Roxboro | 17 159 |
| Lachine | 8 702 |

---

## Géospatial

### 7. Couches patrimoniales du Québec

**Requête :**
> « Quelles couches géospatiales sont disponibles pour le patrimoine culturel du Québec ? »

**Outils utilisés :** `list_geospatial_layers` > `describe_geospatial_layer`

**Réponse :**

7 couches du Ministère de la Culture et des Communications (MCC) :

| Couche | Description |
|--------|-------------|
| `ms:MCC_V_SITE_PATRIMONIAL_NATIONAL_S` | Sites patrimoniaux nationaux (polygones) |
| `ms:MCC_V_SITE_PATRIMONIAL_DECLARE_S` | Sites patrimoniaux déclarés |
| `ms:MCC_V_SITE_PATRIMONIAL_S` | Tous les sites patrimoniaux |
| `ms:MCC_V_SITE_PATRIMONIAL_CITE_P` | Sites cités (points) |
| `ms:MCC_V_IP_TERRAIN_PROTEGE_S` | Terrains d'intérêt patrimonial protégés |
| `ms:MCC_V_IP_CITE_P` | Immeubles patrimoniaux cités |

**Schéma :** `nom_bien`, `bien_id`, `url_rpcq`, `description_bien`, `synthese_historique`, `statut_juridique_princ`, `categorie`, `autorite_protection`, `municipalite`, `adresse`, `debut_construction`, `fin_construction`, `usage_princ`

---

### 8. Carte WMS des casernes d'incendie

**Requête :**
> « Génère une carte WMS des casernes d'incendie dans la région de Montréal. »

**Outils utilisés :** `get_map_url`

**Réponse :**

L'agent génère automatiquement une URL GetMap WMS avec le bbox de Montréal (`-73.7,45.4,-73.5,45.6`) et retourne un lien vers une image PNG de la carte.

---

## Cross-source

### 9. Transport en commun — comparaison multi-portails

**Requête :**
> « Compare ce que Données Québec et donnees.montreal.ca ont comme données sur le transport en commun. »

**Outils utilisés :** `search_datasets` + `search_montreal_datasets`

**Réponse :**

| Source | Jeux trouvés | Exemples |
|--------|-------------|----------|
| Données Québec | 970 | Trains Exo (GTFS), Vision 2050 réseau TC, Déplacements MTL Trajet |
| donnees.montreal.ca | 76 | STM bus temps réel (GTFS-RT), Entraves à la circulation, Schéma d'aménagement |

- **Données exclusives à Données Québec :** données régionales (Exo trains de banlieue, lignes de train)
- **Données exclusives à donnees.montreal.ca :** STM temps réel (GTFS-RT), données de déneigement
- **Données présentes sur les deux :** Vision 2050 réseau TC structurant, données MTL Trajet

---

### 10. Pistes cyclables — recherche multi-sources

**Requête :**
> « Trouve les données sur les pistes cyclables à Montréal via les deux portails et via les couches géospatiales IGO. »

**Outils utilisés :** `search_datasets` + `search_montreal_datasets` + `list_geospatial_layers`

**Réponse :**

| Source | Jeux trouvés | Contenu |
|--------|-------------|---------|
| Données Québec | 501 | Réseau cyclable, REV, comptages vélos, condition chaussées, trajets Mon RésoVélo |
| donnees.montreal.ca | 8 | Réseau cyclable (4 ressources), Comptages vélos (19 écocompteurs), REV, Condition chaussées |
| IGO WFS | 0 | Aucune couche géospatiale de pistes cyclables dans les 29 couches IGO actuelles |

**Jeu clé :** Réseau cyclable — mis à jour en mars 2026, avec géométries et informations sur l'accessibilité 4 saisons.

---

### 11. Statistiques globales du catalogue

**Requête :**
> « Combien d'organisations publient des données sur Données Québec ? »

**Outils utilisés :** `get_catalog_stats`

**Réponse :**

**139 organisations**, **1 584 jeux de données**.

| Organisation | Jeux de données |
|-------------|-----------------|
| Ville de Montréal | 383 |
| Ville de Laval | 133 |
| MELCCFP (Environnement) | 119 |
| Ministère des Ressources naturelles et des Forêts | 117 |
| Ville de Gatineau | 52 |
| Ville de Repentigny | 39 |
| Ville de Québec | 37 |
| Ville de Trois-Rivières | 36 |
| Ministère de la Santé et des services sociaux | 34 |
| Ministère des Transports et de la Mobilité durable | 31 |

La Ville de Montréal domine avec 383 jeux de données, soit près du quart de l'ensemble du catalogue.

---

[Retour au README](README.md)
