!include "MUI.nsh"
!include "x64.nsh"
!include "LogicLib.nsh"

!ifndef ARCH
  !error "No architecture defined (win32 or win-amd64)"
!endif


!ifndef VERSION
  !define VERSION 'DEV'
!endif

; The name of the installer
Name "mousetracker ${VERSION}"

; The name of the installer file to write
OutFile "${TARGET_DIR}\mousetracker-${VERSION}-${ARCH}.exe"

RequestExecutionLevel admin #NOTE: You still need to check user rights with UserInfo!

; The default installation directory
InstallDir "$PROGRAMFILES\IRBA\mousetracker"

; Registry key to check for directory (so if you install again, it will overwrite the old one automatically)
InstallDirRegKey HKLM "Software\IRBA\mousetracker" "Install_Dir"

; Will show the details of installation
ShowInstDetails show

; Will show the details of uninstallation
ShowUnInstDetails show

!define PUBLISHER "IRBA"
!define WEB_SITE "https://gitlab.com/irba/mousetracker"
!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\mousetracker"
!define UNINST_ROOT_KEY "HKLM"

!define ICONS_DIR $INSTDIR\icons

; Prompt the user in case he wants to cancel the installation
!define MUI_ABORTWARNING

; define the icon for the installer file and the installer 'bandeau'
!define MUI_ICON   "icons\mousetracker.ico"
!define MUI_UNICON "icons\mousetracker_uninstall.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "icons\mousetracker_resized.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "icons\mousetracker_uninstall_resized.bmp"

!define WEB_ICON   "icons\website.ico"

!define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of \
mousetracker release ${VERSION}.\
\n\nMousetracker is a program aimed at computing statitistics from experiments on mouse files."

; Insert a "Welcome" page in the installer
!insertmacro MUI_PAGE_WELCOME

; Insert a "License" page in the installer
!insertmacro MUI_PAGE_LICENSE "LICENSE"

; Insert a page to browse for the installation directory
!insertmacro MUI_PAGE_DIRECTORY

; Insert a page for actual installation (+display) of mousetracker
!insertmacro MUI_PAGE_INSTFILES

; Insert in the finish page the possibility to run mousetracker
!define MUI_FINISHPAGE_RUN_NOTCHECKED
!define MUI_FINISHPAGE_RUN_TEXT "Start mousetracker ${VERSION}"
!define MUI_FINISHPAGE_RUN "$INSTDIR\launcher.bat"
; Insert in the finish page the possibility to view the changelog
!define MUI_FINISHPAGE_SHOWREADME_TEXT "View CHANGELOG"
!define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\CHANGELOG.txt"
; Actually insert the finish page to the installer
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Set the installer language to english
!insertmacro MUI_LANGUAGE "English"

;RequestExecutionLevel user

Function .onInit
  ${If} ${ARCH} == "win-amd64"
    StrCpy $INSTDIR "$PROGRAMFILES64\IRBA\mousetracker"
  ${Else}
    StrCpy $INSTDIR "$PROGRAMFILES\IRBA\mousetracker"
  ${EndIf}
FunctionEnd

Section "mousetracker ${VERSION}" SEC01
  SetShellVarContext all
  SetOutPath "$INSTDIR"
  SetOverwrite on
  File /r /x *.pyc /x *.pyo /x *.log "${TARGET_DIR}\*"
  File "CHANGELOG.txt"
  File "LICENSE"
  File "launcher.bat"
  CreateDirectory "${ICONS_DIR}"
  SetOutPath "${ICONS_DIR}"
  SetOverwrite on
  File /oname=run.ico "${MUI_ICON}"
  File /oname=uninstall.ico "${MUI_UNICON}"
  File /oname=web.ico "${WEB_ICON}"
  SetOutPath "$INSTDIR"
  SetOverwrite on
  CreateShortCut "$DESKTOP\mousetracker.lnk" "$INSTDIR\launcher.bat" "" "${ICONS_DIR}\run.ico" 0
  CreateDirectory "$SMPROGRAMS\IRBA\mousetracker"
  CreateShortCut "$SMPROGRAMS\IRBA\mousetracker\mousetracker.lnk" "$INSTDIR\launcher.bat" "" "${ICONS_DIR}\run.ico" 0
  WriteIniStr "$INSTDIR\mousetracker.url" "InternetShortcut" "URL" "${WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\IRBA\mousetracker\Website.lnk" "$INSTDIR\mousetracker.url" "" "${ICONS_DIR}\web.ico" 0
  CreateShortCut "$SMPROGRAMS\IRBA\mousetracker\Uninstall.lnk" "$INSTDIR\uninst.exe" "" "${ICONS_DIR}\uninstall.ico" 0

  WriteRegStr ${UNINST_ROOT_KEY} "${UNINST_KEY}" "DisplayName" "mousetracker"
  WriteRegStr ${UNINST_ROOT_KEY} "${UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${UNINST_ROOT_KEY} "${UNINST_KEY}" "DisplayIcon" "${ICONS_DIR}\run.ico"
  WriteRegStr ${UNINST_ROOT_KEY} "${UNINST_KEY}" "DisplayVersion" "${VERSION}"
  WriteRegStr ${UNINST_ROOT_KEY} "${UNINST_KEY}" "URLInfoAbout" "${WEB_SITE}"
  WriteRegStr ${UNINST_ROOT_KEY} "${UNINST_KEY}" "Publisher" "${PUBLISHER}"

  WriteUninstaller "$INSTDIR\uninst.exe"
  SetAutoClose false
SectionEnd

Function un.onInit
  !insertmacro MUI_UNGETLANGUAGE
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you really sure you want to uninstall mousetracker ?" IDYES +2
  Abort
FunctionEnd

Section uninstall
  SetShellVarContext all
  Delete "$INSTDIR\mousetracker.url"
  Delete "$INSTDIR\python.exe"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\LICENSE"
  Delete "$INSTDIR\LICENSE.txt"
  Delete "$INSTDIR\NEWS.txt"
  Delete "$INSTDIR\CHANGELOG"
  Delete "$INSTDIR\launcher.bat"
  Delete "$INSTDIR\python3.dll"
  Delete "$INSTDIR\python37.dll"
  Delete "${ICONS_DIR}\run.ico"
  Delete "${ICONS_DIR}\terminal.ico"
  Delete "${ICONS_DIR}\uninstall.ico"
  Delete "${ICONS_DIR}\web.ico"
  Delete "${ICONS_DIR}\vcruntime140.dll"
  Delete "${ICONS_DIR}\vcruntime140_1.dll"

  Delete "$DESKTOP\mousetracker.lnk"

  Delete "$SMPROGRAMS\IRBA\mousetracker\Uninstall.lnk"
  Delete "$SMPROGRAMS\IRBA\mousetracker\Website.lnk"
  Delete "$SMPROGRAMS\IRBA\mousetracker\mousetracker.lnk"
  RMDir /r "$SMPROGRAMS\IRBA\mousetracker"
  RMDir /r "$INSTDIR"

  DeleteRegKey ${UNINST_ROOT_KEY} "${UNINST_KEY}"
  SetAutoClose false
SectionEnd
