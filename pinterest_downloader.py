import re
import asyncio
import aiohttp
import json
import os
import time
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Tuple
import yt_dlp

class PinterestDownloader:
    def __init__(self):
        self.session = None
        self.headers = {
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
        
    def is_pinterest_url(self, url: str) -> bool:
        """Vérifier si l'URL est un lien Pinterest valide"""
        url_patterns = [
            r'https?://(www\.)?pinterest\.(com|fr|de|es|it|co\.uk)/pin/\d+',
            r'https?://(www\.)?pinterest\.(com|fr|de|es|it|co\.uk)/[^/]+/pin/\d+',
            r'https?://pin\.it/[a-zA-Z0-9]+',
            r'https?://pinterest\.com/pin/\d+',
            r'https?://pinterest\.fr/pin/\d+',
            r'https?://pinterest\.de/pin/\d+',
            r'https?://pinterest\.es/pin/\d+',
            r'https?://pinterest\.it/pin/\d+',
            r'pinterest://pin/\d+',
            r'https?://(www\.)?pinterest\.(com|fr|de|es|it|co\.uk)/pin/\d+/',
        ]
        
        # Vérifier chaque pattern
        for pattern in url_patterns:
            if re.match(pattern, url.strip()):
                return True
        
        # Vérifier les URLs raccourcies
        if 'pin.it' in url.lower():
            return True
            
        return False
    
    def normalize_pinterest_url(self, url: str) -> str:
        """Normaliser l'URL Pinterest"""
        # Si c'est une URL raccourcie pin.it, on la garde telle quelle
        # yt-dlp sait gérer les redirections
        
        # Nettoyer les paramètres inutiles
        parsed = urlparse(url)
        
        # Garder uniquement les paramètres utiles
        clean_params = []
        if parsed.query:
            params = parsed.query.split('&')
            for param in params:
                if any(key in param.lower() for key in ['utm_', 'source=', 'ref=', 'campaign=']):
                    continue  # Ignorer les paramètres de tracking
                clean_params.append(param)
        
        # Reconstruire l'URL
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if clean_params:
            clean_url += f"?{'&'.join(clean_params)}"
        
        return clean_url
    
    async def extract_video_info(self, url: str) -> Optional[Dict]:
        """Extraire les informations de la vidéo Pinterest"""
        try:
            # Normaliser l'URL
            clean_url = self.normalize_pinterest_url(url)
            
            # Options yt-dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'force_generic_extractor': False,
                'no_check_certificate': True,
                'ignoreerrors': True,
                'socket_timeout': 30,
                'http_headers': self.headers,
            }
            
            video_info = None
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extraire les informations
                info = ydl.extract_info(clean_url, download=False)
                
                if not info:
                    # Essayer une autre méthode
                    return await self.extract_video_info_fallback(clean_url)
                
                # Formater les informations
                video_info = {
                    'title': info.get('title', 'Pinterest Video'),
                    'duration': self.format_duration(info.get('duration', 0)),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'description': info.get('description', '')[:300],
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'url': clean_url,
                    'webpage_url': info.get('webpage_url', clean_url),
                    'formats': [],
                    'qualities': []
                }
                
                # Extraire les formats disponibles
                formats = info.get('formats', [])
                
                if not formats:
                    # Si pas de formats, essayer avec une autre méthode
                    return await self.extract_video_info_fallback(clean_url)
                
                # Organiser les formats par qualité
                quality_map = {}
                
                for fmt in formats:
                    if fmt.get('vcodec') == 'none':
                        continue  # Ignorer les formats audio seulement
                    
                    # Déterminer la qualité
                    height = fmt.get('height', 0)
                    quality_name = self.get_quality_name(height, fmt)
                    
                    # Calculer la taille approximative
                    filesize = fmt.get('filesize', fmt.get('filesize_approx', 0))
                    
                    # Déterminer l'extension
                    ext = fmt.get('ext', 'mp4')
                    if ext == 'unknown_video':
                        ext = 'mp4'
                    
                    # Créer l'entrée qualité
                    quality_entry = {
                        'format_id': fmt.get('format_id', ''),
                        'quality': quality_name,
                        'height': height,
                        'width': fmt.get('width', 0),
                        'fps': fmt.get('fps', 0),
                        'url': fmt.get('url', ''),
                        'filesize': filesize,
                        'size': self.format_size(filesize),
                        'extension': ext,
                        'has_audio': fmt.get('acodec') != 'none',
                        'vcodec': fmt.get('vcodec', 'unknown'),
                        'acodec': fmt.get('acodec', 'none')
                    }
                    
                    # Garder la meilleure qualité pour chaque résolution
                    if quality_name not in quality_map or filesize > quality_map[quality_name]['filesize']:
                        quality_map[quality_name] = quality_entry
                
                # Convertir en liste et trier par qualité
                qualities = list(quality_map.values())
                qualities.sort(key=lambda x: x['height'], reverse=True)
                
                # Limiter à 5 qualités maximum
                video_info['qualities'] = qualities[:5]
                
                # Ajouter les informations de résumé
                if qualities:
                    best = qualities[0]
                    video_info['resolution'] = f"{best['width']}x{best['height']}" if best['width'] else f"{best['height']}p"
                    video_info['best_quality'] = best['quality']
                    video_info['best_size'] = best['size']
                    video_info['has_audio'] = best['has_audio']
                    video_info['format'] = best['extension'].upper()
                
                return video_info
                
        except Exception as e:
            print(f"Error in extract_video_info: {e}")
            # Essayer la méthode fallback
            try:
                return await self.extract_video_info_fallback(url)
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
                return None
    
    async def extract_video_info_fallback(self, url: str) -> Optional[Dict]:
        """Méthode fallback pour extraire les infos vidéo"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                
                # Chercher les données JSON dans la page
                patterns = [
                    r'<script type="application/json" id="initial-state">(.*?)</script>',
                    r'"videos":\s*({.*?})',
                    r'"video_list":\s*({.*?})',
                    r'"url":"(https?://[^"]+\.mp4[^"]*)"',
                    r'src="(https?://[^"]+\.mp4[^"]*)"',
                ]
                
                video_urls = []
                for pattern in patterns:
                    matches = re.findall(pattern, html, re.DOTALL)
                    for match in matches:
                        if '.mp4' in str(match).lower():
                            if isinstance(match, str):
                                video_urls.append(match)
                            elif isinstance(match, tuple):
                                video_urls.extend([m for m in match if '.mp4' in str(m).lower()])
                
                # Nettoyer les URLs
                clean_urls = []
                for video_url in video_urls:
                    # Extraire l'URL propre
                    if 'url' in video_url.lower():
                        try:
                            json_data = json.loads(video_url)
                            if 'url' in json_data:
                                video_url = json_data['url']
                        except:
                            pass
                    
                    if video_url.startswith('"'):
                        video_url = video_url.strip('"')
                    
                    if video_url.startswith('http'):
                        clean_urls.append(video_url)
                
                if not clean_urls:
                    return None
                
                # Prendre la première URL vidéo
                video_url = clean_urls[0]
                
                # Information basique
                video_info = {
                    'title': 'Pinterest Video',
                    'duration': 'Unknown',
                    'thumbnail': '',
                    'uploader': 'Pinterest',
                    'url': url,
                    'qualities': [
                        {
                            'quality': 'Standard',
                            'url': video_url,
                            'size': 'Unknown',
                            'extension': 'mp4',
                            'height': 720,
                            'has_audio': True
                        }
                    ],
                    'best_quality': 'Standard',
                    'resolution': '720p',
                    'has_audio': True,
                    'format': 'MP4'
                }
                
                return video_info
                
        except Exception as e:
            print(f"Error in fallback method: {e}")
            return None
    
    async def download_video(self, video_url: str, user_id: int, quality: str = "best") -> Optional[Dict]:
        """Télécharger la vidéo"""
        try:
            # Créer un nom de fichier unique
            timestamp = int(time.time())
            filename = f"temp/pinterest_{user_id}_{timestamp}.mp4"
            
            # Options yt-dlp
            ydl_opts = {
                'outtmpl': filename,
                'quiet': True,
                'no_warnings': True,
                'format': 'best[height<=1080]/best',  # Maximum 1080p
                'merge_output_format': 'mp4',
                'http_headers': self.headers,
                'socket_timeout': 30,
                'retries': 3,
                'fragment_retries': 3,
                'skip_unavailable_fragments': True,
                'ignoreerrors': True,
                'no_check_certificate': True,
                'progress_hooks': [self.download_progress_hook],
            }
            
            # Si une qualité spécifique est demandée
            if quality != "best":
                # Chercher le format_id correspondant
                ydl_opts['format'] = quality
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Télécharger la vidéo
                info = ydl.extract_info(video_url, download=True)
                
                if not info:
                    return None
                
                # Vérifier si le fichier existe
                if not os.path.exists(filename):
                    # Essayer avec l'extension .webm
                    webm_filename = filename.replace('.mp4', '.webm')
                    if os.path.exists(webm_filename):
                        filename = webm_filename
                    else:
                        return None
                
                # Obtenir les informations du fichier
                filesize = os.path.getsize(filename)
                
                return {
                    'file_path': filename,
                    'size': filesize,
                    'title': info.get('title', 'video'),
                    'duration': info.get('duration', 0),
                    'resolution': f"{info.get('width', 0)}x{info.get('height', 0)}",
                    'format': info.get('ext', 'mp4'),
                    'success': True
                }
                
        except Exception as e:
            print(f"Download error: {e}")
            return None
    
    def download_progress_hook(self, d):
        """Hook pour suivre la progression"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            # Log discret
            if random.random() < 0.1:  # Log seulement 10% du temps
                print(f"Progress: {percent} at {speed}, ETA: {eta}")
        elif d['status'] == 'finished':
            print("Download completed successfully")
    
    def get_quality_name(self, height: int, fmt: Dict) -> str:
        """Obtenir un nom lisible pour la qualité"""
        if height >= 2160:
            return "4K"
        elif height >= 1440:
            return "2K"
        elif height >= 1080:
            return "1080p"
        elif height >= 720:
            return "720p"
        elif height >= 480:
            return "480p"
        elif height >= 360:
            return "360p"
        elif height >= 240:
            return "240p"
        elif height >= 144:
            return "144p"
        else:
            # Essayer de déterminer depuis le format_id
            format_id = fmt.get('format_id', '').lower()
            if 'hd' in format_id:
                return "HD"
            elif 'sd' in format_id:
                return "SD"
            else:
                return f"{height}p" if height > 0 else "Unknown"
    
    def format_duration(self, seconds: int) -> str:
        """Formatter la durée"""
        if not seconds or seconds <= 0:
            return "Unknown"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def format_size(self, bytes_size: int) -> str:
        """Formatter la taille"""
        if not bytes_size or bytes_size <= 0:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    
    async def close(self):
        """Fermer la session"""
        if self.session:
            await self.session.close()
    
    def estimate_download_time(self, file_size: int) -> str:
        """Estimer le temps de téléchargement"""
        if not file_size or file_size <= 0:
            return "Unknown"
        
        # Estimation: 2MB/s pour une connexion moyenne
        download_speed = 2 * 1024 * 1024  # 2 MB/s en bytes/s
        seconds = file_size / download_speed
        
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            return f"{int(seconds/60)} minutes"
        else:
            return f"{int(seconds/3600)} hours"
    
    def get_best_quality(self, qualities: List[Dict]) -> Dict:
        """Obtenir la meilleure qualité disponible"""
        if not qualities:
            return {}
        
        # Trier par hauteur puis par taille de fichier
        sorted_qualities = sorted(qualities, 
                                 key=lambda x: (x.get('height', 0), x.get('filesize', 0)), 
                                 reverse=True)
        
        return sorted_qualities[0] if sorted_qualities else {}
