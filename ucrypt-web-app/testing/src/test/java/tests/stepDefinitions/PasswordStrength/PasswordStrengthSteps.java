package tests.stepDefinitions.PasswordStrength;


import static org.uranus.assertions.UranusAssertions.assertTextContentMatches;

import org.uranus.data.UranusFaker;
import org.uranus.driver.UranusDriver;
import org.uranus.model.UserRegistrationModel;
import org.uranus.pages.HomePage;

import io.cucumber.java.AfterAll;
import io.cucumber.java.Before;
import io.cucumber.java.BeforeAll;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;

// ...existing imports...

public class PasswordStrengthSteps {
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
    
    @Given("I am a new user on the sign up page for password strength")
    public void i_am_a_new_user_on_the_sign_up_page_for_password_strength() {
        // No action needed here, as the setup method initializes the HomePage
    }

    @When("I enter a weak password")
    public void i_enter_a_weak_password() {
        user.password = "123"; // Weak: less than 6 chars
        homePage.enterPassword(user.password);
    }

    @Then("I should be able to see that the password Strength bar is red, and says weak")
    public void i_should_see_weak_password_strength() {
        assertTextContentMatches(homePage.getPasswordStrengthLabel(), "Weak");
        assertTextContentMatches(homePage.getPasswordStrengthBarColor(), "red");
    }

    @When("I enter a Medium password")
    public void i_enter_a_medium_password() {
        user.password = "password1"; // Medium: 6-11 chars, no special/uppercase
        homePage.enterPassword(user.password);
    }

    @Then("I should be able to see that the password Strength bar is yellow, and says Medium")
    public void i_should_see_medium_password_strength() {
        assertTextContentMatches(homePage.getPasswordStrengthLabel(), "Medium");
        assertTextContentMatches(homePage.getPasswordStrengthBarColor(), "yellow");
    }

    @When("I enter a Strong password")
    public void i_enter_a_strong_password() {
        user.password = "longpassword12"; // Strong: >=12 chars, but not all criteria for super strong
        homePage.enterPassword(user.password);
    }

    @Then("I should be able to see that the password Strength bar is green, and says Strong")
    public void i_should_see_strong_password_strength() {
        assertTextContentMatches(homePage.getPasswordStrengthLabel(), "Strong");
        assertTextContentMatches(homePage.getPasswordStrengthBarColor(), "green");
    }

    @When("I enter a Super Strong password")
    public void i_enter_a_super_strong_password() {
        user.password = "Longpassword12!"; // Super Strong: >=12 chars, uppercase, number, special char
        homePage.enterPassword(user.password);
    }

    @Then("I should be able to see that the password Strength bar is blue, and says Super Strong")
    public void i_should_see_super_strong_password_strength() {
        assertTextContentMatches(homePage.getPasswordStrengthLabel(), "Super Strong");
        assertTextContentMatches(homePage.getPasswordStrengthBarColor(), "blue");
    }
}
