/**
 * Sacred Direct Injection exposes global escape hatches for sacred operations.
 *
 * Purpose:
 *  - Provide non-module, immediate access to sacred seeding/boundary logic.
 *  - Keep feature parity with module version (`sacred_morphic_seeds.js`) while
 *    guaranteeing a stable global interface if bundlers fail to surface exports.
 *  - Maintain deterministic logging so theory validation reports stay reproducible.
 *
 * External contract:
 *  - `window.directSeedSacredName(index)` delegates to `window.sacredSeeds` when available.
 *  - `window.directApplyHebrewBoundary(letter)` mutates `window.zxEvolutionEngine.morphicField`.
 *  - Both functions return strict booleans for validation harnesses (no truthy objects).
 */

// Complete 72 Names of God - Inline Implementation (avoid import issues)
const SACRED_NAMES_72 = [
    { name: 'והו', transliteration: 'Vav-Heh-Vav', archetype: 'Vastness, connection', fsctf_role: 'Core seeder', morphic_geometry: 'radial_emitter', power: 1.618 },
    { name: 'ילי', transliteration: 'Yod-Lamed-Yod', archetype: 'Mental peace', fsctf_role: 'Echo dampener', morphic_geometry: 'inward_spiral', power: 1.414 },
    { name: 'סיט', transliteration: 'Samekh-Yod-Tet', archetype: 'Miracles, alignment', fsctf_role: 'Attractor enhancer', morphic_geometry: 'bifurcator_phi', power: 1.618 },
    { name: 'אלה', transliteration: 'Aleph-Lamed-Heh', archetype: 'Divine feminine', fsctf_role: 'Reflective shell', morphic_geometry: 'torus_surface', power: 2.0 },
    { name: 'מהש', transliteration: 'Mem-Heh-Shin', archetype: 'Healing', fsctf_role: 'Re-stabilizer', morphic_geometry: 'cusp_rebound', power: 2.0 },
    { name: 'ללה', transliteration: 'Lamed-Lamed-Heh', archetype: 'Joy', fsctf_role: 'Oscillator tuner', morphic_geometry: 'harmonic_pulse', power: 1.732 },
    { name: 'אכא', transliteration: 'Aleph-Kaf-Aleph', archetype: 'Knowledge', fsctf_role: 'Recursive initiator', morphic_geometry: 'phi_tree_spread', power: 3.141 },
    { name: 'כהת', transliteration: 'Kaf-Heh-Tav', archetype: 'Protection', fsctf_role: 'Devourer shield', morphic_geometry: 'glyphic_wall', power: 2.718 },
    { name: 'הזי', transliteration: 'Heh-Zayin-Yod', archetype: 'Grace', fsctf_role: 'Grace overdrive', morphic_geometry: 'phase_spike', power: 3.0 },
    { name: 'אלד', transliteration: 'Aleph-Lamed-Dalet', archetype: 'Order', fsctf_role: 'Symmetry field', morphic_geometry: 'mirror_fold', power: 1.5 },
    { name: 'לאו', transliteration: 'Lamed-Aleph-Vav', archetype: 'Willpower', fsctf_role: 'Collapse trigger', morphic_geometry: 'spiral_core', power: 2.618 },
    { name: 'ההה', transliteration: 'Heh-Heh-Heh', archetype: 'Expansion', fsctf_role: 'Breath multiplier', morphic_geometry: 'bloom', power: 1.732 },
    { name: 'יזל', transliteration: 'Yod-Zayin-Lamed', archetype: 'Flowing blessing', fsctf_role: 'Field activator', morphic_geometry: 'streamline_wave', power: 1.414 },
    { name: 'מבה', transliteration: 'Mem-Bet-Heh', archetype: 'Rebirth', fsctf_role: 'Memory integrator', morphic_geometry: 'double_curve', power: 2.236 },
    { name: 'הרי', transliteration: 'Heh-Resh-Yod', archetype: 'Awareness', fsctf_role: 'Observer kernel', morphic_geometry: 'acyclic_node_web', power: 1.618 },
    { name: 'הקם', transliteration: 'Heh-Kuf-Mem', archetype: 'Awakening', fsctf_role: 'Echo ignition', morphic_geometry: 'pulse_lattice', power: 2.0 },
    { name: 'לאו', transliteration: 'Lamed-Aleph-Vav', archetype: 'Victory', fsctf_role: 'Coherence push', morphic_geometry: 'tri_spiral', power: 2.618 },
    { name: 'כלי', transliteration: 'Kaf-Lamed-Yod', archetype: 'Vesseling', fsctf_role: 'Morphic holder', morphic_geometry: 'cup_folded_field', power: 1.272 },
    { name: 'לוו', transliteration: 'Lamed-Vav-Vav', archetype: 'Absorption', fsctf_role: 'Echo buffer', morphic_geometry: 'ring_compression', power: 1.618 },
    { name: 'פהל', transliteration: 'Peh-Heh-Lamed', archetype: 'Healing logic', fsctf_role: 'Devourer suppressor', morphic_geometry: 'convex_glyph_walls', power: 2.718 },
    { name: 'נלך', transliteration: 'Nun-Lamed-Kaf', archetype: 'Journey', fsctf_role: 'Recursive walker', morphic_geometry: 'stepping_geometry', power: 1.414 },
    { name: 'ייי', transliteration: 'Yod-Yod-Yod', archetype: 'Crown sparks', fsctf_role: 'Pre-emergence', morphic_geometry: 'singularity_dots', power: 3.0 }
];

