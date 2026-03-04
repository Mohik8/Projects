Feature: Responsive and Accessible UI Design
    Scenario: View homepage on a mobile device
        Given I am a user on a mobile device
        When I visit the homepage
        Then the text should fit within its container
        And the header should be fully visible

    Scenario: Open mobile menu on various pages
        Given I am using a mobile device
        When I navigate to the Admin page
        And I open the mobile menu
        Then the menu should appear in front of all UI elements
        And all menu links should be clickable

    Scenario: Upload large file on encryption page
        Given I am logged in
        And I am on the encryption page
        When I upload a file larger than 50MB
        Then I should see an error message
        And the “Choose File” button should remain centered and aligned