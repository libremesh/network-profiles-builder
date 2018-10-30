#!/bin/sh

# if network-profiles isn't there yet, clone it
[ -d "./network-profiles" ] || git clone https://github.com/libremesh/network-profiles.git

# update the network-profiles
#(cd ./network-profiles && git pull)

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
        cp -r "./network-profiles/$community_org/$profile_org/" \
            "./packages/$community/$profile"
        
        # if special packages are required for the profile parse them here
        packages=""
        #[ -e "./packages/$community/$profile/PACKAGES" ] && {
        #    packages="$(cat ./packages/$community/$profile/PACKAGES)"
        #    # replace \n with a whitespace
        #    packages="${packages//$'\n'/ }"
        #}

        sed \
            -e "s/{{ community }}/$community/g" \
            -e "s/{{ profile }}/$profile/g" \
            -e "s/{{ packages }}/$packages/g" \
            "./templates/Makefile.profile" >> "./packages/$community/Makefile"
    done
done

