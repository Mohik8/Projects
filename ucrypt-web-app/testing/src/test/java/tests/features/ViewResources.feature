Feature: Resources Tab Viewer
    Scenario: User views available resources
        Given I am a signed in as a user with “Employee” or “Admin” role
        When I click on the Resources tab on the Uranus site
        Then I should be able to view the available resources
    
    Scenario: User downloads a resource
        Given I am a signed in as a user with “Employee” or “Admin” role
        And I have navigated to the resources page
        When I click “Download” on a resource 
        Then the resource is downloaded in my browser
