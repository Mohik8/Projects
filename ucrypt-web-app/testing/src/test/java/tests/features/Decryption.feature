Feature: File and text Decryption        
    Scenario: User selects a saved key to use in decryption form
        Given I have logged in
        And I have navigated to the decryption page
        And I have saved the key used during an encryption process
        When I select the saved encryption key from the dropdown
        Then the saved encryption key is present in the encryption key field
    Scenario: User uses copy button to copy plaintext output
        Given I have logged in
        And I have navigated to the decryption page
        And I have successfully decrypted ciphertext
        When I press the copy button on the plaintext output field
        Then the output plaintext has been copied to my clipboard
    Scenario: A user decrypts file using invalid key
        Given I have logged in
        And I have navigated to the decryption page
        And I press the “Upload File” button and select an encrypted file
        And select a file decryption technique
        And enter a key that is invalid for the selected decryption technique
        When I press the decrypt file button
        Then there is an error message pops up saying that the key was invalid

    Scenario: A user decrypts file using valid input, key and technique
        Given I have logged in
        And I have navigated to the decryption page
        And I press the “Upload File” button and select an encrypted file
        And select the encryption technique the file was encrypted with
        And enter the key that the file was encrypted with
        When I press the decrypt file button
        Then the submitted file is successfully decrypted and the original is downloaded

    Scenario: A user decrypts text using an invalid key
        Given I have logged in
        And I have navigated to the decryption page
        And I have entered a ciphertext
        And selected a text decryption technique
        And entered a key that is invalid for the selected text decryption technique
        When I press the decrypt text button
        Then I get an error saying that the selected text decryption key is invalid
    
    Scenario: A user decrypts text using valid input, key and technique
        Given I have logged in
        And I have navigated to the decryption page
        And I have entered a ciphertext
        And select the encryption technique the text was encrypted with
        And enter the key that the text was encrypted with
        When I press the decrypt text button
        Then the ciphertext is decrypted and the plaintext is given as output
    

        