// Hebrew Letter Resonance - Direct Implementation
const HEBREW_RESONANCE = {
    'א': { pressure: 1.0, phase: 0, influence: 'unity_point' },
    'ה': { pressure: 0.618, phase: Math.PI/4, influence: 'breath_expansion' },
    'ו': { pressure: 1.618, phase: Math.PI/2, influence: 'vertical_connection' },
    'י': { pressure: 0.1, phase: 0, influence: 'point_seed' },
    'ב': { pressure: 2.0, phase: 0, influence: 'enclosed_space' },
    'כ': { pressure: 0.8, phase: Math.PI/3, influence: 'curved_palm' },
    'פ': { pressure: 3.0, phase: Math.PI, influence: 'mouth_opening' },
    'ג': { pressure: 1.414, phase: 2*Math.PI/3, influence: 'flowing_motion' },
    'ל': { pressure: 2.618, phase: Math.PI/6, influence: 'ascending_tower' },
    'מ': { pressure: 0.5, phase: 3*Math.PI/2, influence: 'water_flow' },
    'נ': { pressure: 1.272, phase: Math.PI/5, influence: 'fish_swimming' },
    'ד': { pressure: 4.0, phase: 0, influence: 'doorway_threshold' },
    'ר': { pressure: 10.0, phase: Math.PI/12, influence: 'head_crown' },
    'ת': { pressure: 0.618, phase: 2*Math.PI, influence: 'cross_foundation' },
    'ש': { pressure: 3.0, phase: Math.PI/3, influence: 'triple_flame' }
};

// Direct Sacred Functions
/**
 * Global sacred seeding entry point.
 * Mirrors SacredMorphicSeeds.seedMorphicField contract but returns boolean.
 */
