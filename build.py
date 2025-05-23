import shutil
import subprocess
from pathlib import Path

# تنظیم مسیر فایل‌ها
BASE_DIR = Path(__file__).resolve().parent
MAIN_SCRIPT = BASE_DIR / "main.py"
ICON_PATH = BASE_DIR / "RC" / "app-icon.ico"
# ...
# SPLASH_PATH = BASE_DIR / "RC" / "splash.jpg"
# FONTS_DIR = BASE_DIR / "RC" / "fonts"

# نام اجرایی (پوشه خروجی هم همین خواهد بود در حالت --onedir)
APP_NAME = "VidMeter"

# حذف build و dist اگر وجود دارند
for folder in ["build", "dist"]:
    folder_path = BASE_DIR / folder
    if folder_path.exists():
        shutil.rmtree(folder_path)

# ماژول‌هایی که می‌خواهیم حذف کنیم
excluded_modules = [
    "PyQt5", "PyQt6", "PyQt5.sip", "PyQt6.sip",
    "IPython", "cv2", "pygame", "torch", "transformers",
    "sklearn", "scikit_learn", "sentencepiece", "protobuf",
    "gevent", "sqlalchemy", "tornado", "zmq", "yaml", "nltk",
    "pandas",

    "matplotlib.tests",

    # اینها باید در پروژه من باشند. سایر ماژول ها به اینها وابستگی دارند
    # "numpy", "numpy.libs",            # numpy-2.2.4
    # "PIL",                            # pillow-10.4.0
    # "dateutil", "python-dateutil",    # python-dateutil-2.9.0.post0
    # "kiwisolver",                     # kiwisolver-1.4.8
    # "bidi",                           # python-bidi-0.6.6

    # اینها را هنوز تست نکردم
    # "psutil",
    # "markupsafe",
    # "contourpy",  # contourpy-1.3.2
    # "cryptography", "hazmat",  # _rust.pyd
    # "fontTools",  # fonttools-4.57.0

    ]

# ساخت دستور pyinstaller
cmd = [
    "pyinstaller",
    "--noconfirm",
    "--windowed",             #TODO: در انتشار نهایی این را تغییر بدهم
    "--onedir",
    f"--icon={ICON_PATH}",
    f"--name={APP_NAME}",
    ]

# اضافه کردن exclude-module به دستور
for module in excluded_modules:
    cmd.append(f"--exclude-module={module}")

cmd.append(str(MAIN_SCRIPT))

# اجرای دستور
result = subprocess.run(cmd, text=True)
# with open("build-log.txt", "w", encoding="utf-8") as log_file:
#     result = subprocess.run(cmd, text=True, stdout=log_file, stderr=subprocess.STDOUT)

print("_" * 110)

# بررسی موفقیت و کپی فایل‌ها در صورت موفق بودن
if result.returncode == 0:
    print("✅ The executable file was successfully built.")
    # ...
    # output_dir = BASE_DIR / "dist" / APP_NAME

    # کپی splash.png
    # if SPLASH_PATH.exists():
    #     shutil.copy(SPLASH_PATH, output_dir / "_internal" / SPLASH_PATH.name)
    #     print(f"📄 Copied splash.jpg to {output_dir}")

    # کپی پوشه fonts
    # if FONTS_DIR.exists():
    #     dest_fonts = output_dir / "_internal" / "fonts"
    #     shutil.copytree(FONTS_DIR, dest_fonts, dirs_exist_ok=True)
    #     print(f"📁 Copied fonts directory to {dest_fonts}")

else:
    print("❌ Error occurred while building the executable file.")
