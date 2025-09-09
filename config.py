# -*- coding: utf-8 -*-
"""
Configuration pour UltraCompression
"""

# Extensions de fichiers à ignorer (déjà compressés)
IGNORE_EXTENSIONS = {
    '.7z', '.zip', '.rar', '.gz', '.bz2', '.xz', '.tar',
    '.z', '.lz', '.lzma', '.cab', '.arj', '.ace'
}

# Extensions de fichiers système à éviter
SYSTEM_EXTENSIONS = {
    '.sys', '.dll', '.exe', '.msi', '.tmp', '.log'
}

# Taille minimale de fichier pour la compression (en octets)
MIN_FILE_SIZE = 1024  # 1KB

# Nombre maximum de threads pour la compression
MAX_WORKER_THREADS = 4

# Paramètres 7zip optimisés par niveau de compression
COMPRESSION_PARAMS = {
    0: ["-mx0", "-mmt=on"],  # Stockage seulement
    1: ["-mx1", "-mmt=on", "-mfb=32"],
    2: ["-mx2", "-mmt=on", "-mfb=32"],
    3: ["-mx3", "-mmt=on", "-mfb=32", "-md=16m"],
    4: ["-mx4", "-mmt=on", "-mfb=32", "-md=16m"],
    5: ["-mx5", "-mmt=on", "-mfb=32", "-md=32m"],  # Équilibré
    6: ["-mx6", "-mmt=on", "-mfb=64", "-md=32m"],
    7: ["-mx7", "-mmt=on", "-mfb=64", "-md=64m"],
    8: ["-mx8", "-mmt=on", "-mfb=128", "-md=64m"],
    9: ["-mx9", "-mmt=on", "-mfb=273", "-md=128m"]  # Maximum
}

# Types de fichiers prioritaires (compressés en premier pour un feedback rapide)
PRIORITY_EXTENSIONS = {
    '.txt', '.log', '.csv', '.json', '.xml', '.html', '.css', '.js'
}

# Dossiers système à éviter
SYSTEM_FOLDERS = {
    'System Volume Information',
    '$RECYCLE.BIN',
    'Windows',
    'Program Files',
    'Program Files (x86)',
    'ProgramData',
    'Users\\Default',
    'Users\\All Users'
}
