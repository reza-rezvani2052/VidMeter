import os, subprocess


def convert_all_ui_files():
    # ui_dir = "UI"
    ui_dir = "."
    for filename in os.listdir(ui_dir):
        if filename.endswith(".ui"):
            in_path = os.path.join(ui_dir, filename)
            out_name = f"ui_{os.path.splitext(filename)[0]}.py"
            out_path = os.path.join(ui_dir, out_name)
            if not os.path.exists(out_path) or os.path.getmtime(in_path) > os.path.getmtime(out_path):
                print(f"Converting: {filename} -> {out_name}")
                subprocess.run(["pyside6-uic", in_path, "-o", out_path], check=True)


def convert_qrc_to_py():
    qrc_path = os.path.join("RC", "resources.qrc")
    # output_path = os.path.join("UI", "rc_resources.py")

    # TODO: برخی مواقع اسم فایل به دلیل زیر عوض میشه :
    # اگر هنگام تبدیل فایل resource به فایل پایتون از کیوت کریتوراستفاده کنیم
    # بهتر است از کیوت کریتور برای ساخت این فایل استفاه نکنم و فقط طراحی را در آن انجام بدم
    # output_path = "rc_resources.py"
    output_path = "resources_rc.py"

    if not os.path.exists(output_path) or os.path.getmtime(qrc_path) > os.path.getmtime(output_path):
        print(f"Converting: resources.qrc -> rc_resources.py")
        subprocess.run(["pyside6-rcc", qrc_path, "-o", output_path], check=True)

# convert_qrc_to_py()
# convert_all_ui_files()
