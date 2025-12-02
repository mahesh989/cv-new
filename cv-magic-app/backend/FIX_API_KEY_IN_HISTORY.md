# Fix API Key in Git History

## Problem
GitHub is blocking the push because an OpenAI API key is in git history (commits: 7f19a53, 861eec1, 2d3e82e, 36ff4c4).

## Solutions

### Option 1: Allow Secret (Quick - if it's a test key)
1. Visit: https://github.com/mahesh989/cv-new/security/secret-scanning/unblock-secret/36F1Wbgpsmrzp5PCF7cXvCxXitG
2. Click "Allow secret" (only if this is a test key you can rotate)
3. Then push again: `git push origin enhanced-vps-ghs`

**⚠️ WARNING**: Only do this if you can immediately rotate/revoke this API key!

### Option 2: Remove from History (Secure - Recommended)
Use `git filter-branch` or BFG to remove the API key from all commits:

```bash
# Install git-filter-repo (better than filter-branch)
pip install git-filter-repo

# Remove the API key from all commits
git filter-repo --path cv-magic-app/backend/test.py --invert-paths
# Then re-add test.py with the fixed version (using env var)
git add cv-magic-app/backend/test.py
git commit -m "Security: Use environment variable for API key"
git push origin enhanced-vps-ghs --force
```

**⚠️ WARNING**: This rewrites history. You'll need to force push and coordinate with anyone else using this branch.

### Option 3: Rotate the Key (Safest)
1. Go to OpenAI dashboard and revoke the exposed key
2. Generate a new API key
3. Use Option 1 to allow the push (since old key is revoked)
4. Update your local environment with the new key

## Recommended: Option 3 + Option 1
1. Rotate the API key in OpenAI dashboard
2. Use the GitHub allow URL to push
3. Update your local `.env` or environment with new key

