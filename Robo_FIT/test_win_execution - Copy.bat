@echo off

FOR %%A IN ("%~dp0.") DO SET workingDirectory=%%~dpA
echo %workingDirectory%

set PYTHONPATH=%PYTHONPATH%;%workingDirectory%%

echo Python path = %PYTHONPATH%

del %workingDirectory%\robofit_log*.log /q /f

IF [%1]==[] ( 
   goto ExecutionOptions
) ELSE (
   goto ArgumentFound
)

:ExecutionOptions
echo Please select Option
echo ***************************
echo Options can be:
echo ---------------------------
echo 1.Start new execution
echo 2.Upload record only
echo ****************************
set /p executionOption="Do you want to start the new execution or only upload the record?: "
echo %executionOption%
IF /I "%executionOption%" == "1" (
    echo Start the new execution
    goto NoArgumentFound
) ELSE (
    IF /I "%executionOption%" == "2" (
        echo Only upload record
        goto UploadExecutionRecordOnly
    ) ELSE (
        goto END
    )
)

:NoArgumentFound
echo Please pass an argument to execution this Script
echo ***************************
echo Test teams can we:
echo ---------------------------
echo 1.SWE4
echo 2.SWE5
echo 3.SWE6
echo 4.SYS6
echo 5.SYS5
echo 6.RobotScripts (only applicable if you are using new CRE structure)
echo ****************************
set /p teamName="Choose your team name: "
set /p isUploadExecutionRecord="Do you want to upload the execution record, yes/no : "
echo %isUploadExecutionRecord%
If /i "%isUploadExecutionRecord%" == "yes" (
    echo upload Record
    goto UploadExecutionRecord
) ELSE (
    echo not upload record
    goto NotUploadExecutionRecord
)

:UploadExecutionRecord
echo ***************************
echo Test Group Type can we:
echo ---------------------------
echo 1.SW Unit Test
echo 2.SW Integration Test
echo 3.SW Qualification Test
echo 4.System Integration Test
echo 5.System Test
echo ***************************
set /p testCaseGroupType="Choose your test group type: "
echo ***************************
echo Test execution Group can we:
echo ---------------------------
echo 1.Component Functional Test
echo 2.Coverage Test
echo 3.Input/Output Test
echo 4.Platform Test
echo 5.Dynamic Behavior Test
echo 6.Interface Test
echo 7.Performance Test
echo 8.Static Behavior Test
echo 9.SW Architecture Test
echo 10.Functional Test
echo 11.Non-Functional Test
echo 12.Environment Test
echo 13.Hardware Test
echo 14.Manufacturing Test
echo ***************************
set /p testCaseGroup="Choose your test execution group: "
echo ***************************
echo Test execution type can we:
echo ---------------------------
echo 1.Feature Functional
echo 2.Performance
echo 3.Load
echo 4.Stress
echo 5.Failover and Recovery
echo 6.Long Run
echo 7.Storage
echo 8.Capatibility/Conversion
echo 9.Security and Data Access
echo 10.Reliability
echo 11.Procedure
echo 12.Installation
echo 13.Serviceability/Maintainability
echo 14.Usability
echo 15.In-Vehicle
echo 16.Smoke Test
echo 17.BAT
echo 18.Stability
echo 19.KPI Test
echo 20.Issues Prone Test
echo 21.Platform Test
echo 22.CTS/VTS
echo 23.API
echo ***************************
set /p testCaseType="Choose your test execution type: "
set /p testExecutionKey="Please enter the Test Execution Key if you want to link this execution record with existing test execution otherwise type NEW: "
set /p testPlanKey="Please enter the Test Plan key, if not key created please create first and then pass key value: "
echo %testCaseType%
echo %testCaseGroup%
echo %teamName%
echo %testPlanKey%
echo %testExecutionKey%
echo Current Directory path: %cd%
python GenericLibraries/GenericOpLibs/TestArtifacts/ExecutionClass.py -p %cd% -t %teamName% -u "Yes" -tkey %testExecutionKey% -tplankey %testPlanKey% -tgroup %testCaseGroup% -tgrouptype %testCaseGroupType% -ttype %testCaseType%
@REM python GenericLibraries/GenericOpLibs/TestArtifacts/ExecutionClass.py -p %cd% -u "Yes" -tkey %testExecutionKey% -tplankey %testPlanKey% -tgroup %testCaseGroup% -tgrouptype %testCaseGroupType% -ttype %testCaseType%
goto END

