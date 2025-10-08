import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function captureScreenshots() {
  const browser = await puppeteer.launch({
    headless: false, // Set to true for headless mode
    defaultViewport: { width: 1920, height: 1080 }
  });
  
  const page = await browser.newPage();
  
  try {
    console.log('Navigating to localhost:8000...');
    await page.goto('http://localhost:8000', { 
      waitUntil: 'networkidle0',
      timeout: 30000 
    });
    
    // Wait for the system to initialize
    console.log('Waiting for system initialization...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Capture different states and views
    const screenshots = [
      { name: 'hero_interface', selector: 'body' },
      { name: 'comprehensive_interface', selector: 'body' },
      { name: 'evolution_viewport', selector: 'body' },
      { name: 'bootstrap_phase', selector: 'body' },
      { name: 'sovereignty_phase', selector: 'body' },
      { name: 'controls_panel_open', selector: 'body' },
      { name: 'zx_graph_view', selector: 'body' },
      { name: 'e8_topology_view', selector: 'body' },
      { name: 'consciousness_view', selector: 'body' }
    ];
    
    for (const screenshot of screenshots) {
      console.log(`Capturing ${screenshot.name}...`);
      
      // Wait a bit between captures to let the system evolve
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const screenshotPath = path.join(__dirname, 'vercel_screens', `${screenshot.name}.png`);
      await page.screenshot({ 
        path: screenshotPath,
        fullPage: true
      });
      
      console.log(`Saved: ${screenshotPath}`);
    }
    
    console.log('All screenshots captured successfully!');
    
  } catch (error) {
    console.error('Error capturing screenshots:', error);
  } finally {
    await browser.close();
  }
}

captureScreenshots().catch(console.error);
