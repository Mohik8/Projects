"""
Vancouver Island bylaw corpus.
Each bylaw has: id, municipality, category, title, text, constraints (machine-readable).
"""

BYLAWS = [
    # ── VICTORIA ─────────────────────────────────────────────────────────────
    {
        "id": "vic-noise-01",
        "municipality": "Victoria",
        "category": "Noise",
        "title": "Noise Disturbance – General Hours",
        "text": "No person shall cause or permit noise that disturbs a neighbour between 10:00 PM and 8:00 AM on any day.",
        "constraints": {"quiet_start": "22:00", "quiet_end": "08:00"},
        "tags": ["noise", "neighbour", "hours", "party", "music"],
    },
    {
        "id": "vic-noise-02",
        "municipality": "Victoria",
        "category": "Noise",
        "title": "Construction Noise",
        "text": "Construction activity producing noise is prohibited before 7:00 AM or after 8:00 PM Monday–Saturday, and all day Sunday.",
        "constraints": {"allowed_days": ["Mon","Tue","Wed","Thu","Fri","Sat"], "start": "07:00", "end": "20:00"},
        "tags": ["construction", "noise", "hours", "building"],
    },
    {
        "id": "vic-stb-01",
        "municipality": "Victoria",
        "category": "Short-Term Rentals",
        "title": "Short-Term Rental – Principal Residence",
        "text": "Short-term rentals (Airbnb, VRBO, etc.) are only permitted in a host's principal residence. Accessory dwellings may be rented short-term only if the principal dwelling is owner-occupied.",
        "constraints": {"principal_residence_required": True, "max_units": 1},
        "tags": ["airbnb", "rental", "vrbo", "short-term", "principal residence"],
    },
    {
        "id": "vic-stb-02",
        "municipality": "Victoria",
        "category": "Short-Term Rentals",
        "title": "Short-Term Rental Business Licence",
        "text": "All short-term rental operators must obtain an annual business licence from the City of Victoria prior to operating.",
        "constraints": {"licence_required": True, "renewal": "annual"},
        "tags": ["airbnb", "licence", "permit", "rental", "business"],
    },
    {
        "id": "vic-cycling-01",
        "municipality": "Victoria",
        "category": "Cycling",
        "title": "Cycling on Sidewalks",
        "text": "Cycling on sidewalks is prohibited in the Downtown Core. Outside the downtown core, cycling on sidewalks is permitted for persons under 12 years of age.",
        "constraints": {"sidewalk_cycling_prohibited_zone": "Downtown Core", "age_exception": 12},
        "tags": ["cycling", "bike", "sidewalk", "downtown"],
    },
    {
        "id": "vic-cycling-02",
        "municipality": "Victoria",
        "category": "Cycling",
        "title": "Helmet Requirement",
        "text": "Every cyclist must wear an approved bicycle helmet while on a public road or pathway.",
        "constraints": {"helmet_required": True},
        "tags": ["cycling", "helmet", "bike", "safety"],
    },
    {
        "id": "vic-fire-01",
        "municipality": "Victoria",
        "category": "Fire & Burning",
        "title": "Open Burning Prohibition",
        "text": "Open burning (fire pits, campfires, bonfires) is prohibited within the City of Victoria limits without a permit. Approved outdoor fireplaces using natural gas or propane are exempt.",
        "constraints": {"permit_required": True, "gas_exempt": True},
        "tags": ["fire", "bonfire", "campfire", "fire pit", "burning"],
    },
    {
        "id": "vic-dog-01",
        "municipality": "Victoria",
        "category": "Animals",
        "title": "Dog Leash Requirement",
        "text": "All dogs must be kept on a leash no longer than 2 metres when on public property, except in designated off-leash areas.",
        "constraints": {"max_leash_m": 2, "off_leash_areas_exist": True},
        "tags": ["dog", "leash", "pet", "animal", "off-leash"],
    },

    # ── SAANICH ───────────────────────────────────────────────────────────────
    {
        "id": "saa-noise-01",
        "municipality": "Saanich",
        "category": "Noise",
        "title": "Residential Noise Hours",
        "text": "In Saanich, noise that is audible beyond the property boundary is prohibited between 11:00 PM and 7:00 AM weekdays, and between 11:00 PM and 9:00 AM weekends.",
        "constraints": {"weekday_quiet_start": "23:00", "weekday_quiet_end": "07:00", "weekend_quiet_start": "23:00", "weekend_quiet_end": "09:00"},
        "tags": ["noise", "neighbour", "weekday", "weekend", "hours"],
    },
    {
        "id": "saa-cycling-01",
        "municipality": "Saanich",
        "category": "Cycling",
        "title": "Cycling Equipment Requirements",
        "text": "Bicycles operated after dark must have a white front light and a red rear light or reflector visible from 150 metres.",
        "constraints": {"front_light": "white", "rear_light_or_reflector": "red", "visibility_m": 150},
        "tags": ["cycling", "bike", "lights", "night", "equipment"],
    },
    {
        "id": "saa-stb-01",
        "municipality": "Saanich",
        "category": "Short-Term Rentals",
        "title": "Short-Term Rental Zoning Restriction",
        "text": "Short-term rentals in Saanich are only permitted in RS-6, RS-12, and RD zones when the unit is the owner's principal residence. Strata bylaws may impose additional restrictions.",
        "constraints": {"permitted_zones": ["RS-6", "RS-12", "RD"], "principal_residence_required": True},
        "tags": ["airbnb", "rental", "short-term", "zoning", "strata"],
    },

    # ── ESQUIMALT ─────────────────────────────────────────────────────────────
    {
        "id": "esq-noise-01",
        "municipality": "Esquimalt",
        "category": "Noise",
        "title": "Amplified Music",
        "text": "Amplified music outdoors in Esquimalt is prohibited after 9:00 PM without a special event permit.",
        "constraints": {"cutoff": "21:00", "permit_available": True},
        "tags": ["noise", "music", "amplified", "speakers", "outdoor", "party"],
    },
    {
        "id": "esq-cycling-01",
        "municipality": "Esquimalt",
        "category": "Cycling",
        "title": "Cycling Fines",
        "text": "Cyclists in Esquimalt who fail to stop at a stop sign face a fine of $109. Cycling without a helmet carries a fine of $29.",
        "constraints": {"stop_sign_fine": 109, "no_helmet_fine": 29},
        "tags": ["cycling", "fine", "stop sign", "helmet", "ticket"],
    },

    # ── OAK BAY ───────────────────────────────────────────────────────────────
    {
        "id": "ob-stb-01",
        "municipality": "Oak Bay",
        "category": "Short-Term Rentals",
        "title": "Short-Term Rental Prohibition",
        "text": "Short-term rentals are prohibited in Oak Bay. All residential rental periods must be a minimum of one month.",
        "constraints": {"stb_prohibited": True, "min_rental_days": 30},
        "tags": ["airbnb", "rental", "short-term", "prohibited", "oak bay"],
    },
    {
        "id": "ob-noise-01",
        "municipality": "Oak Bay",
        "category": "Noise",
        "title": "Noise Bylaw – General",
        "text": "Oak Bay's noise bylaw prohibits disturbing noise between 10:00 PM and 8:00 AM. Power equipment is restricted to 8:00 AM–8:00 PM Monday–Saturday only.",
        "constraints": {"quiet_start": "22:00", "quiet_end": "08:00"},
        "tags": ["noise", "power tools", "quiet hours"],
    },

    # ── SOOKE ─────────────────────────────────────────────────────────────────
    {
        "id": "soo-fire-01",
        "municipality": "Sooke",
        "category": "Fire & Burning",
        "title": "Recreational Fire Pits",
        "text": "Recreational fires in Sooke are permitted in approved fire pits on private property. The fire must be a minimum of 3 metres from any structure and must not emit smoke that causes a nuisance.",
        "constraints": {"min_distance_m": 3, "permit_required": False, "nuisance_smoke_prohibited": True},
        "tags": ["fire", "fire pit", "backyard", "burning", "recreational"],
    },
    {
        "id": "soo-stb-01",
        "municipality": "Sooke",
        "category": "Short-Term Rentals",
        "title": "Short-Term Rental Licence",
        "text": "Short-term rentals in Sooke require a valid business licence and must comply with the Zoning Bylaw. The operator must reside on the property.",
        "constraints": {"licence_required": True, "owner_occupied": True},
        "tags": ["airbnb", "rental", "short-term", "licence", "zoning"],
    },

    # ── LANGFORD ──────────────────────────────────────────────────────────────
    {
        "id": "lan-noise-01",
        "municipality": "Langford",
        "category": "Noise",
        "title": "Construction & Equipment Noise",
        "text": "In Langford, construction noise is prohibited before 7:00 AM and after 9:00 PM Monday–Friday, and before 9:00 AM and after 6:00 PM on weekends.",
        "constraints": {
            "weekday_start": "07:00", "weekday_end": "21:00",
            "weekend_start": "09:00", "weekend_end": "18:00"
        },
        "tags": ["construction", "noise", "equipment", "hours"],
    },
    {
        "id": "lan-business-01",
        "municipality": "Langford",
        "category": "Business",
        "title": "Home Occupation Bylaw",
        "text": "Home-based businesses in Langford must not create noise, odour, or traffic beyond what is customary for a residential area. No more than one non-resident employee is permitted on site.",
        "constraints": {"max_non_resident_employees": 1, "no_customer_signage": True},
        "tags": ["business", "home occupation", "home office", "zoning"],
    },
]
