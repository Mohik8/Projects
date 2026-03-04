Feature: Copy Key Functionality

  Scenario: Copy decryption key on decryption page
    Given I am logged in as an admin and on the decryption page
    When I enter a sample decryption key
    And I click the copy key button
    Then The clipboard should contain the decryption key

  Scenario: Copy encryption key on encryption page
    Given I am logged in as an admin and on the encryption page
    When I enter a sample encryption key
    And I click the encryption copy key button
    Then The clipboard should contain the encryption key

  Scenario: Copy from blank key field should result in empty clipboard
    Given I am logged in as an admin and on the encryption page
    When I clear the key field and click the copy button
    Then The clipboard should be empty
