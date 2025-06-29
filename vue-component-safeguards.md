# Vue Component File Safeguards

## Issue Prevention Checklist

### ✅ Before Making Changes
1. **Backup Working Files**: Always copy working Vue components before editing
2. **Verify File Structure**: Ensure `<template>`, `<script>`, and `<style>` sections exist
3. **Check File Size**: Vue files should be >1KB, not just a few bytes

### ⚠️ Commands to NEVER Use on Vue Files
```bash
# DANGEROUS - These destroy Vue file structure:
echo 'test' > src/components/ComponentName.vue
echo "anything" > *.vue
# Always use proper editing tools instead
```

### 🛠 Safe Editing Procedures
1. **Use search_replace for small changes**
2. **Use edit_file with proper Vue structure**
3. **Copy working files as templates**
4. **Verify changes immediately**

### 🚨 Quick Recovery Steps
If a Vue file gets corrupted:
1. Remove corrupted file: `Remove-Item "path/to/file.vue"`
2. Copy from working template: `Copy-Item "working-file.vue" "target-file.vue"`
3. Update component name and content as needed
4. Verify file has proper structure

### 📋 Vue File Validation
Every Vue component MUST have:
- `<template>` section with valid HTML
- `<script>` section with `export default`
- `<style>` section (can be empty but should exist)
- Proper component name in script section

### 🔍 Quick Verification Commands
```powershell
# Check file size (should be >1KB for real components)
Get-ChildItem "src/components/*.vue" | Select-Object Name, Length

# Check for proper Vue structure
Select-String -Path "src/components/*.vue" -Pattern "<template>|<script>|<style>" | Group-Object Filename
```

This prevents wasting time on Vue compilation errors in the future. 