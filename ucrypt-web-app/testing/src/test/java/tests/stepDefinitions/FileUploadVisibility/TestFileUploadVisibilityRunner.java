package tests.stepDefinitions.FileUploadVisibility;

import io.cucumber.testng.AbstractTestNGCucumberTests;
import io.cucumber.testng.CucumberOptions;

@CucumberOptions(
        features = "src/test/java/tests/features/FileUploadVisibility.feature",
        glue = "tests.stepDefinitions.FileUploadVisibility",
        plugin = {"pretty", "html:target/cucumber-reports.html", "json:target/cucumber-reports.json"},
        monochrome = true
)
public class TestFileUploadVisibilityRunner extends AbstractTestNGCucumberTests {
    // No additional code needed
}
