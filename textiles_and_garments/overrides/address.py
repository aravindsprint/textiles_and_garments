def validate(doc, method=None):
    # Copy 'states' (GST State dropdown) → 'state' (State/Province)
    # before india_compliance validate_state() runs
    if doc.states and not doc.state:
        doc.state = doc.states