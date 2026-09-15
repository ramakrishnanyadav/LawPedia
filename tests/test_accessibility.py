"""
WCAG 2.2 AAA Contrast Ratio Computation & ARIA Accessibility Test Suite
"""

import re
import os
from pathlib import Path


def parse_css_hex_color(css_content: str, token_name: str) -> str:
    """
    Extracts hex color code for a specific CSS custom property from tokens.css.
    """
    match = re.search(rf"{token_name}:\s*(#[0-9a-fA-F]{{6}})", css_content)
    if not match:
        raise ValueError(f"Token {token_name} not found in CSS content")
    return match.group(1)


def hex_to_relative_luminance(hex_color: str) -> float:
    """
    Computes WCAG 2.2 relative luminance for a 6-digit hex color:
    L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    """
    hex_clean = hex_color.lstrip("#")
    r_255 = int(hex_clean[0:2], 16) / 255.0
    g_255 = int(hex_clean[2:4], 16) / 255.0
    b_255 = int(hex_clean[4:6], 16) / 255.0

    def convert_c(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r = convert_c(r_255)
    g = convert_c(g_255)
    b = convert_c(b_255)

    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def compute_wcag_contrast_ratio(hex_fg: str, hex_bg: str) -> float:
    """
    Computes WCAG contrast ratio (L1 + 0.05) / (L2 + 0.05).
    """
    l1 = hex_to_relative_luminance(hex_fg)
    l2 = hex_to_relative_luminance(hex_bg)
    if l1 < l2:
        l1, l2 = l2, l1
    ratio = (l1 + 0.05) / (l2 + 0.05)
    return round(ratio, 2)


def test_wcag_contrast_ratios_from_tokens_css():
    """
    Computes contrast ratios directly from frontend/src/styles/tokens.css values.
    """
    tokens_path = Path(__file__).parent.parent / "frontend" / "src" / "styles" / "tokens.css"
    assert tokens_path.exists(), f"tokens.css file not found at {tokens_path}"
    
    css_content = tokens_path.read_text(encoding="utf-8")

    ink = parse_css_hex_color(css_content, "--ink")
    ink_muted = parse_css_hex_color(css_content, "--ink-muted")
    paper = parse_css_hex_color(css_content, "--paper")

    status_supported_text = parse_css_hex_color(css_content, "--status-supported-text")
    status_supported_bg = parse_css_hex_color(css_content, "--status-supported-bg")

    status_contradicted_text = parse_css_hex_color(css_content, "--status-contradicted-text")
    status_contradicted_bg = parse_css_hex_color(css_content, "--status-contradicted-bg")

    # 1. Primary Text (--ink #0f172a) on Paper (--paper #ffffff) -> WCAG AAA >= 7.0
    contrast_primary = compute_wcag_contrast_ratio(ink, paper)
    print(f"\nPrimary Text Contrast Ratio ({ink} on {paper}): {contrast_primary}:1")
    assert contrast_primary >= 7.0, f"Primary text contrast ratio {contrast_primary}:1 falls below WCAG AAA (7.0:1)"

    # 2. Muted Text (--ink-muted #475569) on Paper (--paper #ffffff) -> WCAG AA >= 4.5
    contrast_muted = compute_wcag_contrast_ratio(ink_muted, paper)
    print(f"Muted Text Contrast Ratio ({ink_muted} on {paper}): {contrast_muted}:1")
    assert contrast_muted >= 4.5, f"Muted text contrast ratio {contrast_muted}:1 falls below WCAG AA (4.5:1)"

    # 3. Supported Badge Text on Supported BG -> WCAG AA >= 4.5
    contrast_supported = compute_wcag_contrast_ratio(status_supported_text, status_supported_bg)
    print(f"Supported Badge Contrast Ratio ({status_supported_text} on {status_supported_bg}): {contrast_supported}:1")
    assert contrast_supported >= 4.5, f"Supported status contrast ratio {contrast_supported}:1 falls below WCAG AA (4.5:1)"

    # 4. Contradicted Badge Text on Contradicted BG -> WCAG AA >= 4.5
    contrast_contradicted = compute_wcag_contrast_ratio(status_contradicted_text, status_contradicted_bg)
    print(f"Contradicted Badge Contrast Ratio ({status_contradicted_text} on {status_contradicted_bg}): {contrast_contradicted}:1")
    assert contrast_contradicted >= 4.5, f"Contradicted status contrast ratio {contrast_contradicted}:1 falls below WCAG AA (4.5:1)"


def test_aria_and_keyboard_navigation_attributes():
    """
    Inspects frontend source components to verify ARIA roles, skip links, and keyboard navigation.
    """
    app_path = Path(__file__).parent.parent / "frontend" / "src" / "App.tsx"
    navbar_path = Path(__file__).parent.parent / "frontend" / "src" / "components" / "Navbar.tsx"

    assert app_path.exists()
    assert navbar_path.exists()

    app_code = app_path.read_text(encoding="utf-8")
    nav_code = navbar_path.read_text(encoding="utf-8")

    # Verify main content landmark container
    assert 'id="main-content"' in app_code
    assert 'tabIndex={-1}' in app_code or 'tabIndex="-1"' in app_code

    # Verify skip-to-content keyboard link for screen reader users
    assert 'href="#main-content"' in nav_code
    assert 'Skip to main content' in nav_code

    # Verify primary navigation ARIA attributes
    assert 'aria-label=' in nav_code
    assert 'aria-current=' in nav_code

