package tests.stepDefinitions.FileUploadVisibility;

import java.io.File;

import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.testng.Assert;
import org.uranus.configuration.LoadProperties;
import org.uranus.data.UranusFaker;
import org.uranus.driver.UranusDriver;
import org.uranus.model.UserRegistrationModel;
import org.uranus.pages.AdminPanelPage;
import org.uranus.pages.HomePage;

import io.cucumber.java.AfterAll;
import io.cucumber.java.Before;
import io.cucumber.java.BeforeAll;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;

public class FileUploadVisibilitySteps {

    private static UranusDriver webDriver;
    private HomePage homePage;
    private AdminPanelPage adminPanelPage;

    private final String adminEmail = LoadProperties.env.getProperty("ADMIN_EMAIL");
    private final String adminPassword = LoadProperties.env.getProperty("ADMIN_PASSWORD");

    private UserRegistrationModel employeeUser = UranusFaker.getRandomEmployeeRegistration();
    private UserRegistrationModel regularUser = UranusFaker.getRandomUserRegistration();


    private static String testFileName = "png.png";
    private static String testFilePath;

    @BeforeAll
    public static void setup() {
        webDriver = UranusDriver.getInstance();
        webDriver.setup();
        String relativeEncryptedFilePath = "src/test/resources/unencrypted-test-data/png.png";
        File file = new File(relativeEncryptedFilePath);
        testFilePath = file.getAbsolutePath();
    }

    @AfterAll
    public static void teardown() {
        webDriver.teardown();
    }

    @Before
    public void refresh() {
        webDriver.refresh();
        homePage = new HomePage(webDriver);
        adminPanelPage = new AdminPanelPage(webDriver);
    }

    @Given("I am logged in as an admin")
    public void i_am_logged_in_as_an_admin() {
        homePage.login(adminEmail, adminPassword);
        homePage.closeToastMsg();
    }

    @When("I navigate to the resources upload section")
    public void i_navigate_to_the_resources_upload_section() {
        homePage.openAdminPanel();
        adminPanelPage.openResourcesTab();
    }

    @When("I upload the file")
    public void i_upload_the_file() {
        // Upload skipped due to system limit of 20 resources.
        //can be uncommented and works
        adminPanelPage.uploadFile(testFilePath);
        try {
            Thread.sleep(2000); // Wait for download to complete
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        homePage.clickUpload();
        homePage.closeToastMsg();
    }

    //assuming file has already been uploaded
    @Then("The file should be visible to admins and employees only")
    public void the_file_should_be_visible_to_admins_and_employees_only() {
        Assert.assertTrue(adminPanelPage.isFileVisible(testFileName), "Expected file to be visible to Admin.");

        logout();
        approveAccountEmployee();
        homePage.openResourcesMenu();
        Assert.assertTrue(adminPanelPage.isFileVisible(testFileName), "Expected file to be visible to Employee.");

        logout();

    }

    // ========= Scenario 2 ==========
    @Given("I log in as regular user")
    public void i_log_in_as_a_regular_user() {
        approveAccountUser();
        homePage.closeToastMsg();
    }

    @Then("The Resources tab should not be visible")
    public void the_resources_tab_should_not_be_visible() {
        Assert.assertFalse(isResourcesTabPresent(), "Resources tab should NOT be visible to regular users.");
    }


    //===========scenario 3=============
    @Given("I am signed in as an admin user")
    public void i_am_signed_in_as_an_admin_user() {
        logout();
        homePage.closeToastMsg();
        homePage.login(adminEmail, adminPassword);
        homePage.closeToastMsg();
    }

    @Given("I navigate to the resource section of the admin panel")
    public void i_navigate_to_the_resource_section_of_the_admin_panel() {
        homePage.openAdminPanel();
        adminPanelPage.openResourcesTab();
    }

    @Given("I click choose to upload a file")
    public void i_click_choose_to_upload_a_file() {
        // Upload skipped due to system limit of 20 resources.
        // This step is kept for consistency with the user story.
        //can be uncommented and works
        adminPanelPage.uploadFile(testFilePath);
        homePage.clickUpload();
    }

    @Then("the uploaded file is shown as a preview")
    public void the_uploaded_file_is_shown_as_a_preview() {
        boolean isPreviewDisplayed = adminPanelPage.isFileVisible(testFileName); // Check preview by filename
        Assert.assertTrue(isPreviewDisplayed, "Expected file preview to be visible after upload");
    }

    @When("I click the cancel button")
    public void i_click_the_cancel_button() {
        homePage.clickCancelUpload();
    }

    @Then("the staged file is removed from the preview")
    public void the_staged_file_is_removed_from_the_preview() {
        boolean isPreviewDisplayed = adminPanelPage.isFileVisible(testFileName);
        Assert.assertFalse(isPreviewDisplayed, "Expected file preview to be removed after cancel");
    }

    // ========== Helpers ==========

    private void loginAs(String email, String password, String role) {
        homePage.login(email, password);
        homePage.closeToastMsg();
        if (!"user".equalsIgnoreCase(role)) {
            openResourcesForRole(role);
        }
    }


    private void logout() {
        homePage.logout();
    }

    public void openResourcesForRole(String role) {
        if ("admin".equalsIgnoreCase(role)) {
            homePage.openAdminPanel();
            adminPanelPage.openResourcesTab();
        } else {
            clickResourcesNavLink();
        }
    }

    public void clickResourcesNavLink() {
        WebElement resourcesLink = homePage.findElement(By.cssSelector("a[href='#/resources']"));
        resourcesLink.click();
    }

    public boolean isResourcesTabPresent() {
        try {
            homePage.findElement(By.cssSelector("a[href='#/resources']"));
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public void approveButton() {
        try {
            Thread.sleep(2000); // Wait for download to complete
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        WebElement approve =  homePage.findElement(By.cssSelector("app-accounts .active .p-datatable-wrapper tbody tr:nth-child(1) td:nth-child(6) .approve"));
        approve.click();
    }

    public void approveAccountEmployee() {
        homePage.signUp(employeeUser);
        homePage.closeToastMsg();
        homePage.login(adminEmail, adminPassword);
        homePage.closeToastMsg();
        homePage.openAdminPanel();
        String fakerUserEmail = employeeUser.email;
        approveButton();
        homePage.logout();

        homePage.login(fakerUserEmail, employeeUser.password);
        homePage.closeToastMsg();
    }
    public void approveAccountUser() {
        homePage.signUp(regularUser);
        homePage.closeToastMsg();
        homePage.login(adminEmail, adminPassword);
        homePage.closeToastMsg();
        homePage.openAdminPanel();
        String fakerUserEmail = regularUser.email;
        approveButton();
        homePage.logout();
        homePage.login(fakerUserEmail, regularUser.password);
        homePage.closeToastMsg();
    }
}