#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour UltraCompression
Vérifie que tous les composants fonctionnent correctement
"""

import sys
import os
import subprocess
import importlib.util

def test_python_version():
    """Vérifie la version de Python"""
    print("Test de la version Python...")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ requis, version actuelle:", sys.version)
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def test_7zip_installation():
    """Vérifie l'installation de 7zip"""
    print("Test de l'installation 7zip...")
    possible_paths = [
        "7z.exe",
        "C:\\Program Files\\7-Zip\\7z.exe",
        "C:\\Program Files (x86)\\7-Zip\\7z.exe",
    ]
    
    for path in possible_paths:
        try:
            result = subprocess.run([path], capture_output=True, text=True, timeout=5)
            if "7-Zip" in result.stdout or "7-Zip" in result.stderr:
                print(f"✅ 7zip trouvé: {path}")
                return True
        except:
            continue
    
    print("❌ 7zip non trouvé ou non fonctionnel")
    return False

def test_dependencies():
    """Vérifie les dépendances Python"""
    print("Test des dépendances Python...")
    dependencies = ["tkinter", "psutil", "pathlib", "concurrent.futures"]
    
    for dep in dependencies:
        try:
            if dep == "tkinter":
                import tkinter
            elif dep == "psutil":
                import psutil
            elif dep == "pathlib":
                from pathlib import Path
            elif dep == "concurrent.futures":
                from concurrent.futures import ThreadPoolExecutor
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} non disponible")
            return False
    
    return True

def test_file_structure():
    """Vérifie la structure des fichiers"""
    print("Test de la structure des fichiers...")
    required_files = [
        "ultra_compression.py",
        "compression_optimizer.py",
        "config.py",
        "requirements.txt"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} manquant")
            return False
    
    return True

def test_imports():
    """Teste les imports des modules"""
    print("Test des imports des modules...")
    
    try:
        from compression_optimizer import CompressionOptimizer
        print("✅ CompressionOptimizer")
        
        import config
        print("✅ config")
        
        # Test de base de l'optimiseur
        optimizer = CompressionOptimizer()
        print(f"✅ Optimiseur initialisé (CPU: {optimizer.cpu_count}, Disque: {optimizer.disk_type})")
        
        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_gui_basic():
    """Test basique de l'interface graphique"""
    print("Test basique de l'interface graphique...")
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Masquer la fenêtre
        
        # Tester quelques widgets de base
        frame = tk.Frame(root)
        label = tk.Label(frame, text="Test")
        button = tk.Button(frame, text="Test")
        
        root.destroy()
        print("✅ Interface graphique fonctionnelle")
        return True
    except Exception as e:
        print(f"❌ Erreur interface graphique: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("=== Test d'UltraCompression ===\n")
    
    tests = [
        test_python_version,
        test_file_structure,
        test_dependencies,
        test_7zip_installation,
        test_imports,
        test_gui_basic
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Erreur dans {test.__name__}: {e}")
            results.append(False)
            print()
    
    # Résumé
    passed = sum(results)
    total = len(results)
    
    print("=== Résumé ===")
    print(f"Tests réussis: {passed}/{total}")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! L'application est prête à être utilisée.")
        print("\nPour lancer l'application:")
        print("  python ultra_compression.py")
        print("  ou double-cliquez sur lancer_compression.bat")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        
        if not any([results[0], results[2]]):  # Python ou dépendances
            print("\n📝 Actions recommandées:")
            print("1. Installez Python 3.7+ depuis https://python.org")
            print("2. Installez les dépendances: pip install -r requirements.txt")
        
        if not results[3]:  # 7zip
            print("3. Installez 7zip depuis https://7-zip.org")

if __name__ == "__main__":
    main()
