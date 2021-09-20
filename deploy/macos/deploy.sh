#!/bin/bash

#############################
# Create DMG
#############################

if [[ $GITHUB_REF == refs/heads/* ]] ;
then
    VERSION=${GITHUB_REF#refs/heads/}
else
	if [[ $GITHUB_REF == refs/tags/* ]] ;
	then
		VERSION=${GITHUB_REF#refs/tags/}
	else
		exit 1
	fi
fi

rm mousetracker*dmg

MOUSETRACKER_DMG=mousetracker-${VERSION}-macOS-amd64.dmg
hdiutil unmount /Volumes/mousetracker -force -quiet
sleep 5
./deploy/macos/create-dmg --background "./deploy/macos/resources/dmg/dmg_background.jpg" \
                                                     --volname "mousetracker" \
									             	 --window-pos 200 120 \
										 			 --window-size 800 400 \
										 			 --icon mousetracker.app 200 190 \
										 			 --hide-extension mousetracker.app \
										 			 --app-drop-link 600 185 \
										 			 "${MOUSETRACKER_DMG}" \
										 			 ./dist
