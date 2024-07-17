package com.qa.winapp.test;

import org.openqa.selenium.By;
import org.testng.annotations.AfterSuite;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.BeforeSuite;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;
import org.testng.asserts.SoftAssert;
import com.qa.winapp.base.Base;
import com.qa.winapp.util.Obj;

public class Testcases extends Base {
	public SoftAssert softassert;
	public Obj Obj;

	@BeforeSuite
	public void invokeapps() {
		OpenApp(prop.getProperty("fuelpath"));
		OpenApp(prop.getProperty("winapppath"));
		OpenApp(prop.getProperty("pospath"));
	}

	@BeforeClass
	public void Setup() {
		init_driver();
		Obj = new Obj(pos_driver, desktop_driver);
		Obj.Login();
		softassert = new SoftAssert();
	}

	@Test(priority = 1)
	@Parameters({"Itemid_1","Itemid_2"})
	public void dry_trans(String Itemid_1, String Itemid_2) {
		Obj.additem(Itemid_1,Itemid_2);
		Obj.subtotalclick();
		String amount = Obj.gettenderamount().replaceAll("[$]", "");
		System.out.println(amount);
		softassert.assertEquals(amount.equals("8.50"), true);
		Obj.Cards().click();
		softassert.assertAll();
	}

	@Test(priority = 2)
	public void fuel_preset_trans() {
		Obj.fuelpreset("200");
		System.out.println(Obj.gettenderamount());
		String amount = Obj.gettenderamount().replaceAll("[$]", "");
		softassert.assertEquals(amount.equals("2.00"), true);
		Obj.Cards().click();
		softassert.assertAll();
	}

	@Test(priority = 3)
	public void mixed_preset_trans() {
		Obj.waitforElement("posdriver",By.xpath(Obj.objprop.getProperty("Itemupc")));
		Obj.additem("4602787","4602886");
		Obj.fuelpreset("200");
		System.out.println(Obj.gettenderamount());
		String amount = Obj.gettenderamount().replaceAll("[$]", "");
		softassert.assertEquals(amount.equals("10.50"), true);
		Obj.Cards().click();
		softassert.assertAll();
	}

	@Test(priority = 4)
	public void fuel_pak_trans() throws InterruptedException {
		OpenApp(prop.getProperty("fuellingpath"));
		Thread.sleep(15000);
		Obj.authorizefuel();	
		Thread.sleep(10000);
		Obj.Fuelpump().click();
		Obj.Fueltrans().click();
		Obj.waitforElement("posdriver", By.xpath(Obj.objprop.getProperty("Subtotal")));
		while (!Obj.Subtotal().isEnabled()) {
		}
		try {
			Thread.sleep(3000);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		Obj.subtotalclick();
		System.out.println(Obj.gettenderamount());
		Obj.Cards().click();
	}

	@Test(priority = 5)
	public void fuel_prepay_trans() {
		Obj.Fuelpump().click();
		Obj.fuelprepay("200");
		System.out.println(Obj.gettenderamount());
		String amount = Obj.gettenderamount().replaceAll("[$]", "");
		softassert.assertEquals(amount.equals("2.00"), true);
		Obj.Cards().click();
		OpenApp(prop.getProperty("fuellingpath"));
		softassert.assertAll();
	}
	
	@AfterSuite
	public void tearDown() {
		//Obj.ClosePOS();
		//OpenApp(prop.getProperty("termfuelpath"));
		Obj.pos_driver.quit();
		Obj.desktop_driver.quit();
	}
}
