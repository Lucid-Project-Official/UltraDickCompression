# UltraCompression - Compression Intelligente avec 7zip

UltraCompression est une application Python avec interface graphique qui permet de compresser récursivement tous les fichiers d'un disque externe en utilisant 7zip avec des optimisations intelligentes pour maximiser la vitesse.

## Fonctionnalités

- **Interface graphique intuitive** : Sélection simple du disque et niveau de compression
- **Compression récursive** : Traite automatiquement tous les fichiers du disque sélectionné
- **Optimisation intelligente** : 
  - Détection automatique du type de disque (SSD/HDD)
  - Optimisation de l'ordre des fichiers
  - Paramètres 7zip adaptés au contexte
  - Parallélisation intelligente
- **Barre de progression en temps réel** : Affichage du progrès et statistiques
- **Suppression automatique** : Les fichiers originaux sont supprimés après compression réussie
- **Filtrage intelligent** : Évite les fichiers système et déjà compressés
- **Estimation de temps** : Calcul du temps nécessaire basé sur les performances du système

## Prérequis

1. **Python 3.7+** installé sur le système
2. **7zip** installé et accessible dans le PATH système
   - Téléchargez depuis : https://www.7-zip.org/
   - Ou installez via chocolatey : `choco install 7zip`

## Installation

1. Clonez ou téléchargez ce projet
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

1. Lancez l'application :
```bash
python ultra_compression.py
```

2. Dans l'interface :
   - **Sélectionnez le disque externe** à compresser
   - **Choisissez le niveau de compression** (0-9) :
     - 0 : Aucune compression (très rapide)
     - 5 : Équilibré (recommandé)
     - 9 : Compression maximale (très lent)
   - **Cliquez sur "Démarrer la Compression"**

3. L'application va :
   - Analyser tous les fichiers du disque
   - Optimiser l'ordre de traitement
   - Compresser chaque fichier individuellement
   - Supprimer les fichiers originaux après compression réussie
   - Afficher le progrès en temps réel

## Optimisations Intelligentes

### Détection du Type de Disque
- **SSD** : Privilégie l'utilisation du CPU et la parallélisation
- **HDD** : Optimise les accès disque et réduit la fragmentation

### Ordre des Fichiers
- **Fichiers prioritaires** : Texte, logs, JSON traités en premier pour un feedback rapide
- **Groupement par répertoire** : Minimise les déplacements de tête de lecture
- **Tri par taille** : Petits fichiers d'abord pour un progrès visible

### Paramètres 7zip Adaptatifs
- **Multi-threading** : Ajusté selon le nombre de CPU cores
- **Mémoire** : Adaptée selon la RAM disponible
- **Méthodes de compression** : Optimisées selon le contexte

## Fichiers Ignorés

L'application ignore automatiquement :
- **Fichiers déjà compressés** : .7z, .zip, .rar, .gz, etc.
- **Fichiers système** : .sys, .dll, .exe, .tmp
- **Dossiers système** : Windows, Program Files, System Volume Information
- **Fichiers trop petits** : Moins de 1KB

## Configuration Avancée

Modifiez le fichier `config.py` pour personnaliser :
- Extensions de fichiers à ignorer
- Taille minimale des fichiers
- Paramètres de compression par niveau
- Nombre maximum de threads

## Sécurité

⚠️ **ATTENTION** : Cette application supprime les fichiers originaux après compression. Assurez-vous de :
- Faire une sauvegarde avant utilisation
- Tester sur un petit échantillon d'abord
- Vérifier que 7zip est correctement installé

## Structure du Projet

```
UltraCompression/
├── ultra_compression.py      # Application principale
├── compression_optimizer.py  # Module d'optimisation
├── config.py                # Configuration
├── requirements.txt         # Dépendances Python
└── README.md               # Documentation
```

## Dépannage

### 7zip non trouvé
- Vérifiez que 7zip est installé
- Ajoutez le dossier 7zip au PATH système
- Redémarrez l'application

### Erreurs de permissions
- Exécutez en tant qu'administrateur si nécessaire
- Vérifiez les permissions sur le disque externe

### Performances lentes
- Réduisez le niveau de compression
- Vérifiez l'espace disque disponible
- Fermez les autres applications gourmandes

## Licence

Ce projet est fourni tel quel, sans garantie. Utilisez à vos propres risques.

## Support

Pour signaler des bugs ou demander des fonctionnalités, créez une issue dans le repository du projet.
