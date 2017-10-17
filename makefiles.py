import os
import subprocess
from jinja2 import Environment, FileSystemLoader

network_profiles_folder = "network-profiles"

def load_profiles():
    network_profiles = []
    for community in os.listdir(network_profiles_folder):
        community_path = os.path.join(network_profiles_folder, community)
        if os.path.isdir(community_path) and not community.startswith("."):
            for network_profile in os.listdir(os.path.join(community_path)):
                network_profile_path = os.path.join(community_path, network_profile)
                if os.path.isdir(network_profile_path) and not network_profile.startswith("."):
                    network_profiles.append(os.path.join(community, network_profile))
    return network_profiles

def pull_profiles():
        cmdline = "git pull".split(" ")
        proc = subprocess.Popen(
                cmdline,
                cwd=os.path.join(network_profiles_folder),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=False
        )

def create_makefile(network_profile):
        params = {}

        cmdline = "git log -n 1 --pretty=format:%H -- .".split(" ")
        proc = subprocess.Popen(
                cmdline,
                cwd=os.path.join(network_profiles_folder, network_profile),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=False
        )
        git_version_raw, errors = proc.communicate()
        git_version = git_version_raw.decode('utf-8')

        version_file_path = os.path.join(network_profiles_folder, network_profile, "version")
        current_version = ""
        if os.path.exists(version_file_path):
            with open(version_file_path, "r") as version_file:
                current_version = version_file.readline()
        else:
            with open(version_file_path, "w") as version_file:
                version_file.write(git_version)

        if git_version == current_version:
            return

        params["version"] = git_version
        params["name"] = network_profile
        params["name_sanitized"] = network_profile.replace("/", "-").replace(".", "_")

        packages_file_path = os.path.join(network_profiles_folder, network_profile, "PACKAGES")
        if os.path.exists(packages_file_path):
            with open(packages_file_path, "r") as packages_file:
                params["packages"] = " ".join(["+"+package for package in packages_file.read().split()])

        readme_file_path = os.path.join(network_profiles_folder, network_profile, "README.md")
        if os.path.exists(readme_file_path):
            with open(readme_file_path, "r") as readme_file:
                params["readme"] = readme_file.read()

        release_file_path = os.path.join(network_profiles_folder, network_profile, "release")
        current_release = 0
        if os.path.exists(release_file_path):
            print(release_file_path)
            with open(release_file_path, "r") as release_file:
                current_release = int(release_file.readline())

        current_release = current_release + 1

        with open(release_file_path, "w") as release_file:
            release_file.write(str(current_release))
            print("set {} release to {}".format(network_profile, current_release))

        params["release"] = current_release

        env = Environment(loader=FileSystemLoader('templates'))
        rendered = env.get_template("Makefile.j2").render(**params)

        makefile_file_path = os.path.join(network_profiles_folder, network_profile, "Makefile")
        with open(makefile_file_path, "w") as makefile_file:
            makefile_file.write(rendered)

        print("created Makefile for {}".format(network_profile))

pull_profiles()
network_profiles = load_profiles()
for network_profile in network_profiles:
    create_makefile(network_profile)
print("all profiles updated")
