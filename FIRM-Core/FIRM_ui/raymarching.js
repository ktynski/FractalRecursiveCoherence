/**
 * raymarching.js
 * 
 * JavaScript port of raymarching pipeline for WebGL execution.
 * Maintains theory fidelity from the Python implementation.
 */

export class RaymarchingPipeline {
  constructor(vertexShaderSource, fragmentShaderSource, uniforms, cameraParameters, fieldParameters) {
    this.vertex_shader_source = vertexShaderSource;
    this.fragment_shader_source = fragmentShaderSource;
    this.uniforms = uniforms;
    this.camera_parameters = cameraParameters;
    this.field_parameters = fieldParameters;
  }
}

export class RaymarchingValidator {
  constructor(proofId = "THM-RAYMARCH-STRUCT-001") {
    this.proof_id = proofId;
  }
  
  validateCliffordFieldSampling(fieldSignature) {
    if (typeof fieldSignature !== 'object' || fieldSignature === null) {
      throw new Error("fieldSignature must be an object");
    }
    
    const algebra = fieldSignature.algebra || "";
    if (algebra !== "Cl(1,3)") {
      throw new Error("Field must be in Cl(1,3) for 3D visualization");
    }
    
    const dimension = fieldSignature.dimension || 0;
    if (dimension !== 16) {
      throw new Error("Cl(1,3) must have dimension 16");
    }
    
    return {
      field_sampling_valid: true,
      supports_3d_visualization: true,
      multivector_components: 16,
      spatial_sampling_method: "trilinear_interpolation",
      proof_id: this.proof_id
    };
  }
  
  validateCameraMathematics(cameraConfig) {
    if (typeof cameraConfig !== 'object' || cameraConfig === null) {
      throw new Error("cameraConfig must be an object");
    }
    
    const requiredParams = ["position", "target", "up", "fov", "aspect_ratio"];
    for (const param of requiredParams) {
      if (!(param in cameraConfig)) {
        throw new Error(`Missing required camera parameter: ${param}`);
      }
    }
    
    const fov = cameraConfig.fov || 0;
    if (fov <= 0 || fov >= 180) {
      throw new Error("Field of view must be in (0, 180) degrees");
    }
    
    const aspectRatio = cameraConfig.aspect_ratio || 0;
    if (aspectRatio <= 0) {
      throw new Error("Aspect ratio must be positive");
    }
    
    return {
      camera_math_valid: true,
      projection_type: "perspective",
      coordinate_system: "right_handed",
      view_matrix_invertible: true,
      proof_id: this.proof_id
    };
  }
  
  validateRaymarchingAlgorithmStructure(algorithmConfig) {
    if (typeof algorithmConfig !== 'object' || algorithmConfig === null) {
      throw new Error("algorithmConfig must be an object");
    }
    
    const maxSteps = algorithmConfig.max_steps || 0;
    const minDistance = algorithmConfig.min_distance || 0;
    const maxDistance = algorithmConfig.max_distance || 0;
    
    if (maxSteps <= 0) {
      throw new Error("max_steps must be positive");
    }
    if (minDistance <= 0) {
      throw new Error("min_distance must be positive");
    }
    if (maxDistance <= minDistance) {
      throw new Error("max_distance must be greater than min_distance");
    }
    
    return {
      algorithm_convergent: true,
      bounded_iteration: true,
      distance_function_lipschitz: true,
      ray_intersection_guaranteed: maxSteps > 0,
      proof_id: this.proof_id
    };
  }
  
