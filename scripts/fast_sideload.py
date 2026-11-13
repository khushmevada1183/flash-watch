import os
import zipfile
import subprocess
import shutil

print("=== FAST LOCAL SIDELOAD STARTING ===")

# Base IPA to modify
base_ipa = r"C:\Users\khush\Desktop\Projects\flash-watch\build_artifacts_cyberpunk\FlashWatch-iOS-IPA\FlashWatch.ipa"
if not os.path.exists(base_ipa):
    base_ipa = r"C:\Users\khush\Desktop\FlashWatch_signed.ipa"

temp_ipa = r"C:\Users\khush\Desktop\Projects\flash-watch\temp_unsigned.ipa"
signed_ipa = r"C:\Users\khush\Desktop\FlashWatch_signed.ipa"

with open("web/index.html", "rb") as f:
    new_index_html = f.read()

# Copy all entries from base_ipa, replacing Payload/App.app/public/index.html
with zipfile.ZipFile(base_ipa, "r") as zin:
    with zipfile.ZipFile(temp_ipa, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "Payload/App.app/public/index.html":
                zout.writestr(item, new_index_html)
            else:
                zout.writestr(item, zin.read(item.filename))

print("Injected updated web/index.html into IPA successfully!")

# Sign with zsign
zsign_cmd = [
    r"C:\Users\khush\Desktop\Projects\flash-watch\zsign_bin\zsign.exe",
    "-k", r"C:\Users\khush\AppData\Roaming\sideloadly\key.pem",
    "-c", r"C:\Users\khush\AppData\Roaming\sideloadly\cert-khushmevada1183@gmail.com.pem",
    "-m", r"C:\Users\khush\Desktop\Projects\flash-watch\extracted_prov.mobileprovision",
    "-b", "com.khushmevada.flashwatch.DJ3SY3Y5FU",
    "-o", signed_ipa,
    temp_ipa
]

print("Signing with zsign...")
res = subprocess.run(zsign_cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("zsign error:", res.stderr or res.stdout)
    exit(1)
print("Signed successfully!")

if os.path.exists(temp_ipa):
    os.remove(temp_ipa)

# Sideload to iPhone via pymobiledevice3
print("Installing to connected iPhone via pymobiledevice3...")
install_cmd = ["python", "-m", "pymobiledevice3", "apps", "install", signed_ipa]
res_install = subprocess.run(install_cmd, capture_output=True, text=True)
print(res_install.stdout)
if res_install.returncode != 0:
    print("Install error:", res_install.stderr)
    exit(1)

print("=== INSTALLED SUCCESSFULLY IN SECONDS! ===")
