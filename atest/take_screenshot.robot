*** Settings ***
Suite Setup    Cleanup Files
Test Setup     Save Start Time
Test Teardown  Cleanup Files
Resource       resources/common.robot

*** Variables ***
${BASENAME}  ${OUTPUTDIR}${/}screenshot
${FIRST_SCREENSHOT}  ${BASENAME}_1.png
${SECOND_SCREENSHOT}  ${BASENAME}_2.png
${FIRST_CUSTOM_SCREENSHOT}  ${OUTPUTDIR}${/}foo_1.png
${SECOND_CUSTOM_SCREENSHOT}  ${OUTPUTDIR}${/}foo_2.png
${PNG_CUSTOM_SCREENSHOT}  ${OUTPUTDIR}${/}foo.png
${JPG_CUSTOM_SCREENSHOT}  ${OUTPUTDIR}${/}foo.jpg
${WEBP_CUSTOM_SCREENSHOT}  ${OUTPUTDIR}${/}foo.webp
${GTK_PNG_SCREENSHOT}  ${OUTPUTDIR}${/}pygtk_png.png
${GTK_JPEG_SCREENSHOT}  ${OUTPUTDIR}${/}pygtk_jpeg.jpeg
${GTK_WEBP_SCREENSHOT}  ${OUTPUTDIR}${/}pygtk_webp.webp
${GIF_SCREENSHOT}  ${OUTPUTDIR}${/}screenshot_1.gif
${FIRST_VIDEO_FILE}  ${OUTPUTDIR}${/}recording_1.webm
${SECOND_VIDEO_FILE}  ${OUTPUTDIR}${/}recording_2.webm
${THIRD_VIDEO_FILE}  ${OUTPUTDIR}${/}recording_3.webm

*** Test Cases ***
Screenshot Is Taken
    ${path}=  Take Screenshot and Verify  ${FIRST_SCREENSHOT}
    Should Be Equal  ${path}  ${FIRST_SCREENSHOT}

Each Screenshot Gets Separate Index
    Take Screenshot and Verify  ${FIRST_SCREENSHOT}
    Take Screenshot and Verify  ${FIRST_SCREENSHOT}  ${SECOND_SCREENSHOT}

Basename May Be Defined
    Repeat Keyword  2  ScreenCapLibrary.Take Screenshot  foo
    Screenshots Should Exist  ${OUTPUTDIR}  ${FIRST_CUSTOM_SCREENSHOT}  ${SECOND_CUSTOM_SCREENSHOT}

Basename With Extension Turns Off Index Generation
    Repeat Keyword  3  ScreenCapLibrary.Take Screenshot  xxx.jpg  jpg
    Repeat Keyword  2  ScreenCapLibrary.Take Screenshot  yyy.jpeg  jpeg
    Screenshots Should Exist  ${OUTPUTDIR}  ${OUTPUTDIR}${/}xxx.jpg  ${OUTPUTDIR}${/}yyy.jpeg

Screenshot Width Can Be Given
    ScreenCapLibrary.Take Screenshot  width=300px
    Screenshots Should Exist  ${OUTPUTDIR}  ${FIRST_SCREENSHOT}

Basename With Non-existing Directories Fails
    [Documentation]  FAIL Directory '${OUTPUTDIR}${/}non-existing' where to save the screenshot does not exist
    ScreenCapLibrary.Take Screenshot  ${OUTPUTDIR}${/}non-existing${/}foo

Without Embedding
    ScreenCapLibrary.Take Screenshot Without Embedding  no_embed.png

Without Embedding With Delay
    ScreenCapLibrary.Take Screenshot Without Embedding  delay=10seconds

Png Screenshot Quality
    Compare Size  ${PNG_CUSTOM_SCREENSHOT}  png

Jpg Screenshot Quality
    [Tags]  no-xvfb
    Compare Size  ${JPG_CUSTOM_SCREENSHOT}  jpg

Webp Screenshot Quality
    [Tags]  no-xvfb
    Compare Size  ${WEBP_CUSTOM_SCREENSHOT}  webp

