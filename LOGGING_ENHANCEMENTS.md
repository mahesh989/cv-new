# JD Processing Logging Enhancements

## Summary

Enhanced logging throughout the JD processing pipeline to clearly distinguish between **processed JD** and **legacy (original) JD** usage. All logging now includes detailed context for debugging and monitoring.

---

## 📊 Logging Locations

### 1. **JD Processing Service** (`jd_processing_service.py`)

#### `get_jd_text_for_ai()`
**Enhanced logging for processed vs legacy JD selection:**

```python
# When processed JD is found:
✅ [JD_PROCESSING] Using PROCESSED JD for {company} | 
   Mode: universal_ai | Sections: 8 | Length: 1234 chars

# When falling back to original JD:
📄 [JD_PROCESSING] Using LEGACY (original) JD for {company} | 
   Length: 2345 chars | 
   Reason: processed JD not available

# When no JD found:
❌ [JD_PROCESSING] No JD found (neither processed nor original) for {company}
```

**Log Levels:**
- `logger.debug()` - Checking for processed JD
- `logger.info()` - Successfully using processed/legacy JD
- `logger.warning()` - No JD found

---

### 2. **JD Analyzer** (`jd_analyzer.py`)

#### `_read_jd_file()`
**Enhanced logging for file reading with processed JD support:**

```python
# When processed JD is used:
✅ [JD_ANALYZER] Using PROCESSED JD for {company} | 
   Source: jd_processing_service | Length: 1234 chars

# When falling back to original file:
📄 [JD_ANALYZER] Using LEGACY (original) JD file | 
   Path: jd_original_20251124_123456.json | Length: 2345 chars | 
   Reason: Processed JD not available or error occurred

# Debug messages:
🔍 [JD_ANALYZER] Attempting to use processed JD for {company}
⚠️ [JD_ANALYZER] Error attempting processed JD, falling back to LEGACY file: {error}
```

**Log Levels:**
- `logger.debug()` - Attempting processed JD, extraction details
- `logger.info()` - Successfully using processed/legacy JD
- `logger.warning()` - Errors during processed JD attempt

---

### 3. **Skills Analysis** (`skills_analysis.py`)

#### `perform_preliminary_skills_analysis()`
**Enhanced logging for JD source tracking:**

```python
# When processed JD is used:
✅ [SKILLS_ANALYSIS] Using PROCESSED JD for {company} | 
   Original: 2345 chars → Processed: 1234 chars | 
   Reduction: 1111 chars

# When using legacy JD:
📄 [SKILLS_ANALYSIS] Using LEGACY (original) JD for {company} | 
   Length: 2345 chars | 
   Reason: Processed JD not available

# When error occurs:
⚠️ [SKILLS_ANALYSIS] Error getting processed JD for {company}, 
   using LEGACY (original) JD: {error} | Length: 2345 chars

# In detailed logging:
🔍 [SKILLS_ANALYSIS] JD content length: 1234 chars | Source: processed
🔍 [SKILLS_ANALYSIS] JD content length: 2345 chars | Source: legacy (original)
```

**Log Levels:**
- `logger.debug()` - Attempting processed JD, missing company/user info
- `logger.info()` - Successfully using processed/legacy JD with details
- `logger.warning()` - Errors during processed JD lookup

---

## 🔍 Log Message Patterns

### Processed JD Success
```
✅ [COMPONENT] Using PROCESSED JD for {company} | 
   [Additional context: mode, sections, length, etc.]
```

### Legacy JD Fallback
```
📄 [COMPONENT] Using LEGACY (original) JD for {company} | 
   [Additional context: length, reason, path, etc.]
```

### Error/Warning
```
⚠️ [COMPONENT] [Error description] | 
   [Fallback action taken] | 
   [Context: length, path, etc.]
```

---

## 📋 Logging Tags

All logs use consistent tags for easy filtering:

- `[JD_PROCESSING]` - JD processing service operations
- `[JD_ANALYZER]` - JD analyzer operations
- `[SKILLS_ANALYSIS]` - Skills analysis operations

---

## 🎯 Benefits

1. **Clear Visibility**: Instantly see which JD source is being used
2. **Debugging**: Easy to trace why processed JD wasn't used
3. **Monitoring**: Track processed JD adoption across the system
4. **Performance**: See character reduction from processing
5. **Troubleshooting**: Detailed error context for fallback scenarios

---

## 📊 Example Log Flow

### Successful Processed JD Usage:
```
🔍 [JD_PROCESSING] Checking for processed JD: Australia_for_UNHCR
✅ [JD_PROCESSING] Using PROCESSED JD for Australia_for_UNHCR | 
   Mode: universal_ai | Sections: 8 | Length: 1234 chars
✅ [JD_ANALYZER] Using PROCESSED JD for Australia_for_UNHCR | 
   Source: jd_processing_service | Length: 1234 chars
✅ [SKILLS_ANALYSIS] Using PROCESSED JD for Australia_for_UNHCR | 
   Original: 2345 chars → Processed: 1234 chars | Reduction: 1111 chars
```

### Legacy JD Fallback:
```
🔍 [JD_PROCESSING] Checking for processed JD: Australia_for_UNHCR
⚠️ [JD_PROCESSING] No processed JD found for Australia_for_UNHCR, trying original JD
📄 [JD_PROCESSING] Using LEGACY (original) JD for Australia_for_UNHCR | 
   Length: 2345 chars | Reason: processed JD not available
📄 [JD_ANALYZER] Using LEGACY (original) JD file | 
   Path: jd_original_20251124_123456.json | Length: 2345 chars | 
   Reason: Processed JD not available or error occurred
📄 [SKILLS_ANALYSIS] Using LEGACY (original) JD for Australia_for_UNHCR | 
   Length: 2345 chars | Reason: Processed JD not available
```

---

## 🔧 Filtering Logs

### Find all processed JD usage:
```bash
grep "Using PROCESSED JD" logs/*.log
```

### Find all legacy JD fallbacks:
```bash
grep "Using LEGACY" logs/*.log
```

### Find JD processing errors:
```bash
grep "JD_PROCESSING.*Error\|JD_PROCESSING.*Failed" logs/*.log
```

### Find JD source in skills analysis:
```bash
grep "SKILLS_ANALYSIS.*Source:" logs/*.log
```

---

## ✅ Implementation Status

- [x] Enhanced `get_jd_text_for_ai()` logging
- [x] Enhanced `_read_jd_file()` logging
- [x] Enhanced `perform_preliminary_skills_analysis()` logging
- [x] Added JD source tracking
- [x] Added character count comparisons
- [x] Added fallback reason logging
- [x] Consistent log message format
- [x] No linter errors

---

## 📝 Notes

- All logging maintains backward compatibility
- Debug logs are used for detailed tracing
- Info logs are used for important state changes
- Warning logs are used for fallback scenarios
- Error logs are used for actual failures

