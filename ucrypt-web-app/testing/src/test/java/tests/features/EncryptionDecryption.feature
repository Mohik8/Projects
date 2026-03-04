Feature: File Encryption and Decryption

  Scenario: Encrypt a file with a valid key
    Given I am logged in as a user
    When I navigate to the encryption page
    And I enter valid plain text and select encryption type
    Then I should see a success message "data encrypted successfully"

  Scenario: Decrypt an encrypted file with correct key
    Given I am logged in as a user
    When I navigate to the decryption page
    And I enter the encrypted text, encryption type, and correct key
    Then I should receive the original plain text back

  Scenario: Decrypt an encrypted file with incorrect key
    Given I am logged in as a user
    When I navigate to the decryption page
    And I enter the encrypted text, encryption type, and an incorrect key
    Then I should see an error message indicating decryption failed