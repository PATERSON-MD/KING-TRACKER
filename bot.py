#!/usr/bin/env python3
"""
PINTEREST VIDEO DOWNLOADER BOT
Télécharge des vidéos depuis Pinterest
"""

import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from pinterest_downloader import PinterestDownloader
import config
from utils import cleanup_temp_files as cleanup_old_files, format_file_size as format_size, get_user_display

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class PinterestBot:
    def __init__(self):
        self.downloader = PinterestDownloader()
        self.user_sessions = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /start"""
        user = update.effective_user
        
        welcome = f"""
🎬 *Pinterest Video Downloader* 🎬

Bonjour *{user.first_name}* ! 👋

Je peux télécharger des vidéos depuis Pinterest pour vous.

*Comment faire :*
1. 📱 Trouvez une vidéo sur Pinterest
2. 🔗 Copiez le lien
3. 📤 Envoyez-le moi
4. ⬇️ Je vous envoie la vidéo !

*Liens acceptés :*
• https://pinterest.com/pin/123456789/
• https://pin.it/abc123
• Tous liens Pinterest

*Fonctionnalités :*
✅ Qualité HD/SD
✅ Rapide et gratuit
✅ Sans filigrane
✅ Support longues vidéos

Envoyez-moi un lien pour commencer !
        """
        
        keyboard = [
            [InlineKeyboardButton("❓ Aide", callback_data="help"),
             InlineKeyboardButton("⚙️ Paramètres", callback_data="settings")],
            [InlineKeyboardButton("📊 Stats", callback_data="stats")]
        ]
        
        await update.message.reply_text(
            welcome,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gérer les messages avec liens"""
        text = update.message.text.strip()
        user_id = update.effective_user.id
        
        if not self.downloader.is_valid_url(text):
            await update.message.reply_text(
                "❌ *Lien invalide*\n\n"
                "Veuillez envoyer un lien Pinterest valide :\n"
                "• https://pinterest.com/pin/...\n"
                "• https://pin.it/...\n\n"
                "Utilisez /help pour plus d'info.",
                parse_mode='Markdown'
            )
            return
        
        # Message d'attente
        wait_msg = await update.message.reply_text("🔍 *Analyse en cours...*", parse_mode='Markdown')
        
        try:
            # Récupérer les infos de la vidéo
            video_info = await self.downloader.get_video_info(text)
            
            if not video_info:
                await wait_msg.edit_text(
                    "❌ *Vidéo non trouvée*\n\n"
                    "Raisons possibles :\n"
                    "• Vidéo privée\n"
                    "• Lien expiré\n"
                    "• Problème réseau\n\n"
                    "Essayez un autre lien.",
                    parse_mode='Markdown'
                )
                return
            
            # Afficher les options
            await self.show_video_options(wait_msg, video_info, user_id)
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await wait_msg.edit_text(f"❌ Erreur : {str(e)[:100]}")
    
    async def show_video_options(self, message, video_info, user_id):
        """Afficher les options de téléchargement"""
        # Sauvegarder les infos
        self.user_sessions[user_id] = video_info
        
        # Créer les boutons
        buttons = []
        for quality in video_info.get('qualities', []):
            btn_text = f"⬇️ {quality['quality']} ({quality['size']})"
            btn_data = f"download_{quality['id']}"
            buttons.append([InlineKeyboardButton(btn_text, callback_data=btn_data)])
        
        buttons.append([
            InlineKeyboardButton("🔄 Autre lien", callback_data="new"),
            InlineKeyboardButton("📊 Infos", callback_data=f"info_{user_id}")
        ])
        
        text = f"""
🎬 *Vidéo trouvée !*

*Titre :* {video_info.get('title', 'Sans titre')}
*Durée :* {video_info.get('duration', 'Inconnue')}

Choisissez une qualité :
        """
        
        await message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='Markdown'
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gérer les interactions boutons"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        if data.startswith("download_"):
            quality_id = data.replace("download_", "")
            await self.process_download(query, user_id, quality_id)
        
        elif data.startswith("info_"):
            await self.show_info(query, user_id)
        
        elif data == "help":
            await self.show_help(query)
        
        elif data == "settings":
            await self.show_settings(query)
        
        elif data == "stats":
            await self.show_stats(query, user_id)
        
        elif data == "new":
            await query.edit_message_text("📤 *Envoyez un nouveau lien Pinterest*", parse_mode='Markdown')
    
    async def process_download(self, query, user_id, quality_id):
        """Traiter le téléchargement"""
        video_info = self.user_sessions.get(user_id)
        if not video_info:
            await query.edit_message_text("❌ Session expirée. Renvoyez le lien.")
            return
        
        # Trouver la qualité demandée
        quality = None
        for q in video_info.get('qualities', []):
            if q['id'] == quality_id:
                quality = q
                break
        
        if not quality:
            await query.edit_message_text("❌ Qualité non disponible")
            return
        
        # Démarrer le téléchargement
        await query.edit_message_text(
            f"📥 *Téléchargement {quality['quality']}...*\n"
            "Veuillez patienter.",
            parse_mode='Markdown'
        )
        
        try:
            # Télécharger la vidéo
            result = await self.downloader.download_video(
                quality['url'],
                f"{user_id}_{quality_id}"
            )
            
            if not result:
                await query.edit_message_text("❌ Échec du téléchargement")
                return
            
            # Envoyer la vidéo
            await query.message.reply_video(
                video=open(result['path'], 'rb'),
                caption=f"🎬 {video_info.get('title', 'Vidéo Pinterest')}\n"
                       f"📦 {quality['size']} • {quality['quality']}",
                supports_streaming=True
            )
            
            await query.edit_message_text("✅ *Vidéo envoyée !*", parse_mode='Markdown')
            
            # Nettoyer
            os.remove(result['path'])
            
        except Exception as e:
            logger.error(f"Download error: {e}")
            await query.edit_message_text(f"❌ Erreur : {str(e)[:100]}")
    
    async def show_help(self, query):
        """Afficher l'aide"""
        help_text = """
❓ *AIDE*

*Comment utiliser :*
1. Copiez un lien vidéo Pinterest
2. Envoyez-le au bot
3. Choisissez la qualité
4. Recevez la vidéo

*Problèmes courants :*
• *Lien non reconnu* : Vérifiez que c'est un lien Pinterest
• *Téléchargement échoué* : Réessayez ou changez de qualité
• *Vidéo trop grande* : Téléchargez en qualité inférieure

*Commandes :*
/start - Démarrer le bot
/help - Afficher cette aide
        """
        
        await query.edit_message_text(help_text, parse_mode='Markdown')
    
    async def show_settings(self, query):
        """Afficher les paramètres"""
        settings = """
⚙️ *PARAMÈTRES*

*Qualité par défaut :* HD
*Format :* MP4
*Taille max :* 50MB (limite Telegram)

*Options :*
• Compression automatique
• Notification de fin
• Historique des téléchargements

*À venir :*
• Téléchargement multiple
• Plus de formats
• Interface web
        """
        
        await query.edit_message_text(settings, parse_mode='Markdown')
    
    async def show_stats(self, query, user_id):
        """Afficher les statistiques"""
        stats = f"""
📊 *STATISTIQUES*

*Utilisateur :* {query.from_user.first_name}
*Téléchargements :* 0
*Dernier :* Jamais

*Limites :*
• Taille : 50MB max
• Pas de limite quotidienne
• Fichiers temporaires

*Conseil :*
Utilisez le WiFi pour les vidéos HD !
        """
        
        await query.edit_message_text(stats, parse_mode='Markdown')
    
    async def cleanup_task(self):
        """Nettoyage périodique"""
        while True:
            cleanup_old_files("temp", max_age_hours=1)
            await asyncio.sleep(3600)  # Toutes les heures
    
    def run(self):
        """Lancer le bot"""
        # Créer l'application
        app = Application.builder().token(config.TOKEN).build()
        
        # Ajouter les handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.show_help))
        
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Démarrer la tâche de nettoyage
        loop = asyncio.get_event_loop()
        loop.create_task(self.cleanup_task())
        
        # Lancer le bot
        print("🤖 Pinterest Downloader Bot démarré !")
        print(f"👤 Nom : {config.BOT_NAME}")
        print("📤 Envoyez /start pour commencer")
        
        app.run_polling()

if __name__ == "__main__":
    # Vérifier le token
    if not hasattr(config, 'TOKEN') or config.TOKEN == "TON_TOKEN_ICI":
        print("\n⚠️  CONFIGURATION REQUISE")
        print("="*50)
        print("1. Créez un bot sur Telegram avec @BotFather")
        print("2. Copiez le token")
        print("3. Éditez le fichier config.py")
        print("4. Remplacez 'TON_TOKEN_ICI' par votre token")
        print("="*50)
        exit(1)
    
    bot = PinterestBot()
    bot.run()
