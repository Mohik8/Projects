Feature: Changing Users roles
    Scenario: An administrator changes a user to employee
        Given I am logged in with the “Admin” role
        And I navigate to the registered user section of the admin panel
        When I click edit on a user
        And select the employee role from the role dropdown
        And press the save button
        Then the user has been assigned the “Employee” role

    Scenario: Administrator changes employee to user
        Given I am logged in with the “Admin” role
        And I navigate to the registered employees section of the admin panel
        When I click edit on an employee
        And select the user role from the role dropdown
        And press the save button
        Then the employee has been assigned the “User” role
