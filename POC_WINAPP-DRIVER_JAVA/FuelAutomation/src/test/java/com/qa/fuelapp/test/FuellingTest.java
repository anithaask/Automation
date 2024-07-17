package com.qa.fuelapp.test;

import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;
import com.qa.fuelapp.base.FuelBase;
import com.qa.fuelapp.util.Objc;

public class FuellingTest extends FuelBase {

	public Objc Objc;

	@BeforeClass
	public void setup() {
		OpenApp(prop.getProperty("winapppath"));
		init_driver();
	}

	@Test(priority = 1)
	public void fuelling() {
		Objc = new Objc(desktop_driver);
	    Objc.Gsimwindow().click();
		Objc.fuelwindow().click();
		Objc.doFuel();
	}

}
