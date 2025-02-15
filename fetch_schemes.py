import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("/Users/divyamudgil01/Downloads/scheme-reccomendation-module-firebase-adminsdk-fbsvc-a6ecc00c31.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def fetch_schemes(user_input):
    """
    Fetches schemes from Firestore based on user input criteria.
    
    :param user_input: Dictionary containing user attributes (land_size, income, category, etc.)
    :return: List of matching schemes
    """
    schemes_ref = db.collection("schemes")
    query = schemes_ref  # Start with base collection

    # Apply category filter (if given)
    if "category" in user_input and user_input["category"]:
        query = query.where("category", "==", user_input["category"])
    
    # Fetch results
    results = query.stream()
    matching_schemes = []

    for scheme in results:
        scheme_data = scheme.to_dict()
        eligibility = scheme_data.get("eligibility_criteria", {})

        # Apply land size filter (if applicable)
        land_limit = eligibility.get("land_size_limit")
        if land_limit is not None and user_input.get("land_size", float('inf')) > land_limit:
            continue  # Skip scheme if user's land size exceeds limit

        # Apply income limit filter (if applicable)
        income_limit = eligibility.get("income_limit")
        if income_limit is not None and user_input.get("income", 0) > income_limit:
            continue  # Skip scheme if user's income exceeds limit

        # Apply Aadhaar requirement filter
        if eligibility.get("aadhaar_required", False) and not user_input.get("aadhaar_available", False):
            continue  # Skip if Aadhaar is required but not available

        # Apply government employee restriction
        if eligibility.get("govt_employee_restricted", False) and user_input.get("is_govt_employee", False):
            continue  # Skip if user is a government employee

        # Apply state filter
        if "state" in user_input and user_input["state"] not in scheme_data["applicable_states"] and "All" not in scheme_data["applicable_states"]:
            continue  # Skip if scheme is not available in user's state

        matching_schemes.append(scheme_data)

    return matching_schemes

# Example Usage
user_input = {
    "category": "Agriculture",
    "land_size": 1,  # User has 10 hectares of land
    "income": 50000,  # Annual income
    "aadhaar_available": True,
    "is_govt_employee": False,
    "state": "Odisha"
}

try:
    matched_schemes = fetch_schemes(user_input)
    if not matched_schemes:
        print("No matching schemes found for the given input.")
    for scheme in matched_schemes:
        print(f"✅ {scheme['name']} - {scheme['benefits']}")
except Exception as e:
    print(f"Error occurred: {e}")

#collections = db.collections()
#print("Available collections:", [collection.id for collection in collections])

