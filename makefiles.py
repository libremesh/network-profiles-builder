import os
import subprocess
from jinja2 import Environment, FileSystemLoader

network_profiles_folder = "network-profiles"
sdk_folder = "sdk"

def run_sdk():
    cmdlines = [
        "perl scripts/feeds update profiles",
        "perl scripts/feeds install -a -p profiles",
        "make"
    ]
    for cmdline in cmdlines:
        print("run", cmdline.split(" "))
        proc = subprocess.Popen(
                cmdline.split(" "),
                cwd=sdk_folder,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=False
        )
        output, error = proc.communicate()
        return_code = proc.returncode
        print(output.decode("utf-8"))

def load_profiles():
    network_profiles = {}
    for community in os.listdir(network_profiles_folder):
        community_path = os.path.join(network_profiles_folder, community)
        if os.path.isdir(community_path) and not community.startswith("."):
            if not community in network_profiles:
                network_profiles[community] = []
            for network_profile in os.listdir(os.path.join(community_path)):
                network_profile_path = os.path.join(community_path, network_profile)
                if os.path.isdir(network_profile_path) and not network_profile.startswith("."):
                    network_profiles[community].append(network_profile)
                    #network_profiles.append(os.path.join(community, network_profile))
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

def create_makefile(network_profiles):
    for community, profiles in network_profiles.items():
        params = {}
        params["community"] = community
        cmdline = "git log -n 1 --pretty=format:%H -- .".split(" ")
        proc = subprocess.Popen(
                cmdline,
                cwd=os.path.join(network_profiles_folder, community),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=False
        )
        git_version_raw, errors = proc.communicate()
        git_version = git_version_raw.decode('utf-8')

        version_file_path = os.path.join(network_profiles_folder, community, "version")
        current_version = ""
        if os.path.exists(version_file_path):
            with open(version_file_path, "r") as version_file:
                current_version = version_file.readline()
        else:
            with open(version_file_path, "w") as version_file:
                version_file.write(git_version)

        if git_version == current_version:
            print("{} is up to date".format(community))
            continue

        changes = 1

        community_readme = ""
        readme_file_path = os.path.join(network_profiles_folder, community, "README.md")
        if os.path.exists(readme_file_path):
            with open(readme_file_path, "r") as readme_file:
                community_readme = readme_file.read()

        params["version"] = git_version
        params["profiles"] = []

        for profile in profiles:
            profile_data = {}
            profile_data["name"] = profile
            profile_data["name_sanitized"] = profile.replace("/", "-").replace(".", "_")

            packages_file_path = os.path.join(network_profiles_folder, community, profile, "PACKAGES")
            if os.path.exists(packages_file_path):
                with open(packages_file_path, "r") as packages_file:
                    profile_data["packages"] = " ".join(["+"+package for package in packages_file.read().split()])

            readme_file_path = os.path.join(network_profiles_folder, community, profile, "README.md")
            if os.path.exists(readme_file_path):
                with open(readme_file_path, "r") as readme_file:
                    profile_readme = readme_file.read()
                    if profile_readme:
                        profile_data["readme"] = profile_readme
                    elif community_readme:
                        profile_data["readme"] = community_readme

            params["profiles"].append(profile_data)

        release_file_path = os.path.join(network_profiles_folder, community, "release")
        current_release = 0
        if os.path.exists(release_file_path):
            print(release_file_path)
            with open(release_file_path, "r") as release_file:
                current_release = int(release_file.readline())

        current_release = current_release + 1

        with open(release_file_path, "w") as release_file:
            release_file.write(str(current_release))
            print("set {} release to {}".format(community, current_release))

        params["release"] = current_release

        env = Environment(loader=FileSystemLoader('templates'))
        rendered = env.get_template("Makefile.j2").render(**params)

        makefile_file_path = os.path.join(network_profiles_folder, community, "Makefile")
        with open(makefile_file_path, "w") as makefile_file:
            makefile_file.write(rendered)

        print("created Makefile for {}".format(community))

changes = 0
pull_profiles()
network_profiles = load_profiles()
create_makefile(network_profiles)
if changes:
    run_sdk()
