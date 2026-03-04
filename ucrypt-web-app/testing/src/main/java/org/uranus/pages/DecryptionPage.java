package org.uranus.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.Select;
import org.uranus.driver.UranusDriver;
import org.uranus.model.FileDecryptionModel;
import org.uranus.model.TextDecryptionModel;

public class DecryptionPage extends PageBase {
    public DecryptionPage(WebDriver webDriver) {
        super(webDriver);
    }

    public DecryptionPage(UranusDriver uranusDriver) {
        super(uranusDriver.webDriver);
    }

    By textInput = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(2) > form > div > div.mb-3 > textarea");
    By textDecryptionAlgorithmSelector = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(2) > form > div > div.row.px-3 > div:nth-child(1) > select");
    By textDecryptionKeyTypeSelector = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(2) > form > div > div.row.px-3 > div:nth-child(2) > select");
    By generateTextDecryptionKeyButton = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(2) > form > div > div.px-3 > div.pb-4 > label > button");
    public By textDecryptionKeyInput = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(2) > form > div > div:nth-child(3) > div > textarea");
    public By submitTextDecryptionButton = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(2) > form > div > div.d-flex.justify-content-between.align-items-center > div.text-right > button");
    public By textDecryptionOutput = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(2) > form > div > div.enc-group > textarea");
    public By textOutputCopyButton = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(2) > form > div > div.enc-group > div > button");
    public By noTextDecryptionAlgorithmSelectedError = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(2) > form > div > div.px-3 > div.mb-3 > div");
    public By textDecryptionKeyCopyButton = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(2) > form > div > div.px-3 > div.pb-4 > div > div.enc-key-options > button:nth-child(1)");



    By fileUploadInput = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(1) > form > div.upload-card > div.card-body > div.upload-div > p-fileupload");
    By fileDecryptionAlgorithmSelector = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(1) > form > div > div.card-body > div > div:nth-child(2) > div.p-3 > div:nth-child(1) > select");
    By fileDecryptionKeyTypeSelector = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(1) > form > div > div.card-body > div > div:nth-child(2) > div.row.p-3 > div:nth-child(2) > select");
    public By fileDecryptionKeyInput = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(1) > form > div > div.card-body > div > div:nth-child(2) > div.mb-3 > div > textarea");
    By generateFileDecryptionKeyButton = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(1) > form > div > div.card-body > div > div:nth-child(2) > div.p-3 > div:nth-child(2) > label > button");
    public By submitFileDecryptionButton = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(1) > form > div > div.card-body > div > div:nth-child(2) > div.text-right > button");
    By fileDecryptionOutput = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(1) > form > div.enc-group > textarea");
    By fileOutputCopyButton = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(1) > form > div.enc-group > div > button");
    public By fileDecryptionStatus = By.cssSelector("body > app-root > app-layout > div > app-decryption > div > div > div > div:nth-child(1) > form > div > div.card-body > div > div.p-3.d-flex.align-items-center.justify-content-between.border-bottom > span.status");

    public void selectFileDecryptionAlgorithm(String algorithm) {
        Select dropdown = new Select(webDriver.findElement(fileDecryptionAlgorithmSelector));
        dropdown.selectByVisibleText(algorithm);
    }

    public void selectFileDecryptionKeyType(String keyType) {
        Select dropdown = new Select(webDriver.findElement(fileDecryptionKeyTypeSelector));
        dropdown.selectByVisibleText(keyType);
    }

    public void selectTextDecryptionKeyType(String keyType) {
        Select dropdown = new Select(webDriver.findElement(textDecryptionKeyTypeSelector));
        dropdown.selectByVisibleText(keyType);
    }

    public void enterTextDecryptionRequest(TextDecryptionModel requestModel) {
        enterTextToDecrypt(requestModel.ciphertext);
        selectTextDecryptionAlgorithm(requestModel.algorithm);
        enterTextDecryptionKey(requestModel.key);
    }

    public void submitTextDecryptionRequest(TextDecryptionModel requestModel) {
        enterTextDecryptionRequest(requestModel);
        click(submitTextDecryptionButton);
    }

    public void submitTextDecryptionRequest() {
        click(submitTextDecryptionButton);
    }

    public void uploadFile(String filePath) {
        By fileInput = By.cssSelector("input[type='file']");
        webDriver.findElement(fileInput).sendKeys(filePath);
    }
    public void copyTextDecryptionKey() {
        click(textDecryptionKeyCopyButton);
    }

    public void enterFileDecryptionKey(String key) {
        type(fileDecryptionKeyInput, key);
    }

    public void submitFileDecryption() {
        click(submitFileDecryptionButton);
    }

    public void enterFileDecryptionRequest(FileDecryptionModel requestModel) {
        uploadFile(requestModel.filePath);
        selectFileDecryptionAlgorithm(requestModel.algorithm);
        enterFileDecryptionKey(requestModel.key);
    }

    public void submitFileDecryptionRequest(FileDecryptionModel requestModel) {
        enterFileDecryptionRequest(requestModel);
        click(submitFileDecryptionButton);
    }

    public void enterTextToDecrypt(String text) {
        type(textInput, text);
    }

    public void selectTextDecryptionAlgorithm(String algorithm) {
        Select dropdown = new Select(webDriver.findElement(textDecryptionAlgorithmSelector));
        dropdown.selectByVisibleText(algorithm);
    }

    public void enterTextDecryptionKey(String key) {
        type(textDecryptionKeyInput, key);
    }

    public void submitTextDecryption() {
        click(submitTextDecryptionButton);
    }

    public void copyTextDecryptionOutput() {
        click(textOutputCopyButton);
    }

    public void copyFileDecryptionOutput() {
        click(fileOutputCopyButton);
    }

    public void autoGenerateTextDecryptionKey() {
        click(generateTextDecryptionKeyButton);
    }

    public void autoGenerateFileDecryptionKey() {
        click(generateFileDecryptionKeyButton);
    }
}
