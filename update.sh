#!/bin/sh

# if network-profiles isn't there yet, clone it
[ -d "./network-profiles" ] || git clone https://github.com/libremesh/network-profiles.git

# update the network-profiles
#(cd ./network-profiles && git pull)

# create output directory
mkdir -p ./packages

for community in $(ls ./network-profiles); do
    # skip non directories
    [ -d "./network-profiles/$community" ] || continue

    # create network profile folder
    mkdir -p "./packages/$community"

    # move Makefile header to community folder
    cp ./templates/Makefile.header "./packages/$community/Makefile"

    # set PKG_NAME to community
    sed -i \
        -e "s/{{ community }}/$community/g" \
        "./packages/$community/Makefile"

    # loop over all profiles of community
    for profile in $(ls ./network-profiles/$community); do
        # skip non directories
        [ -d "./network-profiles/$community/$profile" ] || continue

        # copy all profile specific files
        cp -r "./network-profiles/$community/$profile/" "./packages/$community/$profile"
        
        # if special packages are required for the profile parse them here
        packages=""
        [ -e "./packages/$community/$profile/PACKAGES" ] && {
            packages="$(cat ./packages/$community/$profile/PACKAGES)"
            # replace \n with a whitespace
            packages="${packages//$'\n'/ }"
        } 

        sed \
            -e "s/{{ community }}/$community/g" \
            -e "s/{{ profile }}/$profile/g" \
            -e "s/{{ packages }}/$packages/g" \
            "./templates/Makefile.profile" >> "./packages/$community/Makefile"
    done
done

