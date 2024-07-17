package com.qa.fuelapp.util;

import java.io.File;
import java.io.IOException;
import java.util.Properties;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import com.qa.fuelapp.base.FuelBase;
import io.appium.java_client.windows.WindowsDriver;

public class Objc {

	public WindowsDriver<WebElement> desktop_driver;
	public Properties objprop;
	public FuelBase b;

	public Objc() {
		b = new FuelBase();
		try {
			String objproppath = new File(".").getCanonicalPath()
					+ "//src//main//java//com//qa//fuelapp//config//ObjectRepository.properties";
			objprop = b.initializeprop(objproppath);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	public Objc(WindowsDriver<WebElement> desktop_driver) {
		this();
		this.desktop_driver = desktop_driver;
	}

	public void waitforElement(By locator) {
		WebDriverWait wait = new WebDriverWait(desktop_driver, 30);
		wait.until(ExpectedConditions.presenceOfElementLocated(locator));
	}

	public WebElement OK() {
		WebElement OK = desktop_driver.findElementByName(objprop.getProperty("OK"));
		return OK;
	}

	public WebElement Fuelnozzle() {
		WebElement fuelnozzle = desktop_driver.findElementByXPath(objprop.getProperty("fuelnozzle"));
		return fuelnozzle;
	}

	public WebElement Slider() {
		WebElement Slider = desktop_driver.findElementByXPath(objprop.getProperty("slider"));
		return Slider;
	}

	public WebElement Close() {
		WebElement Close = desktop_driver.findElementByXPath(objprop.getProperty("Close"));
		return Close;
	}

	public void doFuel()
	{
		waitforElement(By.xpath(objprop.getProperty("fuelnozzle")));
		Fuelnozzle().click();
		waitforElement(By.xpath(objprop.getProperty("slider")));
		Slider().click();
		Slider().click();
		try {
			Thread.sleep(3000);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		Fuelnozzle().click();
	}
	
	public WebElement fuelwindow()
	{
		WebElement fuelwindow = desktop_driver.findElementByXPath(objprop.getProperty("fuelwindow"));
		return fuelwindow;
	}
	
	public WebElement Gsimwindow()
	{
		WebElement Gsimwindow = desktop_driver.findElementByXPath(objprop.getProperty("Gsimwindow"));
		return Gsimwindow;
	}
}
