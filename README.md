# gala-iam-api

Web API for the Identity and Access management for the Gala Event Management System.

## IAM API works with:

- Users, ServiceAccounts (Participants. eg. `john.doe@gala.iam.com or reporting.service.svc@gala.iam.com`)
- Groups (Assignment and naming of Collection of Users and ServiceAccounts. eg. `TeamA -- [john.doe@gala.iam.com, reporting.service.svc@gala.iam.com]`)
- Resource (eg. `TeamA_TestVM -- VirtualMachine`)
- ResourceActions (Actions available for a Resource, eg. `VMCreate, VMPowerOn, VMPowerOff, VMPowerRestart, VMDelete, VMRead`)
- Role (Assignment and naming of a subset of Resource with ResourceAction. eg. `Operator -- TeamA_TestVM -- [VMRead, VMRestart]`)
- Permissions (Assignment and naming of Roles to Users, ServiceAccounts or Groups. eg. `MyTestVMOperator -- Operator -- [TeamA, janedoe@gala.iam.com, health-check.service.svc@gala.iam.com]`)
