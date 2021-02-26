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
${VIDEO_PERCENT}  25
${SCREENSHOT_PERCENT}  40

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
    ${path}=  ScreenCapLibrary.Stop Gif Recording
    Screenshot Should Exist  ${GIF_SCREENSHOT}
    Should Be Equal  ${path}  ${GIF_SCREENSHOT}

Take Gtk Gif
    [Tags]    gtk
    ScreenCapLibraryGtk.Start Gif Recording
    Sleep  2
    ${path}=  ScreenCapLibraryGtk.Stop Gif Recording
    Screenshot Should Exist  ${GIF_SCREENSHOT}
    Should Be Equal  ${path}  ${GIF_SCREENSHOT}

Video Capture
    ScreenCapLibrary.Start Video Recording
    Sleep  3
    ${path}=  ScreenCapLibrary.Stop Video Recording
    Video Should Exist  ${FIRST_VIDEO_FILE}
    Should Be Equal  ${path}  ${FIRST_VIDEO_FILE}

Video Capture Gtk
    [Tags]    gtk
    ScreenCapLibraryGtk.Start Video Recording
    Sleep  3
    ${path}=  ScreenCapLibraryGtk.Stop Video Recording
    Video Should Exist  ${FIRST_VIDEO_FILE}
    Should Be Equal  ${path}  ${FIRST_VIDEO_FILE}

Nested And Consecutive Video Captures
    ScreenCapLibrary.Start Video Recording  1
    Sleep  3
    ScreenCapLibrary.Start Video Recording  2
    Sleep  3
    ${second_video_path}=  ScreenCapLibrary.Stop Video Recording  2
    Sleep  3
    ${first_video_path}=  ScreenCapLibrary.Stop Video Recording  1
    ScreenCapLibrary.Start Video Recording   3
    Sleep  3
    ${third_video_path}=  ScreenCapLibrary.Stop Video Recording    3
    Video Should Exist  ${SECOND_VIDEO_FILE}
    Video Should Exist  ${FIRST_VIDEO_FILE}
    Video Should Exist  ${THIRD_VIDEO_FILE}
    Videos Should Exist  ${OUTPUTDIR}  ${first_video_path}  ${second_video_path}  ${third_video_path}

Nested And Consecutive Video Captures Gtk
    [Tags]  gtk
    ScreenCapLibraryGtk.Start Video Recording   1
    Sleep  3
    ScreenCapLibraryGtk.Start Video Recording  2
    Sleep  3
    ${first_video_path}=  ScreenCapLibraryGtk.Stop Video Recording   2
    Sleep  3
    ${second_video_path}=  ScreenCapLibraryGtk.Stop Video Recording   1
    ScreenCapLibraryGtk.Start Video Recording   3
    Sleep  3
    ${third_video_path}=  ScreenCapLibraryGtk.Stop Video Recording    3
    Video Should Exist  ${FIRST_VIDEO_FILE}
    Video Should Exist  ${SECOND_VIDEO_FILE}
    Video Should Exist  ${THIRD_VIDEO_FILE}
    Videos Should Exist  ${OUTPUTDIR}  ${first_video_path}  ${second_video_path}  ${third_video_path}

Close All Recordings
    ScreenCapLibrary.Start Video Recording  1
    Sleep  3
    ScreenCapLibrary.Start Video Recording  2
    Sleep  3
    @{paths}=  ScreenCapLibrary.Stop All Video Recordings
    Sleep  3
    Video Should Exist  ${FIRST_VIDEO_FILE}
    Video Should Exist  ${SECOND_VIDEO_FILE}
    Videos Should Exist  ${OUTPUTDIR}  @{paths}

Close All Recordings Without Alias
    ScreenCapLibrary.Start Video Recording
    Sleep  3
    ScreenCapLibrary.Start Video Recording
    Sleep  3
    @{paths}=  ScreenCapLibrary.Stop All Video Recordings
    Video Should Exist  ${FIRST_VIDEO_FILE}
    Video Should Exist  ${SECOND_VIDEO_FILE}
    Videos Should Exist  ${OUTPUTDIR}  @{paths}

Close All Recordings Gtk
    [Tags]  gtk
    ScreenCapLibraryGtk.Start Video Recording  1
    Sleep  3
    ScreenCapLibraryGtk.Start Video Recording  2
    Sleep  3
    @{paths}=  ScreenCapLibraryGtk.Stop All Video Recordings
    Video Should Exist  ${FIRST_VIDEO_FILE}
    Video Should Exist  ${SECOND_VIDEO_FILE}
    Videos Should Exist  ${OUTPUTDIR}  @{paths}

Close All Recordings Without Alias Gtk
    [Tags]  gtk
    ScreenCapLibraryGtk.Start Video Recording
    Sleep  3
    ScreenCapLibraryGtk.Start Video Recording
    Sleep  3
    @{paths}=  ScreenCapLibraryGtk.Stop All Video Recordings
    Video Should Exist  ${FIRST_VIDEO_FILE}
    Video Should Exist  ${SECOND_VIDEO_FILE}
    Videos Should Exist  ${OUTPUTDIR}  @{paths}

