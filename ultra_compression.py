#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UltraCompression - Application de compression intelligente avec 7zip
Compresse récursivement tous les fichiers d'un disque externe avec optimisation de vitesse
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import subprocess
import threading
import time
import psutil
from pathlib import Path
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
from compression_optimizer import CompressionOptimizer
import config

class UltraCompressionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UltraCompression - Compression Intelligente 7zip")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        # Variables d'état
        self.is_compressing = False
        self.compression_thread = None
        self.total_files = 0
        self.processed_files = 0
        self.progress_queue = queue.Queue(maxsize=1000)  # Limiter la taille de la queue
        self.selected_drive = tk.StringVar()
        self.compression_level = tk.IntVar(value=5)
        
        # Optimiseur de compression
        self.optimizer = CompressionOptimizer()
        
        # Vérifier la présence de 7zip
        self.seven_zip_path = self.find_7zip()
        if not self.seven_zip_path:
            messagebox.showerror("Erreur", "7zip n'est pas installé ou introuvable dans le PATH")
            sys.exit(1)
            
        self.setup_ui()
        self.update_drives()
        
        # Log d'initialisation
        self.log_realtime("🚀 UltraCompression initialisé", "INFO")
        self.log_realtime(f"📦 7zip trouvé: {os.path.basename(self.seven_zip_path)}", "INFO")
        self.log_realtime(f"💻 Système: {self.optimizer.disk_type}, {self.optimizer.cpu_count} cores", "INFO")
        
        # Démarrer la mise à jour de la progression
        self.root.after(100, self.update_progress)
    
    def find_7zip(self):
        """Trouve l'exécutable 7zip sur le système"""
        possible_paths = [
            "7z.exe",  # Dans le PATH
            "C:\\Program Files\\7-Zip\\7z.exe",
            "C:\\Program Files (x86)\\7-Zip\\7z.exe",
        ]
        
        for path in possible_paths:
            if shutil.which(path) or os.path.exists(path):
                return path
        return None
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration de la grille
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Titre
        title_label = ttk.Label(main_frame, text="UltraCompression", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sélection du disque
        ttk.Label(main_frame, text="Disque externe:", 
                 font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.drive_combo = ttk.Combobox(main_frame, textvariable=self.selected_drive, 
                                       state="readonly", width=40)
        self.drive_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        refresh_btn = ttk.Button(main_frame, text="Actualiser", 
                                command=self.update_drives)
        refresh_btn.grid(row=1, column=2, padx=(10, 0), pady=5)
        
        # Niveau de compression
        ttk.Label(main_frame, text="Niveau de compression:", 
                 font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        compression_frame = ttk.Frame(main_frame)
        compression_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.compression_scale = ttk.Scale(compression_frame, from_=0, to=9, 
                                          variable=self.compression_level, 
                                          orient=tk.HORIZONTAL, length=300)
        self.compression_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.compression_label = ttk.Label(compression_frame, text="Niveau 5 (Équilibré)")
        self.compression_label.grid(row=1, column=0, pady=(5, 0))
        
        self.compression_scale.configure(command=self.update_compression_label)
        
        # Frame pour informations et logs (côte à côte)
        info_logs_frame = ttk.Frame(main_frame)
        info_logs_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        info_logs_frame.columnconfigure(0, weight=1)
        info_logs_frame.columnconfigure(1, weight=1)
        
        # Informations sur la compression (à gauche)
        info_frame = ttk.LabelFrame(info_logs_frame, text="Informations", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Fichiers traités:").grid(row=0, column=0, sticky=tk.W)
        self.files_label = ttk.Label(info_frame, text="0 / 0")
        self.files_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(info_frame, text="Statut:").grid(row=1, column=0, sticky=tk.W)
        self.status_label = ttk.Label(info_frame, text="Prêt")
        self.status_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(info_frame, text="Fichier actuel:").grid(row=2, column=0, sticky=tk.W)
        self.current_file_label = ttk.Label(info_frame, text="Aucun")
        self.current_file_label.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        ttk.Label(info_frame, text="Temps estimé:").grid(row=3, column=0, sticky=tk.W)
        self.time_estimate_label = ttk.Label(info_frame, text="Calcul en cours...")
        self.time_estimate_label.grid(row=3, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(info_frame, text="Optimisations:").grid(row=4, column=0, sticky=tk.W)
        self.optimizations_label = ttk.Label(info_frame, text="Détection automatique")
        self.optimizations_label.grid(row=4, column=1, sticky=tk.W, padx=(10, 0))
        
        # Section logs en temps réel (à droite)
        logs_frame = ttk.LabelFrame(info_logs_frame, text="Logs en Temps Réel", padding="10")
        logs_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(1, weight=1)
        
        # Boutons de contrôle des logs
        logs_buttons_frame = ttk.Frame(logs_frame)
        logs_buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        logs_buttons_frame.columnconfigure(2, weight=1)
        
        self.copy_logs_btn = ttk.Button(logs_buttons_frame, text="📋 Copier", 
                                       command=self.copy_logs_to_clipboard, width=8)
        self.copy_logs_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.clear_logs_btn = ttk.Button(logs_buttons_frame, text="🗑️ Effacer", 
                                        command=self.clear_real_time_logs, width=8)
        self.clear_logs_btn.grid(row=0, column=1, padx=(5, 0))
        
        # Zone de texte pour les logs en temps réel
        self.realtime_log_text = tk.Text(logs_frame, height=8, wrap=tk.WORD, 
                                        font=("Consolas", 9), state=tk.DISABLED)
        logs_scrollbar = ttk.Scrollbar(logs_frame, orient=tk.VERTICAL, 
                                      command=self.realtime_log_text.yview)
        self.realtime_log_text.configure(yscrollcommand=logs_scrollbar.set)
        
        self.realtime_log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        logs_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Barre de progression
        progress_frame = ttk.LabelFrame(main_frame, text="Progression", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_text = ttk.Label(progress_frame, text="0%")
        self.progress_text.grid(row=1, column=0)
        
        # Boutons de contrôle
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        self.start_btn = ttk.Button(button_frame, text="Démarrer la Compression", 
                                   command=self.start_compression, style='Accent.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Arrêter", 
                                  command=self.stop_compression, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.quit_btn = ttk.Button(button_frame, text="Quitter", command=self.quit_app)
        self.quit_btn.pack(side=tk.LEFT)
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="Journal", padding="10")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=20)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def update_compression_label(self, value):
        """Met à jour le label du niveau de compression"""
        level = int(float(value))
        descriptions = {
            0: "Aucune compression (Très rapide)",
            1: "Compression minimale (Rapide)",
            2: "Compression faible",
            3: "Compression normale",
            4: "Compression normale+",
            5: "Compression équilibrée",
            6: "Compression élevée",
            7: "Compression très élevée",
            8: "Compression ultra",
            9: "Compression maximale (Très lent)"
        }
        self.compression_label.config(text=f"Niveau {level} ({descriptions[level]})")
    
    def update_drives(self):
        """Met à jour la liste des disques disponibles"""
        drives = []
        for partition in psutil.disk_partitions():
            if 'removable' in partition.opts or partition.mountpoint != 'C:\\':
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    size_gb = usage.total / (1024**3)
                    free_gb = usage.free / (1024**3)
                    drives.append(f"{partition.mountpoint} ({size_gb:.1f}GB total, {free_gb:.1f}GB libre)")
                except:
                    drives.append(f"{partition.mountpoint} (Inaccessible)")
        
        self.drive_combo['values'] = drives
        if drives and not self.selected_drive.get():
            self.drive_combo.current(0)
    
    def log_message(self, message):
        """Ajoute un message au journal principal"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def log_realtime(self, message, level="INFO"):
        """Ajoute un message aux logs en temps réel de façon asynchrone et non-bloquante"""
        try:
            import datetime
            now = datetime.datetime.now()
            timestamp = now.strftime("%H:%M:%S.") + f"{now.microsecond//1000:03d}"
            
            # Définir les couleurs selon le niveau
            colors = {
                "INFO": "black",
                "ANALYSIS": "blue",
                "COMPRESS": "green",
                "ERROR": "red",
                "WARNING": "orange",
                "SUCCESS": "dark green"
            }
            color = colors.get(level, "black")
            
            # Ajouter au queue de manière non-bloquante
            try:
                self.progress_queue.put_nowait(("realtime_log", timestamp, level, message, color))
            except queue.Full:
                # Si la queue est pleine, ignorer ce log pour éviter le blocage
                pass
        except Exception:
            # En cas d'erreur, ne pas bloquer l'application
            pass
    
    def copy_logs_to_clipboard(self):
        """Copie les logs en temps réel dans le presse-papier"""
        try:
            logs_content = self.realtime_log_text.get("1.0", tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(logs_content)
            self.log_message("Logs copiés dans le presse-papier")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de copier les logs: {e}")
    
    def clear_real_time_logs(self):
        """Efface les logs en temps réel"""
        self.realtime_log_text.config(state=tk.NORMAL)
        self.realtime_log_text.delete("1.0", tk.END)
        self.realtime_log_text.config(state=tk.DISABLED)
        self.log_message("Logs en temps réel effacés")
    
    def get_drive_path(self):
        """Extrait le chemin du disque sélectionné"""
        drive_text = self.selected_drive.get()
        if drive_text:
            return drive_text.split(' ')[0]
        return None
    
    def count_files(self, path):
        """Compte le nombre total de fichiers à traiter avec logs détaillés"""
        count = 0
        total_files_found = 0
        ignored_files = 0
        ignored_dirs = 0
        
        try:
            self.log_realtime(f"📂 Début du scan récursif de: {path}", "ANALYSIS")
            
            for root, dirs, files in os.walk(path):
                if not self.is_compressing:
                    break
                
                # Afficher le répertoire en cours d'analyse
                rel_path = os.path.relpath(root, path)
                if rel_path != ".":
                    self.log_realtime(f"📁 Scan: {rel_path}", "ANALYSIS")
                
                # Compter les fichiers trouvés dans ce répertoire
                total_files_found += len(files)
                
                # Filtrer les dossiers système et logger les exclusions
                original_dirs = dirs.copy()
                dirs[:] = [d for d in dirs if not any(sys_folder in os.path.join(root, d) 
                          for sys_folder in config.SYSTEM_FOLDERS)]
                
                excluded_dirs = set(original_dirs) - set(dirs)
                for excluded_dir in excluded_dirs:
                    ignored_dirs += 1
                    self.log_realtime(f"🚫 Dossier ignoré: {excluded_dir} (système)", "WARNING")
                
                # Analyser chaque fichier
                eligible_in_dir = 0
                ignored_in_dir = 0
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.optimizer.should_compress_file(file_path):
                        count += 1
                        eligible_in_dir += 1
                    else:
                        ignored_files += 1
                        ignored_in_dir += 1
                        # Logger seulement quelques exemples pour éviter la surcharge
                        if ignored_in_dir <= 3:  # Limiter à 3 exemples par répertoire
                            reason = self._get_exclusion_reason(file_path)
                            self.log_realtime(f"⚠️ Fichier ignoré: {file} ({reason})", "WARNING")
                        elif ignored_in_dir == 4:
                            self.log_realtime(f"⚠️ ... et {len(files) - eligible_in_dir - 3} autres fichiers ignorés", "WARNING")
                
                # Résumé pour ce répertoire
                if files:  # Seulement si le répertoire contient des fichiers
                    dir_name = os.path.basename(root) if rel_path != "." else "racine"
                    self.log_realtime(f"📊 {dir_name}: {eligible_in_dir}/{len(files)} fichiers éligibles", "ANALYSIS")
            
            # Résumé final de l'analyse
            self.log_realtime(f"✅ Analyse terminée:", "ANALYSIS")
            self.log_realtime(f"   📁 Fichiers trouvés: {total_files_found}", "ANALYSIS")
            self.log_realtime(f"   ✅ Fichiers éligibles: {count}", "ANALYSIS")
            self.log_realtime(f"   ⚠️ Fichiers ignorés: {ignored_files}", "ANALYSIS")
            self.log_realtime(f"   🚫 Dossiers ignorés: {ignored_dirs}", "ANALYSIS")
            
        except Exception as e:
            self.log_message(f"Erreur lors du comptage des fichiers: {e}")
            self.log_realtime(f"💥 Erreur d'analyse: {e}", "ERROR")
            
        return count
    
    def _get_exclusion_reason(self, file_path):
        """Détermine la raison pour laquelle un fichier est exclu"""
        try:
            path_obj = Path(file_path)
            
            # Vérifier les dossiers système
            if any(sys_folder in str(path_obj) for sys_folder in config.SYSTEM_FOLDERS):
                return "dossier système"
            
            # Vérifier les extensions système
            if path_obj.suffix.lower() in config.SYSTEM_EXTENSIONS:
                return "extension système"
            
            # Vérifier les fichiers déjà compressés
            if path_obj.suffix.lower() in config.IGNORE_EXTENSIONS:
                return "déjà compressé"
            
            # Vérifier la taille minimale
            if os.path.getsize(file_path) < config.MIN_FILE_SIZE:
                return "trop petit"
            
            return "autre raison"
            
        except Exception:
            return "erreur d'accès"
    
    def compress_file(self, file_path, compression_level):
        """Compresse un fichier individuel avec 7zip"""
        try:
            output_path = file_path + ".7z"
            filename = os.path.basename(file_path)
            
            # Log du début de compression
            self.log_realtime(f"🔄 {filename}", "COMPRESS")
            
            # Obtenir les paramètres optimisés
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            optimized_params = self.optimizer.get_optimal_compression_params(compression_level, file_size)
            
            # Construire la commande 7zip optimisée
            cmd = [self.seven_zip_path, "a"] + optimized_params + [output_path, file_path]
            
            # Exécuter la commande sans interface
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                # Supprimer le fichier original si la compression a réussi
                try:
                    os.remove(file_path)
                    # Calculer le taux de compression
                    original_size = file_size
                    compressed_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
                    ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
                    
                    return True, f"Compressé: {os.path.basename(file_path)} ({ratio:.1f}% économisé)"
                except OSError as e:
                    return False, f"Erreur suppression {os.path.basename(file_path)}: {e}"
            else:
                return False, f"Erreur compression {os.path.basename(file_path)}: {result.stderr}"
                
        except Exception as e:
            return False, f"Erreur: {e}"
    
    def compression_worker(self):
        """Thread principal de compression"""
        drive_path = self.get_drive_path()
        if not drive_path or not os.path.exists(drive_path):
            self.progress_queue.put(("error", "Disque sélectionné invalide"))
            return
        
        self.log_message(f"Démarrage de la compression sur {drive_path}")
        self.log_message(f"Niveau de compression: {self.compression_level.get()}")
        self.log_realtime(f"🚀 Initialisation de la compression", "INFO")
        self.log_realtime(f"📁 Disque cible: {drive_path}", "INFO")
        self.log_realtime(f"⚙️ Niveau de compression: {self.compression_level.get()}", "INFO")
        
        # Compter les fichiers
        self.progress_queue.put(("status", "Analyse des fichiers..."))
        self.log_realtime("🔍 Début de l'analyse des fichiers...", "ANALYSIS")
        self.total_files = self.count_files(drive_path)
        self.progress_queue.put(("total", self.total_files))
        
        if self.total_files == 0:
            self.log_realtime("⚠️ Aucun fichier éligible trouvé", "WARNING")
            self.progress_queue.put(("complete", "Aucun fichier à compresser"))
            return
        
        self.log_message(f"Fichiers à traiter: {self.total_files}")
        self.log_realtime(f"📊 {self.total_files} fichiers éligibles détectés", "ANALYSIS")
        
        # Collecter tous les fichiers éligibles
        self.log_realtime("📋 Collecte des fichiers pour la compression...", "ANALYSIS")
        files_to_compress = []
        current_dir = ""
        collected_count = 0
        
        for root, dirs, files in os.walk(drive_path):
            if not self.is_compressing:
                self.log_realtime("⏹️ Collecte interrompue par l'utilisateur", "WARNING")
                break
            
            # Log du répertoire en cours de collecte (seulement tous les 10 répertoires)
            if root != current_dir:
                current_dir = root
                rel_path = os.path.relpath(root, drive_path)
                if rel_path != "." and len(files_to_compress) % 50 == 0:  # Log tous les 50 fichiers collectés
                    self.log_realtime(f"📁 Collecte: {rel_path} ({len(files_to_compress)} fichiers collectés)", "ANALYSIS")
            
            # Filtrer les dossiers système
            dirs[:] = [d for d in dirs if not any(sys_folder in os.path.join(root, d) 
                      for sys_folder in config.SYSTEM_FOLDERS)]
            
            # Collecter les fichiers éligibles
            eligible_in_dir = 0
            for file in files:
                file_path = os.path.join(root, file)
                if self.optimizer.should_compress_file(file_path):
                    files_to_compress.append(file_path)
                    collected_count += 1
                    eligible_in_dir += 1
            
            # Log du nombre de fichiers collectés (seulement pour les gros répertoires)
            if eligible_in_dir > 10:  # Seulement si plus de 10 fichiers dans le répertoire
                dir_name = os.path.basename(root) if rel_path != "." else "racine"
                self.log_realtime(f"✅ {dir_name}: {eligible_in_dir} fichiers ajoutés à la file", "ANALYSIS")
        
        self.log_realtime(f"📦 Collecte terminée: {collected_count} fichiers prêts pour compression", "ANALYSIS")
        
        # Optimiser l'ordre des fichiers pour maximiser la vitesse
        self.progress_queue.put(("status", "Optimisation de l'ordre des fichiers..."))
        self.log_realtime("🔧 Optimisation de l'ordre des fichiers...", "ANALYSIS")
        
        # Analyser les types de fichiers avant optimisation
        file_types = {}
        total_size = 0
        for file_path in files_to_compress:
            try:
                ext = Path(file_path).suffix.lower() or "sans_extension"
                size = os.path.getsize(file_path)
                file_types[ext] = file_types.get(ext, 0) + 1
                total_size += size
            except:
                continue
        
        # Logger les statistiques des types de fichiers
        self.log_realtime("📈 Analyse des types de fichiers:", "ANALYSIS")
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:  # Top 10
            self.log_realtime(f"   {ext}: {count} fichiers", "ANALYSIS")
        
        self.log_realtime(f"💾 Taille totale à compresser: {total_size/(1024*1024):.1f} MB", "ANALYSIS")
        
        # Optimisation de l'ordre
        self.log_realtime("🎯 Tri par priorité et taille...", "ANALYSIS")
        files_to_compress = self.optimizer.optimize_file_order(files_to_compress)
        
        self.log_realtime("📂 Groupement par répertoire...", "ANALYSIS")
        files_to_compress = self.optimizer.group_files_by_location(files_to_compress)
        
        # Estimer le temps de compression
        self.log_realtime("📈 Calcul des estimations de performance...", "ANALYSIS")
        estimation = self.optimizer.estimate_compression_time(files_to_compress)
        self.log_message(f"Estimation: {estimation['estimated_minutes']:.1f} minutes pour {estimation['total_size_mb']:.1f} MB")
        self.progress_queue.put(("time_estimate", f"{estimation['estimated_minutes']:.1f} min"))
        
        # Détails de l'estimation
        self.log_realtime("⏱️ Estimations détaillées:", "ANALYSIS")
        self.log_realtime(f"   📊 Taille totale: {estimation['total_size_mb']:.1f} MB", "ANALYSIS")
        self.log_realtime(f"   📈 Vitesse estimée: {estimation['total_size_mb']/estimation['estimated_minutes']:.1f} MB/min", "ANALYSIS")
        self.log_realtime(f"   ⏱️ Temps estimé: {estimation['estimated_minutes']:.1f} minutes", "ANALYSIS")
        
        # Informations d'optimisation
        disk_type = self.optimizer.disk_type
        cpu_count = self.optimizer.cpu_count
        available_ram = self.optimizer.available_memory / (1024**3)  # GB
        
        self.progress_queue.put(("optimizations", f"{disk_type}, {cpu_count} CPU cores"))
        self.log_realtime("🔧 Configuration système détectée:", "INFO")
        self.log_realtime(f"   💾 Type de disque: {disk_type}", "INFO")
        self.log_realtime(f"   🖥️ CPU cores: {cpu_count}", "INFO")
        self.log_realtime(f"   💻 RAM disponible: {available_ram:.1f} GB", "INFO")
        
        # Nombre optimal de workers
        max_workers = self.optimizer.get_optimal_thread_count(len(files_to_compress))
        self.log_message(f"Utilisation de {max_workers} threads pour la compression")
        self.log_realtime("⚡ Optimisations appliquées:", "INFO")
        self.log_realtime(f"   🔀 Threads parallèles: {max_workers}", "INFO")
        self.log_realtime(f"   📋 Ordre optimisé: {len(files_to_compress)} fichiers", "INFO")
        
        # Paramètres 7zip pour ce niveau
        sample_params = self.optimizer.get_optimal_compression_params(self.compression_level.get())
        self.log_realtime(f"   🗜️ Paramètres 7zip: {' '.join(sample_params[:3])}", "INFO")
        
        self.log_realtime("🎯 Début de la compression...", "COMPRESS")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Soumettre les tâches
            future_to_file = {
                executor.submit(self.compress_file, file_path, self.compression_level.get()): file_path
                for file_path in files_to_compress
            }
            
            for future in as_completed(future_to_file):
                if not self.is_compressing:
                    break
                    
                file_path = future_to_file[future]
                try:
                    success, message = future.result()
                    self.processed_files += 1
                    
                    self.progress_queue.put(("progress", self.processed_files, os.path.basename(file_path)))
                    
                    if success:
                        self.progress_queue.put(("log", message))
                        # Log en temps réel pour succès
                        filename = os.path.basename(file_path)
                        self.log_realtime(f"✅ {filename}", "SUCCESS")
                    else:
                        self.progress_queue.put(("error_log", message))
                        # Log en temps réel pour erreur
                        filename = os.path.basename(file_path)
                        self.log_realtime(f"❌ {filename} - {message}", "ERROR")
                        
                except Exception as e:
                    self.progress_queue.put(("error_log", f"Erreur inattendue: {e}"))
                    filename = os.path.basename(file_path)
                    self.log_realtime(f"💥 {filename} - Erreur inattendue: {e}", "ERROR")
                    self.processed_files += 1
        
        if self.is_compressing:
            self.log_realtime("🎉 Compression terminée avec succès!", "SUCCESS")
            self.progress_queue.put(("complete", f"Compression terminée! {self.processed_files} fichiers traités"))
        else:
            self.log_realtime("⏹️ Compression arrêtée par l'utilisateur", "WARNING")
            self.progress_queue.put(("stopped", "Compression arrêtée par l'utilisateur"))
    
    def update_progress(self):
        """Met à jour l'interface avec les informations de progression"""
        try:
            while not self.progress_queue.empty():
                item = self.progress_queue.get_nowait()
                
                if item[0] == "status":
                    self.status_label.config(text=item[1])
                    
                elif item[0] == "total":
                    self.total_files = item[1]
                    self.files_label.config(text=f"0 / {self.total_files}")
                    
                elif item[0] == "progress":
                    processed, current_file = item[1], item[2]
                    self.files_label.config(text=f"{processed} / {self.total_files}")
                    self.current_file_label.config(text=current_file)
                    
                    if self.total_files > 0:
                        progress_percent = (processed / self.total_files) * 100
                        self.progress_bar['value'] = progress_percent
                        self.progress_text.config(text=f"{progress_percent:.1f}%")
                    
                elif item[0] == "log":
                    self.log_message(item[1])
                    
                elif item[0] == "error_log":
                    self.log_message(f"ERREUR: {item[1]}")
                
                elif item[0] == "time_estimate":
                    self.time_estimate_label.config(text=item[1])
                
                elif item[0] == "optimizations":
                    self.optimizations_label.config(text=item[1])
                
                elif item[0] == "realtime_log":
                    try:
                        timestamp, level, message, color = item[1], item[2], item[3], item[4]
                        self.realtime_log_text.config(state=tk.NORMAL)
                        
                        # Ajouter le message de manière simplifiée
                        log_line = f"[{timestamp}] {message}\n"
                        self.realtime_log_text.insert(tk.END, log_line)
                        
                        # Appliquer la couleur de manière optimisée
                        start_pos = self.realtime_log_text.index(f"{tk.END}-1c linestart")
                        end_pos = self.realtime_log_text.index(f"{tk.END}-1c")
                        
                        # Créer un tag pour cette couleur si nécessaire
                        tag_name = f"color_{level.lower()}"
                        if tag_name not in self.realtime_log_text.tag_names():
                            self.realtime_log_text.tag_configure(tag_name, foreground=color)
                        
                        # Appliquer le tag à la ligne (après le timestamp)
                        timestamp_end = f"{start_pos}+{len(f'[{timestamp}] ')}c"
                        self.realtime_log_text.tag_add(tag_name, timestamp_end, end_pos)
                        
                        # Faire défiler vers le bas seulement si nécessaire
                        self.realtime_log_text.see(tk.END)
                        
                        # Limiter à 500 lignes pour de meilleures performances
                        lines = int(self.realtime_log_text.index('end-1c').split('.')[0])
                        if lines > 500:
                            self.realtime_log_text.delete("1.0", "50.0")  # Supprimer les 50 premières lignes
                        
                        self.realtime_log_text.config(state=tk.DISABLED)
                    except Exception:
                        # En cas d'erreur, ignorer ce log pour éviter le crash
                        pass
                    
                elif item[0] == "error":
                    messagebox.showerror("Erreur", item[1])
                    self.reset_ui()
                    
                elif item[0] == "complete":
                    self.log_message(item[1])
                    messagebox.showinfo("Terminé", item[1])
                    self.reset_ui()
                    
                elif item[0] == "stopped":
                    self.log_message(item[1])
                    self.reset_ui()
                    
        except queue.Empty:
            pass
        
        # Programmer la prochaine mise à jour avec une fréquence adaptative
        if self.is_compressing:
            # Plus fréquent pendant la compression pour la réactivité
            self.root.after(50, self.update_progress)
        else:
            # Moins fréquent quand inactif pour économiser les ressources
            self.root.after(200, self.update_progress)
    
    def start_compression(self):
        """Démarre le processus de compression"""
        if not self.selected_drive.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un disque")
            return
        
        if self.is_compressing:
            return
        
        # Confirmation
        drive_path = self.get_drive_path()
        result = messagebox.askyesno(
            "Confirmation",
            f"Êtes-vous sûr de vouloir compresser tous les fichiers sur {drive_path}?\n"
            f"Les fichiers originaux seront supprimés après compression.\n"
            f"Niveau de compression: {self.compression_level.get()}"
        )
        
        if not result:
            return
        
        # Démarrer la compression
        self.is_compressing = True
        self.processed_files = 0
        
        # Mettre à jour l'interface
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.drive_combo.config(state=tk.DISABLED)
        self.compression_scale.config(state=tk.DISABLED)
        
        self.status_label.config(text="Initialisation...")
        self.progress_bar['value'] = 0
        self.progress_text.config(text="0%")
        
        # Démarrer le thread de compression
        self.compression_thread = threading.Thread(target=self.compression_worker, daemon=True)
        self.compression_thread.start()
    
    def stop_compression(self):
        """Arrête le processus de compression"""
        self.is_compressing = False
        self.log_message("Arrêt de la compression demandé...")
    
    def reset_ui(self):
        """Remet l'interface dans son état initial"""
        self.is_compressing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.drive_combo.config(state="readonly")
        self.compression_scale.config(state=tk.NORMAL)
        self.status_label.config(text="Prêt")
        self.current_file_label.config(text="Aucun")
    
    def quit_app(self):
        """Ferme l'application"""
        if self.is_compressing:
            result = messagebox.askyesno(
                "Confirmation",
                "Une compression est en cours. Voulez-vous vraiment quitter?"
            )
            if not result:
                return
            self.is_compressing = False
        
        self.root.quit()


def main():
    """Point d'entrée principal"""
    root = tk.Tk()
    app = UltraCompressionApp(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.quit_app()


if __name__ == "__main__":
    main()
