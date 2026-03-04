package tests.stepDefinitions.UserRegistration;


import static org.uranus.assertions.UranusAssertions.assertTextContentMatches;

import org.uranus.configuration.LoadProperties;
import org.uranus.data.UranusFaker;
import org.uranus.driver.UranusDriver;
import org.uranus.model.UserRegistrationModel;
import org.uranus.pages.AdminPanelPage;
import org.uranus.pages.HomePage;

import io.cucumber.java.After;
import io.cucumber.java.AfterAll;
import io.cucumber.java.Before;
import io.cucumber.java.BeforeAll;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;

public class UserRegistrationSteps {

    private HomePage homePage;
    private UserRegistrationModel user;
    private static UranusDriver webDriver;

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
    public void refresh() {
        webDriver.refresh();
        user = UranusFaker.getRandomUserRegistration();
        homePage = new HomePage(webDriver);
    }

    @After
    public void afterScenario() {
        webDriver.refresh();
    }

    @Given("I am a new user on the sign up page")
    public void i_am_a_new_user_on_the_sign_up_page() {
        // No action needed here, as the setup method initializes the HomePage
    }

    @When("I enter all mandatory registration details correctly")
    public void i_enter_all_mandatory_registration_details_correctly() {
        homePage.signUp(user);
    }

    @Then("I should be able to register successfully and receive a confirmation email")
    public void i_should_be_able_to_register_successfully_and_receive_a_confirmation_email() {
        assertTextContentMatches(webDriver.getText(homePage.toastMsg), "Registerd successfully, please wait for admin approval to login!");
        homePage.closeToastMsg();
    }

    @When("I enter weak password in the password field")
    public void i_enter_weak_password_in_the_password_field() {
        user.password = "123"; // Example of a weak password
        user.confirmPassword = user.password; // Ensure confirm password matches
    }

    @Then("I should get an error message showing the number of characters needed for the password for successful sign up")
    public void i_should_get_an_error_message_showing_the_number_of_characters_needed_for_the_password() {
        // Functionality being tested here is not implemented yet
    }

    @When("I enter password in confirm password field that doesn’t match with password entered in password field")
    public void i_enter_password_in_confirm_password_field_that_doesnt_match() {
        user.confirmPassword = "differentPassword"; // Example of a mismatch
        homePage.signUp(user);
    }

    @Then("I should get an error message indicating that the passwords do not match")
    public void i_should_get_an_error_message_indicating_that_the_passwords_do_not_match() {
        assertTextContentMatches(webDriver.getText(homePage.toastMsg), "Password Confirmation is not valid");
        homePage.closeToastMsg();
    }

    @When("I enter an invalid email address that matches email address format \\(email@domain.com\\) with all other required field correctly")
    public void i_enter_an_invalid_email_address_that_matches_format() {
        user.email = "doesnotexist@doesnotexist.abc"; // Example of an invalid email format
    }

    @Then("I should get an error message saying that this email doesn’t exist")
    public void i_should_get_an_error_message_saying_that_this_email_doesnt_exist() {
        // Functionality being tested here is not implemented yet
    }

    @When("I enter an invalid email address that doesn’t matche email address format \\(email@domain.com\\) with all other required field correctly")
    public void i_enter_an_invalid_email_address_that_doesnt_match_format() {
        user.email = "invalid-email-format"; // Example of an invalid email format
        homePage.signUp(user);
    }

    @Then("I should get an error message saying that this email provided is invalid")
    public void i_should_get_an_error_message_saying_that_this_email_provided_is_invalid() {
        assertTextContentMatches(webDriver.getText(homePage.invalidEmailError), "Please enter a valid email!");
    }

    @Given("A new user has signed up")
    public void a_new_user_has_signed_up() {
        homePage.signUp(user);
        assertTextContentMatches(webDriver.getText(homePage.toastMsg), "Registerd successfully, please wait for admin approval to login!");
        homePage.closeToastMsg();
    }

    @When("An administrator logs in and navigates to the admin panel")
    public void an_administrator_logs_in_and_navigates_to_the_admin_panel() {
        homePage.login(LoadProperties.env.getProperty("ADMIN_EMAIL"), LoadProperties.env.getProperty("ADMIN_PASSWORD"));
        homePage.closeToastMsg();

        homePage.openAdminPanel();
    }

    @Then("The admin can locate the users registration request and accept it")
    public void the_administrator_approves_the_new_user_registration() {
        AdminPanelPage adminPanelPage = new AdminPanelPage(webDriver);
        adminPanelPage.approveSignUpRequest(user);

        webDriver.refresh();
        homePage.logout();
    }

    @Then("The user should be able to log in")
    public void the_user_should_be_able_to_log_in() {
        homePage.login(user.email, user.password);
        assertTextContentMatches(webDriver.getElement(homePage.toastMsg), "Successfully logged in!");
        homePage.closeToastMsg();
    }

    @Then("I should not be able to login if the admin has not approved me")
    public void i_should_not_be_able_to_login_if_the_admin_has_not_approved_me() {
        homePage.login(user.email, user.password);
        assertTextContentMatches(webDriver.getElement(homePage.toastMsg), "Invalid credentials!");
        homePage.closeToastMsg();
    }
}