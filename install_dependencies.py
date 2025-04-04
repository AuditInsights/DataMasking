import subprocess
import sys

# List of packages to install
packages = [
    "streamlit",
    "pandas",
    "numpy",
    "openpyxl",
    "plotly",
    "xlsxwriter"
]

def install():
    for pkg in packages:
        print(f"📦 Installing: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
    print("\n✅ All packages installed successfully!")

if __name__ == "__main__":
    install()
