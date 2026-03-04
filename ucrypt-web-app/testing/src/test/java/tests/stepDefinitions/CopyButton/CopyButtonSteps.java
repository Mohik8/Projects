package tests.stepDefinitions.CopyButton;

import java.awt.Toolkit;
import java.awt.datatransfer.Clipboard;
import java.awt.datatransfer.DataFlavor;
import java.awt.datatransfer.StringSelection;

import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.testng.Assert;
import org.uranus.configuration.LoadProperties;
import org.uranus.driver.UranusDriver;
import org.uranus.pages.HomePage;

import io.cucumber.java.AfterAll;
import io.cucumber.java.Before;
import io.cucumber.java.BeforeAll;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;

public class CopyButtonSteps {

    private static UranusDriver webDriver;
    private HomePage homePage;


    String adminEmail = LoadProperties.env.getProperty("ADMIN_EMAIL");
    String adminPassword = LoadProperties.env.getProperty("ADMIN_PASSWORD");
    @BeforeAll
    public static void setup() {
        webDriver = UranusDriver.getInstance();
        webDriver.setup();
    }

    @AfterAll
    public static void teardown() {
        webDriver.teardown();
    }

    @Before
    public void init() {
        webDriver.refresh();
        homePage = new HomePage(webDriver);
    }

    //======scenario 1==========
    @Given("I am logged in as an admin and on the decryption page")
    public void i_am_logged_in_as_an_admin_and_on_the_decryption_page() {
        homePage.login(adminEmail, adminPassword);
        homePage.closeToastMsg();
        webDriver.webDriver.findElement(By.cssSelector("a#dropdownId")).click();
        webDriver.webDriver.findElement(By.xpath("//a[contains(text(),'Try Decrypt')]")).click();
    }

    @When("I enter a sample decryption key")
    public void i_enter_a_sample_decryption_key() {
        WebElement keyTextarea = webDriver.webDriver.findElement(By.cssSelector("textarea[formControlName='encryptionKeySelected']"));
        keyTextarea.clear();
        keyTextarea.sendKeys("dGVzdC1kZWNyeXB0aW9uLWtleQ=="); // Base64 of 'test-decryption-key'
    }

    @When("I click the copy key button")
    public void i_click_the_copy_key_button() {
        WebElement copyBtn = webDriver.webDriver.findElement(By.cssSelector("button svg"));
        copyBtn.click();
    }

    @Then("The clipboard should contain the decryption key")
    public void the_clipboard_should_contain_the_decryption_key() throws Exception {
        // NOTE: This uses AWT clipboard and works only if your test runner allows desktop access.
        Toolkit toolkit = Toolkit.getDefaultToolkit();
        String clipboardContent = (String) toolkit.getSystemClipboard().getData(DataFlavor.stringFlavor);
        Assert.assertEquals(clipboardContent.trim(), "dGVzdC1kZWNyeXB0aW9uLWtleQ==", "Clipboard does not contain expected key");

    }
    //============scenario 2===============
    @Given("I am logged in as an admin and on the encryption page")
    public void i_am_logged_in_as_an_admin_and_on_the_encryption_page() {

        webDriver.webDriver.findElement(By.cssSelector("a#dropdownId")).click();
        webDriver.webDriver.findElement(By.xpath("//a[contains(text(),'Encryption')]")).click();
    }

    @When("I enter a sample encryption key")
    public void i_enter_a_sample_encryption_key() {
        WebElement keyTextarea = webDriver.webDriver.findElement(By.cssSelector("textarea[formcontrolname='encryptionKey']"));
        keyTextarea.clear();
        keyTextarea.sendKeys("ZW5jcnlwdC1rZXktc2FtcGxl"); // Base64 of 'encrypt-key-sample'
    }

    @When("I click the encryption copy key button")
    public void i_click_the_encryption_copy_key_button() {
        WebElement copyBtn = webDriver.webDriver.findElement(By.cssSelector("svg"));
        copyBtn.click();
    }

    @Then("The clipboard should contain the encryption key")
    public void the_clipboard_should_contain_the_encryption_key() throws Exception {
        Toolkit toolkit = Toolkit.getDefaultToolkit();
        String clipboardContent = (String) toolkit.getSystemClipboard().getData(DataFlavor.stringFlavor);
        Assert.assertEquals(clipboardContent.trim(), "ZW5jcnlwdC1rZXktc2FtcGxl", "Clipboard does not contain expected encryption key");
    }
//==============scenario 3================
    @When("I clear the key field and click the copy button")
    public void i_clear_the_key_field_and_click_copy() {
    Toolkit toolkit = Toolkit.getDefaultToolkit();
    Clipboard clipboard = toolkit.getSystemClipboard();
    clipboard.setContents(new StringSelection(""), null);
    WebElement keyTextarea = webDriver.webDriver.findElement(By.cssSelector("textarea[formcontrolname='encryptionKey']")); // adjust if you're on decryption page
    keyTextarea.clear();
    WebElement copyBtn = webDriver.webDriver.findElement(By.cssSelector("svg"));
    copyBtn.click();
}

    @Then("The clipboard should be empty")
    public void the_clipboard_should_be_empty() throws Exception {
        Toolkit toolkit = Toolkit.getDefaultToolkit();
        String clipboardContent = (String) toolkit.getSystemClipboard().getData(DataFlavor.stringFlavor);
        Assert.assertTrue(clipboardContent.trim().isEmpty(), "Clipboard should be empty but contains: " + clipboardContent);
    }

}
