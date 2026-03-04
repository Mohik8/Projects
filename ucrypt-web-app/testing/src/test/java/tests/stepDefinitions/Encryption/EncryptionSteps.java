package tests.stepDefinitions.Encryption;

import static org.uranus.assertions.UranusAssertions.assertIsValidKey;
import static org.uranus.assertions.UranusAssertions.assertTextContentMatches;

import java.io.File;

import org.uranus.configuration.LoadProperties;
import org.uranus.driver.UranusDriver;
import org.uranus.model.FileEncryptionRequestModel;
import org.uranus.model.TextEncryptionModel;
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

public class EncryptionSteps {

    private static HomePage homePage;
    private static UranusDriver webDriver;
    private static EncryptionPage encryptionPage;

    private static FileEncryptionRequestModel fileEncryptionModel;
    private static TextEncryptionModel textEncryptionModel;
    private static String filePath;

    @BeforeAll
    public static void setup() {
        webDriver = UranusDriver.getInstance();
        webDriver.setup();
        String relativeEncryptedFilePath = "src/test/resources/unencrypted-test-data/png.png"; // Relative path to the unencrypted file
        File file = new File(relativeEncryptedFilePath);
        filePath = file.getAbsolutePath();
    }

    @AfterAll
    public static void teardown() {
        webDriver.teardown();
    }
  
    @Before
    public void refresh() {
        homePage = new HomePage(webDriver);
        encryptionPage = new EncryptionPage(webDriver);
        fileEncryptionModel = FileEncryptionRequestModel.builder()
            .filePath(filePath) // Replace with actual file path
            .algorithm("AES") // Default algorithm, can be changed
            .key("WrN88AbYhJJ7pyw3u9HwZ6mBQYHOt2je+FUp1KLcDnw=") // Default key, can be changed
            .build();
        textEncryptionModel = TextEncryptionModel.builder()
            .plaintext("Sample text to encrypt") // Example text
            .algorithm("AES") // Default algorithm, can be changed
            .key("WrN88AbYhJJ7pyw3u9HwZ6mBQYHOt2je+FUp1KLcDnw=") // Default key, can be changed
            .cipherText("") // Initially empty, will be filled after encryption
            .build();
    }

    @After
    public void afterScenario() {
        webDriver.refresh();
        webDriver.navigateToHome();
        homePage.logout();
        homePage.closeToastMsg();
        webDriver.refresh();
    }

    // Scenario: Logged in user uses an invalid key during file encryption
    @Given("I am a logged in user")
    public void i_am_a_logged_in_user() {
        homePage.login(
            LoadProperties.env.getProperty("ADMIN_EMAIL"),
            LoadProperties.env.getProperty("ADMIN_PASSWORD")
        );
        homePage.closeToastMsg();
    }

    @When("I navigate to the encryption service")
    public void i_navigate_to_the_encryption_service() {
        homePage.openEncryptionPage();
    }

    @When("I upload a file by clicking the “Upload File” button")
    public void i_upload_a_file_by_clicking_upload_file_button() {
        encryptionPage.uploadFile(fileEncryptionModel.filePath);
    }

    @And("select a text encryption technique")
    public void select_an_encryption_technique() {
        encryptionPage.selectTextEncryptionAlgorithm(textEncryptionModel.algorithm);
    }

    @And("select a file encryption technique")
    public void select_an_encryption_technique_file() {
        encryptionPage.selectFileEncryptionAlgorithm(fileEncryptionModel.algorithm);
    }

    @When("I enter an invalid key for the chosen file encryption technique")
    public void i_enter_an_invalid_key_for_the_chosen_encryption_technique() {
        encryptionPage.enterFileEncryptionKey("invalidKey123"); // Example invalid key
    }

    @When("I enter an invalid key for the chosen text encryption technique")
    public void i_enter_an_invalid_key_for_the_chosen_text_encryption_technique() {
        encryptionPage.enterTextEncryptionKey("invalidKey123"); // Example invalid key
    }

    @When("I click on the encrypt file button")
    public void i_click_on_the_encrypt_button() {
        encryptionPage.click(encryptionPage.submitFileEncryptionButton);
    }

    @When("I click on the encrypt text button")
    public void i_click_on_the_encrypt_text_button() {
        encryptionPage.click(encryptionPage.submitTextEncryptionButton);
    }

    @Then("I should get a pop up saying “Encryption key for Algorithm <selected algorithm> is not a valid key!” for file encryption")
    public void i_should_get_a_pop_up_saying_invalid_key() {
        webDriver.getElement(homePage.toastMsg)
            .getText()
            .contains("Encryption key for Algorithm " + fileEncryptionModel.algorithm + " is not a valid key!");
    }

    @Then("I should get a pop up saying “Encryption key for Algorithm <selected algorithm> is not a valid key!” for text encryption")
    public void i_should_get_a_pop_up_saying_invalid_key_text() {
        webDriver.getElement(homePage.toastMsg)
            .getText()
            .contains("Encryption key for Algorithm " + textEncryptionModel.algorithm + " is not a valid key!");
    }

