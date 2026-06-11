from flask import Flask, render_template, request, jsonify
import mysql.connector
import re

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
# Update these with your actual local MySQL credentials
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password', 
    'database': 'voice_pos_db'
}

# --- DATA CLEANING PIPELINE ---
def parse_voice_order(text):
    """
    Extracts the quantity and item from a spoken string.
    Example: "two packets of milk" -> quantity: 2, item: "packets of milk"
    """
    text = text.lower().strip()
    
    # Dictionary to handle numbers spoken as words
    word_to_num = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
    }
    
    # Look for the first word or digit in the sentence
    words = text.split()
    if not words:
        return None, None
        
    first_word = words[0]
    quantity = None
    
    if first_word.isdigit():
        quantity = int(first_word)
    elif first_word in word_to_num:
        quantity = word_to_num[first_word]
    else:
        # Default to 1 if no quantity is explicitly stated
        quantity = 1 
        
    # The rest of the string is assumed to be the item
    item_name = " ".join(words[1:]) if quantity != 1 else text
    
    return quantity, item_name

# --- ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process_voice', methods=['POST'])
def process_voice():
    data = request.get_json()
    spoken_text = data.get('text', '')
    
    # 1. Extract the data
    quantity, item = parse_voice_order(spoken_text)
    
    print(f"\n🎤 [RAW]: {spoken_text}")
    print(f"📦 [EXTRACTED] -> Item: {item} | Qty: {quantity}")
    
    # 2. Insert into MySQL (Simulated for now until we build the tables)
    try:
        # Uncomment this block once your database is set up!
        '''
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Deduct the quantity from inventory
        sql = "UPDATE inventory SET stock = stock - %s WHERE item_name LIKE %s"
        cursor.execute(sql, (quantity, f"%{item}%"))
        conn.commit()
        
        cursor.close()
        conn.close()
        '''
        message = f"Successfully logged {quantity} of '{item}'"
        print("✅ [DATABASE]: Simulated successful update.\n")
        
    except Exception as e:
        message = f"Database error: {str(e)}"
        print(f"❌ [DATABASE ERROR]: {str(e)}\n")

    return jsonify({
        "status": "success", 
        "message": message
    })

if __name__ == '__main__':
    app.run(debug=True)