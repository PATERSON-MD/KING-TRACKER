"""
Configuration du Pinterest Video Downloader Bot
Toutes les variables de configuration centralisées ici
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# ============================================================================
# 1. CONFIGURATION DU BOT TELEGRAM
# ============================================================================

# Token du bot Telegram - À MODIFIER OBLIGATOIREMENT
# Obtenez-le auprès de @BotFather sur Telegram
TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")

# Liste des administrateurs (IDs Telegram)
# Ajoutez votre ID pour avoir accès aux commandes admin
ADMIN_IDS: List[int] = []

# Mode debug
DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Nom du bot (affiché dans les messages)
BOT_NAME: str = "Pinterest Downloader Bot"

# Nom d'utilisateur du bot (sans le @)
BOT_USERNAME: str = ""  # Sera automatiquement détecté

# Langue par défaut
DEFAULT_LANGUAGE: str = "fr"

# ============================================================================
# 2. CONFIGURATION DES TÉLÉCHARGEMENTS
# ============================================================================

# Taille maximale des fichiers pour Telegram (en bytes)
# Telegram limite à 50MB pour les fichiers vidéo
MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB

# Taille recommandée (pour éviter les problèmes)
RECOMMENDED_MAX_SIZE: int = 45 * 1024 * 1024  # 45 MB

# Durée maximale des vidéos (en secondes)
MAX_VIDEO_DURATION: int = 600  # 10 minutes

# Qualité par défaut
DEFAULT_QUALITY: str = "best[height<=1080]"  # Maximum 1080p

# Formats supportés
SUPPORTED_FORMATS: List[str] = ["mp4", "webm", "mkv"]

# Extension par défaut pour les fichiers
DEFAULT_EXTENSION: str = "mp4"

# ============================================================================
# 3. CONFIGURATION DES DOSSIERS
# ============================================================================

# Dossier de base
BASE_DIR: Path = Path(__file__).parent.absolute()

# Dossier temporaire pour les téléchargements
TEMP_DIR: Path = BASE_DIR / "temp"

# Sous-dossiers organisés
SUBDIRS: Dict[str, Path] = {
    "videos": TEMP_DIR / "videos",
    "thumbnails": TEMP_DIR / "thumbnails",
    "logs": TEMP_DIR / "logs",
    "cache": TEMP_DIR / "cache",
}

# Durée de conservation des fichiers temporaires (en heures)
TEMP_FILE_RETENTION_HOURS: int = 1

# ============================================================================
# 4. CONFIGURATION DES LOGS
# ============================================================================

# Niveau de log
LOG_LEVEL: int = logging.DEBUG if DEBUG_MODE else logging.INFO

# Format des logs
LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Fichier de log principal
LOG_FILE: Path = TEMP_DIR / "logs" / "bot.log"

# Rotation des logs (taille maximale en bytes)
LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT: int = 5

# ============================================================================
# 5. CONFIGURATION PINTEREST
# ============================================================================

# URLs Pinterest supportées
PINTEREST_URL_PATTERNS: List[str] = [
    r'https?://(www\.)?pinterest\.(com|fr|de|es|it|co\.uk)/pin/\d+',
    r'https?://(www\.)?pinterest\.(com|fr|de|es|it|co\.uk)/[^/]+/pin/\d+',
    r'https?://pin\.it/[a-zA-Z0-9]+',
    r'https?://pinterest\.com/pin/\d+',
    r'https?://pinterest\.fr/pin/\d+',
    r'pinterest://pin/\d+',
]

# Headers pour les requêtes HTTP
HTTP_HEADERS: Dict[str, str] = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}

# Timeout pour les requêtes HTTP (en secondes)
HTTP_TIMEOUT: int = 30

# Nombre maximum de tentatives
MAX_RETRIES: int = 3

# Délai entre les tentatives (en secondes)
RETRY_DELAY: int = 2

# ============================================================================
# 6. CONFIGURATION yt-dlp
# ============================================================================

YTDLP_OPTIONS: Dict[str, Any] = {
    # Options générales
    'quiet': True,
    'no_warnings': True,
    'ignoreerrors': True,
    'no_color': True,
    
    # Options de téléchargement
    'format': 'best[height<=1080]/best',
    'merge_output_format': 'mp4',
    'outtmpl': str(TEMP_DIR / 'videos' / '%(title)s_%(id)s.%(ext)s'),
    
    # Options réseau
    'socket_timeout': HTTP_TIMEOUT,
    'retries': MAX_RETRIES,
    'fragment_retries': MAX_RETRIES,
    'skip_unavailable_fragments': True,
    
    # Headers
    'http_headers': HTTP_HEADERS,
    
    # Options de conversion
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',
    }],
}

# ============================================================================
# 7. CONFIGURATION DES MESSAGES
# ============================================================================

# Messages en français
MESSAGES_FR: Dict[str, str] = {
    # Messages généraux
    'welcome': (
        "👋 *Bienvenue sur Pinterest Downloader Bot!*\n\n"
        "Je peux télécharger des vidéos depuis Pinterest pour vous.\n\n"
        "*Comment utiliser:*\n"
        "1. Envoyez-moi un lien Pinterest\n"
        "2. Je vais analyser la vidéo\n"
        "3. Choisissez la qualité\n"
        "4. Recevez votre vidéo!\n\n"
        "⚠️ *Limites:*\n"
        "• Max 10 minutes\n"
        "• Max 50MB\n"
        "• Vidéos publiques uniquement"
    ),
    
    'help': (
        "❓ *AIDE*\n\n"
        "*Commandes disponibles:*\n"
        "• Envoyez un lien Pinterest → Téléchargement\n"
        "• /start → Démarrer le bot\n"
        "• /help → Afficher cette aide\n"
        "• /stats → Voir les statistiques\n"
        "• /clean → Nettoyer les fichiers\n\n"
        "*Liens supportés:*\n"
        "• https://pinterest.com/pin/123456\n"
        "• https://pin.it/abc123\n"
        "• Tous les domaines Pinterest\n\n"
        "*Problèmes courants:*\n"
        "• Vérifiez que le lien est public\n"
        "• La vidéo ne doit pas dépasser 10 minutes\n"
        "• Votre connexion doit être stable"
    ),
    
    'processing': "🔍 *Analyse en cours...* Patientez s'il vous plaît.",
    'analyzing': "📊 Analyse du lien Pinterest...",
    'downloading': "📥 Téléchargement de la vidéo...",
    'uploading': "📤 Envoi vers Telegram...",
    'success': "✅ Téléchargement réussi!",
    'error': "❌ Une erreur est survenue. Veuillez réessayer.",
    'invalid_url': "❌ Lien Pinterest invalide. Vérifiez le format.",
    'too_large': "❌ La vidéo dépasse la limite de 50MB.",
    'too_long': "❌ La vidéo dépasse la limite de 10 minutes.",
    'private': "❌ Vidéo privée ou inaccessible.",
    
    # Qualités
    'quality_select': "🎬 Sélectionnez la qualité:",
    'quality_best': "Meilleure",
    'quality_1080': "1080p (Full HD)",
    'quality_720': "720p (HD)",
    'quality_480': "480p",
    'quality_360': "360p",
    
    # Informations vidéo
    'video_info': (
        "📊 *Informations Vidéo*\n\n"
        "• Titre: {title}\n"
        "• Durée: {duration}\n"
        "• Qualité: {quality}\n"
        "• Taille: {size}\n"
        "• Audio: {audio}"
    ),
    
    # Statistiques
    'stats': (
        "📈 *Statistiques*\n\n"
        "• Téléchargements totaux: {total}\n"
        "• Réussis: {success}\n"
        "• Échecs: {failed}\n"
        "• Taille totale: {total_size}\n"
        "• Aujourd'hui: {today}"
    ),
}

# Messages en anglais
MESSAGES_EN: Dict[str, str] = {
    'welcome': "👋 Welcome to Pinterest Downloader Bot!",
    'help': "❓ HELP",
    'processing': "🔍 Processing...",
    # ... ajoutez les autres traductions
}

# Dictionnaire des langues
MESSAGES: Dict[str, Dict[str, str]] = {
    'fr': MESSAGES_FR,
    'en': MESSAGES_EN,
}

# ============================================================================
# 8. CONFIGURATION DES LIMITES
# ============================================================================

# Nombre maximum de téléchargements simultanés par utilisateur
MAX_CONCURRENT_DOWNLOADS: int = 1

# Taux limite par utilisateur (téléchargements par heure)
RATE_LIMIT_PER_HOUR: int = 10

# Taille maximale du cache (en bytes)
MAX_CACHE_SIZE: int = 100 * 1024 * 1024  # 100 MB

# ============================================================================
# 9. CONFIGURATION DE SÉCURITÉ
# ============================================================================

# Autoriser les téléchargements depuis des sources externes
ALLOW_EXTERNAL_SOURCES: bool = False

# Vérifier les types MIME des fichiers
VERIFY_FILE_TYPES: bool = True

# Types MIME autorisés
ALLOWED_MIME_TYPES: List[str] = [
    'video/mp4',
    'video/webm',
    'video/x-matroska',
]

# Vérifier les signatures de fichiers
VERIFY_FILE_SIGNATURES: bool = True

# ============================================================================
# 10. FONCTIONS UTILITAIRES DE CONFIGURATION
# ============================================================================

def init_config() -> None:
    """
    Initialiser la configuration
    Crée les dossiers nécessaires et vérifie les dépendances
    """
    try:
        # Créer les dossiers
        TEMP_DIR.mkdir(exist_ok=True)
        for subdir in SUBDIRS.values():
            subdir.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Dossiers créés dans: {BASE_DIR}")
        
        # Vérifier le token
        if not TELEGRAM_TOKEN:
            print("⚠️  ATTENTION: TELEGRAM_TOKEN non défini!")
            print("   Obtenez un token auprès de @BotFather")
            print("   Ajoutez-le dans le fichier .env ou modifiez config.py")
            sys.exit(1)
        
        # Vérifier ffmpeg
        try:
            import subprocess
            subprocess.run(['ffmpeg', '-version'], 
                          capture_output=True, 
                          check=True)
            print("✅ FFmpeg détecté")
        except:
            print("⚠️  FFmpeg non trouvé. L'installation est recommandée:")
            print("   Termux: pkg install ffmpeg")
            print("   Ubuntu: apt install ffmpeg")
            print("   La conversion vidéo sera limitée.")
        
        print(f"✅ Configuration initialisée pour {BOT_NAME}")
        
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        sys.exit(1)

def get_message(key: str, lang: str = DEFAULT_LANGUAGE) -> str:
    """
    Obtenir un message traduit
    
    Args:
        key: Clé du message
        lang: Langue ('fr' ou 'en')
    
    Returns:
        str: Message traduit ou clé si non trouvé
    """
    messages = MESSAGES.get(lang, MESSAGES_FR)
    return messages.get(key, key)

def validate_config() -> bool:
    """
    Valider la configuration
    
    Returns:
        bool: True si la configuration est valide
    """
    errors = []
    
    # Vérifier le token
    if not TELEGRAM_TOKEN or len(TELEGRAM_TOKEN) < 10:
        errors.append("Token Telegram invalide")
    
    # Vérifier les dossiers
    if not TEMP_DIR.parent.exists():
        errors.append("Dossier parent inexistant")
    
    # Vérifier les limites
    if MAX_FILE_SIZE > 50 * 1024 * 1024:
        errors.append("MAX_FILE_SIZE dépasse la limite Telegram (50MB)")
    
    if MAX_VIDEO_DURATION > 600:
        errors.append("MAX_VIDEO_DURATION dépasse la limite recommandée (600s)")
    
    if errors:
        print("❌ Erreurs de configuration:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    return True

# ============================================================================
# 11. VARIABLES D'ENVIRONNEMENT
# ============================================================================

# Charger les variables d'environnement depuis un fichier .env
def load_env_file(env_file: str = ".env") -> None:
    """
    Charger les variables d'environnement depuis un fichier
    
    Args:
        env_file: Chemin vers le fichier .env
    """
    env_path = BASE_DIR / env_file
    if env_path.exists():
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            print(f"✅ Fichier .env chargé: {env_path}")
        except Exception as e:
            print(f"⚠️  Erreur chargement .env: {e}")

# Charger automatiquement le fichier .env
load_env_file()

# ============================================================================
# 12. EXPORT DES CONFIGURATIONS UTILES
# ============================================================================

# Liste de toutes les configurations exportées
__all__ = [
    # Bot
    'TELEGRAM_TOKEN',
    'ADMIN_IDS',
    'DEBUG_MODE',
    'BOT_NAME',
    'BOT_USERNAME',
    'DEFAULT_LANGUAGE',
    
    # Téléchargements
    'MAX_FILE_SIZE',
    'RECOMMENDED_MAX_SIZE',
    'MAX_VIDEO_DURATION',
    'DEFAULT_QUALITY',
    'SUPPORTED_FORMATS',
    'DEFAULT_EXTENSION',
    
    # Dossiers
    'BASE_DIR',
    'TEMP_DIR',
    'SUBDIRS',
    'TEMP_FILE_RETENTION_HOURS',
    
    # Logs
    'LOG_LEVEL',
    'LOG_FORMAT',
    'LOG_FILE',
    
    # Pinterest
    'PINTEREST_URL_PATTERNS',
    'HTTP_HEADERS',
    'HTTP_TIMEOUT',
    'MAX_RETRIES',
    'RETRY_DELAY',
    
    # yt-dlp
    'YTDLP_OPTIONS',
    
    # Messages
    'MESSAGES',
    
    # Limites
    'MAX_CONCURRENT_DOWNLOADS',
    'RATE_LIMIT_PER_HOUR',
    'MAX_CACHE_SIZE',
    
    # Sécurité
    'ALLOW_EXTERNAL_SOURCES',
    'VERIFY_FILE_TYPES',
    'ALLOWED_MIME_TYPES',
    'VERIFY_FILE_SIGNATURES',
    
    # Fonctions
    'init_config',
    'validate_config',
    'get_message',
    'load_env_file',
]

# ============================================================================
# 13. INITIALISATION AUTOMATIQUE
# ============================================================================

# Initialiser au chargement du module
if __name__ != "__main__":
    init_config()
    
    if not validate_config():
        print("❌ Configuration invalide. Correction nécessaire.")
        # Ne pas quitter pour permettre les tests
