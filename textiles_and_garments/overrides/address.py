# import frappe
# from india_compliance.gst_india.constants import STATE_NUMBERS


# def validate(doc, method=None):
#     # Copy states (GST dropdown) → state before india_compliance checks
#     # if doc.states and not doc.state:
#     #     doc.state = doc.states

#     # If still no state and country is India, pick from GSTIN or skip gracefully
#     if doc.country == "India" and not doc.state:
#         # Set a default to prevent india_compliance from throwing
#         if doc.gstin and len(doc.gstin) >= 2:
#             prefix = doc.gstin[:2]
#             # Reverse lookup state from STATE_NUMBERS
#             state_by_number = {v: k for k, v in STATE_NUMBERS.items()}
#             doc.state = state_by_number.get(prefix, "Tamil Nadu")
#         else:
#             doc.state = "Tamil Nadu"  # your default fallback

# def validate(doc, method=None):
#     # Copy 'states' (GST State dropdown) → 'state' (State/Province)
#     # before india_compliance validate_state() runs
#     if doc.custom_states and not doc.state:
#         doc.state = doc.custom_states

def before_validate(doc, method=None):
    if doc.country == "India" and not doc.state:
        if getattr(doc, 'states', None):
            doc.state = doc.states
        elif getattr(doc, 'gst_state', None):
            doc.state = doc.gst_state