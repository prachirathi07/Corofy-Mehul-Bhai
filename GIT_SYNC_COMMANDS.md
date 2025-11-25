# Git Sync Commands - Step by Step

## Situation
- You have local changes that work
- You want to pull from: https://github.com/Dharm2412/dharm-mehulbhai.git
- The remote doesn't have your latest changes yet

## Recommended Approach: Commit First, Then Merge

### Step 1: Check Current Status
```powershell
cd C:\Users\prach\Desktop\NenoTechnology\mehulbhai
git status
```

### Step 2: Check Current Remotes
```powershell
git remote -v
```

### Step 3: Add Remote (if not already added)
If the remote doesn't exist or you want to add it with a specific name:
```powershell
git remote add upstream https://github.com/Dharm2412/dharm-mehulbhai.git
```
OR if it already exists with a different name, check with `git remote -v` first.

### Step 4: Commit Your Local Changes (IMPORTANT!)
First, make sure all your working changes are committed:
```powershell
# Check what files are modified
git status

# Add all changes
git add .

# Commit with a descriptive message
git commit -m "Local changes: removed redundant files, fixed followups router, cleaned up codebase"
```

### Step 5: Fetch Latest Changes from Remote
```powershell
git fetch upstream
```
(Replace `upstream` with the actual remote name if different - check with `git remote -v`)

### Step 6: Check What Will Be Merged
```powershell
# See commits that will be merged
git log HEAD..upstream/main --oneline
```
(Replace `main` with `master` if that's the branch name)

### Step 7: Merge Remote Changes
```powershell
# Merge the remote changes into your local branch
git merge upstream/main
```
(Replace `main` with `master` if needed)

**If there are conflicts:**
- Git will tell you which files have conflicts
- You'll need to manually resolve them
- After resolving, run:
```powershell
git add <resolved-files>
git commit -m "Merge remote changes with local updates"
```

### Step 8: Verify Everything Works
```powershell
git status
git log --oneline -10
```

---

## Alternative Approach: Stash Changes (If You Don't Want to Commit Yet)

If you prefer to stash your changes temporarily:

### Step 1-3: Same as above

### Step 4: Stash Your Changes
```powershell
git stash save "My local working changes"
```

### Step 5: Pull Remote Changes
```powershell
git pull upstream main
```

### Step 6: Reapply Your Stashed Changes
```powershell
git stash pop
```

**If there are conflicts after stash pop:**
- Resolve conflicts manually
- Run: `git add <resolved-files>`
- Run: `git stash drop` (to remove the stash after successful merge)

---

## If Remote Branch Name is Different

Check the branch name on the remote:
```powershell
git branch -r
```

Common branch names: `main`, `master`, `develop`

---

## Summary of Commands (Quick Reference)

**Recommended Flow:**
```powershell
cd C:\Users\prach\Desktop\NenoTechnology\mehulbhai
git status
git remote -v
git remote add upstream https://github.com/Dharm2412/dharm-mehulbhai.git
git add .
git commit -m "Local changes: removed redundant files, fixed followups router, cleaned up codebase"
git fetch upstream
git log HEAD..upstream/main --oneline
git merge upstream/main
git status
```

**If conflicts occur, you'll need to:**
1. Open conflicted files and resolve manually
2. `git add <resolved-files>`
3. `git commit -m "Resolved merge conflicts"`

