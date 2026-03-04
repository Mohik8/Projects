Feature: Contact us
    Scenario: User can successfully fill out contact us form
        Given the user is on the “contact” page
        When the user scrolls to the “Get in Touch” section
        And puts their information including name, phone, email, subject and message
        Then they should be able to send their message to the team by clicking on “submit”