Nested Videos Without Alias
    ScreenCapLibrary.Start Video Recording
    Sleep  3
    ScreenCapLibrary.Start Video Recording
    Sleep  3
    ${first_video_path}=  ScreenCapLibrary.Stop Video Recording
    Sleep  3
    ${second_video_path}=  ScreenCapLibrary.Stop Video Recording
    Video Should Exist  ${FIRST_VIDEO_FILE}
    Video Should Exist  ${SECOND_VIDEO_FILE}
    Videos Should Exist  ${OUTPUTDIR}  ${first_video_path}  ${second_video_path}

Nested Videos Without Alias Gtk
    [Tags]  gtk
    ScreenCapLibraryGtk.Start Video Recording
    Sleep  3
    ScreenCapLibraryGtk.Start Video Recording
    Sleep  3
    ${second_video_path}=  ScreenCapLibraryGtk.Stop Video Recording
    Sleep  3
    ${first_video_path}=  ScreenCapLibraryGtk.Stop Video Recording
    Video Should Exist  ${FIRST_VIDEO_FILE}
    Video Should Exist  ${SECOND_VIDEO_FILE}
    Videos Should Exist  ${OUTPUTDIR}  ${first_video_path}  ${second_video_path}

Close Video Recording With Non-Existent Alias
    ScreenCapLibrary.Start Video Recording   1
    Sleep  3
    Run Keyword And Expect Error  No video recording with alias `2` found!  ScreenCapLibrary.Stop Video Recording  2
    ScreenCapLibrary.Stop Video Recording   1

Close Not Started Video Recording
    Run Keyword And Expect Error  No video recordings are started!  ScreenCapLibrary.Stop Video Recording
    Run Keyword And Expect Error  No video recordings are started!  ScreenCapLibrary.Stop All Video Recordings

Video Capture With Size Percentage
    ScreenCapLibrary.Start Video Recording  size_percentage=1
    Sleep  3
    ScreenCapLibrary.Stop Video Recording
    ScreenCapLibrary.Start Video Recording   size_percentage=0.1
    Sleep  3
    ScreenCapLibrary.Stop Video Recording
    ${high_quality_size}=  Get File Size  ${FIRST_VIDEO_FILE}
    ${low_quality_size}=  Get File Size  ${SECOND_VIDEO_FILE}
    Should ${high_quality_size} Be Greater Than ${low_quality_size} By ${VIDEO_PERCENT}

Video Capture With Size Percentage Gtk
    [Tags]    gtk  no-xvfb
    ScreenCapLibraryGtk.Start Video Recording  size_percentage=1
    Sleep  3
    ScreenCapLibraryGtk.Stop Video Recording
    ScreenCapLibraryGtk.Start Video Recording   size_percentage=0.1
    Sleep  3
    ScreenCapLibraryGtk.Stop Video Recording
    ${high_quality_size}=  Get File Size  ${FIRST_VIDEO_FILE}
    ${low_quality_size}=  Get File Size  ${SECOND_VIDEO_FILE}
    Should ${high_quality_size} Be Greater Than ${low_quality_size} By ${VIDEO_PERCENT}

Size Percentage Inferior Limits
    Run Keyword And Expect Error  Size percentage should take values > than 0 and <= to 1.  Size Percentage Check  0

Size Percentage Superior Limits
    Run Keyword And Expect Error  Size percentage should take values > than 0 and <= to 1.  Size Percentage Check  1.1

Close All Recordings With Same Alias
    ScreenCapLibrary.Start Video Recording  1
    Sleep  3
    ScreenCapLibrary.Start Video Recording  1
    Sleep  3
    ${paths}=  ScreenCapLibrary.Stop Video Recording  1
    Videos Should Exist  ${OUTPUTDIR}  @{paths}
    Video Should Exist  ${FIRST_VIDEO_FILE}
    Video Should Exist  ${SECOND_VIDEO_FILE}

Pause And Resume Video
    ScreenCapLibrary.Start Video Recording  1
    Sleep  3s
    ScreenCapLibrary.Pause Video Recording  1
    Sleep  5s
    ScreenCapLibrary.Resume Video Recording  1
    Sleep  3s
    ScreenCapLibrary.Stop Video Recording  1

Pause And Resume Video Gtk
    [Tags]  gtk
    ScreenCapLibraryGtk.Start Video Recording  1
    ScreenCapLibraryGtk.Start Video Recording  1
    Sleep  3s
    ScreenCapLibraryGtk.Pause Video Recording  1
    Sleep  5s
    ScreenCapLibraryGtk.Resume Video Recording  1
    Sleep  3s
    ScreenCapLibraryGtk.Stop Video Recording  1

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
    Should ${high_quality_size} Be Greater Than ${low_quality_size} By ${SCREENSHOT_PERCENT}

Should ${high_quality_size} Be Greater Than ${low_quality_size} By ${percent}
    ${decrease}=  Evaluate  ${high_quality_size} - ${low_quality_size}
    ${percentage_size_decrease}=  Evaluate  float(${decrease}) / float(${high_quality_size}) * 100
    Should Be True  ${percentage_size_decrease} > ${percent}

Size Percentage Check
    [Arguments]  ${size_percentage}
    ScreenCapLibraryGtk.Start Video Recording  size_percentage=${size_percentage}
    Sleep  3
    ScreenCapLibraryGtk.Stop Video Recording