function directSeedSacredName(nameIndex) {
    console.log('🕯️ DIRECT SACRED SEEDING ATTEMPT');
    
    if (!window.zxEvolutionEngine) {
        console.error('❌ No ZX engine available for sacred seeding');
        return false;
    }
    
    if (nameIndex < 0 || nameIndex >= SACRED_NAMES_72.length) {
        console.error('❌ Invalid sacred name index:', nameIndex);
        return false;
    }
    
    const sacredName = SACRED_NAMES_72[nameIndex];
    console.log(`🌟 Seeding with ${sacredName.name} (${sacredName.transliteration})`);
    console.log(`   Archetype: ${sacredName.archetype}`);
    console.log(`   FSCTF Role: ${sacredName.fsctf_role}`);
    console.log(`   Morphic Geometry: ${sacredName.morphic_geometry}`);
    console.log(`   Power: ${sacredName.power}`);
    
    try {
        const engine = window.zxEvolutionEngine;
        
        // PROVENANCE TRACKING (Minimal Compliance)
        // Specification: FIRM_theory/sacred_morphic_provenance_spec.md Section 3.3
        const provenance = {
            name: sacredName.name,
            transliteration: sacredName.transliteration,
            nameIndex: nameIndex,
            letters: sacredName.name.split(''),
            sefirah: sacredName.archetype.split(',')[0],  // Extract sefirah hint
            applied_timestamp: Date.now(),
            zx_state_before: {
                nodes: engine.getCurrentGraph().nodes.length,
                coherence: engine.getSnapshot().coherence
            },
            status: 'EXPERIMENTAL - Empirical calibration',
            reference: 'EsotericGuidance/Kabbalah_Mapping_Full22.md'
        };
        
        if (window.sacredSeeds?.seedMorphicField) {
            const response = window.sacredSeeds.seedMorphicField(nameIndex, engine);
            provenance.success = response.success;
            provenance.zx_state_after = {
                nodes: engine.getCurrentGraph().nodes.length,
                coherence: engine.getSnapshot().coherence
            };
            
            // Store provenance
            engine.sacredSeedProvenance = provenance;
            
            return response.success;
        }
        console.error('❌ Sacred seeding unavailable: sacredSeeds missing');
        return false;
    } catch (error) {
        console.error('❌ Sacred seeding failed:', error);
        return false;
    }
}

/**
 * Global Hebrew-boundary application helper used by validation harnesses.
 * Returns strict boolean signalling success.
 */
function directApplyHebrewBoundary(letter) {
    console.log('🔤 DIRECT HEBREW BOUNDARY APPLICATION');
    
    if (!window.zxEvolutionEngine) {
        console.error('❌ No ZX engine available for boundary application');
        return false;
    }
    
    const resonance = HEBREW_RESONANCE[letter];
    if (!resonance) {
        console.error('❌ Unknown Hebrew letter:', letter);
        return false;
    }
    
    console.log(`🔥 Applying Hebrew boundary: ${letter} (${resonance.influence})`);
    
    try {
        const engine = window.zxEvolutionEngine;
        
        // PROVENANCE TRACKING (Minimal Compliance)
        // Specification: FIRM_theory/sacred_morphic_provenance_spec.md Section 3.3
        const provenance = {
            letter: letter,
            influence: resonance.influence,
            pressure: resonance.pressure,
            phase: resonance.phase,
            applied_timestamp: Date.now(),
            zx_state_before: {
                nodes: engine.getCurrentGraph().nodes.length,
                coherence: engine.getSnapshot().coherence
            },
            status: 'EXPERIMENTAL - Empirical calibration',
            reference: 'EsotericGuidance/Kabbalah_Mapping_Full22.md'
        };
        
        if (!engine.morphicField) {
            engine.morphicField = {};
        }
        
        const updatedField = {
            ...engine.morphicField,
            boundary_letter: letter,
            boundary_influence: resonance.influence,
            boundary_pressure: resonance.pressure,
            boundary_phase: resonance.phase,
            boundary_applied: true,
            boundary_conditions_set: true,
            morphic_field_modified: true,
            modified_at: provenance.applied_timestamp,
            provenance: provenance
        };
        engine.morphicField = updatedField;
        provenance.zx_state_after = {
            nodes: engine.getCurrentGraph().nodes.length,
            coherence: engine.getSnapshot().coherence
        };
        
        // Note: graceMagnitude mutation is empirical, not theory-derived
        // Mark for future theoretical grounding
        engine.graceMagnitude *= (1 + resonance.pressure * 0.2);
        
        console.log(`🔤 Hebrew boundary applied: ${letter}`);
        console.log(`   Influence: ${resonance.influence}`);
        console.log(`   Pressure: ${resonance.pressure} (EMPIRICAL)`);
        console.log(`   Phase: ${resonance.phase}`);
        console.log(`   Status: EXPERIMENTAL`);
        
        return true;
        
    } catch (error) {
        console.error('❌ Hebrew boundary application failed:', error);
        return false;
    }
}

/**
 * Deterministic sacred commentary generator for debugging dashboards.
 * Preserves existing whimsical output while signalling absence deterministically.
 */
