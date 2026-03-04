package org.uranus.driver;

import java.time.Duration;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.uranus.configuration.LoadProperties;

import io.github.bonigarcia.wdm.WebDriverManager;

public class UranusDriver {

    private static UranusDriver instance;
    public WebDriver webDriver;
    WebDriverWait webDriverWait;
    WebElement webElement;
    private boolean isSetup = false;

    private UranusDriver() {}

    public static synchronized UranusDriver getInstance() {
        if (instance == null) {
            instance = new UranusDriver();
        }
        return instance;
    }

    public synchronized void setup() {
        if (!isSetup) {
            WebDriverManager.chromedriver().setup();
            webDriver = new ChromeDriver();
            webDriver.navigate().to(LoadProperties.env.getProperty("URL"));
            webDriver.manage().window().maximize();
            isSetup = true;
        }
    }

    public void teardown() {
        if (webDriver != null) {
            webDriver.close();
            webDriver = null;
            isSetup = false;
        }
    }

    public void refresh() {
        if (webDriver != null) {
            webDriver.navigate().refresh();
        }
    }

    public void navigateToHome() {
        webDriver.navigate().to(LoadProperties.env.getProperty("URL"));
    }

    public WebElement getElement(By by) {
        webDriverWait = new WebDriverWait(webDriver, Duration.ofSeconds(30));
        webDriverWait.until(ExpectedConditions.refreshed(ExpectedConditions.visibilityOfElementLocated(by)));
        webElement = webDriver.findElement(by);
        webDriverWait.until(ExpectedConditions.refreshed(ExpectedConditions.visibilityOf(webElement)));
        return webElement;
    }

    public String getText(By by) {
        webDriverWait = new WebDriverWait(webDriver, Duration.ofSeconds(30));
        webDriverWait.until(ExpectedConditions.refreshed(ExpectedConditions.visibilityOfElementLocated(by)));
        webElement = webDriver.findElement(by);
        webDriverWait.until(ExpectedConditions.refreshed(ExpectedConditions.visibilityOf(webElement)));
        return webElement.getText();
    }

    //make this enter password into password field fucntion
    public String enterText(String password, By by) {
        webDriverWait = new WebDriverWait(webDriver, Duration.ofSeconds(30));
        webDriverWait.until(ExpectedConditions.refreshed(ExpectedConditions.visibilityOfElementLocated(by)));
        webElement = webDriver.findElement(by);
        webElement.clear();
        webElement.sendKeys(password);
        return webElement.getAttribute("value");
    }
}
