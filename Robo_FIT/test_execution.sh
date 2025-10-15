#!/usr/bin/env bash
(( $UID != 0 )) && ( echo "You need to run this as root." && exit -13 )
ps | grep robot && killall robot
ps | grep python3 && killall python3

parentDirectory="$(dirname "$(pwd)")"
rm -rf robofit_log*.log
export PYTHONPATH=$parentDirectory

runWithArguments (){
  echo "Running the script with arguments $@"
  python3 GenericLibraries/GenericOpLibs/TestArtifacts/ExecutionClass.py -p $(pwd) $@
}

runExecutionWithoutUploadExecutionRecord (){
  echo "Running the script without arguments and without upload execution recoard $(pwd)"
  python3 GenericLibraries/GenericOpLibs/TestArtifacts/ExecutionClass.py -p $(pwd) -t $teamName -u "No"
}

runExecutionWithUploadExecutionRecord (){
  echo "***************************"
  echo "Test Group Type can we:"
  echo "---------------------------"
  echo "1.SW Unit Test"
  echo "2.SW Integration Test"
  echo "3.SW Qualification Test"
  echo "4.System Integration Test"
  echo "5.System Test"
  echo "***************************"
  read -p "Please select the Test Group: " testCaseGroupType
  echo "***************************"
  echo "Test execution Group can we:"
  echo "---------------------------"
  echo "1.Component Functional Test"
  echo "2.Coverage Test"
  echo "3.Input/Output Test"
  echo "4.Platform Test"
  echo "5.Dynamic Behavior Test"
  echo "6.Interface Test"
  echo "7.Performance Test"
  echo "8.Static Behavior Test"
  echo "9.SW Architecture Test"
  echo "10.Functional Test"
  echo "11.Non-Functional Test"
  echo "12.Environment Test"
  echo "13.Hardware Test"
  echo "14.Manufacturing Test"
  echo "***************************"
  read -p "Choose your test execution group: " testCaseGroup
  echo "***************************"
  echo "Test execution type can we:"
  echo "---------------------------"
  echo "1.Feature Functional"
  echo "2.Performance"
  echo "3.Load"
  echo "4.Stress"
  echo "5.Failover and Recovery"
  echo "6.Long Run"
  echo "7.Storage"
  echo "8.Capatibility/Conversion"
  echo "9.Security and Data Access"
  echo "10.Reliability"
  echo "11.Procedure"
  echo "12.Installation"
  echo "13.Serviceability/Maintainability"
  echo "14.Usability"
  echo "15.In-Vehicle"
  echo "16.Smoke Test"
  echo "17.BAT"
  echo "18.Stability"
  echo "19.KPI Test"
  echo "20.Issues Prone Test"
  echo "21.Platform Test"
  echo "22.CTS/VTS"
  echo "23.API"
  echo "***************************"
  read -p "Please select the test execution type: " testCaseType
  read -p "Please enter the Test Execution Key if you want to link this execution record with existing test execution otherwise type NEW: " testExecutionKey
  read -p "Please enter the Test Plan key, if not key created please create first and then pass key value: " testPlanKey
  echo "User wants to run the execution for Test Group: $testCaseGroupType, Test Sub Group: $testCaseGroup, Test Case Type: $testCaseType, Test Execution: $testExecutionKey and wants to link with Test Plan: $testPlanKey"
  python3 GenericLibraries/GenericOpLibs/TestArtifacts/ExecutionClass.py -p $(pwd) -t $teamName -u "Yes" -tkey $testExecutionKey -tplankey $testPlanKey -tgroup $testCaseGroup -tgrouptype $testCaseGroupType -ttype $testCaseType
}

# check if user provided any command line arguments
if [ "$1" = "" ]
then
  echo "Please pass an argument to execution this Script:"
  echo "Please pass an argument to execution this Script"
  echo "***************************"
  echo "Test teams can we:"
  echo "---------------------------"
  echo "1.SWE4"
  echo "2.SWE5"
  echo "3.SWE6"
  echo "4.SYS6"
  echo "5.SYS5"
  echo "6.RobotScripts"
  echo "****************************"
  echo "Please select your team name: "
  read teamName
  read -p "Do you want to upload the execution record, yes/no : " isUploadExecutionRecord
  if [ "$isUploadExecutionRecord" = "yes" ] || [ "$isUploadExecutionRecord" = "YES" ] || [ "$isUploadExecutionRecord" = "Yes" ]
  then
    echo "User wants to upload the execution record"
    runExecutionWithUploadExecutionRecord $teamName $testCaseGroupType $testCaseGroup $testCaseType $testExecutionKey $testPlanKey
  else
    echo "Uer doesn't wants to upload the execution record"
    runExecutionWithoutUploadExecutionRecord $teamName
  fi
else
  runWithArguments $*
fi

