#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer des fichiers de test pour UltraCompression
"""

import os
import random
import string
from pathlib import Path

def create_test_directory(base_path="test_drive"):
    """Crée un répertoire de test avec différents types de fichiers"""
    
    # Créer le dossier principal
    test_path = Path(base_path)
    test_path.mkdir(exist_ok=True)
    
    print(f"Création du répertoire de test: {test_path.absolute()}")
    
    # Types de fichiers à créer
    file_types = [
        (".txt", "text", 1024),      # Fichiers texte 1KB
        (".log", "text", 2048),      # Fichiers log 2KB
        (".json", "json", 512),      # Fichiers JSON 512B
        (".csv", "csv", 4096),       # Fichiers CSV 4KB
        (".xml", "xml", 8192),       # Fichiers XML 8KB
        (".dat", "binary", 16384),   # Fichiers binaires 16KB
    ]
    
    # Créer des sous-dossiers
    subdirs = ["documents", "logs", "data", "backup", "temp"]
    
    total_files = 0
    total_size = 0
    
    for subdir in subdirs:
        subdir_path = test_path / subdir
        subdir_path.mkdir(exist_ok=True)
        
        # Créer des fichiers dans chaque sous-dossier
        for ext, file_type, size in file_types:
            num_files = random.randint(3, 8)  # 3-8 fichiers par type
            
            for i in range(num_files):
                filename = f"{file_type}_{i+1:03d}{ext}"
                filepath = subdir_path / filename
                
                # Générer le contenu selon le type
                if file_type == "text":
                    content = generate_text_content(size)
                elif file_type == "json":
                    content = generate_json_content(size)
                elif file_type == "csv":
                    content = generate_csv_content(size)
                elif file_type == "xml":
                    content = generate_xml_content(size)
                else:  # binary
                    content = generate_binary_content(size)
                
                # Écrire le fichier
                mode = 'wb' if file_type == "binary" else 'w'
                encoding = None if file_type == "binary" else 'utf-8'
                
                with open(filepath, mode, encoding=encoding) as f:
                    f.write(content)
                
                total_files += 1
                total_size += len(content) if isinstance(content, bytes) else len(content.encode('utf-8'))
    
    # Créer quelques fichiers déjà compressés (à ignorer)
    compressed_dir = test_path / "compressed"
    compressed_dir.mkdir(exist_ok=True)
    
    compressed_files = ["archive1.7z", "backup.zip", "data.rar"]
    for comp_file in compressed_files:
        filepath = compressed_dir / comp_file
        with open(filepath, 'wb') as f:
            f.write(b"Fake compressed file content" * 100)
    
    print(f"✅ Créé {total_files} fichiers de test ({total_size/1024:.1f} KB total)")
    print(f"✅ Créé {len(compressed_files)} fichiers compressés (seront ignorés)")
    print(f"\n📁 Répertoire de test prêt: {test_path.absolute()}")
    print(f"💡 Utilisez ce chemin dans UltraCompression pour tester l'application")
    
    return test_path

def generate_text_content(target_size):
    """Génère du contenu textuel"""
    words = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
             "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
             "magna", "aliqua", "enim", "ad", "minim", "veniam", "quis", "nostrud"]
    
    content = []
    current_size = 0
    
    while current_size < target_size:
        line = " ".join(random.choices(words, k=random.randint(5, 15))) + "\n"
        content.append(line)
        current_size += len(line)
    
    return "".join(content)[:target_size]

def generate_json_content(target_size):
    """Génère du contenu JSON"""
    import json
    
    data = {
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0",
        "data": []
    }
    
    # Ajouter des entrées jusqu'à atteindre la taille cible
    while len(json.dumps(data)) < target_size:
        entry = {
            "id": random.randint(1000, 9999),
            "name": "".join(random.choices(string.ascii_letters, k=10)),
            "value": random.uniform(0, 100),
            "active": random.choice([True, False])
        }
        data["data"].append(entry)
    
    return json.dumps(data, indent=2)

def generate_csv_content(target_size):
    """Génère du contenu CSV"""
    content = ["ID,Name,Value,Date,Active\n"]
    current_size = len(content[0])
    
    while current_size < target_size:
        row = f"{random.randint(1, 9999)},"
        row += f"{''.join(random.choices(string.ascii_letters, k=8))},"
        row += f"{random.uniform(0, 1000):.2f},"
        row += f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d},"
        row += f"{random.choice(['True', 'False'])}\n"
        
        content.append(row)
        current_size += len(row)
    
    return "".join(content)

def generate_xml_content(target_size):
    """Génère du contenu XML"""
    content = ['<?xml version="1.0" encoding="UTF-8"?>\n<root>\n']
    current_size = sum(len(line) for line in content)
    
    while current_size < target_size - 50:  # Laisser de la place pour la fermeture
        item = f'  <item id="{random.randint(1, 9999)}">\n'
        item += f'    <name>{"".join(random.choices(string.ascii_letters, k=10))}</name>\n'
        item += f'    <value>{random.uniform(0, 100):.2f}</value>\n'
        item += f'  </item>\n'
        
        content.append(item)
        current_size += len(item)
    
    content.append('</root>\n')
    return "".join(content)

def generate_binary_content(target_size):
    """Génère du contenu binaire"""
    return bytes([random.randint(0, 255) for _ in range(target_size)])

def main():
    """Fonction principale"""
    print("=== Création de fichiers de test pour UltraCompression ===\n")
    
    test_path = create_test_directory()
    
    print("\n=== Instructions d'utilisation ===")
    print("1. Lancez UltraCompression: python ultra_compression.py")
    print(f"2. Sélectionnez le disque/dossier: {test_path.absolute()}")
    print("3. Choisissez un niveau de compression (ex: 5)")
    print("4. Cliquez sur 'Démarrer la Compression'")
    print("\n⚠️  Les fichiers de test seront supprimés après compression!")
    print("💡 Utilisez un niveau de compression faible (0-2) pour tester rapidement")

if __name__ == "__main__":
    main()
