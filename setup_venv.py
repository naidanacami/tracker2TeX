import os, subprocess, io


# Sets up a venv and installs packages. Also creates a batfile that activates the venv and launches main.py in that venv
def setup_venv(requirements_dot_txt, venv_name: str) -> None:
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    requirements_path = os.path.join(curr_dir, requirements_dot_txt if requirements_dot_txt != None else "")
    batfile_path = os.path.join(curr_dir, "venv_activate.bat")
    
    # Venv setup && package install
    subprocess.run(f"python -m venv {venv_name}", cwd=curr_dir)     # Makes the venv
    with io.open(batfile_path, "w", encoding = "utf-8") as f:
        f.write(f"\"{os.path.join(curr_dir, venv_name)}\\scripts\\activate.bat\"")
        f.write(f" && pip install -r \"{requirements_path}\"" if requirements_dot_txt != None else "")
    subprocess.run(batfile_path)     # Runs the batfile_path which activates the venv and installs the requirements.txt packages (if any)

    # Writes the code to activate the venv and main.py
    with io.open(batfile_path, "w", encoding = "utf-8") as f:
        f.write(f"\"{os.path.join(curr_dir, venv_name)}\\scripts\\activate.bat\"")
        f.write(f" && python \"{os.path.join(curr_dir, 'main.py')}\"")


if __name__ == "__main__":
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    setup_venv(os.path.join(curr_dir, "requirements.txt"), "ttt_venv")