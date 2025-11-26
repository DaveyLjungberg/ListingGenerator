"""
CSS Styles Module

Contains all premium PropTech styling for Listing Magic application.
"""


def get_premium_css():
    """
    Returns the complete premium CSS styling for the application

    Returns:
        str: Complete CSS styling as a string
    """
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600;700&display=swap');

/* Global Color Variables */
:root {
    --primary-navy: #1E293B;
    --accent-gold: #D4AF37;
    --surface-white: #FFFFFF;
    --background-gray: #F8FAFC;
    --text-primary: #334155;
    --text-secondary: #64748B;
}

/* Main Background */
.main {
    background-color: var(--background-gray);
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

/* Premium Card Design with Hover Effect */
.result-card {
    background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
    padding: 2.5rem;
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    border-left: 4px solid var(--accent-gold);
    margin-bottom: 1.5rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.result-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.card-header {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 1.2rem;
    margin-bottom: 1.5rem;
    color: var(--primary-navy);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 0.75rem;
}

.result-card p {
    margin-bottom: 1.5em;
    line-height: 1.8;
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
}

/* Premium Button Styling with Gold Glow */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-gold) 0%, #C4A137 100%) !important;
    color: var(--primary-navy) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.75rem 2rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 20px rgba(212, 175, 55, 0.4) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* Typography Hierarchy */
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: var(--primary-navy) !important;
    font-weight: 700 !important;
}

h3 {
    margin-top: 2rem;
    margin-bottom: 1rem;
}

p, div, span, label {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary);
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: var(--primary-navy) !important;
}

section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #FFFFFF !important;
}

/* Metrics/Status Dashboard */
[data-testid="stMetricValue"] {
    font-size: 2rem;
    font-weight: 700;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.875rem;
    font-family: 'Inter', sans-serif !important;
}

/* Photo Thumbnails with Hover */
img {
    border-radius: 8px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

img:hover {
    transform: scale(1.03);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    z-index: 10;
}

/* File Uploader Styling */
[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] + div {
    display: none !important;
}

[data-testid="stFileUploaderDropzone"] {
    text-align: center;
    border: 2px dashed var(--accent-gold) !important;
    background-color: rgba(212, 175, 55, 0.05) !important;
    border-radius: 12px !important;
}

/* Hide unnecessary elements */
[data-testid="InputInstructions"] {
    display: none !important;
}

/* Dividers */
hr {
    margin: 2rem 0;
    border: none;
    border-top: 2px solid #E2E8F0;
}

/* Input Fields */
input, textarea {
    font-family: 'Inter', sans-serif !important;
    border-radius: 8px !important;
}

/* Checkbox Styling */
[data-testid="stCheckbox"] {
    font-family: 'Inter', sans-serif !important;
}
</style>
"""
