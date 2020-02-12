from subprocess import check_output, STDOUT, call as _call
from sys import argv
from shutil import which
import tarfile
from pathlib import Path
import re
import json

JUPYTER_LABEXTENSION_PKGS = {
    "@jupyter-widgets/jupyterlab-manager": "1.0.3",
    # "jupyterlab-plotly": "1.5.0", causes a build issue on QUT's network as of 12/02/2020 - can't fetch 3d-view@2.0.0 from yarnpkg registry
    "jupyter-ros": "0.3.0"
}

VSCODE_EXTENSIONS = [
    "ms-python.python",
    "esbenp.prettier-vscode",
    "blanu.vscode-styled-jsx",
    "kelvin.vscode-sshfs"
]


def call(cmd, **kwargs):
    return _call(cmd, shell=True, **kwargs)


if __name__ == "__main__":

    with open("./win-environment.yml", "r") as env_file:
        conda_env_name = env_file.readline().split()[1]

    CACHE_ENV_ARG_FLAG = "--cache-env="
    cache_env = (
        Path(argv[1][len(CACHE_ENV_ARG_FLAG) :])
        if len(argv) > 1 and argv[1].startswith(CACHE_ENV_ARG_FLAG)
        else None
    )

    print("updating conda version")

    # ensure conda is at the latest version
    call("conda update -n base -y conda")

    target_env_dir = (
        Path(
            re.search(
                r"envs directories : (\S+?)\s",
                check_output("conda info".split()).decode(),
            ).group(1)
        )
        / conda_env_name
    )

    # extract the env cache if it has been specified and exists
    if cache_env is not None and cache_env.exists():

        if not target_env_dir.exists():
            target_env_dir.mkdir(parents=True)

        tarfile.open(cache_env, "r:gz").extractall(target_env_dir)

    print(f"syncing {conda_env_name} with environment.yml")

    # install / update the conda environment and all python / C++ / binary dependencies
    call("conda env update -f ./win-environment.yml --prune")

    existing_labextensions = {
        match.group(1): match.group(2)
        for match in re.finditer(
            r"(\S+) v([\d\.]+) enabled  ok",
            check_output(
                (f"conda run -n {conda_env_name} jupyter labextension list").split(),
                stderr=STDOUT,  # for some reason the labextension list outputs to stderr??
            ).decode(),
        )
    }

    # we need to check the currently installed jupyterlab extension versions and install anything that doesnt match.
    # don't run the install script every time because unlike the other install commands, jupyterlabextension install invokes
    # --force-reinstall essentially every time it is run
    labextensions_install_list = [
        f"{npm_package}@{version}"
        for npm_package, version in JUPYTER_LABEXTENSION_PKGS.items()
        if npm_package not in existing_labextensions
        or existing_labextensions[npm_package] != version
    ]

    print("installing labextensions:", labextensions_install_list)

    call(
        # install js dependencies of the config app
        f"conda run -n {conda_env_name} npm i"
        # install any required js components of jupyterlab and their widgets at once
        + (
            f' && jupyter labextension install {" ".join(labextensions_install_list)}'
            if any(labextensions_install_list)
            else ""
        )
    )

    # if env_cache was specified, use conda-pack to update / create the cache
    if cache_env is not None:
        call(
            f"conda run -n {conda_env_name} conda pack -f -n {conda_env_name} -o {cache_env} --n-threads=4 --ignore-package-mods=jupyterlab,llvm-openmp"
        )

    # install vscode extensions helpful for development
    call(" && ".join([f"code --install-extension {ext}" for ext in VSCODE_EXTENSIONS]))

    with open("./.vscode/settings.json", "r") as vscode_settings_f:
        vscode_settings = json.load(vscode_settings_f)

    with open("./.vscode/settings.json", "w") as vscode_settings_f:
        vscode_settings["python.pythonPath"] = f"{target_env_dir}\\python"
        json.dump(vscode_settings, vscode_settings_f)
