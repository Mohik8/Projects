Feature: Role-Based Access Control
    Scenario: Any website visitor can see public pages
        Given I am visiting the Uranus website with or without being logged in
        When I try to access a public page
        Then I successfully load the page and view the content

    Scenario: A visitor that is not logged in cannot see non-public content
        Given I am visiting the Uranus website without being logged in
        When I try to access a non-public page
        Then I am rerouted to the home page

    Scenario: A user logged in with “User”, “Employee” or “Admin” role can see crypto services
        Given I am logged in as a user with a  “User”, “Employee” or “Admin” role on the Uranus website
        When I access the decryption and encryption pages
        Then the pages load successfully and I can use the services as expected

    Scenario: A user logged in with the “User” role cannot see resources
        Given I am logged in as a user with a “User” role on the Uranus website
        When I try to access the resources page
        Then I am rerouted to the home page

    Scenario: A user logged in with “Employee” or “Admin” role can access resources
        Given I am logged in as a user with a “Employee” or “Admin” role on the Uranus website
        When I try to access the resources page
        Then the page loads correctly and I can see available resources

    Scenario: A user logged in with the “User” or “Employee” role cannot access administrative services
        Given I am logged in as a user with the “User” or “Employee” role
        When I try to access the resources page
        Then I am rerouted to the home page

    Scenario: A user logged in with the “Admin” role can access administrative services
        Given I am logged in as a user with an “Admin” role
        When I try to access administrative services
        Then the services load and I can use them as expected
