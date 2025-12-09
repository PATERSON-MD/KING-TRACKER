import os
import time
import json
import shutil
import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import subprocess
import mimetypes

class Utils:
    @staticmethod
    def cleanup_temp_files(file_path: Optional[str] = None, max_age_hours: int = 1):
        """
        Nettoyer les fichiers temporaires
        
        Args:
            file_path: Chemin spécifique à supprimer
            max_age_hours: Âge maximum des fichiers en heures
        """
        temp_dir = "temp"
        
        # Supprimer un fichier spécifique
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🗑️ Fichier supprimé: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"⚠️ Erreur suppression fichier {file_path}: {e}")
        
        # Nettoyer le dossier temp des fichiers anciens
        if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
            current_time = time.time()
            
            for filename in os.listdir(temp_dir):
                filepath = os.path.join(temp_dir, filename)
                
                if os.path.isfile(filepath):
                    try:
                        file_age = current_time - os.path.getmtime(filepath)
                        
                        # Supprimer les fichiers trop anciens
                        if file_age > (max_age_hours * 3600):
                            os.remove(filepath)
                            print(f"🧹 Fichier ancien nettoyé: {filename}")
                    except Exception as e:
                        print(f"⚠️ Erreur nettoyage {filename}: {e}")
    
    @staticmethod
    def format_file_size(bytes_size: int) -> str:
        """
        Formater la taille de fichier en unités lisibles
        
        Args:
            bytes_size: Taille en bytes
            
        Returns:
            str: Taille formatée (ex: "1.5 MB")
        """
        if not bytes_size or bytes_size <= 0:
            return "Inconnu"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        
        while bytes_size >= 1024 and unit_index < len(units) - 1:
            bytes_size /= 1024.0
            unit_index += 1
        
        return f"{bytes_size:.2f} {units[unit_index]}"
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """
        Formater la durée en format lisible
        
        Args:
            seconds: Durée en secondes
            
        Returns:
            str: Durée formatée (ex: "02:30")
        """
        if not seconds or seconds <= 0:
            return "00:00"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def generate_unique_filename(prefix: str = "video", extension: str = "mp4") -> str:
        """
        Générer un nom de fichier unique
        
        Args:
            prefix: Préfixe du nom de fichier
            extension: Extension du fichier
            
        Returns:
            str: Nom de fichier unique
        """
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"{prefix}_{timestamp}_{random_str}.{extension}"
    
    @staticmethod
    def create_temp_directory() -> str:
        """
        Créer le dossier temporaire s'il n'existe pas
        
        Returns:
            str: Chemin du dossier temporaire
        """
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)
            print(f"📁 Dossier temporaire créé: {temp_dir}")
        
        # Créer des sous-dossiers pour l'organisation
        subdirs = ['videos', 'thumbnails', 'logs']
        for subdir in subdirs:
            subdir_path = os.path.join(temp_dir, subdir)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path, exist_ok=True)
        
        return temp_dir
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Vérifier si une URL est valide
        
        Args:
            url: URL à vérifier
            
        Returns:
            bool: True si l'URL est valide
        """
        import re
        
        url_pattern = re.compile(
            r'^(https?://)?'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domaine
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return url_pattern.match(url) is not None
    
    @staticmethod
    def extract_urls_from_text(text: str) -> List[str]:
        """
        Extraire toutes les URLs d'un texte
        
        Args:
            text: Texte contenant des URLs
            
        Returns:
            List[str]: Liste des URLs trouvées
        """
        import re
        
        url_pattern = re.compile(
            r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/?=\w&%.#-]*'
        )
        
        return url_pattern.findall(text)
    
    @staticmethod
    def log_download(user_id: int, username: str, url: str, 
                    success: bool = True, file_size: int = 0, 
                    duration: int = 0):
        """
        Journaliser un téléchargement
        
        Args:
            user_id: ID de l'utilisateur
            username: Nom d'utilisateur
            url: URL téléchargée
            success: Si le téléchargement a réussi
            file_size: Taille du fichier en bytes
            duration: Durée de la vidéo en secondes
        """
        log_dir = "temp/logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"downloads_{datetime.now().strftime('%Y-%m-%d')}.log")
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'username': username,
            'url': url[:100],  # Limiter la longueur de l'URL
            'success': success,
            'file_size': file_size,
            'duration': duration,
            'size_formatted': Utils.format_file_size(file_size),
            'duration_formatted': Utils.format_duration(duration)
        }
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"⚠️ Erreur écriture log: {e}")
    
    @staticmethod
    def get_download_stats() -> Dict:
        """
        Obtenir les statistiques de téléchargement
        
        Returns:
            Dict: Statistiques
        """
        stats = {
            'total_downloads': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'total_size': 0,
            'today_downloads': 0
        }
        
        log_dir = "temp/logs"
        if not os.path.exists(log_dir):
            return stats
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            for log_file in os.listdir(log_dir):
                if log_file.endswith('.log'):
                    filepath = os.path.join(log_dir, log_file)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                
                                stats['total_downloads'] += 1
                                
                                if entry.get('success'):
                                    stats['successful_downloads'] += 1
                                else:
                                    stats['failed_downloads'] += 1
                                
                                stats['total_size'] += entry.get('file_size', 0)
                                
                                # Compter les téléchargements d'aujourd'hui
                                entry_date = entry.get('timestamp', '').split('T')[0]
                                if entry_date == today:
                                    stats['today_downloads'] += 1
                                    
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            print(f"⚠️ Erreur lecture stats: {e}")
        
        stats['total_size_formatted'] = Utils.format_file_size(stats['total_size'])
        
        return stats
    
    @staticmethod
    def compress_video(input_path: str, output_path: str, 
                      max_size_mb: int = 50) -> bool:
        """
        Compresser une vidéo pour respecter la limite Telegram
        
        Args:
            input_path: Chemin de la vidéo source
            output_path: Chemin de la vidéo compressée
            max_size_mb: Taille maximum en MB
            
        Returns:
            bool: True si la compression a réussi
        """
        try:
            if not os.path.exists(input_path):
                return False
            
            # Vérifier la taille actuelle
            file_size = os.path.getsize(input_path)
            max_size_bytes = max_size_mb * 1024 * 1024
            
            # Si la vidéo est déjà assez petite
            if file_size <= max_size_bytes:
                shutil.copy2(input_path, output_path)
                return True
            
            # Calculer le bitrate cible
            duration = Utils.get_video_duration(input_path)
            if duration <= 0:
                return False
            
            target_bitrate = int((max_size_bytes * 8) / duration) - 128000
            
            # Commande ffmpeg pour compression
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', 'libx264',
                '-b:v', f'{target_bitrate}',
                '-preset', 'fast',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',  # Overwrite output
                output_path
            ]
            
            # Exécuter la commande
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                print(f"✅ Vidéo compressée: {Utils.format_file_size(file_size)} → {Utils.format_file_size(os.path.getsize(output_path))}")
                return True
            else:
                print(f"❌ Erreur compression: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"⚠️ Exception compression: {e}")
            return False
    
    @staticmethod
    def get_video_duration(file_path: str) -> float:
        """
        Obtenir la durée d'une vidéo
        
        Args:
            file_path: Chemin de la vidéo
            
        Returns:
            float: Durée en secondes, 0 si erreur
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                return 0
        except:
            return 0
    
    @staticmethod
    def get_video_resolution(file_path: str) -> Tuple[int, int]:
        """
        Obtenir la résolution d'une vidéo
        
        Args:
            file_path: Chemin de la vidéo
            
        Returns:
            Tuple[int, int]: (largeur, hauteur)
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height',
                '-of', 'csv=s=x:p=0',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                dimensions = result.stdout.strip().split('x')
                if len(dimensions) == 2:
                    return int(dimensions[0]), int(dimensions[1])
        except:
            pass
        
        return 0, 0
    
    @staticmethod
    def split_video(file_path: str, max_part_size_mb: int = 45) -> List[str]:
        """
        Diviser une vidéo en plusieurs parties
        
        Args:
            file_path: Chemin de la vidéo
            max_part_size_mb: Taille maximum par partie
            
        Returns:
            List[str]: Liste des chemins des parties
        """
        try:
            if not os.path.exists(file_path):
                return []
            
            file_size = os.path.getsize(file_path)
            max_part_size = max_part_size_mb * 1024 * 1024
            
            # Si le fichier est assez petit, pas besoin de diviser
            if file_size <= max_part_size:
                return [file_path]
            
            duration = Utils.get_video_duration(file_path)
            if duration <= 0:
                return []
            
            # Calculer combien de parties sont nécessaires
            num_parts = (file_size + max_part_size - 1) // max_part_size
            part_duration = duration / num_parts
            
            output_files = []
            
            for i in range(num_parts):
                output_file = f"{file_path}_part{i+1}.mp4"
                start_time = i * part_duration
                
                cmd = [
                    'ffmpeg',
                    '-i', file_path,
                    '-ss', str(start_time),
                    '-t', str(part_duration),
                    '-c', 'copy',
                    '-y',
                    output_file
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(output_file):
                    output_files.append(output_file)
                else:
                    # Nettoyer les fichiers créés en cas d'erreur
                    for f in output_files:
                        Utils.cleanup_temp_files(f)
                    return []
            
            return output_files
            
        except Exception as e:
            print(f"⚠️ Erreur division vidéo: {e}")
            return []
    
    @staticmethod
    def generate_thumbnail(video_path: str, thumbnail_path: str, time_sec: int = 10) -> bool:
        """
        Générer une miniature pour une vidéo
        
        Args:
            video_path: Chemin de la vidéo
            thumbnail_path: Chemin de sortie pour la miniature
            time_sec: Moment à capturer en secondes
            
        Returns:
            bool: True si réussi
        """
        try:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', str(time_sec),
                '-vframes', '1',
                '-vf', 'scale=320:-1',
                '-y',
                thumbnail_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0 and os.path.exists(thumbnail_path)
            
        except Exception as e:
            print(f"⚠️ Erreur génération miniature: {e}")
            return False
    
    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """
        Calculer le hash MD5 d'un fichier
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            str: Hash MD5
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return ""

