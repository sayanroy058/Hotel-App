# 📖 Document Reuse Feature - Quick Guide

## 🎯 What's New?

When you search for a document ID that already exists, instead of showing an error, the system now asks:

**"Do you want to use this existing document?"**

You can choose:
- ✅ **Yes** - Reuse the existing document (no upload needed!)
- ❌ **No** - Upload a new document instead

---

## 🚀 How to Use It

### Step-by-Step Guide

#### **Scenario: Guest checking in with existing document**

1. **Navigate to Check-in Page**
   ```
   Dashboard → Check-in/Check-out → Select Booking → Check-in
   ```

2. **Search for Document ID**
   - Enter document ID (e.g., "777777")
   - Click "Search" button

3. **Review Search Result**
   
   If document exists, you'll see:
   ```
   ┌──────────────────────────────────────┐
   │ ℹ️ Document Found!                   │
   │                                      │
   │ Previously uploaded by:              │
   │ Test - Guest 1                       │
   │ on 2025-09-22 17:17:10              │
   │                                      │
   │ Room: 501 | Type: voter_id          │
   │ ──────────────────────────────────  │
   │                                      │
   │ Do you want to use this document?   │
   │                                      │
   │ [✅ Yes, Use This Document]          │
   │ [❌ No, Upload New One    ]          │
   └──────────────────────────────────────┘
   ```

4. **Choose Your Option**

   **Option A: Reuse Existing Document**
   - Click "✅ Yes, Use This Document"
   - System will:
     - Link existing document to current booking
     - Show success message: "✅ Existing document reused successfully!"
     - Update progress counter
     - No file upload needed!

   **Option B: Upload New Document**
   - Click "❌ No, Upload New One"
   - System will:
     - Clear the search result
     - Show upload form
     - Allow you to upload a different file

5. **Complete Check-in**
   - Once all documents are ready
   - Click "Complete Check-in" button
   - Guest is checked in!

---

## 💡 Common Use Cases

### Use Case 1: Returning Guest
**Problem:** Guest stayed before and you have their documents.  
**Solution:** Search for their document ID → Click "Yes" → Done!

### Use Case 2: Family Booking
**Problem:** Multiple family members share same address proof.  
**Solution:** 
- Upload for Guest 1
- For Guest 2: Search same ID → Click "Yes"
- For Guest 3: Search same ID → Click "Yes"

### Use Case 3: Wrong Guest
**Problem:** Searched wrong document ID.  
**Solution:** Click "No, Upload New One" → Search correct ID

---

## 🎨 Visual Flow

```
START
  ↓
Enter Document ID
  ↓
Click "Search"
  ↓
┌─────────────────┐
│ Document Found? │
└─────────────────┘
  ↓              ↓
 YES            NO
  ↓              ↓
Show Dialog    Enable Upload Form
  ↓              ↓
User Choice    Upload Document
  ↓          ↓
┌────────────────┐
│ Yes   │   No   │
└────────────────┘
  ↓          ↓
Reuse      Upload New
Document   Document
  ↓          ↓
✅ Success  ✅ Success
  ↓          ↓
Progress   Progress
Updated    Updated
  ↓          ↓
Check-in Complete
```

---

## 📋 Quick Tips

### ✅ Do's
- ✅ **Verify guest details** before clicking "Yes"
- ✅ **Check room number** matches expected guest
- ✅ **Review document type** is correct
- ✅ **Use for returning guests** to save time
- ✅ **Use for family members** sharing documents

### ❌ Don'ts
- ❌ **Don't reuse wrong guest's document** - Always verify
- ❌ **Don't skip verification** - Check details carefully
- ❌ **Don't assume** - Read the confirmation dialog

---

## 🔍 What You'll See

### When Document Exists
```
📄 Document Information Shown:
- Guest Name: Who uploaded it originally
- Upload Date: When it was first uploaded
- Room Number: Which room was it for
- Document Type: What kind of document
```

### After Clicking "Yes"
```
✅ Success Message:
"Existing document reused successfully for Guest 1!"

📊 Progress Updates:
- Uploaded counter increases
- Progress bar moves forward
- Document appears in list
```

### After Clicking "No"
```
🔄 Form Resets:
- Search result clears
- Upload form appears
- Ready for new document
```

---

## ❓ Frequently Asked Questions

### Q: Will the original file be affected?
**A:** No! The system creates a new database link but uses the same file. The original is never modified.

### Q: Can I reuse a document multiple times?
**A:** Yes! The same document can be reused for unlimited bookings.

### Q: What if I click "Yes" by mistake?
**A:** You can still delete it later from the documents list and upload a new one.

### Q: Does this work across different hotels?
**A:** No. Document search is restricted to your hotel only for privacy.

### Q: Will this slow down the system?
**A:** No! It actually saves storage space and speeds up check-in.

---

## 🎯 Benefits at a Glance

| Before | After |
|--------|-------|
| ❌ Error message | ✅ Confirmation dialog |
| ❌ Must upload again | ✅ Can reuse existing |
| ❌ Duplicate files | ✅ Shared files |
| ❌ Slower check-in | ✅ Faster check-in |
| ❌ More storage used | ✅ Less storage used |

---

## 🆘 Need Help?

**If document search doesn't work:**
1. Check if document ID is correct
2. Verify you're logged in as owner
3. Ensure document was uploaded previously
4. Try refreshing the page

**If "Yes" button doesn't work:**
1. Check your internet connection
2. Wait for page to fully load
3. Try clicking again
4. Check for any error messages

**If wrong document was reused:**
1. Go to Documents section
2. Find the incorrect document
3. Delete it
4. Go back to check-in
5. Search correct document ID

---

## 📞 Contact Support

For technical issues or questions, please contact your system administrator.

---

*Quick Guide Created: October 6, 2025*
*Feature Version: 1.0*
