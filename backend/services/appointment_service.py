# Dummy database of facility capacities (In a real app, this is in SQL)
FACILITY_METADATA = {
    "HSP123": {
        "Neurology": {"doctors": 2, "hours": 8, "slot_mins": 30}, # 32 slots total
        "Orthopedics": {"doctors": 4, "hours": 8, "slot_mins": 30} # 64 slots total
    }
}

def get_specialty_availability(facility_id: str, requested_dept: str, current_cases: int):
    """
    LOGIC EXPLANATION:
    1. We fetch the fixed 'Capacity' for the specific department from our metadata.
    2. We take the 'Real-time Load' (total_cases) from the latest ingestion.
    3. Available Slots = Total Theoretical Slots - Current Busy Patients.
    """
    facility = FACILITY_METADATA.get(facility_id)
    if not facility or requested_dept not in facility:
        return {"status": "Unknown", "message": "Department not found at this facility"}

    dept_info = facility[requested_dept]
    
    # Calculate Total Capacity: (Doctors * Hours * 60 mins) / slot_mins
    total_slots = (dept_info["doctors"] * dept_info["hours"] * 60) // dept_info["slot_mins"]
    
    # Calculate Remaining Capacity
    available_now = total_slots - current_cases

    # ########################################################################
    # SMART REDIRECTION LOGIC:
    # Solves PS 2.3: Redirecting from high-risk/overloaded zones.
    # ########################################################################
    if available_now <= 2:
        return {
            "status": "CRITICAL",
            "available_slots": 0,
            "message": f"The {requested_dept} department is at capacity. Redirecting to nearest PHC."
        }
    
    return {
        "status": "AVAILABLE",
        "available_slots": available_now,
        "message": f"Successfully found {available_now} slots in {requested_dept}."
    }