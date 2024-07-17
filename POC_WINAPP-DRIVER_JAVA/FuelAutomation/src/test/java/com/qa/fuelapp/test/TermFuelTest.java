package com.qa.fuelapp.test;

import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;

import com.qa.fuelapp.base.FuelBase;
import com.qa.fuelapp.util.Objc;

public class TermFuelTest extends FuelBase {

	public Objc Objc;

	@BeforeClass
	public void setup() {
		OpenApp(prop.getProperty("winapppath"));
		init_driver();
	}

	@Test
	public void termFuel() {		
		Objc = new Objc(desktop_driver);
		Objc.Close().click();
	}
}
