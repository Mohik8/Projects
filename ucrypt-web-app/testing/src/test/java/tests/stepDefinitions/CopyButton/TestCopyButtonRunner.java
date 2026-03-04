package tests.stepDefinitions.CopyButton;

import io.cucumber.testng.AbstractTestNGCucumberTests;
import io.cucumber.testng.CucumberOptions;

@CucumberOptions(
        features = "src/test/java/tests/features/CopyButton.feature",
        glue = "tests.stepDefinitions.CopyButton",
        plugin = {"pretty", "html:target/cucumber-reports.html", "json:target/cucumber-reports.json"},
        monochrome = true
)
public class TestCopyButtonRunner extends AbstractTestNGCucumberTests {
    // No additional code needed
}