# Fonctions pratiques pour l'usage direct
def cleanup_temp_files(file_path: Optional[str] = None, max_age_hours: int = 1):
    """Nettoyer les fichiers temporaires"""
    Utils.cleanup_temp_files(file_path, max_age_hours)

def format_file_size(bytes_size: int) -> str:
    """Formater la taille de fichier"""
    return Utils.format_file_size(bytes_size)

def format_duration(seconds: int) -> str:
    """Formater la durée"""
    return Utils.format_duration(seconds)

def create_temp_directory() -> str:
    """Créer le dossier temporaire"""
    return Utils.create_temp_directory()

def log_download(user_id: int, username: str, url: str, 
                success: bool = True, file_size: int = 0, 
                duration: int = 0):
    """Journaliser un téléchargement"""
    Utils.log_download(user_id, username, url, success, file_size, duration)

def get_download_stats() -> Dict:
    """Obtenir les statistiques"""
    return Utils.get_download_stats()

def is_valid_url(url: str) -> bool:
    """Vérifier si une URL est valide"""
    return Utils.is_valid_url(url)

# Test rapide
if __name__ == "__main__":
    print("🧪 Test des utilitaires...")
    
    # Test formatage
    print(f"Taille formatée: {format_file_size(1500000)}")
    print(f"Durée formatée: {format_duration(125)}")
    
    # Créer dossier temp
    temp_dir = create_temp_directory()
    print(f"Dossier temp: {temp_dir}")
    
    # Test URL
    print(f"URL valide: {is_valid_url('https://pinterest.com/pin/123')}")
    
    print("✅ Tests terminés")
