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