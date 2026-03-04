Feature: Logout Functionality
    Scenario: Successful Log out on UCrypt
        Given I am a logged-in user
        When I click "Logout"
        Then I should be logged out and redirected to the home page

    Scenario: Unsuccessful Log out on UCrypt
        Given I am a logged-in user
        When I click "Logout"
        Then the system keeps me on the same page and logged in
