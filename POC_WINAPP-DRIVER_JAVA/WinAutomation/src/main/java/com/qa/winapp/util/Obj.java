package com.qa.winapp.util;

import java.io.File;
import java.io.IOException;
import java.util.Properties;
import java.util.concurrent.TimeUnit;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import com.qa.winapp.base.Base;

import io.appium.java_client.windows.WindowsDriver;

public class Obj {

	public WindowsDriver<WebElement> pos_driver;
	public WindowsDriver<WebElement> desktop_driver;
	public Properties objprop;
	public Base b;

	public Obj() {
		b = new Base();
		try {
			String objproppath = new File(".").getCanonicalPath()
					+ "//src//main//java//com//qa//winapp//config//ObjectRepository.properties";

			objprop = b.initializeprop(objproppath);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	public Obj(WindowsDriver<WebElement> pos_driver, WindowsDriver<WebElement> desktop_driver) {
		this();
		this.pos_driver = pos_driver;
		this.desktop_driver = desktop_driver;
		pos_driver.manage().timeouts().implicitlyWait(10, TimeUnit.SECONDS);
	}

	public void waitforElement(String driver, By locator) {
		if (driver.equals("posdriver")) {
			WebDriverWait wait = new WebDriverWait(pos_driver, 40);
			wait.until(ExpectedConditions.presenceOfElementLocated(locator));
		} else if (driver.equals("desktopdriver")) {
			WebDriverWait wait = new WebDriverWait(desktop_driver, 40);
			wait.until(ExpectedConditions.presenceOfElementLocated(locator));
		}
	}
	
	public void waitforElementenabled(String driver, By locator) {
		if (driver.equals("posdriver")) {
			WebDriverWait wait = new WebDriverWait(pos_driver, 40);
			wait.until(ExpectedConditions.presenceOfElementLocated(locator));
			wait.until(ExpectedConditions.elementToBeClickable(locator));

		} else if (driver.equals("desktopdriver")) {
			WebDriverWait wait = new WebDriverWait(desktop_driver, 40);
			wait.until(ExpectedConditions.presenceOfElementLocated(locator));
			wait.until(ExpectedConditions.elementToBeClickable(locator));
		}
	}

	public WebElement ts() {
		WebElement TS = pos_driver.findElementByXPath(objprop.getProperty("TS"));
		return TS;
	}

	public WebElement pwrd() {
		WebElement pwrd = pos_driver.findElementByXPath(objprop.getProperty("Pwrd"));
		return pwrd;
	}

	public WebElement OK() {
		WebElement OK = pos_driver.findElementByXPath(objprop.getProperty("OK"));
		return OK;
	}

	public WebElement Signin() {
		WebElement Signin = pos_driver.findElementByXPath(objprop.getProperty("Signin"));
		return Signin;
	}

	public WebElement Signout() {
		WebElement Signout = pos_driver.findElementByXPath(objprop.getProperty("Signout"));
		return Signout;
	}

	public WebElement Quit() {
		WebElement Quit = pos_driver.findElementByXPath(objprop.getProperty("Quit"));
		return Quit;
	}

	public WebElement Itemupc() {
		WebElement Itemupc = pos_driver.findElementByXPath(objprop.getProperty("Itemupc"));
		return Itemupc;
	}

	public WebElement Enteritemid() {
		WebElement Enteritemid = pos_driver.findElementByXPath(objprop.getProperty("Enteritemid"));
		return Enteritemid;
	}

	public WebElement Subtotal() {
		WebElement Subtotal = pos_driver.findElementByXPath(objprop.getProperty("Subtotal"));
		return Subtotal;
	}

	public WebElement Close() {
		WebElement Close = pos_driver.findElementByName(objprop.getProperty("Close"));
		return Close;
	}

	public WebElement Cards() {
		WebElement Cards = pos_driver.findElementByName(objprop.getProperty("Cards"));
		return Cards;
	}

	public WebElement Tenderamount() {
		WebElement Tenderamount = pos_driver.findElementByClassName(objprop.getProperty("Tenderamount"));
		return Tenderamount;
	}

	public WebElement Fuelpump() {
		WebElement Fuelpump = desktop_driver.findElementByXPath(objprop.getProperty("Fuelpump"));
		return Fuelpump;
	}

	public WebElement Fueltrans() {
		WebElement Fueltrans = desktop_driver.findElementByXPath(objprop.getProperty("Fueltrans"));
		return Fueltrans;		
	}
	
	public WebElement prepay()
	{
		WebElement prepay = desktop_driver.findElementByXPath(objprop.getProperty("prepay"));
		return prepay;
	}

	public WebElement ult98()
	{
		WebElement ult98 = desktop_driver.findElementByXPath(objprop.getProperty("ult98"));
		return ult98;
	}
	
	public WebElement ultdiesel()
	{
		WebElement ultdiesel = desktop_driver.findElementByXPath(objprop.getProperty("ultdiesel"));
		return ultdiesel;
	}
	
	
	public WebElement prepayamnt()
	{
		WebElement prepayamnt = desktop_driver.findElementByXPath(objprop.getProperty("prepayamnt"));
		return prepayamnt;
	}
	
	public WebElement Functionmenu()
	{
		WebElement Functionmenu = desktop_driver.findElementByXPath(objprop.getProperty("Functionmenu"));
		return Functionmenu;
	}
	
	public WebElement Yes()
	{
		WebElement Yes = desktop_driver.findElementByXPath(objprop.getProperty("Yes"));
		return Yes;
	}
	

    public void ClosePOS()
    {
    	Functionmenu().click();
    	Quit().click();
    	Yes().click();
    }
	
	
	public void Login() {
		ts().click();
		pwrd().sendKeys(b.prop.getProperty("password"));
		OK().click();
	}


	public void additem(String... Itemid) {
		
		for (String s : Itemid) {
			
			waitforElementenabled("posdriver", By.xpath(objprop.getProperty("Itemupc")));

			Itemupc().click();

			waitforElement("posdriver", By.xpath(objprop.getProperty("Enteritemid")));

			Enteritemid().sendKeys(s);
			OK().click();
			waitforElementenabled("posdriver", By.xpath(objprop.getProperty("Quantity")));
			waitforElement("posdriver", By.xpath(objprop.getProperty("Subtotal")));
			while (!Subtotal().isEnabled()) {
			}
			try {
				Thread.sleep(2000);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
	}

	public void subtotalclick(){
		Subtotal().click();
		Close().click();
	}

	public String gettenderamount() {
		waitforElement("posdriver", By.className(objprop.getProperty("Tenderamount")));
		return Tenderamount().getText();
	}

	public void authorizefuel() {
		waitforElement("desktopdriver", By.xpath(objprop.getProperty("Fuelpump")));
		Fuelpump().click();
	}
	
	public void fuelprepay(String amnt)
	{
		prepay().click();
		ultdiesel().click();
		waitforElement("posdriver",By.xpath(objprop.getProperty("prepayamnt")));
		prepayamnt().sendKeys(amnt);
		OK().click();
		waitforElement("posdriver", By.xpath(objprop.getProperty("Subtotal")));
		while (!Subtotal().isEnabled()) {
		}
		try {
			Thread.sleep(3000);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		subtotalclick();
	}
	
	public void fuelpreset(String amnt)
	{
		desktop_driver.findElementByXPath(objprop.getProperty("controls_1")).click();
		desktop_driver.findElementByXPath(objprop.getProperty("controls_2")).click();
		desktop_driver.findElementByXPath(objprop.getProperty("preset")).click();
		Fuelpump().click();
		waitforElement("posdriver",By.xpath(objprop.getProperty("prstpayamnt")));
		prepayamnt().sendKeys(amnt);
		OK().click();	
		desktop_driver.findElementByXPath(objprop.getProperty("controls_3")).click();
		b.OpenApp(b.prop.getProperty("fuellingpath"));
		try {
			Thread.sleep(25000);
		} catch (InterruptedException e1) {
			e1.printStackTrace();
		}
		Fuelpump().click();
		Fueltrans().click();
		waitforElement("posdriver", By.xpath(objprop.getProperty("Subtotal")));
		while (!Subtotal().isEnabled()) {
		}
		try {
			Thread.sleep(3000);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		subtotalclick();
	}

}