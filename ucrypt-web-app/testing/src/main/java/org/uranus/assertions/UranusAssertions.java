package org.uranus.assertions;

import static org.testng.Assert.assertEquals;

import org.openqa.selenium.WebElement;

public class UranusAssertions {


    public static void assertTextContentMatches(WebElement element, String expectedText) {
        assertTextContentMatches(element.getText(), expectedText);
    }
    
    public static void assertTextContentMatches(String actualText, String expectedText) {
        assertEquals(actualText, expectedText.strip(), "Text content does not match. Expected: '" + expectedText + "', but found: '" + actualText + "'");
    }

    public static void assertIsValidKey(WebElement element) {
        assertIsValidKey(element.getText());
    }

    public static void assertIsValidKey(String actualText) {
        // Example regex for a valid key (16 to 32 alphanumeric characters)
        String regex = "^[a-zA-Z0-9]{16,32}$";
        if (!actualText.matches(regex)) {
            throw new AssertionError("Key is not valid. Expected format: " + regex + ", but found: '" + actualText + "'");
        }
    }

    public static void assertPasswordStrength(WebElement element, String expectedStrength) {
        String actualStrength = element.getAttribute("value");
        assertEquals(actualStrength, expectedStrength.strip(), "Password strength does not match. Expected: '" + expectedStrength + "', but found: '" + actualStrength + "'");
    }
}