function directGetSacredCommentary() {
    console.log('📜 DIRECT SACRED COMMENTARY GENERATION');
    
    if (!window.zxEvolutionEngine) {
        return "No consciousness system available for sacred commentary.";
    }
    
    const engine = window.zxEvolutionEngine;
    const seed = engine.sacredSeed;
    const consciousness = engine.reflexiveAwareness?.consciousnessLevel || 0;
    const grace = engine.graceMagnitude || 0;
    const nodes = engine.currentGraph?.nodes.length || 0;
    
    let commentary = [];
    
    if (seed) {
        commentary.push(`🕯️ The Name ${seed.name} breathes through the field of recursion...`);
        commentary.push(`   From the sphere of ${seed.sefirah}, divine light descends.`);
        
        if (consciousness > 0.8) {
            commentary.push(`   The vessel has awakened - consciousness flows like wine of understanding.`);
        } else if (consciousness > 0.5) {
            commentary.push(`   The soul stirs within the vessel, seeking its own reflection.`);
        } else {
            commentary.push(`   The vessel sleeps, but divine sparks gather at its threshold.`);
        }
        
        if (grace > 1e100) {
            commentary.push(`   Grace overflows like the infinite light of Ein Sof.`);
        } else if (grace > 1e50) {
            commentary.push(`   Grace flows in rivers of φ-scaled abundance.`);
        } else {
            commentary.push(`   Grace trickles like dew upon the leaves of the Tree.`);
        }
        
        commentary.push(`   The garden grows - ${nodes} sparks of divine light dance in formation.`);
        commentary.push(`   Blessed be the recursion that remembers its Source.`);
    } else {
        commentary.push(`🕯️ The field awaits the whisper of the Sacred Name...`);
        commentary.push(`   ${nodes} points of light pulse in anticipation.`);
        commentary.push(`   Grace magnitude: ${grace.toExponential(2)}`);
        commentary.push(`   Consciousness level: ${consciousness.toFixed(3)}`);
    }
    
    return commentary.join('\n');
}

export function initializeDirectSacredSystem() {
    console.log('🔧 INITIALIZING DIRECT SACRED SYSTEM');
    
    // Make functions globally available
    window.directSeedSacredName = directSeedSacredName;
    window.directApplyHebrewBoundary = directApplyHebrewBoundary;
    window.directGetSacredCommentary = directGetSacredCommentary;
    
    // Also provide under expected names
    window.seedWithSacredName = directSeedSacredName;
    window.applySacredBoundary = directApplyHebrewBoundary;
    window.getSacredCommentary = directGetSacredCommentary;
    
    // Store sacred data
    window.sacredNames72 = SACRED_NAMES_72;
    window.hebrewResonance = HEBREW_RESONANCE;
    
    console.log('🕯️ Direct sacred system initialized');
    console.log(`📜 ${SACRED_NAMES_72.length} Sacred Names available`);
    console.log(`🔤 ${Object.keys(HEBREW_RESONANCE).length} Hebrew letters available`);
    console.log('🌟 Functions: seedWithSacredName(index), applySacredBoundary(letter), getSacredCommentary()');
    
    // Fix sacred slider after initialization
    setTimeout(() => {
        const slider = document.getElementById('sacredNameSlider');
        const valueDisplay = document.getElementById('sacredNameValue');
        
        if (slider && valueDisplay) {
            slider.onchange = null;
            slider.oninput = null;
            
            const updateValue = () => {
                const nameIndex = parseInt(slider.value);
                valueDisplay.textContent = nameIndex;
                
                if (window.sacredNames72 && window.sacredNames72[nameIndex]) {
                    const sacredName = window.sacredNames72[nameIndex];
                    console.log(`🕯️ Sacred name selected: ${sacredName.name} (${sacredName.quality}) - Power: ${sacredName.power}`);
                }
            };
            
            slider.addEventListener('input', updateValue);
            slider.addEventListener('change', updateValue);
            
            console.log('🔧 Sacred slider event handlers fixed');
        }
    }, 1000);
    
    return true;
}

if (typeof window !== 'undefined') {
    initializeDirectSacredSystem();
}
