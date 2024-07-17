package com.qa.fuelapp.base;

import java.awt.Desktop;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.net.ConnectException;
import java.net.Socket;
import java.net.URL;
import java.util.Properties;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.remote.DesiredCapabilities;
import io.appium.java_client.windows.WindowsDriver;

public class FuelBase {

	public WindowsDriver<WebElement> desktop_driver = null;
	public Properties prop;

	public FuelBase() {
		try {
			String proppath = new File(".").getCanonicalPath()
					+ "//src//main//java//com//qa//fuelapp//config//config.properties";

			prop = initializeprop(proppath);

		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	public Properties initializeprop(String filepath) {
		Properties prp = new Properties();
		try {
			FileInputStream fs = new FileInputStream(filepath);
			prp.load(fs);
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return prp;
	}

	public void OpenApp(String path) {
		File f = new File(path);
		Desktop desktop = Desktop.getDesktop();
		try {
			desktop.open(f);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	public void init_driver() {

		boolean connected = false;
		while (!connected) {			
			Socket s;
			try {
			   s=new Socket("127.0.0.1", 4723);
				connected = true;
				s.close();
			} catch (ConnectException e) {
			} catch (IOException e) {
				e.printStackTrace();
			}
		}

		String winapp_url = prop.getProperty("winappurl");
		DesiredCapabilities desktop_cap = new DesiredCapabilities();
		desktop_cap.setCapability("app", "Root");
		desktop_cap.setCapability("platformName", "Windows");
		desktop_cap.setCapability("deviceName", "WindowsPC");

		try {
			desktop_driver = new WindowsDriver<WebElement>(new URL(winapp_url), desktop_cap);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}