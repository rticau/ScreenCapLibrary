*** Settings ***
Library  ScreenCapLibrary
Library  ScreenCapLibrary  screenshot_module=PyGTK  WITH NAME  ScreenCapLibraryGtk
Library  OperatingSystem
Library  Collections
Library  DateTime

*** Keywords ***
Screenshot Should Exist
    [Arguments]  ${path}
    [Documentation]  Checks that screenshot file exists and is newer than
    ...  timestamp set in test setup.
    File Should Exist  ${path}
    ${filetime} =  Get Modified Time  ${path}
    Should Be True  '${filetime}' >= '${START TIME}'

Save Start Time
    ${start time} =  Get Time
    Set Test Variable  \${START TIME}

Screenshots Should Exist
    [Arguments]  ${directory}  @{files}
    @{actual_png_files}=  List Directory  ${directory}  *.png  absolute
    @{actual_jpg_files}=  List Directory  ${directory}  *.jp*g  absolute
    @{all_files}=  Combine Lists  ${actual_png_files}  ${actual_jpg_files}
    List Should Contain Sub List  ${files}  ${all_files}

Screenshot Number In ${directory} Should Be ${expected}
    @{actual_png_files}=  List Directory  ${directory}  *.png  absolute
    @{actual_jpg_files}=  List Directory  ${directory}  *.jp*g  absolute
    @{all_files}=  Combine Lists  ${actual_png_files}  ${actual_jpg_files}
    ${actual}  Get Length  ${all_files}
    Should Be Equal As Integers  ${actual}  ${expected}

Cleanup Files
    Remove Files  ${OUTPUT_DIR}/*.jp*g  ${OUTPUT_DIR}/*.png  ${OUTPUT_DIR}/*.gif  ${OUTPUT_DIR}/*.webp
    Sleep  10
    Remove Files  ${OUTPUT_DIR}/*.webm
