*** Settings ***
Library  ScreenCapLibrary
Library  ScreenCapLibrary  screenshot_module=gdk  WITH NAME  ScreenCapLibraryGdk
Library  OperatingSystem
Library  Collections

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
