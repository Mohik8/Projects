package tests.stepDefinitions.Decryption;

import static org.testng.Assert.assertTrue;
import static org.uranus.assertions.UranusAssertions.assertTextContentMatches;

import java.io.File;

import org.uranus.configuration.LoadProperties;
import org.uranus.driver.UranusDriver;
import org.uranus.model.FileDecryptionModel;
import org.uranus.model.TextDecryptionModel;
import org.uranus.model.TextEncryptionModel;
import org.uranus.pages.DecryptionPage;
import org.uranus.pages.EncryptionPage;
import org.uranus.pages.HomePage;

import io.cucumber.java.After;
import io.cucumber.java.AfterAll;
import io.cucumber.java.Before;
import io.cucumber.java.BeforeAll;
import io.cucumber.java.en.And;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;

public class DecryptionSteps {

    private static HomePage homePage;
    private static UranusDriver webDriver;
    private static DecryptionPage decryptionPage;
    private static EncryptionPage encryptionPage;

    private static FileDecryptionModel fileDecryptionModel;
    private static TextDecryptionModel textDecryptionModel;
    private static String encryptedFilePath;

    @BeforeAll
    public static void setup() {
        String relativeEncryptedFilePath = "src/test/resources/encrypted-test-data/aes/png.png.enc";
        File file = new File(relativeEncryptedFilePath);
        encryptedFilePath = file.getAbsolutePath();
        webDriver = UranusDriver.getInstance();
        webDriver.setup();
    }

    @AfterAll
    public static void teardown() {
        webDriver.teardown();
    }
  
    @Before
    public void refresh() {
        homePage = new HomePage(webDriver);
        decryptionPage = new DecryptionPage(webDriver);
        fileDecryptionModel = FileDecryptionModel.builder()
            .filePath(encryptedFilePath)
            .algorithm("AES")
            .key("WrN88AbYhJJ7pyw3u9HwZ6mBQYHOt2je+FUp1KLcDnw=")
            .keyType("manual")
            .build();
        textDecryptionModel = TextDecryptionModel.builder()
            .ciphertext("SampleEncryptedText")
            .algorithm("AES")
            .key("WrN88AbYhJJ7pyw3u9HwZ6mBQYHOt2je+FUp1KLcDnw=")
            .plaintext("")
            .keyType("manual")
            .build();
    }

    @After
    public void afterScenario() {
        webDriver.refresh();
        homePage.logout();
        homePage.closeToastMsg();
        webDriver.refresh();
    }

    @Given("I have logged in")
    public void i_have_logged_in() {
        homePage.login(
            LoadProperties.env.getProperty("ADMIN_EMAIL"),
            LoadProperties.env.getProperty("ADMIN_PASSWORD")
        );
        homePage.closeToastMsg();
    }

    // Scenario: A user decrypts file using invalid key
    @And("I have navigated to the decryption page")
    public void i_have_navigated_to_the_decryption_page() {
        homePage.openDecryptionPage();
    }

    @And("I press the “Upload File” button and select an encrypted file")
    public void i_press_upload_file_and_select_encrypted_file() {
        decryptionPage.uploadFile(fileDecryptionModel.filePath);
    }

    @And("select a file decryption technique")
    public void select_a_file_decryption_technique() {
        decryptionPage.selectFileDecryptionAlgorithm(fileDecryptionModel.algorithm);
        decryptionPage.selectFileDecryptionKeyType(fileDecryptionModel.keyType);
    }

    @And("enter a key that is invalid for the selected decryption technique")
    public void enter_invalid_key_for_file_decryption() {
        decryptionPage.enterFileDecryptionKey("invalidKey123");
    }

    @Then("there is an error message pops up saying that the key was invalid")
    public void error_message_for_invalid_key() {
        assertTextContentMatches(webDriver.getElement(homePage.toastMsg), "Encryption key for Algorithm " + fileDecryptionModel.algorithm + " is not a valid key!");
    }

    // Scenario: A user decrypts file using valid input, key and technique
    @And("select the encryption technique the file was encrypted with")
    public void select_encryption_technique_file_was_encrypted_with() {
        decryptionPage.selectFileDecryptionAlgorithm(fileDecryptionModel.algorithm);
    }

    @And("enter the key that the file was encrypted with")
    public void enter_valid_key_for_file_decryption() {
        decryptionPage.enterFileDecryptionKey(fileDecryptionModel.key);
    }

