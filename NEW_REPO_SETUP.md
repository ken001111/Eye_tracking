# Setting Up a New GitHub Repository

## Step 1: Create New Repository on GitHub

1. Go to https://github.com/new
2. Repository name: Choose a name (e.g., `gaze-tracking-system`, `eye-tracking-research`, `stanford-gaze-tracking`)
3. Description: "Enhanced real-time gaze tracking system for clinical research - Stanford Neuroradiology Project"
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Connect Local Repository to New GitHub Repo

After creating the repository on GitHub, run these commands:

```bash
cd "Corey Keller/Eye/gaze_tracking"

# Add the new remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Verify remote
git remote -v

# Push to new repository
git push -u origin main
```

## Step 3: Update Repository Information

After pushing, update these files with your new repository URL:

1. **README.md** - Update clone URL in installation section
2. **README.md** - Update citation section with new URL
3. **AUTHORS.md** - Update if needed

## Alternative: Start Fresh (Clean History)

If you want a completely fresh start with only one commit:

```bash
cd "Corey Keller/Eye/gaze_tracking"

# Remove old git history
rm -rf .git

# Initialize new repository
git init
git add .
git commit -m "Initial commit: Enhanced Gaze Tracking System for Stanford Neuroradiology Research"

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

## Repository Name Suggestions

- `gaze-tracking-system`
- `eye-tracking-research`
- `stanford-gaze-tracking`
- `clinical-gaze-tracking`
- `real-time-eye-tracking`
