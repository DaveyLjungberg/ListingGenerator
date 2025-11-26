"""
Address Parser Utility

Parses street addresses into components required by RESO standards.
"""

import re


def parse_street_address(address):
    """
    Parse street address into components required by RESO

    Args:
        address: e.g., "383 East Main Street"

    Returns:
        dict with keys: street_number, street_name, street_suffix

    Examples:
        "383 East Main Street" -> {street_number: "383", street_name: "East Main", street_suffix: "Street"}
        "42 Oak Avenue" -> {street_number: "42", street_name: "Oak", street_suffix: "Avenue"}
        "100-102 Park Rd" -> {street_number: "100-102", street_name: "Park", street_suffix: "Rd"}
    """
    # Common street suffixes
    suffixes = [
        'Street', 'St', 'Avenue', 'Ave', 'Road', 'Rd', 'Boulevard', 'Blvd',
        'Drive', 'Dr', 'Lane', 'Ln', 'Court', 'Ct', 'Circle', 'Cir',
        'Place', 'Pl', 'Way', 'Terrace', 'Ter', 'Parkway', 'Pkwy'
    ]

    # Create regex pattern for suffixes (case insensitive)
    suffix_pattern = '|'.join([re.escape(s) for s in suffixes])

    # Pattern: (number) (street name) (suffix)
    pattern = r'^(\d+[-\d]*)\s+(.+?)\s+(' + suffix_pattern + r')\.?$'

    match = re.match(pattern, address.strip(), re.IGNORECASE)

    if match:
        return {
            'street_number': match.group(1),
            'street_name': match.group(2).strip(),
            'street_suffix': match.group(3).capitalize()
        }
    else:
        # Fallback: try to at least get the number
        number_match = re.match(r'^(\d+[-\d]*)\s+(.+)$', address.strip())
        if number_match:
            return {
                'street_number': number_match.group(1),
                'street_name': number_match.group(2).strip(),
                'street_suffix': None
            }
        else:
            # Can't parse - return address as street name
            return {
                'street_number': None,
                'street_name': address.strip(),
                'street_suffix': None
            }
