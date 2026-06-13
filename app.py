from flask import Flask, render_template, request, jsonify
from database import get_db_connection 
import re
import urllib.parse

app = Flask(__name__)

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
    quantity, item = parse_voice_order(spoken_text)
    
    print(f"\n🎤 [RAW]: {spoken_text}")
    print(f"📦 [EXTRACTED] -> Item: {item} | Qty: {quantity}")
    
    alert_message = None
    wa_url = None # Variable to hold our WhatsApp link

    try:
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)

        # 1. Deduct the quantity from inventory
        update_sql = "UPDATE inventory SET stock = stock - %s WHERE item_name LIKE %s"
        cursor.execute(update_sql, (quantity, f"%{item}%"))

        # 2. Check if the item just hit low stock
        check_sql = "SELECT item_name, stock, reorder_threshold FROM inventory WHERE item_name LIKE %s"
        cursor.execute(check_sql, (f"%{item}%",))
        result = cursor.fetchone()

        if result:
            db_item_name, current_stock, threshold = result

            if current_stock <= threshold:
                alert_message = f"⚠️ URGENT: {db_item_name.title()} is low! Only {current_stock} left."
                print(f"🚨 [ALERT TRIPPED]: {alert_message}")

                # --- 🟢 THE ZERO-SETUP WHATSAPP TRICK ---
                # actual phone number here (Include country code, e.g., 91 for India, but NO '+' sign)
                merchant_phone = "919451620308" 
                encoded_msg = urllib.parse.quote(alert_message)
                wa_url = f"https://wa.me/{merchant_phone}?text={encoded_msg}"

        conn.commit()
        cursor.close()
        conn.close()

        message = f"Successfully logged {quantity} of '{item}'"

    except Exception as e:
        message = f"Database error: {str(e)}"
        print(f"❌ [DATABASE ERROR]: {str(e)}\n")

    # 🟢 NEW: Send the wa_url back to the browser alongside the alert
    return jsonify({
        "status": "success", 
        "message": message,
        "alert": alert_message,
        "wa_url": wa_url
    })

@app.route('/restock', methods=['POST'])
def restock_inventory():
    data = request.get_json()
    item = data.get('item', '')
    
    # Ensure quantity is a positive integer
    try:
        quantity = abs(int(data.get('quantity', 0)))
    except ValueError:
        return jsonify({"status": "error", "message": "Quantity must be a number."})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)
        
        # 1. Verify the item actually exists first
        check_sql = "SELECT item_name, stock FROM inventory WHERE item_name LIKE %s"
        cursor.execute(check_sql, (f"%{item}%",))
        result = cursor.fetchone()
        
        if result:
            db_item_name, current_stock = result
            
            # 2. Add the new shipment to the existing stock
            update_sql = "UPDATE inventory SET stock = stock + %s WHERE item_name LIKE %s"
            cursor.execute(update_sql, (quantity, f"%{item}%"))
            conn.commit()
            
            new_stock = current_stock + quantity
            message = f"📦 Restock successful! Added {quantity} to '{db_item_name.title()}'. New total: {new_stock}."
            print(f"🟢 [RESTOCK]: {message}")
            
        else:
            message = f"❌ Item '{item}' not found in database. Cannot restock."
            print(f"⚠️ [RESTOCK FAILED]: {message}")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        message = f"Database error: {str(e)}"
        print(f"❌ [DATABASE ERROR]: {str(e)}\n")

    return jsonify({"status": "success", "message": message})

if __name__ == '__main__':
    app.run(debug=True)