#!/bin/sh

# if network-profiles isn't there yet, clone it
[ -d "./network-profiles" ] || git clone https://github.com/libremesh/network-profiles.git

# update the network-profiles

touch .network_profiles_commit
git --git-dir=network-profiles/.git/ pull
latest_commit="$(git --git-dir=network-profiles/.git/ log --pretty=format:'%h' -n 1)"
if [ "$latest_commit" != "$(cat .network_profiles_commit)" -o -n "$FORCE_REBUILD" ]; then
    echo "$latest_commit" > .network_profiles_commit
else
    echo "no updates"
    exit 0
fi

# create output directory
mkdir -p ./packages

for community_org in $(ls ./network-profiles); do
    # skip non directories
    [ -d "./network-profiles/$community_org" ] || continue

    community="$(echo $community_org | sed -e s/[^A-Za-z0-9\-]/_/g)"

    # create network profile folder
    mkdir -p "./packages/$community"

    # move Makefile header to community folder
    cp ./templates/Makefile.header "./packages/$community/Makefile"

    # set PKG_NAME to community
    sed -i \
        -e "s/{{ community }}/$community/g" \
        "./packages/$community/Makefile"

    # loop over all profiles of community
    for profile_org in $(ls ./network-profiles/$community_org); do
        # skip non directories
        [ -d "./network-profiles/$community_org/$profile_org" ] || continue

        profile="$(echo $profile_org | sed -e s/[^A-Za-z0-9\-]/_/g)"

        # copy all profile specific files
        cp -rp "./network-profiles/$community_org/$profile_org/" \
            "./packages/$community/"

        # if special packages are required for the profile parse them here
        packages=""
        [ -e "./packages/$community/$profile/PACKAGES" ] && {
            for p in $(cat ./packages/$community/$profile/PACKAGES); do
              # negative packages are discarted
              packages="$packages $(echo -n "$p" | grep -v "^-")"
            done
            # replace \n with a whiespace
            # packages="${packages//$'\n'/ }"
        }

        sed \
            -e "s/{{ community }}/$community/g" \
            -e "s/{{ profile }}/$profile/g" \
            -e "s/{{ packages }}/$packages/g" \
            "./templates/Makefile.profile" >> "./packages/$community/Makefile"
        done
    done

    (cd sdk && \
        ./scripts/feeds update -a && \
        ./scripts/feeds install -p networkprofiles -a && \
        make -j 4)
