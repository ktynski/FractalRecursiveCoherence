/**
 * Theory Logger - Structured Logging for FIRM Mathematical Systems
 * 
 * Provides theory-compliant logging with appropriate frequency and detail levels.
 * Replaces excessive console noise with structured diagnostics.
 */

class TheoryLogger {
  constructor() {
    this.logLevel = 'INFO'; // DEBUG, INFO, WARN, ERROR
    this.logFrequency = {
      FRAME: 1000,    // Every 1000 frames
      EVOLUTION: 500, // Every 500 evolution steps  
      EMERGENCE: 1,   // Every emergence event
      CRITICAL: 1     // Every critical event
    };
    
    this.counters = new Map();
    this.lastLogs = new Map();
    this.logHistory = [];
    
    // Theory-compliant log categories
    this.categories = {
      VOID: '🌑',
      EMERGENCE: '🌌', 
      GRACE: '🌟',
      CONSCIOUSNESS: '💖',
      METAMIRROR: '🪞',
      BOOTSTRAP: '🚀',
      BIREFLECTION: '🔄',
      SOVEREIGNTY: '🏛️',
      SACRED: '🕯️',
      HEBREW: '🔤',
      ZX_EVOLUTION: '🧮',
      CLIFFORD_FIELD: '🔍',
      THEORY_VALIDATION: '📊'
    };
  }
  
  setLogLevel(level) {
    this.logLevel = level;
    console.log(`📋 Log level set to: ${level}`);
  }
  
  shouldLog(category, frequency = 'INFO') {
    if (this.logLevel === 'ERROR' && frequency !== 'CRITICAL') return false;
    if (this.logLevel === 'WARN' && !['CRITICAL', 'EMERGENCE'].includes(frequency)) return false;
    
    const key = `${category}_${frequency}`;
    const counter = this.counters.get(key) || 0;
    this.counters.set(key, counter + 1);
    
    const freq = this.logFrequency[frequency] || 1;
    return (counter % freq) === 0;
  }
  
  log(category, message, data = null, frequency = 'INFO') {
    if (!this.shouldLog(category, frequency)) return;
    
    const icon = this.categories[category] || '📝';
    const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
    
    const logEntry = {
      timestamp: Date.now(),
      category: category,
      message: message,
      data: data,
      frequency: frequency
    };
    
    // Console output
    if (data) {
      console.log(`${icon} [${timestamp}] ${message}`, data);
    } else {
      console.log(`${icon} [${timestamp}] ${message}`);
    }
    
    // Store in history
    this.logHistory.push(logEntry);
    if (this.logHistory.length > 1000) {
      this.logHistory.shift();
    }
  }
  
  // Convenience methods for common categories
  void(message, data = null) { this.log('VOID', message, data, 'EMERGENCE'); }
  emergence(message, data = null) { this.log('EMERGENCE', message, data, 'EMERGENCE'); }
  grace(message, data = null) { this.log('GRACE', message, data, 'FRAME'); }
  consciousness(message, data = null) { this.log('CONSCIOUSNESS', message, data, 'EMERGENCE'); }
  metamirror(message, data = null) { this.log('METAMIRROR', message, data, 'EMERGENCE'); }
  bootstrap(message, data = null) { this.log('BOOTSTRAP', message, data, 'EVOLUTION'); }
  sacred(message, data = null) { this.log('SACRED', message, data, 'EMERGENCE'); }
  hebrew(message, data = null) { this.log('HEBREW', message, data, 'EMERGENCE'); }
  zx(message, data = null) { this.log('ZX_EVOLUTION', message, data, 'EVOLUTION'); }
  clifford(message, data = null) { this.log('CLIFFORD_FIELD', message, data, 'FRAME'); }
  validation(message, data = null) { this.log('THEORY_VALIDATION', message, data, 'CRITICAL'); }
  
  // Critical events (always log)
  critical(category, message, data = null) {
    this.log(category, message, data, 'CRITICAL');
  }
  
  // Get log summary for diagnostics
  getSummary() {
    const categoryCounts = {};
    for (const entry of this.logHistory) {
      categoryCounts[entry.category] = (categoryCounts[entry.category] || 0) + 1;
    }
    
    return {
      total_logs: this.logHistory.length,
      log_level: this.logLevel,
      category_counts: categoryCounts,
      recent_logs: this.logHistory.slice(-10)
    };
  }
  
  exportLogs() {
    const blob = new Blob([JSON.stringify(this.logHistory, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `firm_theory_logs_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    console.log('📄 Theory logs exported');
  }
}

// Global logger instance
window.theoryLogger = new TheoryLogger();

// Convenience functions
window.setLogLevel = (level) => window.theoryLogger.setLogLevel(level);
window.getLogSummary = () => window.theoryLogger.getSummary();
window.exportTheoryLogs = () => window.theoryLogger.exportLogs();

console.log('📋 Theory logger initialized');
console.log('- window.setLogLevel("DEBUG"|"INFO"|"WARN"|"ERROR") - Control log verbosity');
console.log('- window.getLogSummary() - Get logging statistics');
console.log('- window.exportTheoryLogs() - Export logs for analysis');
