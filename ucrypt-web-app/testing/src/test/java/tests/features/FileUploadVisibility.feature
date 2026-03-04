Feature: File Upload Visibility

  Scenario: Admin uploads a file and verifies visibility
    Given I am logged in as an admin
    When I navigate to the resources upload section
    And I upload the file
    Then The file should be visible to admins and employees only

  Scenario: Regular user cannot access the resources tab
    Given I log in as regular user
    Then The Resources tab should not be visible

  Scenario: Admin cancels process during upload
     Given I am logged in as an admin
     And I navigate to the resource section of the admin panel
     And I click choose to upload a file
     Then the uploaded file is shown as a preview
     When I click the cancel button
     Then the staged file is removed from the preview