:NotUploadExecutionRecord
echo Current Directory path: %cd%
python GenericLibraries/GenericOpLibs/TestArtifacts/ExecutionClass.py -p %cd% -t %teamName% -u "No"
@REM python GenericLibraries/GenericOpLibs/TestArtifacts/ExecutionClass.py -p %cd% -u "No"
goto END

:UploadExecutionRecordOnly
echo ***************************
echo Test teams can we:
echo ---------------------------
echo 1.SWE4
echo 2.SWE5
echo 3.SWE6
echo 4.SYS6
echo 5.SYS5
echo ****************************
set /p teamName="Choose your team name: "
set /p reportPath="Please enter the report folder name or folder path you want to upload: "
echo Report path: %reportPath%
echo ***************************
echo Test Group Type can we:
echo ---------------------------
echo 1.SW Unit Test
echo 2.SW Integration Test
echo 3.SW Qualification Test
echo 4.System Integration Test
echo 5.System Test
echo ***************************
set /p testCaseGroupType="Choose your test group type: "
echo ***************************
echo Test execution Group can we:
echo ---------------------------
echo 1.Component Functional Test
echo 2.Coverage Test
echo 3.Input/Output Test
echo 4.Platform Test
echo 5.Dynamic Behavior Test
echo 6.Interface Test
echo 7.Performance Test
echo 8.Static Behavior Test
echo 9.SW Architecture Test
echo 10.Functional Test
echo 11.Non-Functional Test
echo 12.Environment Test
echo 13.Hardware Test
echo 14.Manufacturing Test
echo ***************************
set /p testCaseGroup="Choose your test execution group: "
echo ***************************
echo Test execution type can we:
echo ---------------------------
echo 1.Feature Functional
echo 2.Performance
echo 3.Load
echo 4.Stress
echo 5.Failover and Recovery
echo 6.Long Run
echo 7.Storage
echo 8.Capatibility/Conversion
echo 9.Security and Data Access
echo 10.Reliability
echo 11.Procedure
echo 12.Installation
echo 13.Serviceability/Maintainability
echo 14.Usability
echo 15.In-Vehicle
echo 16.Smoke Test
echo 17.BAT
echo 18.Stability
echo 19.KPI Test
echo 20.Issues Prone Test
echo 21.Platform Test
echo 22.CTS/VTS
echo 23.API
echo ***************************
set /p testCaseType="Choose your test execution type: "
set /p testExecutionKey="Please enter the Test Execution Key if you want to link this execution record with existing test execution otherwise type NEW: "
set /p testPlanKey="Please enter the Test Plan key, if not key created please create first and then pass key value: "
echo %testCaseType%
echo %testCaseGroup%
echo %testPlanKey%
echo %testExecutionKey%
echo Current Directory path: %cd%
python GenericLibraries/GenericOpLibs/TestArtifacts/ExecutionClass.py -p %cd% -t %teamName% -op %executionOption% -rp %reportPath% -u "Yes" -tkey %testExecutionKey% -tplankey %testPlanKey% -tgroup %testCaseGroup% -tgrouptype %testCaseGroupType% -ttype %testCaseType%
goto END

:ArgumentFound
python GenericLibraries/GenericOpLibs/TestArtifacts/ExecutionClass.py -p %cd% %*
goto END

:END
pause
