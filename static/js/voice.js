const startBtn = document.getElementById('start-btn');
const output = document.getElementById('output');

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-IN'; // Tuned for Indian English accents

    function resetButton() {
        startBtn.textContent = "Start Listening";
        startBtn.style.backgroundColor = "#2ed573";
    }

    recognition.onstart = function() {
        startBtn.textContent = "🔴 Listening...";
        startBtn.style.backgroundColor = "#ff4757";
        output.innerHTML = "Speak now...";
    };

    recognition.onresult = function(event) {
        // Get the current phrase the AI is working on
        const current = event.resultIndex;
        const transcript = event.results[current][0].transcript;
        
        // Show the live typing on the merchant's screen
        output.innerHTML = "You said: <br><br><strong>" + transcript + "</strong>";

        // 🔴 NEW: Only send to Python if the sentence is completely finished
        if (event.results[current].isFinal) {
            resetButton();

            fetch('/process_voice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: transcript })
            })
            .then(response => response.json())
            .then(data => {
                output.innerHTML += `<br><br><span style="color: #2ed573;">🟢 Backend says: ${data.message}</span>`;
                
                // If Python tripped the alarm...
                if (data.alert) {
                    // 1. Build the red warning box
                    let alertHTML = `
                        <div style="background-color: #ff4757; color: white; padding: 15px; border-radius: 8px; font-weight: bold; margin-top: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            ${data.alert}
                    `;
                    
                    // 2. Build the WhatsApp button if the URL exists
                    if (data.wa_url) {
                        alertHTML += `
                            <br><br>
                            <a href="${data.wa_url}" target="_blank" style="background-color: #25D366; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; display: inline-block; font-size: 14px;">
                                📱 Send WhatsApp Alert
                            </a>
                        `;
                    }
                    
                    // 3. Close the box and print it to the screen
                    alertHTML += `</div>`;
                    output.innerHTML += alertHTML;
                }
            })
            .catch(error => {
                console.error("Error sending to backend:", error);
            });
        }
    };

    // 🔴 Automatically resets the button if a timeout or connection error happens
    recognition.onerror = function(event) {
        console.error("Speech Error:", event.error);
        output.innerHTML = "⚠️ Echo dropped (" + event.error + "). Click again to speak.";
        resetButton();
    };

    // 🔴 Resets if the mic stops picking up audio completely
    recognition.onend = function() {
        if (startBtn.textContent === "🔴 Listening...") {
            resetButton();
            output.innerHTML = "No speech detected. Try again!";
        }
    };

    startBtn.addEventListener('click', () => {
        recognition.start();
    });

} else {
    output.innerHTML = "Your browser does not support Voice Recognition. Please use standard Chrome.";
}