Screenshot Formats Gtk
    [Tags]    gtk
    ScreenCapLibraryGtk.Take Screenshot  ${GTK_PNG_SCREENSHOT}  png
    Screenshot Should Exist  ${GTK_PNG_SCREENSHOT}
    ScreenCapLibraryGtk.Take Screenshot  ${GTK_JPEG_SCREENSHOT}  jpeg
    Screenshot Should Exist  ${GTK_JPEG_SCREENSHOT}
    ScreenCapLibraryGtk.Take Screenshot  ${GTK_WEBP_SCREENSHOT}  webp
    Screenshot Should Exist  ${GTK_WEBP_SCREENSHOT}

Take Screenshot With Delay
    ${start_date}=  DateTime.Get Current Date
    ${screenshot_with_delay}=  ScreenCapLibrary.Take Screenshot  screenshot_with_delay  delay=10seconds
    ${end_date}=  DateTime.Get Current Date
    Screenshots Should Exist  ${OUTPUTDIR}  ${screenshot_with_delay}
    ${actual_time}=  DateTime.Subtract Date From Date  ${end_date}  ${start_date}
    Should Be True  ${actual_time} > 10

Take Multiple Screenshots
    ScreenCapLibrary.Take Multiple Screenshots  screenshot_number=4  delay_time=1 second
    Sleep  10
    Screenshot Number In ${OUTPUTDIR} Should Be 4

Take Multiple Gtk Screenshots
    [Tags]    gtk
    ScreenCapLibraryGtk.Take Multiple Screenshots  format=png  screenshot_number=4  delay_time=1 second
    Sleep  10
    Screenshot Number In ${OUTPUTDIR} Should Be 4

Take Screenshot With Partial Dimensions
    ${partial_screenshot}=  ScreenCapLibrary.Take Partial Screenshot  left=50  height=300  width=700
    Screenshot Should Exist  ${partial_screenshot}

Take Partial Gtk Screenshot
    [Tags]    gtk
    ${partial_screenshot}=  ScreenCapLibraryGtk.Take Partial Screenshot  left=50  height=300  width=700
    Screenshot Should Exist  ${partial_screenshot}

Take Gif
    ScreenCapLibrary.Start Gif Recording
    Sleep  2
    ScreenCapLibrary.Stop Gif Recording
    Screenshot Should Exist  ${GIF_SCREENSHOT}

Take Gtk Gif
    [Tags]    gtk
    ScreenCapLibraryGtk.Start Gif Recording
    Sleep  2
    ScreenCapLibraryGtk.Stop Gif Recording
    Screenshot Should Exist  ${GIF_SCREENSHOT}

Video Capture
    ScreenCapLibrary.Start Video Recording
    Sleep  5
    ScreenCapLibrary.Stop Video Recording
    Screenshot Should Exist  ${FIRST_VIDEO_FILE}
    Sleep  10

Video Capture Gtk
    [Tags]    gtk
    ScreenCapLibraryGtk.Start Video Recording
    Sleep  5
    ScreenCapLibraryGtk.Stop Video Recording
    Screenshot Should Exist  ${FIRST_VIDEO_FILE}
    Sleep  10

Nested And Consecutive Video Captures
    ScreenCapLibrary.Start Video Recording  1
    Sleep  5
    ScreenCapLibrary.Start Video Recording  2
    Sleep  5
    ScreenCapLibrary.Stop Video Recording  2
    Sleep  5
    ScreenCapLibrary.Stop Video Recording  1
    ScreenCapLibrary.Start Video Recording   3
    Sleep  5
    ScreenCapLibrary.Stop Video Recording    3
    Screenshot Should Exist  ${SECOND_VIDEO_FILE}
    Screenshot Should Exist  ${FIRST_VIDEO_FILE}
    Screenshot Should Exist  ${THIRD_VIDEO_FILE}
    Sleep  10

