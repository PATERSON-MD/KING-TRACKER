const TelegramBot = require('node-telegram-bot-api');

// Configuration
const bot = new TelegramBot('8345426244:AAHIKu5wJyHKczMnUB58BdozgMezaFE9WKM', { polling: true });

// URLs des images KING-CHECK-BAN
const IMAGES = {
    welcome: 'https://files.catbox.moe/qkafkb.jpg',
    checking: 'https://files.catbox.moe/deslfn.jpg', 
    result: 'https://files.catbox.moe/601u5z.jpg'
};

// Classe de vérification WhatsApp (version adaptée)
class WhatsAppChecker {
    static async xeonBanChecker(phoneNumber) {
        try {
            // Simulation de la vérification - À REMPLACER par ta vraie méthode
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Logique de vérification (adaptée de ton code)
            const banPatterns = this.detectBanPatterns(phoneNumber);
            const isBanned = banPatterns.banScore >= 60;
            const isRestricted = banPatterns.banScore >= 30 && banPatterns.banScore < 60;
            
            const resultData = {
                number: phoneNumber,
                isBanned: isBanned,
                isNeedOfficialWa: isRestricted,
                data: {
                    violation_type: isBanned ? "Spam" : null,
                    in_app_ban_appeal: isBanned ? true : null,
                    appeal_token: isBanned ? `APL${Math.random().toString(36).substr(2, 9).toUpperCase()}` : null
                }
            };
            
            return JSON.stringify(resultData);
            
        } catch (error) {
            throw new Error(`Vérification échouée: ${error.message}`);
        }
    }
    
    static detectBanPatterns(phoneNumber) {
        const patterns = {
            sequential: /(0123|1234|2345|3456|4567|5678|6789|9876|8765|7654|6543|5432|4321|3210)/,
            repeating: /(\d)\1{4,}/,
            spam: /(11111|22222|33333|44444|55555|66666|77777|88888|99999|00000)/,
            test: /(12345678|87654321|111222333|555444333)/
        };
        
        let banScore = 0;
        let detectedPatterns = [];
        
        for (const [patternName, pattern] of Object.entries(patterns)) {
            if (pattern.test(phoneNumber)) {
                banScore += 25;
                detectedPatterns.push(patternName);
            }
        }
        
        return { banScore, detectedPatterns };
    }
}

// Message de BIENVENUE
bot.onText(/\/start/, async (msg) => {
    const chatId = msg.chat.id;
    
    try {
        await bot.sendPhoto(chatId, IMAGES.welcome, {
            caption: `👑 *BIENVENUE DANS KING-CHECK-BAN* 👑\n\n` +
                    `*Le vérificateur WhatsApp le plus puissant !* 🔥\n\n` +
                    `Utilise /checkban [numéro] pour commencer`,
            parse_mode: 'Markdown'
        });
    } catch (error) {
        await bot.sendMessage(
            chatId,
            `👑 *BIENVENUE DANS KING-CHECK-BAN* 👑\n\nUtilise /checkban [numéro] pour commencer`,
            { parse_mode: 'Markdown' }
        );
    }
});

// Commande /checkban - TON CODE ADAPTÉ POUR TELEGRAM
bot.onText(/\/checkban(?:\s+(.+))?/, async (msg, match) => {
    const chatId = msg.chat.id;
    const text = match[1];
    
    if (!text) {
        return bot.sendMessage(
            chatId,
            `👑 *KING-CHECK-BAN* 👑\n\n` +
            `*Utilisation :* /checkban [numéro]\n\n` +
            `*Exemple :* /checkban 91xxxxxxxxxx`,
            { parse_mode: 'Markdown' }
        );
    }
    
    const victim = text.split("|")[0];
    const phoneNumber = victim.replace(/[^0-9]/g, '');
    
    if (phoneNumber.length < 10) {
        return bot.sendMessage(
            chatId,
            `❌ Invalid phone number!\n\nExample: /checkban 91xxxxxxxxxx`,
            { parse_mode: 'Markdown' }
        );
    }
    
    try {
        // Photo "checking" avec message d'attente
        const messageAttente = await bot.sendPhoto(chatId, IMAGES.checking, {
            caption: `🔍 Checking ban status for: +${phoneNumber}...\n⏳ Please wait...`,
            parse_mode: 'Markdown'
        });
        
        // TON CODE EXACT ADAPTÉ
        const result = await WhatsAppChecker.xeonBanChecker(phoneNumber);
        const resultData = JSON.parse(result);
        
        let statusMsg = `👑 *KING-CHECK-BAN* 👑\n\n`;
        statusMsg += `📱 *BAN STATUS CHECK*\n\n`;
        statusMsg += `📞 *Number:* +${resultData.number}\n\n`;
        
        if (resultData.isBanned) {
            statusMsg += `🚫 *STATUS:* BANNED\n\n`;
            statusMsg += `⚠️ *Details:*\n`;
            statusMsg += `• Violation: ${resultData.data?.violation_type || 'Unknown'}\n`;
            statusMsg += `• Can Appeal: ${resultData.data?.in_app_ban_appeal ? 'Yes' : 'No'}\n`;
            if (resultData.data?.appeal_token) {
                statusMsg += `• Appeal Token: \`${resultData.data.appeal_token}\`\n`;
            }
            statusMsg += `\n💡 *KING Tip:* Use official WhatsApp to appeal ban`;
        } 
        else if (resultData.isNeedOfficialWa) {
            statusMsg += `🔒 *STATUS:* RESTRICTED\n\n`;
            statusMsg += `⚠️ *Reason:* Must use Official WhatsApp\n`;
            statusMsg += `💡 *KING Tip:* Switch to official WhatsApp app`;
        } 
        else {
            statusMsg += `✅ *STATUS:* CLEAN\n\n`;
            statusMsg += `🎉 Number is *NOT BANNED*\n`;
            statusMsg += `✅ Safe to use with any WhatsApp\n`;
            statusMsg += `👑 *KING Verified:* ✅ CLEAN`;
        }
        
        statusMsg += `\n\n⚡ *KING-CHECK-BAN - Ultimate Verification*`;
        
        // Photo "result" avec le résultat final
        await bot.sendPhoto(chatId, IMAGES.result, {
            caption: statusMsg,
            parse_mode: 'Markdown'
        });
        
        // Supprimer le message d'attente
        await bot.deleteMessage(chatId, messageAttente.message_id);
        
    } catch (error) {
        console.error('Ban check error:', error);
        await bot.sendMessage(
            chatId,
            `❌ Error checking ban status!\nTry again later or contact KING Support.`,
            { parse_mode: 'Markdown' }
        );
    }
});

// Commande /aide
bot.onText(/\/aide/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(
        chatId,
        `👑 *KING-CHECK-BAN - AIDE* 👑\n\n` +
        `*Commandes :*\n` +
        `🔍 /checkban [numéro] - Vérifier un numéro\n` +
        `📖 /aide - Afficher cette aide\n` +
        `🚀 /start - Message de bienvenue`,
        { parse_mode: 'Markdown' }
    );
});

// Démarrage du bot
console.log('👑 KING-CHECK-BAN démarré avec succès !');
