package org.uranus.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.Select;
import org.uranus.driver.UranusDriver;
import org.uranus.model.FileEncryptionRequestModel;
import org.uranus.model.TextEncryptionModel;

// <div _ngcontent-vca-c64="" class="col-md-6"><form _ngcontent-vca-c64="" novalidate="" class="ng-untouched ng-pristine ng-invalid"><h5 _ngcontent-vca-c64="" class="title"><img _ngcontent-vca-c64="" src="./assets/images/icons/upload.svg" alt=""> Upload File </h5><div _ngcontent-vca-c64="" class="upload-card"><div _ngcontent-vca-c64="" class="card-header fs-18"> Choose any file with max size 50 MB </div><div _ngcontent-vca-c64="" class="card-body"><div _ngcontent-vca-c64="" class="upload-div ng-star-inserted"><p-fileupload _ngcontent-vca-c64="" chooselabel="Browse" class="p-element"><div class="p-fileupload p-fileupload-advanced p-component ng-star-inserted"><div class="p-fileupload-buttonbar"><span pripple="" tabindex="0" class="p-ripple p-element p-button p-component p-fileupload-choose"><input type="file" accept="undefined" title=""><span class="pi pi-plus p-button-icon p-button-icon-left"></span><span class="p-button-label">Browse</span></span><!----><!----><!----></div><div class="p-fileupload-content"><!----><p-messages class="p-element ng-tns-c50-34 ng-star-inserted"><div role="alert" class="p-messages p-component ng-tns-c50-34"><!----><!----><!----><!----></div></p-messages><!----><!----></div></div><!----><!----></p-fileupload></div><!----><!----><!----></div></div></form></div>

public class EncryptionPage extends PageBase {
    
    public EncryptionPage(WebDriver webDriver) {
        super(webDriver);
    }

    public EncryptionPage(UranusDriver uranusDriver) {
        super(uranusDriver.webDriver);
    }
    
    By textInput = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(2) > form > div > div.mb-3 > textarea");
    By textEncryptionAlgorithmSelector = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(2) > form > div > div.px-3 > div.mb-3 > select");
    By generateTextDecryptionKeyButton = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(2) > form > div > div.px-3 > div.pb-4 > label > button");
    public By textEncryptionKeyInput = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(2) > form > div > div.px-3 > div.pb-4 > div > textarea");
    public By submitTextEncryptionButton = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(2) > form > div > div.d-flex.justify-content-between.align-items-center > div.text-right > button");
    public By textEncryptionOutput = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(2) > form > div > div.enc-group > textarea");
    public By textOutputCopyButton = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(2) > form > div > div.enc-group > div > button");
    public By noTextEncryptionAlgorithmSelectedError = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(2) > form > div > div.px-3 > div.mb-3 > div");
    public By textEncryptionKeyCopyButton = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(2) > form > div > div.px-3 > div.pb-4 > div > div.enc-key-options > button:nth-child(1)");
    public By saveTextEncryptionKeyButton = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(2) > form > div > div.px-3 > div.pb-4 > div > div.enc-key-options > button:nth-child(2)");

    By fileUploadInput = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(1) > form > div.upload-card > div.card-body > div.upload-div > p-fileupload");
    By fileEncryptionAlgorithmSelector = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(1) > form > div > div.card-body > div > div:nth-child(2) > div.p-3 > div:nth-child(1) > select");
    public By fileEncryptionKeyInput = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(1) > form > div > div.card-body > div > div:nth-child(2) > div.p-3 > div:nth-child(2) > div > textarea");
    By generateFileEncryptionKeyButton = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(1) > form > div > div.card-body > div > div:nth-child(2) > div.p-3 > div:nth-child(2) > label > button");
    public By submitFileEncryptionButton = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(1) > form > div > div.card-body > div > div:nth-child(2) > div.text-right > button");
    By fileEncryptionOutput = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(1) > form > div.enc-group > textarea");
    By fileOutputCopyButton = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(1) > form > div.enc-group > div > button");
    public By fileEncryptionStatus = By.cssSelector("body > app-root > app-layout > div > app-encryption > div > div > div > div:nth-child(1) > form > div > div.card-body > div > div.p-3.d-flex.align-items-center.justify-content-between.border-bottom > span.status");

    public void selectFileEncryptionAlgorithm(String algorithm) {
        Select dropdown = new Select(webDriver.findElement(fileEncryptionAlgorithmSelector));
        dropdown.selectByVisibleText(algorithm);
    }

    public void enterTextEncryptionRequest(TextEncryptionModel requestModel) {
        enterTextToEncrypt(requestModel.plaintext);
        selectTextEncryptionAlgorithm(requestModel.algorithm);
        enterTextEncryptionKey(requestModel.key);
    }

    public void submitTextEncryptionRequest(TextEncryptionModel requestModel) {
        enterTextEncryptionRequest(requestModel);
        click(submitTextEncryptionButton);
    }

    public void submitTextEncryptionRequest() {
        click(submitTextEncryptionButton);
    }

    public void uploadFile(String filePath) {
        By fileInput = By.cssSelector("input[type='file']");
        webDriver.findElement(fileInput).sendKeys(filePath);
    }
    public void copyTextEncryptionKey() {
        click(textEncryptionKeyCopyButton);
    }


    public void enterFileEncryptionKey(String key) {
        type(fileEncryptionKeyInput, key);
    }

    public void submitFileEncryption() {
        click(submitFileEncryptionButton);
    }

    public void enterFileEncryptionRequest(FileEncryptionRequestModel requestModel) {
        uploadFile(requestModel.filePath);
        selectFileEncryptionAlgorithm(requestModel.algorithm);
        enterFileEncryptionKey(requestModel.key);
    }

    public void submitFileEncryptionRequest(FileEncryptionRequestModel requestModel) {
        enterFileEncryptionRequest(requestModel);
        click(submitFileEncryptionButton);
    }


    public void enterTextToEncrypt(String text) {
        type(textInput, text);
    }

    public void selectTextEncryptionAlgorithm(String algorithm) {
        Select dropdown = new Select(webDriver.findElement(textEncryptionAlgorithmSelector));
        dropdown.selectByVisibleText(algorithm);
    }

    public void enterTextEncryptionKey(String key) {
        type(textEncryptionKeyInput, key);
    }

    public void submitTextEncryption() {
        click(submitTextEncryptionButton);
    }

    public void copyTextEncryptionOutput() {
        click(textOutputCopyButton);
    }

    public void copyFileEncryptionOutput() {
        click(fileOutputCopyButton);
    }

    public void autoGenerateTextEncryptionKey() {
        click(generateTextDecryptionKeyButton);
    }

    public void autoGenerateFileEncryptionKey() {
        click(generateFileEncryptionKeyButton);
    }
}
