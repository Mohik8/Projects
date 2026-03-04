package tests.stepDefinitions.UserRegistration;

import io.cucumber.testng.AbstractTestNGCucumberTests;
import io.cucumber.testng.CucumberOptions;

@CucumberOptions(
        features = "src/test/java/tests/features/UserRegistration.feature",
        glue = "tests.stepDefinitions.UserRegistration",
        plugin = {"pretty", "html:target/cucumber-reports.html", "json:target/cucumber-reports.json"},
        monochrome = true
)
public class TestUserRegistrationRunner extends AbstractTestNGCucumberTests {
    // No additional code needed
}
