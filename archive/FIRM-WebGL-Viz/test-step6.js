#!/usr/bin/env node

/**
 * Test Step 6: Sovereignty Attractor (Recursive Self-Composition)
 * Validates recursive depth, fractal dimension, and self-referential dynamics
 */

import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testStep6() {
    console.log('🧪 Testing Step 6: Sovereignty Attractor...');
    
    let browser;
    try {
        browser = await puppeteer.launch({
            headless: false,
            defaultViewport: { width: 1200, height: 800 },
            args: [
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--use-fake-ui-for-media-stream',
                '--use-fake-device-for-media-stream',
                '--allow-running-insecure-content',
                '--disable-web-security'
            ]
        });
        
        const page = await browser.newPage();
        
        // Grant microphone permissions
        const context = browser.defaultBrowserContext();
        await context.overridePermissions('http://localhost:5173', ['microphone']);
        
        // Capture console messages
        const consoleMessages = [];
        page.on('console', msg => {
            consoleMessages.push({
                type: msg.type(),
                text: msg.text(),
                timestamp: new Date().toISOString()
            });
            console.log(`[Browser Console] ${msg.type()}: ${msg.text()}`);
        });
        
        // Navigate to app
        console.log('📍 Navigating to http://localhost:5173');
        await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
        
        // Wait for full initialization including Sovereignty attractor
        console.log('⏳ Waiting for Sovereignty Attractor initialization...');
        await new Promise(resolve => setTimeout(resolve, 15000)); // Longer wait for complex recursive system
        
        // Check Sovereignty Attractor status
        const sovereigntyStatus = await page.evaluate(() => {
            const canvas = document.querySelector('canvas');
            const statusIndicators = document.querySelectorAll('.status-indicator');
            const sovereigntyIndicator = statusIndicators[7]; // 8th indicator (Sovereignty)
            
            // Get UI elements
            const recursiveDepth = document.getElementById('recursive-depth')?.textContent;
            const fractalDimension = document.getElementById('fractal-dimension')?.textContent;
            const selfComposition = document.getElementById('self-composition')?.textContent;
            const fps = document.getElementById('fps')?.textContent;
            const objects = document.getElementById('objects')?.textContent;
            const stepNumber = document.getElementById('current-step')?.textContent;
            
            return {
                canvasExists: !!canvas,
                sovereigntyIndicatorActive: sovereigntyIndicator?.classList.contains('status-active'),
                recursiveDepth: parseInt(recursiveDepth) || 0,
                fractalDimension: parseFloat(fractalDimension) || 0,
                selfComposition,
                fps: parseInt(fps) || 0,
                objects: parseInt(objects) || 0,
                stepNumber,
                allStatusActive: Array.from(statusIndicators).every(el => 
                    el.classList.contains('status-active')
                )
            };
        });
        
        console.log('👑 Sovereignty Attractor Status:', sovereigntyStatus);
        
        // Check for Sovereignty-related console messages
        const sovereigntyValidation = {
            hasSovereigntyInit: consoleMessages.some(msg => 
                msg.text.includes('Sovereignty') || msg.text.includes('👑') || msg.text.includes('recursive self-composition')
            ),
            hasRecursiveDepth: consoleMessages.some(msg => 
                msg.text.includes('Recursive Depth') || msg.text.includes('recursive')
            ),
            hasFractalDimension: consoleMessages.some(msg => 
                msg.text.includes('Fractal Dimension') || msg.text.includes('dimension')
            ),
            hasSelfReference: consoleMessages.some(msg => 
                msg.text.includes('Self-Reference') || msg.text.includes('Autonomy')
            ),
            hasSovereigntySuccess: consoleMessages.some(msg => 
                msg.text.includes('Sovereignty Attractor created successfully') ||
                msg.text.includes('Sovereignty Attractor integration complete')
            ),
            noSovereigntyErrors: !consoleMessages.some(msg => 
                msg.type === 'error' && msg.text.toLowerCase().includes('sovereignty')
            ),
            hasParticleGeneration: consoleMessages.some(msg => 
                msg.text.includes('Generated') && msg.text.includes('points')
            )
        };
        
        console.log('🔄 Sovereignty Validation:', sovereigntyValidation);
        
        // Take screenshot
        const screenshotPath = join(__dirname, 'screenshots', 'step6-sovereignty-attractor.png');
        await page.screenshot({ 
            path: screenshotPath,
            fullPage: true 
        });
        console.log(`📸 Screenshot saved: ${screenshotPath}`);
        
        // Test camera controls to view sovereignty attractor
        console.log('🎮 Testing camera controls with Sovereignty attractor...');
        
        // Rotate camera for better view of sovereignty attractor
        await page.mouse.move(600, 400);
        await page.mouse.down();
        await page.mouse.move(400, 500); // Rotate to see sovereignty attractor
        await page.mouse.up();
        
        // Wait for rendering update
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const finalCheck = await page.evaluate(() => {
            const fps = document.getElementById('fps')?.textContent;
            const objects = document.getElementById('objects')?.textContent;
            const recursiveDepth = document.getElementById('recursive-depth')?.textContent;
            const fractalDimension = document.getElementById('fractal-dimension')?.textContent;
            
            return {
                finalFPS: parseInt(fps) || 0,
                finalObjects: parseInt(objects) || 0,
                recursiveDepthStable: parseInt(recursiveDepth) >= 6,
                fractalDimensionValid: parseFloat(fractalDimension) > 2.0
            };
        });
        
        console.log('🎯 Final Sovereignty Check:', finalCheck);
        
        // Verify success criteria for Step 6
        const success = {
            webglWorking: sovereigntyStatus.canvasExists,
            allSystemsActive: sovereigntyStatus.allStatusActive,
            correctStep: sovereigntyStatus.stepNumber === '6/8',
            sovereigntyUIPresent: sovereigntyStatus.recursiveDepth > 0,
            validRecursiveDepth: sovereigntyStatus.recursiveDepth >= 6,
            validFractalDimension: sovereigntyStatus.fractalDimension > 2.0,
            selfCompositionActive: sovereigntyStatus.selfComposition === 'Active',
            renderingSmooth: sovereigntyStatus.fps > 20, // Allow lower FPS due to complexity
            sovereigntyInitialized: sovereigntyValidation.hasSovereigntyInit,
            recursiveDepthLogged: sovereigntyValidation.hasRecursiveDepth,
            fractalDimensionLogged: sovereigntyValidation.hasFractalDimension,
            selfReferenceLogged: sovereigntyValidation.hasSelfReference,
            sovereigntyComplete: sovereigntyValidation.hasSovereigntySuccess,
            noSovereigntyErrors: sovereigntyValidation.noSovereigntyErrors,
            particleGenerationWorking: sovereigntyValidation.hasParticleGeneration,
            objectCountIncreased: sovereigntyStatus.objects > 4, // Should have all previous + Sovereignty
            recursiveDepthStability: finalCheck.recursiveDepthStable,
            fractalDimensionStability: finalCheck.fractalDimensionValid
        };
        
        console.log('✅ Success Criteria Check:', success);
        
        // Calculate overall success
        const criticalSuccess = [
            success.webglWorking,
            success.correctStep,
            success.sovereigntyUIPresent,
            success.validRecursiveDepth,
            success.validFractalDimension,
            success.renderingSmooth,
            success.sovereigntyInitialized,
            success.sovereigntyComplete,
            success.noSovereigntyErrors
        ].every(Boolean);
        
        const allPassed = criticalSuccess;
        
        console.log(allPassed ? '🎉 Step 6 PASSED! Sovereignty Attractor is operational!' : '❌ Step 6 FAILED!');
        
        const results = {
            timestamp: new Date().toISOString(),
            step: 6,
            description: 'Sovereignty Attractor (Recursive Self-Composition)',
            success: allPassed,
            criteria: success,
            sovereigntyStatus,
            sovereigntyValidation,
            finalCheck,
            consoleMessages: consoleMessages.slice(-35) // Last 35 messages
        };
        
        // Save results to browser storage
        await page.evaluate((results) => {
            localStorage.setItem('step6Results', JSON.stringify(results));
        }, results);
        
        return results;
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        return { success: false, error: error.message };
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Run test
testStep6().then(results => {
    console.log('\n📋 Final Results:', JSON.stringify(results, null, 2));
    
    if (results.success) {
        console.log('\n🎉 Step 6 COMPLETE! Sovereignty Attractor is operational.');
        console.log('👑 Recursive self-composition with autonomous dynamics');
        console.log('📐 Fractal dimension D₀ = 2 + δ (recursive depth encoding)');
        console.log('🔄 Self-referential identity: Ψₙ₊₁ = Ψₙ ∘ Ψₙ');
        console.log('🎤 Audio-responsive recursive complexity modulation');
        console.log('✨ Ready to proceed to Step 7: Bireflection Operator');
    } else {
        console.log('\n❌ Step 6 FAILED! Check the issues above.');
    }
    
    process.exit(results.success ? 0 : 1);
}).catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
