# Chrome Profiles: CDP vs Normal Chrome

## Important: Your Data is Safe

**Your original Chrome history, bookmarks, passwords, and all data are completely safe and untouched.**

The CDP setup uses a separate, temporary profile - it does NOT affect your normal Chrome data.

---

## Understanding Chrome Profiles

### Your Normal Chrome Profile
- **Location**: `~/Library/Application Support/Google/Chrome/`
- **Contains**: All your history, bookmarks, passwords, extensions, cookies, etc.
- **How to open**: Click Chrome icon in Applications or Dock (normal way)
- **Status**: Completely safe and untouched

### CDP Temporary Profile
- **Location (ví dụ)**: `/tmp/chrome-cdp-profile/` (macOS/Linux) hoặc một thư mục bất kỳ bạn chỉ định với `--user-data-dir`
- **Contains**: Empty profile created fresh for testing
- **How to open**: Start Chrome với các flag `--user-data-dir=...` và `--remote-debugging-port=9224` như hướng dẫn trong tài liệu CDP
- **Purpose**: Allow Playwright to connect and automate without affecting your real data

---

## How to Switch Between Profiles

### To Use Your Normal Chrome (with all your data)
```bash
# 1. Close CDP Chrome if running
pkill "Google Chrome"

# 2. Open Chrome normally
# - Click Chrome in Applications folder
# - Click Chrome in Dock
# - Or use Spotlight search
```

Your history, bookmarks, and everything will be back instantly.

### To Use CDP Chrome (for automation/testing)
```bash
# macOS (ví dụ)
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9224 \
  --user-data-dir=/tmp/chrome-cdp-profile

# Windows (ví dụ)
"C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=9224 ^
  --user-data-dir="C:\tmp\chrome-cdp-profile"
```

This starts a fresh, empty Chrome for testing purposes.

---

## Why Two Separate Profiles?

1. **Safety**: Automation scripts can't accidentally mess with your real data
2. **Clean Testing**: Empty profile ensures consistent test results
3. **Isolation**: Your browsing history stays private from automation scripts
4. **Required by CDP**: Chrome requires `--user-data-dir` flag for remote debugging

---

## Common Questions

### Q: Did the CDP script delete my history?
**A: No!** Your history is in your normal Chrome profile, which was never touched.

### Q: How do I get my history back?
**A:** Just close the CDP Chrome and open Chrome normally. Your data is already there.

### Q: Can I use my normal profile with CDP?
**A:** Not recommended. It's safer to keep automation separate from your personal data.

### Q: Where is my real Chrome data?
**A (macOS ví dụ):** `~/Library/Application Support/Google/Chrome/Default/`

### Q: Can I delete the CDP profile?
**A:** Yes! It's just for testing. Delete with: `rm -rf /tmp/chrome-cdp-profile`

---

## Quick Reference

| Action | Command/Method |
|--------|----------------|
| Open normal Chrome | Click Chrome icon (Applications/Dock) |
| Start CDP Chrome | `./scripts/start_chrome_with_cdp.sh` |
| Close all Chrome | `pkill "Google Chrome"` |
| Check CDP is running | `curl http://localhost:9224/json` |
| Delete CDP profile | `rm -rf /tmp/chrome-cdp-profile` |

---

## Visual Guide

```
Your Mac
├── Normal Chrome Profile (Your Data)
│   └── Location: ~/Library/Application Support/Google/Chrome/
│   └── Contains: History, Bookmarks, Passwords, Extensions
│   └── SAFE AND UNTOUCHED ✓
│
└── CDP Temporary Profile (Testing Only)
    └── Location: /tmp/chrome-cdp-profile/
    └── Contains: Empty/Fresh for each use
    └── Used by: Playwright automation scripts
```

---

## If You're Worried About Your Data

Run these commands to verify your Chrome data is still there:

```bash
# Check your Chrome profile exists
ls -la ~/Library/Application\ Support/Google/Chrome/Default/

# Check history file exists (it will show the file size)
ls -lh ~/Library/Application\ Support/Google/Chrome/Default/History

# Check bookmarks exist
cat ~/Library/Application\ Support/Google/Chrome/Default/Bookmarks | head -n 20
```

If these commands show files and data, your Chrome profile is intact!

---

## Summary

- **Normal Chrome** = Your real data (always safe)
- **CDP Chrome** = Temporary testing profile (empty, disposable)
- **They are completely separate** - one does not affect the other
- **To get your data back** = Just open Chrome normally
