import os
import subprocess

# Color definitions for terminal output
class Colors:
    BBlack = '\033[1;30m'
    BRed = '\033[1;31m'
    BGreen = '\033[1;32m'
    BYellow = '\033[1;33m'
    BBlue = '\033[1;34m'
    BPurple = '\033[1;35m'
    BCyan = '\033[1;36m'
    BWhite = '\033[1;37m'
    UWhite = '\033[4;37m'
    Color_Off = '\033[0m'

CONFIG_FILE = os.path.expanduser("~/.host_data_path.conf")
TETHYS_SCRIPT = "./viewOnTethys.sh"
IMAGE_NAME = "awiciroh/ciroh-ngen-image:latest"


def get_input_data_path():
    """Get or set the input data directory path."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            last_path = file.read().strip()
        print(f"Last used data directory path: {Colors.BBlue}{last_path}{Colors.Color_Off}")
        use_last_path = input("Do you want to use the same path? (Y/n): ").strip().lower()
        if use_last_path not in ['n', 'no']:
            return last_path

    new_path = input("Enter your input data directory path (use absolute path): ").strip()
    with open(CONFIG_FILE, "w") as file:
        file.write(new_path)
    return new_path


def validate_directory(directory, name, color):
    """Validate the existence of a directory and count its files."""
    if os.path.isdir(directory):
        count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
        print(f"{color}{name}{Colors.Color_Off} exists. {count} {name} files found.")
    else:
        print(f"Error: Directory {directory} does not exist.")


def cleanup_folder(folder_path, file_types, folder_name):
    """Clean up files in a folder based on given types."""
    print(f"Files found in {folder_name}: {len(os.listdir(folder_path))}")

    print(f"{Colors.BYellow}Cleanup Process: matching files in {folder_name}:{Colors.Color_Off}")
    options = ["Delete files and run fresh", "Continue without cleaning", "Exit"]
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    choice = int(input("Choose an option: ").strip())
    if choice == 1:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if any(file.endswith(ext) for ext in file_types):
                    os.remove(os.path.join(root, file))
        print("Folder cleaned.")
    elif choice == 3:
        print("Exiting script. Have a nice day!")
        exit(0)


def find_files(path, name, pattern):
    """Find and list files matching a pattern in a directory."""
    print(f"{Colors.BGreen}Searching for {name} files...{Colors.Color_Off}")
    for root, dirs, files in os.walk(path):
        for file in files:
            if pattern in file:
                print(f"Found {name} file: {os.path.join(root, file)}")


def main():
    print(f"{Colors.UWhite}Welcome to CIROH-UA: NextGen National Water Model App!{Colors.Color_Off}")

    # Get the input data path
    host_data_path = get_input_data_path()
    if not os.path.isdir(host_data_path):
        print(f"{Colors.BRed}Directory does not exist. Exiting the program.{Colors.Color_Off}")
        exit(1)

    print(f"The directory you've given is: {host_data_path}")

    # Validate required subdirectories
    validate_directory(os.path.join(host_data_path, "forcings"), "forcings", Colors.BBlue)
    validate_directory(os.path.join(host_data_path, "config"), "config", Colors.BGreen)
    validate_directory(os.path.join(host_data_path, "outputs"), "outputs", Colors.BPurple)

    # Cleanup outputs and restarts folders
    cleanup_folder(os.path.join(host_data_path, "outputs"), ["*"], "Outputs")
    cleanup_folder(os.path.join(host_data_path, "restart"), ["*"], "Restarts")

    # Find specific files
    find_files(host_data_path, "hydrofabric", ".gpkg")
    find_files(host_data_path, "realization", "realization.json")

    # Docker operations
    print(f"{Colors.BYellow}Select an option for running the model:{Colors.Color_Off}")
    options = [
        "Run NextGen using existing local docker image",
        "Run NextGen after updating to latest docker image",
        "Exit",
    ]
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    choice = int(input("Choose an option: ").strip())
    if choice == 2:
        subprocess.run(["docker", "pull", IMAGE_NAME])
    elif choice == 3:
        print("Exiting script. Have a nice day!")
        exit(0)

    subprocess.run(["docker", "run", "--rm", "-it", "-v", f"{host_data_path}:/ngen/ngen/data", IMAGE_NAME, "/ngen/ngen/data/"])

    print("Thank you for running NextGen In A Box: National Water Model! Have a nice day!")


if __name__ == "__main__":
    main()
