# Clear Browser State - Graph Corruption

**Issue:** Graph state with huge phase denominators persists in browser storage.

**Run in browser console:**

```javascript
// 1. Clear all storage
localStorage.clear();
sessionStorage.clear();

// 2. Clear IndexedDB (if used)
indexedDB.databases().then(dbs => {
  dbs.forEach(db => indexedDB.deleteDatabase(db.name));
});

// 3. Reload
location.reload(true);
```

**Or manual DevTools:**

1. Open DevTools (`F12` or `Cmd+Option+I`)
2. Application tab
3. Storage → Clear site data
4. Check all boxes
5. Click "Clear site data"
6. Hard reload (`Cmd+Shift+R`)

**This will:**
- Clear corrupted graph state
- Force fresh graph creation
- Load new code with bounds
- Start clean

