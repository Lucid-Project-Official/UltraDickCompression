# -*- coding: utf-8 -*-
"""
Module d'optimisation pour la compression avec 7zip
Contient des algorithmes pour maximiser la vitesse de compression
"""

import os
import psutil
from pathlib import Path
from collections import defaultdict
import config

class CompressionOptimizer:
    """Optimise l'ordre et la méthode de compression des fichiers"""
    
    def __init__(self):
        self.cpu_count = os.cpu_count()
        self.available_memory = psutil.virtual_memory().available
        self.disk_type = self._detect_disk_type()
    
    def _detect_disk_type(self):
        """Détecte le type de disque (SSD/HDD) pour optimiser les paramètres"""
        try:
            # Heuristique simple basée sur les performances de lecture
            import time
            test_file = Path.cwd() / "temp_test_file"
            
            # Créer un fichier test
            with open(test_file, 'wb') as f:
                f.write(b'0' * 1024 * 1024)  # 1MB
            
            # Mesurer le temps de lecture
            start_time = time.time()
            with open(test_file, 'rb') as f:
                f.read()
            read_time = time.time() - start_time
            
            # Nettoyer
            test_file.unlink()
            
            # SSD si lecture très rapide (< 10ms pour 1MB)
            return "SSD" if read_time < 0.01 else "HDD"
            
        except Exception:
            return "HDD"  # Par défaut
    
    def optimize_file_order(self, file_paths):
        """
        Optimise l'ordre de traitement des fichiers pour maximiser la vitesse
        """
        files_info = []
        
        for file_path in file_paths:
            try:
                stat = os.stat(file_path)
                ext = Path(file_path).suffix.lower()
                
                files_info.append({
                    'path': file_path,
                    'size': stat.st_size,
                    'extension': ext,
                    'priority': self._get_file_priority(ext, stat.st_size)
                })
            except (OSError, IOError):
                continue
        
        # Trier par priorité puis par taille
        files_info.sort(key=lambda x: (x['priority'], x['size']))
        
        return [f['path'] for f in files_info]
    
    def _get_file_priority(self, extension, size):
        """Calcule la priorité d'un fichier (plus bas = plus prioritaire)"""
        priority = 5  # Priorité par défaut
        
        # Fichiers prioritaires (feedback rapide)
        if extension in config.PRIORITY_EXTENSIONS:
            priority -= 2
        
        # Petits fichiers d'abord
        if size < 10 * 1024 * 1024:  # < 10MB
            priority -= 1
        elif size > 100 * 1024 * 1024:  # > 100MB
            priority += 2
        
        # Fichiers déjà compressés (très basse priorité)
        if extension in config.IGNORE_EXTENSIONS:
            priority += 10
        
        return priority
    
    def get_optimal_compression_params(self, compression_level, file_size=0):
        """
        Retourne les paramètres 7zip optimisés selon le contexte
        """
        base_params = config.COMPRESSION_PARAMS.get(compression_level, config.COMPRESSION_PARAMS[5])
        optimized_params = base_params.copy()
        
        # Optimisations selon le type de disque
        if self.disk_type == "SSD":
            # SSD: Privilégier le CPU over I/O
            optimized_params.append("-mqs=on")  # Quick sort
            optimized_params.append("-ms=on")   # Solid archive
        else:
            # HDD: Réduire les accès disque
            optimized_params.append("-mqs=off")
            optimized_params.append("-ms=off")
        
        # Optimisations selon la taille du fichier
        if file_size > 100 * 1024 * 1024:  # > 100MB
            # Gros fichiers: plus de mémoire, moins de threads
            if "-md=16m" in optimized_params:
                optimized_params[optimized_params.index("-md=16m")] = "-md=64m"
            elif "-md=32m" in optimized_params:
                optimized_params[optimized_params.index("-md=32m")] = "-md=128m"
        
        # Optimisations selon la mémoire disponible
        available_gb = self.available_memory / (1024**3)
        if available_gb < 4:  # < 4GB RAM
            # Réduire l'usage mémoire
            optimized_params = [p for p in optimized_params if not p.startswith("-md=")]
            optimized_params.append("-md=16m")
        
        return optimized_params
    
    def get_optimal_thread_count(self, file_count):
        """Calcule le nombre optimal de threads selon le contexte"""
        base_threads = min(config.MAX_WORKER_THREADS, self.cpu_count)
        
        # Ajustements selon le nombre de fichiers
        if file_count < 10:
            return 1  # Peu de fichiers: un seul thread suffit
        elif file_count < 100:
            return min(2, base_threads)
        else:
            return base_threads
    
    def should_compress_file(self, file_path):
        """Détermine si un fichier doit être compressé"""
        try:
            path_obj = Path(file_path)
            
            # Ignorer les fichiers système
            if any(sys_folder in str(path_obj) for sys_folder in config.SYSTEM_FOLDERS):
                return False
            
            # Ignorer les extensions système
            if path_obj.suffix.lower() in config.SYSTEM_EXTENSIONS:
                return False
            
            # Ignorer les fichiers déjà compressés
            if path_obj.suffix.lower() in config.IGNORE_EXTENSIONS:
                return False
            
            # Ignorer les fichiers trop petits
            if os.path.getsize(file_path) < config.MIN_FILE_SIZE:
                return False
            
            return True
            
        except (OSError, IOError):
            return False
    
    def estimate_compression_time(self, file_paths):
        """Estime le temps total de compression"""
        total_size = 0
        file_count = 0
        
        for file_path in file_paths:
            if self.should_compress_file(file_path):
                try:
                    total_size += os.path.getsize(file_path)
                    file_count += 1
                except (OSError, IOError):
                    continue
        
        # Estimation basée sur des benchmarks typiques
        # Vitesse approximative: 50MB/s pour compression niveau 5
        base_speed_mbs = 50
        
        # Ajustements selon le type de disque
        if self.disk_type == "SSD":
            base_speed_mbs *= 1.5
        
        # Ajustements selon le CPU
        cpu_factor = min(2.0, self.cpu_count / 4.0)
        effective_speed = base_speed_mbs * cpu_factor
        
        total_size_mb = total_size / (1024 * 1024)
        estimated_seconds = total_size_mb / effective_speed
        
        return {
            'total_files': file_count,
            'total_size_mb': total_size_mb,
            'estimated_seconds': estimated_seconds,
            'estimated_minutes': estimated_seconds / 60
        }
    
    def group_files_by_location(self, file_paths):
        """Groupe les fichiers par répertoire pour optimiser l'accès disque"""
        groups = defaultdict(list)
        
        for file_path in file_paths:
            directory = os.path.dirname(file_path)
            groups[directory].append(file_path)
        
        # Trier les groupes par nombre de fichiers (plus gros groupes d'abord)
        sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        # Retourner les fichiers dans l'ordre optimisé
        optimized_order = []
        for directory, files in sorted_groups:
            # Trier les fichiers du répertoire par taille
            files.sort(key=lambda x: os.path.getsize(x) if os.path.exists(x) else 0)
            optimized_order.extend(files)
        
        return optimized_order
