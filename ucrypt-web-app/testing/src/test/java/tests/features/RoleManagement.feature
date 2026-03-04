Feature: Role Management
  Scenario: Admin edits a user's role successfully
    Given I am logged in as an admin
    When I open the admin panel
    And I edit the role of the first user to "User"
    Then I should see a success message "Role is Edited Successfully"
  Scenario: Non-admin user cannot edit roles
    Given I am logged in as a regular user
    When I try to access the admin panel or edit roles
    Then I should be denied access or not see any role editing option
