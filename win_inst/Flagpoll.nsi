!define PRODUCT_NAME "Flagpoll"
!define FLAGPOLL_VERSION "0.9.1"
!define PRODUCT_VERSION "${FLAGPOLL_VERSION}"
!define FILE_VERSION "${FLAGPOLL_VERSION}.0"
!define PRODUCT_PUBLISHER "Daniel Shipton"
!define PRODUCT_WEB_SITE "https://realityforge.vrsource.org/view/FlagPoll/WebHome"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\${PRODUCT_NAME} ${FLAGPOLL_VERSION}"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME} ${FLAGPOLL_VERSION}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PRODUCT_FULL_NAME "${PRODUCT_NAME}"

SetCompressor bzip2
CRCCheck on

# Define this if you want the environment variables set for all users
!define ALL_USERS "1"

# MUI 1.67 compatible ------
!include "MUI.nsh"
!include WriteEnvStr.nsh
!include AppendPathStr.nsh
!include StartMenu.nsh
!include "Sections.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"

!insertmacro GetOptions
!insertmacro GetParameters

# MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "icon_transparent.ico"
!define MUI_UNICON "icon_transparent.ico"

# Welcome page
!insertmacro MUI_PAGE_WELCOME
# License page
!insertmacro MUI_PAGE_LICENSE "gpl.rtf"
# Components page
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE ComponentLeaveFunc
!insertmacro MUI_PAGE_COMPONENTS
# Directory page
!insertmacro MUI_PAGE_DIRECTORY
# Instfiles page
!insertmacro MUI_PAGE_INSTFILES
# Finish page
!insertmacro MUI_PAGE_FINISH

# Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

# Language files
!insertmacro MUI_LANGUAGE "English"

# Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

# MUI end ------

# Variables
Var FLAGPOLL_INST
Var DOC_INST
Var SET_ENV

Name "${PRODUCT_FULL_NAME}"
OutFile "${PRODUCT_FULL_NAME}-${FLAGPOLL_VERSION}-Setup.exe"
RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\${PRODUCT_FULL_NAME}"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails hide
ShowUnInstDetails hide
BrandingText "Flagpoll ${PRODUCT_VERSION} Installer"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "Daniel Shipton © 2006–2007"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "${FILE_VERSION}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "Flagpoll Installer"
VIProductVersion "${FILE_VERSION}"

!define SHCNE_ASSOCCHANGED 0x08000000
!define SHCNF_IDLIST 0

Section "Flagpoll Application" SecFlagpoll
  SetOverwrite try

  SetOutPath "$INSTDIR"
  File ..\dist\*.exe
  File ..\dist\*.dll
  File ..\dist\*.pyd
  File ..\dist\library.zip

  SetOutPath "$INSTDIR\share\flagpoll"
  File /r ..\dist\share\flagpoll\*
SectionEnd

Section /o "Flagpoll Documentation" SecDocs
  SetOverwrite try

  SetOutPath "$INSTDIR\share\html"
  File /r ..\dist\share\html\*
SectionEnd

Section "Set Environment Variables" SecEnv
  # Add PATH extension
  Push $INSTDIR
  Call AddToPath
SectionEnd

LangString DESC_SecFlagpoll ${LANG_ENGLISH} "flagpoll.exe program"
LangString DESC_SecDocs ${LANG_ENGLISH} "Flagpoll documentation"
LangString DESC_SecEnv ${LANG_ENGLISH} \
   "Extend application path for easy command line usage"

# Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecFlagpoll} $(DESC_SecFlagpoll)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDocs} $(DESC_SecDocs)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecEnv} $(DESC_SecEnv)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Section -AdditionalIcons
  SetOutPath "$INSTDIR"
  File icon_transparent.ico

  Call SetStartMenuToUse

  CreateDirectory "$SMPROGRAMS\${PRODUCT_FULL_NAME}"

  ${If} $DOC_INST == '1'
    CreateShortCut "$SMPROGRAMS\${PRODUCT_FULL_NAME}\Flagpoll Documentation.lnk" "$INSTDIR\share\html\flagpoll-manual.html"
  ${EndIf}

  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" \
    "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_FULL_NAME}\Website.lnk" \
    "$INSTDIR\${PRODUCT_NAME}.url" "" "$INSTDIR\icon_transparent.ico"

  CreateShortCut "$SMPROGRAMS\${PRODUCT_FULL_NAME}\Uninstall.lnk" \
    "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" ""
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\bin\catior.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

Function .onInit
  Call GetParameters
  Pop $2
  ${GetOptions} $2 "/app=" $FLAGPOLL_INST
  ${GetOptions} $2 "/doc=" $DOC_INST
  ${GetOptions} $2 "/setenv=" $SET_ENV

  StrCmp $FLAGPOLL_INST "0" 0 flagpollEnd
    SectionSetFlags ${SecFlagpoll} 0
  flagpollEnd:

  StrCmp $DOC_INST "0" 0 docEnd
    SectionSetFlags ${SecDocs} 0
  docEnd:

  StrCmp $SET_ENV "0" 0 envEnd
    SectionSetFlags ${SecEnv} 0
  envEnd:
FunctionEnd

Function ComponentLeaveFunc
  !insertmacro SectionFlagIsSet ${SecFlagpoll} ${SF_PSELECTED} flagpollIsSel flagpollChkAll
  flagpollChkAll:
  !insertmacro SectionFlagIsSet ${SecFlagpoll} ${SF_SELECTED} flagpollIsSel flagpollNotSel
    flagpollIsSel:
      StrCpy $FLAGPOLL_INST "1"
      Goto flagpollEnd
    flagpollNotSel:
      StrCpy $FLAGPOLL_INST "0"
  flagpollEnd:

  !insertmacro SectionFlagIsSet ${SecDocs} ${SF_PSELECTED} docIsSel docChkAll
  docChkAll:
  !insertmacro SectionFlagIsSet ${SecDocs} ${SF_SELECTED} docIsSel docNotSel
    docIsSel:
      StrCpy $DOC_INST "1"
      Goto docEnd
    docNotSel:
      StrCpy $DOC_INST "0"
  docEnd:

FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "${PRODUCT_FULL_NAME} was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove ${PRODUCT_FULL_NAME} and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Call un.SetStartMenuToUSe

  # Remove both install directories
  RMDir /r "$SMPROGRAMS\${PRODUCT_FULL_NAME}"
  RMDir /r /REBOOTOK "$INSTDIR"

  # Remove PATH extensions
  Push $INSTDIR
  Call un.RemoveFromPath

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd
