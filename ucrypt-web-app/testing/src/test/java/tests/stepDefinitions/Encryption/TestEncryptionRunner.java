package tests.stepDefinitions.Encryption;

import io.cucumber.testng.AbstractTestNGCucumberTests;
import io.cucumber.testng.CucumberOptions;

@CucumberOptions(
        features = "src/test/java/tests/features/Encryption.feature",
        glue = "tests.stepDefinitions.Encryption",
        plugin = {"pretty", "html:target/cucumber-reports.html", "json:target/cucumber-reports.json"},
        monochrome = true
)
public class TestEncryptionRunner extends AbstractTestNGCucumberTests {
    // No additional code needed
}
