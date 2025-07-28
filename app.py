from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
import shippo
import stripe

# === SET YOUR API KEYS ===
shippo.api_key = "shippo_live_9f7350d4c74a959ffddc8b384ce0b874ecfd60e1"
stripe.api_key = "shippo_live_9f7350d4c74a959ffddc8b384ce0b874ecfd60e1"  # 🔁 Replace this

# === APP SETUP ===
app = Flask(__name__)
CORS(app)  # Allows requests from frontend

# === FROM ADDRESS ===
FROM_ADDRESS = {
    "name": "Mbaise Youth Association",
    "street1": "7118 Rocky Ridge Lane",
    "city": "Richmond",
    "state": "TX",
    "zip": "77407",
    "country": "US",
    "email": "myanational@gmail.com"
}

# === GET SHIPPING RATES ===
@app.route('/shipping-rates', methods=['POST'])
def get_shipping_rates():
    data = request.json
    to_address = {
        "name": data['name'],
        "street1": data['street1'],
        "city": data['city'],
        "state": data['state'],
        "zip": data['zip'],
        "country": "US"
    }

    parcel = {
        "length": "10",
        "width": "7",
        "height": "4",
        "distance_unit": "in",
        "weight": "2",
        "mass_unit": "lb"
    }

    try:
        shipment = shippo.Shipment.create(
            address_from=FROM_ADDRESS,
            address_to=to_address,
            parcels=[parcel],
            async_=False  # 🛠 async_ not async
        )

        rates = shipment['rates']
        return jsonify(rates)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# === STRIPE CHECKOUT SESSION ===
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.json
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': data['product_name'],
                        },
                        'unit_amount': int(float(data['amount']) * 100),  # e.g., $19.99 = 1999
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='https://your-site.com/success',
            cancel_url='https://your-site.com/cancel',
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# === START SERVER ===
if __name__ == '__main__':
    app.run(port=4242)