    @When("I enter a valid key for the chosen text encryption technique")
    public void i_enter_a_valid_key_for_the_chosen_encryption_technique() {
        encryptionPage.enterTextEncryptionKey(textEncryptionModel.key); // Example valid key
    }

    
    @When("I enter a valid key for the chosen file encryption technique")
    public void i_enter_a_valid_key_for_the_chosen_file_encryption_technique() {
        encryptionPage.enterFileEncryptionKey(fileEncryptionModel.key); // Example valid key
    }

    @Then("the file output by the selected encryption technique, using the entered key is downloaded")
    public void file_output_by_selected_encryption_technique_is_downloaded() {
        try {
            Thread.sleep(2000); // Wait for download to complete
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        assertTextContentMatches(webDriver.getText(encryptionPage.fileEncryptionStatus), "Finished");
    }

    @When("I enter text to encrypt")
    public void i_enter_text_to_encrypt() {
        textEncryptionModel = TextEncryptionModel.builder()
            .plaintext("Sample text to encrypt") // Example text
            .algorithm("AES") // Default algorithm, can be changed
            .key("defaultKey") // Default key, can be changed
            .cipherText("") // Initially empty, will be filled after encryption
            .build();
        encryptionPage.enterTextToEncrypt(textEncryptionModel.plaintext);
    }

    // Scenario: Logged in user uses valid key during text encryption
    @Then("then ciphertext that has been encrypted with the chosen key and technique should be output")
    public void ciphertext_encrypted_with_chosen_key_and_technique_should_be_output() {
        assertTextContentMatches(webDriver.getElement(encryptionPage.textEncryptionOutput), textEncryptionModel.cipherText);
    }

    // Scenario: User copies contents of key field in encryption form
    @And("I am in the process of completing a text encryption form")
    public void i_am_in_the_process_of_completing_an_encryption_form() {
        textEncryptionModel = TextEncryptionModel.builder()
            .plaintext("Sample text to encrypt") // Example text
            .algorithm("AES") // Default algorithm, can be changed
            .key("defaultKey") // Default key, can be changed
            .cipherText("") // Initially empty, will be filled after encryption
            .build();
    }

    @Given("there is a value present in the text encryption key field")
    public void there_is_a_value_present_in_the_key_field() {
        encryptionPage.enterTextEncryptionRequest(textEncryptionModel);
    }

    @When("I press the copy text button")
    public void i_press_the_copy_button() {
        encryptionPage.copyTextEncryptionOutput();
    }

    @When("I press the copy button on the text encryption key field")
    public void i_press_the_copy_button_on_key_field() {
        encryptionPage.copyTextEncryptionKey(); // Assuming this method exists in EncryptionPage
    }

    @Then("the contents of the key field are present in my clipboard")
    public void contents_of_key_field_are_in_clipboard() {
        // String clipboardContent = webDriver.getClipboardContent();
        // assertTextContentMatches(clipboardContent, textEncryptionModel.key);
    }

    // Scenario: User copies contents of text encryption output
    @And("I have successfully completed the text encryption process")
    public void i_have_successfully_completed_text_encryption_process() {
        encryptionPage.submitTextEncryptionRequest(textEncryptionModel);
    }

    @When("I press the copy button on the ciphertext output field")
    public void i_press_the_copy_button_on_ciphertext_output_field() {
        // TODO: Implement copy button press on output
    }

    @Then("my clipboard contains the ciphertext")
    public void my_clipboard_contains_the_ciphertext() {
        // TODO: Assert clipboard contains ciphertext
    }

    // Scenario: User saves a key to their profile
    @When("I press the save key icon")
    public void i_press_the_save_key_icon() {
        // TODO: Implement save key icon press
    }

    @Then("the key is saved to my profile and available to be used on the decryption form")
    public void key_is_saved_to_profile_and_available_for_decryption() {
        // TODO: Assert key saved and available
    }

    // Scenario: User saves a blank key to their profile
    @Given("there is no value present in the key field")
    public void there_is_no_value_present_in_the_key_field() {
        // TODO: Ensure key field is blank
    }

    @Then("the key is not saved to my profile and an error message is shown")
    public void key_not_saved_and_error_message_shown() {
        // TODO: Assert key not saved and error shown
    }

    // Scenario: User auto-generates a key after selecting encryption technique
    @Given("I have selected any text encryption technique")
    public void i_have_selected_any_encryption_technique() {
        encryptionPage.selectTextEncryptionAlgorithm(textEncryptionModel.algorithm);
    }

    @When("I press the auto-generate text encryption key button")
    public void i_press_the_auto_generate_key_button() {
        encryptionPage.autoGenerateTextEncryptionKey(); // Assuming this method exists in EncryptionPage
    }

    @Then("valid key for the selected text encryption technique is generated in the key field")
    public void valid_key_for_selected_encryption_technique_generated_in_key_field() {
        assertIsValidKey(
            webDriver.getElement(encryptionPage.textEncryptionKeyInput)
        );
    }

    // Scenario: User auto-generates a key without having selected an encryption technique
    @Given("I have not selected an encryption technique")
    public void i_have_not_selected_an_encryption_technique() {
        // Do nothing, as no technique is selected
    }

    @Then("I am prompted with an error saying an encryption type must be selected")
    public void prompted_with_error_encryption_type_must_be_selected() {
        assertTextContentMatches(webDriver.getElement(homePage.toastMsg), "encryptionTechnique field is not selected");
    }
}
