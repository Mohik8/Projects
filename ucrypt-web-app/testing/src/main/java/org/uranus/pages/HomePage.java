package org.uranus.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.uranus.driver.UranusDriver;
import org.uranus.model.UserRegistrationModel;

public class HomePage extends PageBase {
    protected WebDriver driver;

    public HomePage(WebDriver webDriver) {
        super(webDriver);
        this.driver = webDriver;
    }

    public HomePage(UranusDriver uranusDriver) {
        super(uranusDriver.webDriver);
        this.driver = uranusDriver.webDriver;
    }   

    // This defines a locators for a Elements in a webpage.
    By signUpBtn = By.cssSelector("#collapsibleNavId div a:first-child");
    By loginBtn = By.cssSelector(".btn-outline-secondary");
    By nameField = By.id("signUpName");
    By emailField = By.id("loginEmail");
    public By invalidEmailError = By.cssSelector("#login > div > app-sign-up-page > div > div.modal-body > form > div:nth-child(2) > div");
    //potentially will need to be public for future implementation
    public By passField = By.id("loginPassword");
    By confirmPassField = By.id("signUpConfirmPassword");
    By roleField = By.id("signUpRole");
    By signUpSubmitBtn = By.cssSelector("app-sign-up-page form .btn-submit");
   public By toastMsg=By.cssSelector(".p-toast-detail");
   public By closeToastMsg=By.cssSelector(".p-toast-icon-close");
   By emailLoginField=By.cssSelector("app-header #signUp app-login-page .auth-form #loginEmail");
   By passwordLoginField=By.cssSelector("app-header #signUp app-login-page .auth-form #loginPassword");
   By loginSubmitBtn=By.cssSelector("app-header #signUp app-login-page .auth-form button");
   By adminPanelModule=By.cssSelector("div #collapsibleNavId ul li:nth-child(8) a");
    public By profileDropdown = By.cssSelector("#collapsibleNavId>div>ul>li>a");
    public By profileDropdownLogoutLink = By.cssSelector("#collapsibleNavId > div > ul > li > div > a:nth-child(2)");
   By uploadOptionSelect = By.cssSelector(".p-fileupload-upload");
    By upload = By.cssSelector("p-button.p-element");
    By homePageLink = By.cssSelector("a.nav-link[href='#/index']");

    public By tryUcryptDropdown = By.cssSelector("#collapsibleNavId > ul > li.nav-item.dropdown.ng-star-inserted>a");
    public By tryUcryptDropdownEncryptionLink = By.cssSelector("#collapsibleNavId > ul > li.nav-item.dropdown.ng-star-inserted > div > a:nth-child(1)");
    public By tryUcryptDropdownDecryptionLink = By.cssSelector("#collapsibleNavId > ul > li.nav-item.dropdown.ng-star-inserted > div > a:nth-child(2)");    
    By resourcesMenu = By.cssSelector("a.nav-link[href='#/resources']");

    public void enterPassword(String password) {
        click(signUpBtn);
        type(nameField, "Test User");
        type(emailField, "test@example.com");
        type(passField, password);
    }

    public String getPasswordStrengthLabel() {
        // Adjust selector as needed to match your HTML
        WebElement label = driver.findElement(By.cssSelector(".progress ~ small.text-muted"));
        return label.getText().trim();
    }

    public String getPasswordStrengthBarColor() {
        // Adjust selector as needed to match your HTML
        WebElement bar = driver.findElement(By.cssSelector(".progress-bar"));
        String classAttr = bar.getAttribute("class");
        // Map class to color
        if (classAttr.contains("bg-danger")) return "red";
        if (classAttr.contains("bg-warning")) return "yellow";
        if (classAttr.contains("bg-success")) return "green";
        if (classAttr.contains("bg-info")) return "blue";
        return "unknown";
    }
    public void openResourcesMenu() {
        click(resourcesMenu);
    }
    //Method to log in a user with the provided information.
    public void login(String email, String password){
        click(loginBtn);
        type(emailLoginField,email);
        type(passwordLoginField,password);
        click(loginSubmitBtn);
    }

    public void openAdminPanel(){
        click(adminPanelModule);
    }

    public void closeToastMsg() {
        click(closeToastMsg);
    }

    public void openEncryptionPage() {
        click(tryUcryptDropdown);
        click(tryUcryptDropdownEncryptionLink);
    }

    public void openDecryptionPage() {
        click(tryUcryptDropdown);
        click(tryUcryptDropdownDecryptionLink);
    }
    public void openChoose(){
        click(uploadOptionSelect);
    }
    public void clickUpload(){
        click(upload);
    }
    public void goToHomePage() {
        click(homePageLink);
    }
    public void logout() {
        click(profileDropdown);
        click(profileDropdownLogoutLink);
    }

    public void clickCancelUpload() {
        WebElement cancelBtn = webDriver.findElement(By.xpath("//p-fileupload//button[.//span[text()='Cancel']]"));
        cancelBtn.click();
    }
    public void signUp(UserRegistrationModel user) {
        click(signUpBtn);
        type(nameField, user.name);
        type(emailField, user.email);
        type(passField, user.password);
        type(confirmPassField, user.confirmPassword);
        select(roleField, user.role);
        click(signUpSubmitBtn);
    }

}