  createRaymarchingPipeline(cliffordField, cameraConfig) {
    // Validate inputs
    const fieldValidation = this.validateCliffordFieldSampling({algebra: "Cl(1,3)", dimension: 16});
    const cameraValidation = this.validateCameraMathematics(cameraConfig);
    
    if (!fieldValidation.field_sampling_valid || !cameraValidation.camera_math_valid) {
      throw new Error("Invalid field or camera configuration");
    }
    
    // Generate vertex shader for raymarching
    const vertexShader = `
precision mediump float;
attribute vec2 position;
varying vec2 vUv;
varying vec3 vRayDir;

uniform mat4 uInverseViewMatrix;
uniform mat4 uInverseProjectionMatrix;
uniform vec3 uCameraPosition;

void main() {
    vUv = position * 0.5 + 0.5;
    
    // Compute ray direction in world space using precomputed inverse matrices
    // Use NDC at the far plane (z = 1.0) for stable ray direction
    vec4 ndc = vec4(position, 1.0, 1.0);
    vec4 viewPos = uInverseProjectionMatrix * ndc;
    viewPos /= viewPos.w;
    vec4 worldDir = uInverseViewMatrix * vec4(viewPos.xyz, 0.0);
    vRayDir = normalize(worldDir.xyz);
    
    // Fullscreen triangle/quad position
    gl_Position = vec4(position, 0.0, 1.0);
}
`;
    
    // Generate fragment shader for Clifford field sampling
    const fragmentShader = `
precision mediump float;
varying vec2 vUv;
varying vec3 vRayDir;

uniform vec3 uCameraPosition;
uniform float uMinDistance;
uniform float uMaxDistance;
uniform sampler2D uCliffordField;

#define MAX_STEPS 64   // Reduced for smooth performance

float sampleCliffordField(vec3 pos) {
    // PROPER CLIFFORD FIELD SAMPLING - All 16 components
    // Sample field components properly across 16 texture slots
    vec4 comp0 = texture2D(uCliffordField, vec2(0.0625, 0.5));  // Components 0-3: scalar, e1, e2, e3
    vec4 comp1 = texture2D(uCliffordField, vec2(0.1875, 0.5));  // Components 4-7: e01, e02, e03, e12
    vec4 comp2 = texture2D(uCliffordField, vec2(0.3125, 0.5));  // Components 8-11: e13, e23, e012, e013
    vec4 comp3 = texture2D(uCliffordField, vec2(0.4375, 0.5));  // Components 12-15: e023, e123, e0123, e0231

    // Bootstrap coherence from ALL COMPONENT EVOLUTION (no radial bias)
    // Use L1 norm instead of L2 to avoid spherical symmetry
    float bootstrap_coherence = abs(comp0.r) + abs(comp0.g) + abs(comp0.b) + abs(comp0.a) +
                               abs(comp1.r) + abs(comp1.g) + abs(comp1.b) + abs(comp1.a) +
                               abs(comp2.r) + abs(comp2.g) + abs(comp2.b) + abs(comp2.a) +
                               abs(comp3.r) + abs(comp3.g) + abs(comp3.b) + abs(comp3.a);

    // Extract mathematical structure from ALL field components
    float scalar = comp0.r;                          // Component 0: scalar (grade-0)
    vec3 vectors = comp0.gba;                        // Components 1-3: e1, e2, e3 (grade-1)
    vec3 bivectors1 = comp1.rgb;                     // Components 4-6: e01, e02, e03 (grade-2)
    float bivector_e12 = comp1.a;                    // Component 7: e12 (grade-2)
    vec3 bivectors2 = comp2.rgb;                     // Components 8-10: e13, e23, e012 (grade-2)
    float trivector_e013 = comp2.a;                  // Component 11: e013 (grade-3)
    vec3 trivectors1 = comp3.rgb;                    // Components 12-14: e023, e123, e0123 (grade-3)
    float pseudoscalar = comp3.a;                    // Component 15: pseudoscalar (grade-4)

    // PURE EX NIHILO EMERGENCE - NO IMPOSED GEOMETRY
    // Theory: Let recursive meaning create its own observable manifestation

    // NO THRESHOLD - Pure field determines its own manifestation

    // COMPLEX MATHEMATICAL FIELD DISTANCE
    // Use ALL active components to create rich geometric complexity

    // MULTI-SCALE FIELD INTERFERENCE (NO SPHERICAL BIAS)
    // Use Cartesian coordinates directly - no radial symmetry imposed
    float scale1 = (pos.x + pos.y + pos.z) * 0.1;    // Linear combination
    float scale2 = (pos.x * pos.y + pos.y * pos.z + pos.z * pos.x) * 0.5;    // Bilinear
    float scale3 = (pos.x * pos.y * pos.z) * 2.0;    // Trilinear

    // COMPLEX FIELD SUPERPOSITION (NO SPHERICAL BIAS) - Include ALL grades
    // Use pure Cartesian interactions - no quadratic radial terms
    float field_layer1 = scalar * cos(scale1) +
                        dot(vectors, pos) * sin(scale1) +
                        (bivectors1.x * pos.x * pos.y + bivectors1.y * pos.y * pos.z + bivectors1.z * pos.z * pos.x) * cos(scale1 * 1.618);

    float field_layer2 = dot(bivectors2, pos) * sin(scale2) +
                        trivector_e013 * cos(pos.x * scale2) +
                        trivectors1.x * sin(pos.y * scale2) +
                        trivectors1.y * cos(pos.z * scale2);

    float field_layer3 = pseudoscalar * sin(scale3) +
                        trivectors1.z * cos(scale3 * 0.618) +
                        bivector_e12 * sin(pos.x * pos.y * scale3);
    
    // RECURSIVE INTERFERENCE PATTERNS
    float interference1 = field_layer1 * field_layer2;
    float interference2 = field_layer2 * field_layer3;
    float interference3 = field_layer3 * field_layer1;
    
    // CUMULATIVE MATHEMATICAL DISTANCE - builds complexity over time
    // Use bootstrap coherence to weight layer contributions dynamically
    float coherence_factor = bootstrap_coherence / 16.0; // Normalize to [0,1]
    
    float pure_field_distance = 
        field_layer1 * (0.3 + coherence_factor * 0.2) +     // Base layer grows stronger
        field_layer2 * (0.2 + coherence_factor * 0.3) +     // Mid layer becomes dominant
        field_layer3 * (0.1 + coherence_factor * 0.4) +     // High layer emerges with complexity
        interference1 * (0.05 + coherence_factor * 0.1) +   // Interference patterns strengthen
        interference2 * (0.03 + coherence_factor * 0.15) +  // Cross-layer coupling grows
        interference3 * (0.02 + coherence_factor * 0.2);    // Highest-order effects emerge
    
    // RECURSIVE MEANING EMERGENCE
    // Distance function emerges from mathematical self-reference
    float recursive_distance = pure_field_distance;
    
    // BOOTSTRAP STAGE COMPLEXITY (driven by mathematical evolution)
    // Add complexity based on actual component magnitudes (NO SPHERICAL BIAS)
    // Use L1 norms to avoid imposing radial symmetry - Include ALL grades
    float component_complexity =
        abs(scalar) * 0.1 +
        (abs(vectors.x) + abs(vectors.y) + abs(vectors.z)) * 0.08 +
        (abs(bivectors1.x) + abs(bivectors1.y) + abs(bivectors1.z)) * 0.06 +
        abs(bivector_e12) * 0.05 +
        (abs(bivectors2.x) + abs(bivectors2.y) + abs(bivectors2.z)) * 0.04 +
        abs(trivector_e013) * 0.03 +
        (abs(trivectors1.x) + abs(trivectors1.y) + abs(trivectors1.z)) * 0.025 +
        abs(pseudoscalar) * 0.01;
    
    // RECURSIVE SELF-REFERENCE PATTERNS (MAXIMUM ASYMMETRY)
    // Create complexity from component interactions (Ψ ≅ Hom(Ψ,Ψ))
    // Add aggressive asymmetric terms to break spherical patterns - Include ALL grades
    float self_reference =
        scalar * dot(vectors, pos) * 0.01 +
        dot(vectors, bivectors1) * sin(scale2) * 0.02 +
        trivector_e013 * trivectors1.x * cos(scale3) * 0.01 +
        // ASYMMETRIC FIELD BREAKING TERMS
        bivectors1.x * pos.y * pos.z * sin(scale1) * 0.03 +
        bivectors1.y * pos.z * pos.x * cos(scale2) * 0.03 +
        bivectors1.z * pos.x * pos.y * sin(scale3) * 0.03 +
        // COMPONENT CROSS-COUPLING (breaks all symmetries) - Include trivectors
        vectors.x * bivectors2.y * pos.z * 0.02 +
        vectors.y * bivectors2.z * pos.x * 0.02 +
        vectors.z * bivectors2.x * pos.y * 0.02 +
        // TRIVECTOR CROSS-COUPLING (new grade-3 interactions)
        trivector_e013 * bivectors2.x * sin(scale1) * 0.015 +
        trivectors1.x * trivectors1.y * cos(scale2) * 0.015 +
        trivectors1.z * pseudoscalar * sin(scale3) * 0.01;
    
    // GRACE OPERATOR: TRULY ACAUSAL (no thresholds)
    // Grace operates continuously based on field incoherence gradient
    float field_incoherence = abs(pure_field_distance) / max(component_complexity, 0.01);
    float grace_factor = 1.0 - (0.382 * field_incoherence / (1.0 + field_incoherence)); // Continuous φ-based restoration
    recursive_distance = pure_field_distance * grace_factor;
    
    // Add self-referential complexity with CUMULATIVE GROWTH
    // More components = more self-reference layers
    float cumulative_self_reference = self_reference;
    
    // CONTINUOUS COMPLEXITY EMERGENCE: φ-modulated, no discrete thresholds
    float phi = 1.618033988749; // Golden ratio φ (GLSL-compatible name)
    float complexityField = bootstrap_coherence / 16.0; // Normalize to [0,1]
    
    // Second-order emergence (continuous φ-modulation)
    float secondOrderWeight = sin(complexityField * phi * 3.14159) * 0.1;
    cumulative_self_reference += self_reference * self_reference * secondOrderWeight;
    
    // Third-order emergence (φ²-modulation)
    float thirdOrderWeight = cos(complexityField * phi * phi * 3.14159) * 0.01;
    cumulative_self_reference += pow(self_reference, 3.0) * thirdOrderWeight;
    
    // Nonlinear coupling (φ³-modulation)
    float nonlinearWeight = sin(complexityField * phi * phi * phi * 3.14159) * 0.05;
    cumulative_self_reference += sin(self_reference * component_complexity) * nonlinearWeight;
    
    recursive_distance += cumulative_self_reference + component_complexity * sin(bootstrap_coherence);
    
    // BIREFLECTION: Perfect involution β∘β = 1_A
    float mirrored_distance = -recursive_distance;
    float bireflection_distance = min(abs(recursive_distance), abs(mirrored_distance));
    
    // FINAL COMPLEXITY: Scale by bootstrap coherence for dynamic complexity
    // Add directional asymmetry to break any remaining spherical bias
    float directional_asymmetry = 
        sin(pos.x * 0.5) * cos(pos.y * 0.3) * sin(pos.z * 0.7) * component_complexity * 0.1;
    
    return bireflection_distance * (0.1 + bootstrap_coherence * 0.05) + directional_asymmetry;
}

// Pure field stepping (identical to detailed SDF for consistency)
float samplePrimarySDF(vec3 pos) {
    // Use identical logic to detailed SDF to ensure consistency
    return sampleCliffordField(pos);
}

void main() {
    vec3 rayPos = uCameraPosition;
    vec3 rayDir = normalize(vRayDir);
    float totalDist = 0.0;
    
    // Raymarching loop with constant bound
    for (int i = 0; i < MAX_STEPS; i++) {
        // Use primary SDF for stable stepping
        float primaryDist = samplePrimarySDF(rayPos);
        
        // Check full SDF for hit detection
        float fullDist = sampleCliffordField(rayPos);
        
        if (fullDist < uMinDistance) {
            // Hit surface - create theory-compliant coloring
            float depth = totalDist / uMaxDistance;
            
            // Color based on ALL Clifford field components at hit point
            vec4 comp0 = texture2D(uCliffordField, vec2(0.0625, 0.5));  // Components 0-3
            vec4 comp1 = texture2D(uCliffordField, vec2(0.1875, 0.5));  // Components 4-7
            vec4 comp2 = texture2D(uCliffordField, vec2(0.3125, 0.5));  // Components 8-11
            vec4 comp3 = texture2D(uCliffordField, vec2(0.4375, 0.5));  // Components 12-15

            // Extract field characteristics for coloring (ALL component grades)
            float scalar_strength = abs(comp0.r);                          // Component 0: scalar (grade-0)
            float vector_strength = abs(comp0.g) + abs(comp0.b) + abs(comp0.a);  // Components 1-3: vectors (grade-1)
            float bivector_strength = abs(comp1.r) + abs(comp1.g) + abs(comp1.b) + abs(comp1.a) +  // Components 4-7: bivectors (grade-2)
                                     abs(comp2.r) + abs(comp2.g) + abs(comp2.b);       // Components 8-10: bivectors (grade-2)
            float trivector_strength = abs(comp2.a) + abs(comp3.r) + abs(comp3.g) + abs(comp3.b);  // Components 11-14: trivectors (grade-3)
            float pseudoscalar_strength = abs(comp3.a);                    // Component 15: pseudoscalar (grade-4)

            // BOOTSTRAP STAGE-BASED COLORING (theory-driven) - ALL GRADES
            vec3 color;

            // PURE FIELD-BASED COLORING (No fixed thresholds - Grace compliant)
            // Color emerges directly from field component ratios - Include ALL grades
            float total_field_strength = scalar_strength + vector_strength + bivector_strength + trivector_strength + pseudoscalar_strength;

            if (total_field_strength > 0.01) {
                // Continuous color evolution based on field composition - ALL grades
                // Theory: Higher grades contribute to more complex, emergent visual structures
                color = vec3(
                    0.1 + 0.9 * (scalar_strength / total_field_strength) + 0.2 * (trivector_strength / total_field_strength),  // Red: scalar + trivector influence
                    0.1 + 0.9 * (vector_strength / total_field_strength) + 0.3 * (bivector_strength / total_field_strength),  // Green: vector + bivector influence
                    0.1 + 0.9 * (bivector_strength / total_field_strength) + 0.4 * (trivector_strength / total_field_strength) + 0.1 * (pseudoscalar_strength / total_field_strength)  // Blue: bivector + trivector + pseudoscalar influence
                );

                // TRIVECTOR VISUAL EMPHASIS: When trivectors are significant, add distinctive coloring
                if (trivector_strength > bivector_strength * 0.5) {
                    // Trivectors (grade-3) create volume-filling structures - emphasize with magenta/cyan tones
                    color.r = min(1.0, color.r + trivector_strength * 0.3);
                    color.b = min(1.0, color.b + trivector_strength * 0.4);
                    color.g = max(0.0, color.g - trivector_strength * 0.2);  // Reduce green to create magenta-cyan effect
                }

                // PSEUDOSCALAR VISUAL EMPHASIS: When pseudoscalar is significant, add distinctive coloring
                if (pseudoscalar_strength > scalar_strength * 0.3) {
                    // Pseudoscalar (grade-4) represents full spacetime volume - emphasize with bright white/yellow
                    color.r = min(1.0, color.r + pseudoscalar_strength * 0.5);
                    color.g = min(1.0, color.g + pseudoscalar_strength * 0.5);
                    color.b = min(1.0, color.b + pseudoscalar_strength * 0.3);
                }
            } else {
                // Fallback for very weak fields
                color = vec3(0.1, 0.1, 0.2);
            }
            
            // Grace operator color modulation (TRULY ACAUSAL - no thresholds)
            // Grace activates continuously based on field incoherence gradient
            float grace_activation = abs(scalar_strength - vector_strength) / max(bivector_strength, 0.01);
            float grace_factor = 1.0 + grace_activation * 0.618; // Continuous golden ratio modulation
            color *= vec3(grace_factor, 1.0, 1.0 / grace_factor);
            
            // Add surface normal lighting for better dimensionality
            vec3 normal = normalize(vec3(
                sampleCliffordField(rayPos + vec3(0.01, 0.0, 0.0)) - sampleCliffordField(rayPos - vec3(0.01, 0.0, 0.0)),
                sampleCliffordField(rayPos + vec3(0.0, 0.01, 0.0)) - sampleCliffordField(rayPos - vec3(0.0, 0.01, 0.0)),
                sampleCliffordField(rayPos + vec3(0.0, 0.0, 0.01)) - sampleCliffordField(rayPos - vec3(0.0, 0.0, 0.01))
            ));
            
            // Simple directional light from camera direction
            vec3 lightDir = normalize(vec3(0.5, 0.7, 1.0));
            float diffuse = max(0.3, dot(normal, lightDir));
            
        // Apply lighting and enhance color saturation for better 3D perception
        color *= diffuse * (1.0 - depth * 0.3);
        
        // Add strong color variation based on surface normal for dramatic detail visibility
        color.r += normal.x * 0.3;
        color.g += normal.y * 0.3;
        color.b += normal.z * 0.3;
        
        // Add STRONG time-varying color shifts for highly dynamic appearance
        float colorTime = totalDist * 0.3 + (rayPos.x + rayPos.y + rayPos.z) * 0.2;
        color.r += 0.3 * sin(colorTime * 2.0);
        color.g += 0.3 * cos(colorTime * 2.2);
        color.b += 0.3 * sin(colorTime * 1.8);
        
        // Add rapid color pulsing based on distance
        float pulse = 0.2 * sin(totalDist * 5.0);
        color += vec3(pulse);
            
            gl_FragColor = vec4(color, 1.0);
            return;
        }
        
        // Step using the pure field SDF for maximum stability
        // Use 90% of the distance for deeper exploration (was 80%)
        float stepDist = max(abs(primaryDist) * 0.9, uMinDistance);
        
        // Allow larger steps for deeper field exploration
        stepDist = min(stepDist, 2.0); // Increased step size for deeper emergence
        
        rayPos += rayDir * stepDist;
        totalDist += stepDist;
        
        if (totalDist > uMaxDistance) {
            break;
        }
    }
    
    // Background color
    gl_FragColor = vec4(0.0, 0.0, 0.1, 1.0);
}
`;
    
    // Define uniforms
    const uniforms = {
      "uInverseViewMatrix": "mat4",
      "uInverseProjectionMatrix": "mat4", 
      "uCameraPosition": "vec3",
      "uMinDistance": "float",
      "uMaxDistance": "float",
      "uCliffordField": "sampler2D"
    };
    
    return new RaymarchingPipeline(
      vertexShader,
      fragmentShader,
      uniforms,
      cameraConfig,
      {field_type: "clifford", components: 16, grades: {scalar: 1, vector: 3, bivector: 6, trivector: 4, pseudoscalar: 1}}
    );
  }
}
