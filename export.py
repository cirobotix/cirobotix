import os

OUTPUT_FILE = "project_dump.txt"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MAIN_FILE = os.path.join(BASE_DIR, "main.py")
CORE_DIR = os.path.join(BASE_DIR, "core")


def read_file(filepath):
    try:
        with open(filepath, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[ERROR reading file: {e}]"


def collect_core_files(core_dir):
    file_paths = []

    for root, dirs, files in os.walk(core_dir):
        for file in files:
            if file.endswith(".py"):  # optional Filter
                full_path = os.path.join(root, file)
                file_paths.append(full_path)

    # Sortieren für deterministische Reihenfolge
    file_paths.sort()
    return file_paths


def write_output(main_file, core_files, output_file):
    with open(output_file, "w", encoding="utf-8") as out:
        # main.py zuerst
        out.write("=" * 80 + "\n")
        out.write("FILE: main.py\n")
        out.write("=" * 80 + "\n\n")
        out.write(read_file(main_file))
        out.write("\n\n")

        # core Dateien
        for file_path in core_files:
            relative_path = os.path.relpath(file_path, BASE_DIR)

            out.write("=" * 80 + "\n")
            out.write(f"FILE: {relative_path}\n")
            out.write("=" * 80 + "\n\n")

            out.write(read_file(file_path))
            out.write("\n\n")


def main():
    if not os.path.exists(MAIN_FILE):
        print("main.py nicht gefunden!")
        return

    if not os.path.exists(CORE_DIR):
        print("core/ Ordner nicht gefunden!")
        return

    core_files = collect_core_files(CORE_DIR)
    write_output(MAIN_FILE, core_files, OUTPUT_FILE)

    print(f"Fertig! Output geschrieben nach: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