    @When("I press the decrypt file button")
    public void press_decrypt_button_and_file_is_decrypted() {
        decryptionPage.click(decryptionPage.submitFileDecryptionButton);
    }

    @Then("the submitted file is successfully decrypted and the original is downloaded")
    public void file_is_decrypted_and_downloaded() {
        assertTextContentMatches(webDriver.getText(decryptionPage.fileDecryptionStatus), "Finished");
    }

    // Scenario: A user decrypts text using an invalid key
    @And("I have entered a ciphertext")
    public void i_have_entered_a_ciphertext() {
        decryptionPage.enterTextToDecrypt(textDecryptionModel.ciphertext);
    }

    @And("selected a text decryption technique")
    public void selected_text_decryption_technique() {
        decryptionPage.selectTextDecryptionAlgorithm(textDecryptionModel.algorithm);
    }

    @And("entered a key that is invalid for the selected text decryption technique")
    public void entered_invalid_key_for_text_decryption() {
        decryptionPage.enterTextDecryptionKey("invalidKey123");
    }

    @When("I press the decrypt text button")
    public void press_decrypt_button_and_error_for_invalid_text_key() {
        decryptionPage.click(decryptionPage.submitTextDecryptionButton);
    }

    @Then("I get an error saying that the selected text decryption key is invalid")
    public void error_for_invalid_text_key() {
        assertTextContentMatches(webDriver.getElement(homePage.toastMsg), "Encryption key for Algorithm " + textDecryptionModel.algorithm + " is not a valid key!");
    }

    // Scenario: A user decrypts text using valid input, key and technique
    @And("select the encryption technique the text was encrypted with")
    public void select_encryption_technique_text_was_encrypted_with() {
        decryptionPage.selectTextDecryptionAlgorithm(textDecryptionModel.algorithm);
    }

    @And("enter the key that the text was encrypted with")
    public void enter_valid_key_for_text_decryption() {
        decryptionPage.enterTextDecryptionKey(textDecryptionModel.key);
    }

    @Then("the ciphertext is decrypted and the plaintext is given as output")
    public void ciphertext_is_decrypted_and_plaintext_output() {
        assertTextContentMatches(webDriver.getElement(decryptionPage.textDecryptionOutput), textDecryptionModel.plaintext);
    }

    // Scenario: User selects a saved key to use in decryption form
    @And("I have saved the key used during an encryption process")
    public void i_have_saved_the_key_used_during_encryption() {
        encryptionPage = new EncryptionPage(webDriver);
        homePage.openEncryptionPage();
        TextEncryptionModel textEncryptionRequest = TextEncryptionModel.builder()
            .plaintext(textDecryptionModel.plaintext)
            .algorithm(textDecryptionModel.algorithm)
            .key(textDecryptionModel.key)
            .build();
        encryptionPage.enterTextEncryptionRequest(textEncryptionRequest);
        encryptionPage.click(encryptionPage.saveTextEncryptionKeyButton); // Assuming this button exists to save the key
        homePage.closeToastMsg(); // Close the toast message after saving
        homePage.openDecryptionPage(); // Navigate back to decryption page
    }

    @When("I select the saved encryption key from the dropdown")
    public void select_saved_key_from_dropdown() {
        decryptionPage.selectTextDecryptionKeyType(textDecryptionModel.key); // Assuming "saved" is the option for saved keys
    }

    @Then("the saved encryption key is present in the encryption key field")
    public void saved_key_present_in_key_field() {
        assertTextContentMatches(webDriver.getElement(decryptionPage.textDecryptionKeyInput), textDecryptionModel.key);
    }

    // Scenario: User uses copy button to copy plaintext output
    @Given("I have successfully decrypted ciphertext")
    public void i_have_successfully_decrypted_ciphertext() {
        decryptionPage.submitTextDecryptionRequest(textDecryptionModel);
    }

    @When("I press the copy button on the plaintext output field")
    public void press_copy_button_on_plaintext_output() {
        try {
            Thread.sleep(2500); // Wait for decryption to complete
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        decryptionPage.copyTextDecryptionOutput();
    }

    @Then("the output plaintext has been copied to my clipboard")
    public void output_plaintext_copied_to_clipboard() {
        assertTrue(false); // Clipboard is failing, this assertion is a placeholder
    }

}
