package tests.stepDefinitions.Decryption;

import io.cucumber.testng.AbstractTestNGCucumberTests;
import io.cucumber.testng.CucumberOptions;

@CucumberOptions(
        features = "src/test/java/tests/features/Decryption.feature",
        glue = "tests.stepDefinitions.Decryption",
        plugin = {"pretty", "html:target/cucumber-reports.html", "json:target/cucumber-reports.json"},
        monochrome = true
)
public class TestDecryptionRunner extends AbstractTestNGCucumberTests {
    // No additional code needed
}
