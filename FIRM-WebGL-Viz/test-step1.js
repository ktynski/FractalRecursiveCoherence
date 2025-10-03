#!/usr/bin/env node

/**
 * Test Step 1: Basic Three.js Setup
 * This script will open the browser, take a screenshot, and capture console output
 */

import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testStep1() {
    console.log('🧪 Testing Step 1: Basic Three.js Setup...');
    
    let browser;
    try {
        // Launch browser
        browser = await puppeteer.launch({
            headless: false, // Show browser for debugging
            defaultViewport: { width: 1200, height: 800 },
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        const page = await browser.newPage();
        
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
        
        // Capture errors
        page.on('error', error => {
            console.error(`[Browser Error] ${error.message}`);
        });
        
        // Navigate to our app
        console.log('📍 Navigating to http://localhost:5173');
        await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
        
        // Wait for initialization
        console.log('⏳ Waiting for initialization...');
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Check if WebGL is working
        const webglStatus = await page.evaluate(() => {
            const canvas = document.querySelector('canvas');
            return {
                canvasExists: !!canvas,
                canvasSize: canvas ? `${canvas.width}x${canvas.height}` : null,
                webglContext: !!canvas?.getContext('webgl2') || !!canvas?.getContext('webgl')
            };
        });
        
        console.log('📊 WebGL Status:', webglStatus);
        
        // Get status indicators
        const statusInfo = await page.evaluate(() => {
            const indicators = document.querySelectorAll('.status-indicator');
            const fps = document.getElementById('fps')?.textContent;
            const objects = document.getElementById('objects')?.textContent;
            
            return {
                statusCount: indicators.length,
                activeCount: document.querySelectorAll('.status-active').length,
                fps: fps,
                objects: objects,
                statusClasses: Array.from(indicators).map(el => el.className)
            };
        });
        
        console.log('📈 App Status:', statusInfo);
        
        // Take screenshot
        const screenshotPath = join(__dirname, 'screenshots', 'step1-basic-setup.png');
        await page.screenshot({ 
            path: screenshotPath,
            fullPage: true 
        });
        console.log(`📸 Screenshot saved: ${screenshotPath}`);
        
        // Verify success criteria
        const success = {
            webglSupported: webglStatus.webglContext,
            canvasRendering: webglStatus.canvasExists,
            statusIndicators: statusInfo.activeCount >= 2, // At least WebGL and Scene should be active
            fpsPositive: parseInt(statusInfo.fps) > 0,
            objectsPresent: parseInt(statusInfo.objects) > 0
        };
        
        console.log('✅ Success Criteria Check:', success);
        
        const allPassed = Object.values(success).every(Boolean);
        console.log(allPassed ? '🎉 Step 1 PASSED!' : '❌ Step 1 FAILED!');
        
        // Save test results
        const results = {
            timestamp: new Date().toISOString(),
            step: 1,
            description: 'Basic Three.js Setup',
            success: allPassed,
            criteria: success,
            webglStatus,
            statusInfo,
            consoleMessages: consoleMessages.slice(-10) // Last 10 messages
        };
        
        await page.evaluate((results) => {
            localStorage.setItem('step1Results', JSON.stringify(results));
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

// Create screenshots directory
import { mkdirSync } from 'fs';
try {
    mkdirSync(join(__dirname, 'screenshots'), { recursive: true });
} catch (e) {
    // Directory might already exist
}

// Run test
testStep1().then(results => {
    console.log('\n📋 Final Results:', JSON.stringify(results, null, 2));
    process.exit(results.success ? 0 : 1);
}).catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
