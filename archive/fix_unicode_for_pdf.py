#!/usr/bin/env python3
"""
Fix Unicode mathematical symbols for LaTeX/PDF compatibility
"""

import re

def fix_unicode_for_latex(input_file, output_file):
    """Replace Unicode math symbols with LaTeX-compatible versions"""
    
    # Define replacements for mathematical symbols
    replacements = {
        # FIRM operators
        '𝒳': r'$\mathcal{X}$',
        '𝒢': r'$\mathcal{G}$', 
        '𝒟': r'$\mathcal{D}$',
        'Ψ': r'$\Psi$',
        'β': r'$\beta$',
        'σ': r'$\sigma$',
        'Φ': r'$\Phi$',
        '𝒜': r'$\mathcal{A}$',
        '𝒦': r'$\mathcal{K}$',
        '𝒞': r'$\mathcal{C}$',
        '𝒪': r'$\mathcal{O}$',
        '𝒮': r'$\mathcal{S}$',
        '𝒱': r'$\mathcal{V}$',
        '𝑀': r'$M$',
        
        # Greek letters and mathematical symbols
        'φ': r'$\phi$',
        'α': r'$\alpha$',
        'γ': r'$\gamma$',
        'δ': r'$\delta$',
        'ε': r'$\epsilon$',
        'ζ': r'$\zeta$',
        'η': r'$\eta$',
        'θ': r'$\theta$',
        'ι': r'$\iota$',
        'κ': r'$\kappa$',
        'λ': r'$\lambda$',
        'μ': r'$\mu$',
        'ν': r'$\nu$',
        'ξ': r'$\xi$',
        'π': r'$\pi$',
        'ρ': r'$\rho$',
        'τ': r'$\tau$',
        'χ': r'$\chi$',
        'ψ': r'$\psi$',
        'ω': r'$\omega$',
        
        # Mathematical operators
        '∅': r'$\emptyset$',
        '∘': r'$\circ$',
        '⊗': r'$\otimes$',
        '∈': r'$\in$',
        '∉': r'$\notin$',
        '⊆': r'$\subseteq$',
        '∪': r'$\cup$',
        '∩': r'$\cap$',
        '→': r'$\rightarrow$',
        '←': r'$\leftarrow$',
        '↔': r'$\leftrightarrow$',
        '≈': r'$\approx$',
        '≅': r'$\cong$',
        '≠': r'$\neq$',
        '≤': r'$\leq$',
        '≥': r'$\geq$',
        '∞': r'$\infty$',
        '∀': r'$\forall$',
        '∃': r'$\exists$',
        '∑': r'$\sum$',
        '∏': r'$\prod$',
        '∫': r'$\int$',
        '∂': r'$\partial$',
        '∇': r'$\nabla$',
        '⊕': r'$\oplus$',
        '⊖': r'$\ominus$',
        '⊙': r'$\odot$',
        '⊘': r'$\oslash$',
        
        # Subscripts and superscripts (common ones)
        '₀': r'$_0$',
        '₁': r'$_1$', 
        '₂': r'$_2$',
        '₃': r'$_3$',
        '₄': r'$_4$',
        '₅': r'$_5$',
        '₆': r'$_6$',
        '₇': r'$_7$',
        '₈': r'$_8$',
        '₉': r'$_9$',
        'ₙ': r'$_n$',
        'ₜ': r'$_t$',
        'ₓ': r'$_x$',
        'ᵢ': r'$_i$',
        'ⱼ': r'$_j$',
        
        # Hebrew letters (keep as is but ensure proper encoding)
        'א': 'Aleph',
        'ב': 'Bet', 
        'ג': 'Gimel',
        'ד': 'Dalet',
        'ה': 'Heh',
        'ו': 'Vav',
        'ז': 'Zayin',
        'ח': 'Chet',
        'ט': 'Teth',
        'י': 'Yod',
        'כ': 'Kaf',
        'ל': 'Lamed',
        'מ': 'Mem',
        'נ': 'Nun',
        'ס': 'Samekh',
        'ע': 'Ayin',
        'פ': 'Peh',
        'צ': 'Tzaddi',
        'ק': 'Qof',
        'ר': 'Resh',
        'ש': 'Shin',
        'ת': 'Tav',
    }
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply replacements
    for unicode_char, latex_replacement in replacements.items():
        content = content.replace(unicode_char, latex_replacement)
    
    # Fix some specific patterns that might cause issues
    content = re.sub(r'D_H', r'$D_H$', content)
    content = re.sub(r'D_0', r'$D_0$', content)  
    content = re.sub(r'H\(X\)', r'$H(X)$', content)
    content = re.sub(r'TE_\{([^}]+)\}', r'$TE_{\1}$', content)
    content = re.sub(r'MI\(([^)]+)\)', r'$MI(\1)$', content)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed Unicode symbols in {input_file} -> {output_file}")
    return output_file

if __name__ == "__main__":
    input_file = "/Users/fractlphoneroom1/Desktop/AnalogExNahilo/EsotericGuidance/FIRM_Complete_Documentation.md"
    output_file = "/Users/fractlphoneroom1/Desktop/AnalogExNahilo/EsotericGuidance/FIRM_Complete_Documentation_PDF.md"
    fix_unicode_for_latex(input_file, output_file)