Nested And Consecutive Video Captures Gtk
    [Tags]  gtk
    ScreenCapLibraryGtk.Start Video Recording   1
    Sleep  5
    ScreenCapLibraryGtk.Start Video Recording  2
    Sleep  5
    ScreenCapLibraryGtk.Stop Video Recording   2
    Sleep  5
    ScreenCapLibraryGtk.Stop Video Recording   1
    ScreenCapLibraryGtk.Start Video Recording   3
    Sleep  5
    ScreenCapLibraryGtk.Stop Video Recording    3
    Screenshot Should Exist  ${FIRST_VIDEO_FILE}
    Screenshot Should Exist  ${SECOND_VIDEO_FILE}
    Screenshot Should Exist  ${THIRD_VIDEO_FILE}
    Sleep  10

Close All Recordings
    ScreenCapLibrary.Start Video Recording  1
    Sleep  5
    ScreenCapLibrary.Start Video Recording  2
    Sleep  5
    ScreenCapLibrary.Stop All Video Recordings
    Screenshot Should Exist  ${FIRST_VIDEO_FILE}
    Screenshot Should Exist  ${SECOND_VIDEO_FILE}
    Sleep  10

Close All Recordings Without Alias
    ScreenCapLibrary.Start Video Recording
    Sleep  5
    ScreenCapLibrary.Start Video Recording
    Sleep  5
    ScreenCapLibrary.Stop All Video Recordings
    Screenshot Should Exist  ${FIRST_VIDEO_FILE}
    Screenshot Should Exist  ${SECOND_VIDEO_FILE}
    Sleep  10

Close All Recordings Gtk
    [Tags]  gtk
    ScreenCapLibraryGtk.Start Video Recording  1
    Sleep  5
    ScreenCapLibraryGtk.Start Video Recording  2
    Sleep  5
    ScreenCapLibraryGtk.Stop All Video Recordings
    Screenshot Should Exist  ${FIRST_VIDEO_FILE}
    Screenshot Should Exist  ${SECOND_VIDEO_FILE}
    Sleep  10

Close All Recordings Without Alias Gtk
    [Tags]  gtk
    ScreenCapLibraryGtk.Start Video Recording
    Sleep  5
    ScreenCapLibraryGtk.Start Video Recording
    Sleep  5
    ScreenCapLibraryGtk.Stop All Video Recordings
    Screenshot Should Exist  ${FIRST_VIDEO_FILE}
    Screenshot Should Exist  ${SECOND_VIDEO_FILE}
    Sleep  10

Nested Videos Without Alias
    ScreenCapLibrary.Start Video Recording
    Sleep  5
    ScreenCapLibrary.Start Video Recording
    Sleep  5
    ScreenCapLibrary.Stop Video Recording
    Sleep  5
    ScreenCapLibrary.Stop Video Recording
    Screenshot Should Exist  ${FIRST_VIDEO_FILE}
    Screenshot Should Exist  ${SECOND_VIDEO_FILE}
    Sleep  10

Nested Videos Without Alias Gtk
    [Tags]  gtk
    ScreenCapLibraryGtk.Start Video Recording
    Sleep  5
    ScreenCapLibraryGtk.Start Video Recording
    Sleep  5
    ScreenCapLibraryGtk.Stop Video Recording
    Sleep  5
    ScreenCapLibraryGtk.Stop Video Recording
    Screenshot Should Exist  ${FIRST_VIDEO_FILE}
    Screenshot Should Exist  ${SECOND_VIDEO_FILE}
    Sleep  10

*** Keywords ***
Take Screenshot And Verify
    [Arguments]  @{expected files}
    ${path}=  ScreenCapLibrary.Take Screenshot  format=png
    Screenshots Should Exist  ${OUTPUTDIR}  @{expected files}
    [Return]  ${path}

Compare Size
    [Arguments]  ${screenshot_name}  ${screenshot_format}
    ScreenCapLibrary.Take Screenshot  ${screenshot_name}  ${screenshot_format}  quality=100
    ${high_quality_size}=  Get File Size  ${screenshot_name}
    ScreenCapLibrary.Take Screenshot    ${screenshot_name}  ${screenshot_format}  quality=0
    ${low_quality_size}=  Get File Size  ${screenshot_name}
    ${decrease}=  Evaluate  ${high_quality_size} - ${low_quality_size}
    ${percentage_size_decrease}=  Evaluate  float(${decrease}) / float(${high_quality_size}) * 100
    Should Be True  ${percentage_size_decrease} > 50
