import subprocess

def run_command(command, cwd=None):
    """Run a shell command and return the output."""
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode

# Set your project directory
project_path = "E:/FreeLancePRojects/restrauntapp"  # Change if needed

# Step 1: Git Add
print("Adding files to Git...")
if run_command(["git", "add", "."], cwd=project_path) != 0:
    print("Error in git add. Exiting.")
    exit(1)

# Step 2: Get Commit Message
commit_msg = input("Enter commit message: ")

# Step 3: Git Commit
print("Committing changes...")
if run_command(["git", "commit", "-m", commit_msg], cwd=project_path) != 0:
    print("Error in git commit. Exiting.")
    exit(1)

# Step 4: Git Push
print("Pushing to origin master...")
if run_command(["git", "push", "origin", "master"], cwd=project_path) != 0:
    print("Error in git push. Exiting.")
    exit(1)

print("Git push completed successfully!")
