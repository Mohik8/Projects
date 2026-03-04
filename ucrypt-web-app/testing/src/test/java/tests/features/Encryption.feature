Feature: File and Text Encryption    

    Scenario: User auto-generates a key after selecting text encryption technique
        Given I am a logged in user
        When I navigate to the encryption service
        And I am in the process of completing a text encryption form
        And I have selected any text encryption technique
        When I press the auto-generate text encryption key button
        Then valid key for the selected text encryption technique is generated in the key field

    Scenario: Logged in user uses an invalid key during file encryption
        Given I am a logged in user
        When I navigate to the encryption service
        And I upload a file by clicking the “Upload File” button
        And select a file encryption technique
        And I enter an invalid key for the chosen file encryption technique
        And I click on the encrypt file button
        Then I should get a pop up saying “Encryption key for Algorithm <selected algorithm> is not a valid key!” for file encryption

    Scenario: Logged in user uses a valid key during file encryption
        Given I am a logged in user
        When I navigate to the encryption service
        And I upload a file by clicking the “Upload File” button
        And select a file encryption technique
        And I enter a valid key for the chosen file encryption technique
        And I click on the encrypt file button
        Then the file output by the selected encryption technique, using the entered key is downloaded

    Scenario: Logged in user uses invalid key during text encryption
        Given I am a logged in user
        When I navigate to the encryption service
        And I enter text to encrypt
        And select a text encryption technique
        And I enter an invalid key for the chosen text encryption technique
        And I click on the encrypt text button
        Then I should get a pop up saying “Encryption key for Algorithm <selected algorithm> is not a valid key!” for text encryption

    Scenario: Logged in user uses valid key during text encryption
        Given I am a logged in user
        When I navigate to the encryption service
        And I enter text to encrypt
        And select a text encryption technique
        And I enter a valid key for the chosen text encryption technique
        And I click on the encrypt text button
        Then then ciphertext that has been encrypted with the chosen key and technique should be output



    Scenario: User copies contents of key field in encryption form
        Given I am a logged in user
        When I navigate to the encryption service
        And I am in the process of completing a text encryption form
        And there is a value present in the text encryption key field
        When I press the copy button on the text encryption key field
        Then the contents of the key field are present in my clipboard

    Scenario: User copies contents of text encryption output
        Given I am a logged in user
        And I navigate to the encryption service
        And I have successfully completed the text encryption process
        When I press the copy button on the ciphertext output field
        Then my clipboard contains the ciphertext

    Scenario: User saves a key to their profile
        Given I am a logged in user
        When I navigate to the encryption service
        And I am in the process of completing a text encryption form
        And there is a value present in the text encryption key field
        When I press the save key icon
        Then the key is saved to my profile and available to be used on the decryption form

    Scenario: User saves a blank key to their profile
        Given I am a logged in user
        When I navigate to the encryption service
        And I am in the process of completing a text encryption form
        And there is no value present in the key field
        When I press the save key icon
        Then the key is not saved to my profile and an error message is shown


    Scenario: User auto-generates a key without having selected an encryption technique
        Given I am a logged in user
        When I navigate to the encryption service
        And I am in the process of completing a text encryption form
        And I have not selected an encryption technique
        When I press the auto-generate text encryption key button
        Then I am prompted with an error saying an encryption type must be selected
