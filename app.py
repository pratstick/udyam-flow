import os
import csv
import json
import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='static', template_folder='templates')

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

# Load Product Catalogue
PRODUCTS = []
with open(os.path.join(DATA_DIR, 'product_catalogue.csv'), mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        PRODUCTS.append(row)

# Load Mock GSTINs (keyed by gstin uppercase)
GSTIN_MAP = {}
with open(os.path.join(DATA_DIR, 'mock_gstin_registry.csv'), mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        GSTIN_MAP[row['gstin'].strip().upper()] = row

# Load Mock Udyams (keyed by udyam_number uppercase)
UDYAM_MAP = {}
with open(os.path.join(DATA_DIR, 'mock_udyam_registry.csv'), mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        UDYAM_MAP[row['udyam_number'].strip().upper()] = row

# Load SMB Leads Sample for Back-Office Triage
LEADS_SAMPLE = []
with open(os.path.join(DATA_DIR, 'smb_leads.csv'), mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if row.get('outcome') == 'Dropped':
            LEADS_SAMPLE.append(row)
        if len(LEADS_SAMPLE) >= 50:
            break

# In-memory orders store
ORDERS = {
    "ORD-82914": {
        "order_id": "ORD-82914",
        "business_name": "Balaji Dental Care",
        "contact_name": "Dr. Ramesh Nair",
        "phone": "+91 98451 23456",
        "bundle_name": "Office Pro Suite (Biz Fibre 300 + Cloud Suite)",
        "monthly_amount": 2247,
        "setup_fee": 0,
        "contract_months": 12,
        "stage": "TECH_DISPATCHED",
        "status_text": "Field Engineer Dispatched",
        "technician_name": "Suresh Kumar",
        "technician_phone": "+91 98110 54321",
        "scheduled_slot": "Tomorrow, 10:30 AM - 12:30 PM",
        "address": "Shop 164, Station Road, Kochi, Kerala",
        "created_at": "2026-11-04 15:30",
        "history": [
            {"time": "15:30", "title": "Order Placed", "desc": "Custom bundle configured via AI Advisor"},
            {"time": "15:32", "title": "Smart KYC Verified", "desc": "GSTIN & DigiLocker e-Sign approved"},
            {"time": "16:00", "title": "Field Dispatch Assigned", "desc": "Engineer Suresh Kumar scheduled"}
        ]
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify({"status": "success", "products": PRODUCTS})

@app.route('/api/gstin/<gstin>', methods=['GET'])
def lookup_gstin(gstin):
    q = gstin.strip().upper()
    if q in GSTIN_MAP:
        return jsonify({"found": True, "data": GSTIN_MAP[q]})
    
    # Partial search
    matches = [v for k, v in GSTIN_MAP.items() if q in k or q.lower() in v['legal_name'].lower()][:5]
    if matches:
        return jsonify({"found": True, "data": matches[0], "suggestions": matches})
    return jsonify({"found": False, "message": "GSTIN not found in mock registry"}), 404

@app.route('/api/udyam/<udyam_num>', methods=['GET'])
def lookup_udyam(udyam_num):
    q = udyam_num.strip().upper()
    if q in UDYAM_MAP:
        return jsonify({"found": True, "data": UDYAM_MAP[q]})
    
    matches = [v for k, v in UDYAM_MAP.items() if q in k or q.lower() in v['enterprise_name'].lower()][:5]
    if matches:
        return jsonify({"found": True, "data": matches[0], "suggestions": matches})
    return jsonify({"found": False, "message": "Udyam registration not found in mock registry"}), 404

@app.route('/api/advisor/recommend', methods=['POST'])
def recommend_bundle():
    data = request.json or {}
    btype = data.get('business_type', 'retail').lower() # retail, clinic, office, multi_site, manufacturing
    size = int(data.get('employee_count', 3))
    sites = int(data.get('num_sites', 1))
    needs = data.get('key_needs', []) # backup, cctv, pos, email, wifi, whatsapp
    has_gstin = data.get('has_gstin', True)

    selected_pids = []
    bundle_name = ""
    rationale = ""

    if btype in ['clinic', 'office', 'ca_firm', 'coaching']:
        bundle_name = "Office Pro Suite"
        selected_pids = ['P02', 'P16', 'P17', 'P20']
        if 'cctv' in needs:
            selected_pids.append('P23')
        if 'static_ip' in needs or size > 10:
            selected_pids.append('P11')
        rationale = "Recommended for high-trust professional firms requiring 99.9% uptime, compliant 1TB cloud backup for client records, and endpoint cybersecurity."

    elif sites > 1 or btype in ['restaurant_chain', 'multi_retail']:
        bundle_name = "Omni-Connect & Retail Guardian"
        selected_pids = ['P02', 'P09', 'P19', 'P23', 'P10']
        rationale = "Designed for multi-location businesses needing seamless central billing, automated 4G/5G failover for zero POS downtime, and centralized CCTV surveillance."

    elif btype in ['manufacturing', 'factory', 'textile']:
        bundle_name = "Smart Factory Enterprise Suite"
        selected_pids = ['P05', 'P21', 'P24']
        if 'fleet' in needs:
            selected_pids.append('P25')
        rationale = "Engineered for industrial units requiring dedicated 1:1 leased bandwidth, managed perimeter firewall, and real-time machine IoT health telemetry."

    else: # Micro retail, kirana, salon, pharmacy
        bundle_name = "Kirana Digital Booster"
        selected_pids = ['P04', 'P15', 'P22']
        if 'pos' in needs:
            selected_pids.append('P19')
        if 'cctv' in needs:
            selected_pids.append('P23')
        rationale = "Perfect for retail shops wanting rapid 2-day 5G AirFiber installation, WhatsApp catalog order generation, and guest Wi-Fi to engage customers."

    # Fetch product objects and calculate price
    recom_products = [p for p in PRODUCTS if p['product_id'] in selected_pids]
    monthly_total = sum(int(p['price_min_inr_per_month']) for p in recom_products)
    setup_total = sum(int(p['one_time_setup_inr']) for p in recom_products)

    return jsonify({
        "status": "success",
        "bundle_name": bundle_name,
        "rationale": rationale,
        "monthly_price": monthly_total,
        "setup_fee": setup_total,
        "recommended_pids": selected_pids,
        "products": recom_products
    })

@app.route('/api/kyc/verify', methods=['POST'])
def verify_kyc():
    data = request.json or {}
    gstin = data.get('gstin', '').strip().upper()
    udyam = data.get('udyam', '').strip().upper()
    doc_type = data.get('doc_type', 'gst')
    doc_date = data.get('doc_date', '2026-06-15')
    signatory_name = data.get('signatory_name', '').strip()

    anomalies = []
    
    # Reference date is 2026-07-15 as per case README
    ref_date = datetime.date(2026, 7, 15)

    # 1. Date Check (>90 days)
    try:
        d = datetime.datetime.strptime(doc_date, "%Y-%m-%d").date()
        days_old = (ref_date - d).days
        if days_old > 90:
            anomalies.append({
                "field": "doc_date",
                "severity": "CRITICAL",
                "message": f"Document is {days_old} days old (exceeds 90-day validity rule as of July 15, 2026). Please upload a utility bill from the last 3 months."
            })
    except Exception:
        pass

    # 2. GSTIN Status Check
    if gstin:
        if gstin in GSTIN_MAP:
            rec = GSTIN_MAP[gstin]
            if rec.get('status') in ['Cancelled', 'Suspended']:
                anomalies.append({
                    "field": "gstin",
                    "severity": "CRITICAL",
                    "message": f"GSTIN {gstin} is currently '{rec.get('status')}'. Enterprise telecom contracts require an Active status."
                })
        else:
            anomalies.append({
                "field": "gstin",
                "severity": "WARNING",
                "message": f"GSTIN {gstin} could not be found in active tax records. Proceeding via Sole Proprietor path."
            })

    # 3. Signatory Name check
    if gstin and gstin in GSTIN_MAP and signatory_name:
        legal = GSTIN_MAP[gstin]['legal_name'].lower()
        sig = signatory_name.lower()
        if GSTIN_MAP[gstin]['constitution'] == 'Proprietorship':
            sig_words = set(sig.split())
            legal_words = set(legal.split())
            if not sig_words.intersection(legal_words):
                anomalies.append({
                    "field": "signatory_name",
                    "severity": "WARNING",
                    "message": f"Signatory name '{signatory_name}' does not directly match Proprietor name '{GSTIN_MAP[gstin]['legal_name']}'. Additional authorization required."
                })

    passed = len([a for a in anomalies if a['severity'] == 'CRITICAL']) == 0

    return jsonify({
        "status": "success" if passed else "anomaly_detected",
        "passed": passed,
        "anomalies": anomalies,
        "verified_fields": {
            "legal_name": GSTIN_MAP[gstin]['legal_name'] if gstin in GSTIN_MAP else (UDYAM_MAP[udyam]['enterprise_name'] if udyam in UDYAM_MAP else signatory_name),
            "address": GSTIN_MAP[gstin]['principal_place_of_business'] if gstin in GSTIN_MAP else "Validated Business Address",
            "masked_aadhaar": "XXXX-XXXX-8924",
            "dpdp_consent_logged": True,
            "audit_hash": "sha256_e9c8f04b2a8d1e3a"
        }
    })

@app.route('/api/orders/create', methods=['POST'])
def create_order():
    data = request.json or {}
    order_id = f"ORD-{int(datetime.datetime.now().timestamp()) % 100000}"
    
    order = {
        "order_id": order_id,
        "business_name": data.get("business_name", "My Store"),
        "contact_name": data.get("contact_name", "Business Owner"),
        "phone": data.get("phone", "+91 98000 12345"),
        "bundle_name": data.get("bundle_name", "Kirana Digital Booster"),
        "monthly_amount": data.get("monthly_amount", 1499),
        "setup_fee": data.get("setup_fee", 0),
        "contract_months": data.get("contract_months", 12),
        "stage": "KYC_VERIFIED",
        "status_text": "KYC Approved · Dispatch Scheduled",
        "technician_name": "Rohan Verma",
        "technician_phone": "+91 98765 43210",
        "scheduled_slot": "Tomorrow, 11:00 AM",
        "address": data.get("address", "Main Market, Sector 17, Chandigarh"),
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "history": [
            {"time": "Just now", "title": "Order Confirmed", "desc": "Custom bundle selected"},
            {"time": "Just now", "title": "Smart KYC Approved", "desc": "Digital identity verified under DPDP Act"}
        ]
    }
    ORDERS[order_id] = order
    return jsonify({"status": "success", "order": order})

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = ORDERS.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify({"status": "success", "order": order})

@app.route('/api/orders/<order_id>/advance', methods=['POST'])
def advance_order(order_id):
    order = ORDERS.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    stages = ["ORDER_PLACED", "KYC_VERIFIED", "TECH_DISPATCHED", "SITE_FEASIBILITY", "ACTIVATED"]
    cur_idx = stages.index(order["stage"]) if order["stage"] in stages else 0
    next_idx = min(cur_idx + 1, len(stages) - 1)
    
    order["stage"] = stages[next_idx]
    
    status_map = {
        "ORDER_PLACED": "Order Received & Drafted",
        "KYC_VERIFIED": "Smart KYC Approved · Installation Scheduled",
        "TECH_DISPATCHED": "Technician En Route to Site",
        "SITE_FEASIBILITY": "On-Site Hardware Installation in Progress",
        "ACTIVATED": "Service Active & Live (99.9% SLA Online)"
    }
    order["status_text"] = status_map[order["stage"]]
    order["history"].append({
        "time": "Just now",
        "title": order["status_text"],
        "desc": f"Automated milestone transition to {order['stage']}"
    })
    
    return jsonify({"status": "success", "order": order})

@app.route('/api/leads/dropped', methods=['GET'])
def get_dropped_leads():
    results = []
    for l in LEADS_SAMPLE:
        score = 20
        if l.get('has_gstin') == 'Y':
            score += 40
        if l.get('annual_turnover_band') in ['25L-1Cr', '1Cr-5Cr', '5Cr+']:
            score += 25
        if l.get('stage_reached') in ['Needs assessed', 'Quote accepted']:
            score += 20
        
        tier = "HIGH" if score >= 70 else ("MEDIUM" if score >= 45 else "LOW")
        
        results.append({
            "lead_id": l.get('lead_id'),
            "business_name": l.get('business_name'),
            "segment": l.get('segment'),
            "city": l.get('city'),
            "drop_reason": l.get('drop_reason'),
            "stage_reached": l.get('stage_reached'),
            "propensity_score": min(score, 98),
            "propensity_tier": tier,
            "monthly_spend": l.get('monthly_telecom_spend_inr', '3000'),
            "recommended_action": "Partner Dispatch (Warm Assist)" if tier == "HIGH" else "WhatsApp Nudge Campaign"
        })
    return jsonify({"status": "success", "leads": results})

if __name__ == '__main__':
    print("Starting Airtel SYNC: Project Udyam Digital Prototype Server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
