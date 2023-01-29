package Alpha;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.Keys;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

public class livechat {

	public static void main(String[] args) throws InterruptedException {
		
		System.setProperty("webdriver.chrome.driver", "/home/allincall/Music/Automation Testing/chromedriver");
		WebDriver driver= new ChromeDriver();
		driver.manage().window().maximize();
			
// Chat with an expert in chatbot -------------------------------------------------------------------------------------------
 	     
			Thread.sleep(2000);	
			String winHandleBefore1 = driver.getWindowHandle();
			driver.get("https://easychat-uat.allincall.in/chat/bots/");
			Thread.sleep(2000);
	        for(String winHandle : driver.getWindowHandles())
	        {
	            driver.switchTo().window(winHandle);
	        }
	        driver.switchTo().window(winHandleBefore1);	
			
	        Thread.sleep(2000);
			driver.findElement(By.xpath("//*[@id=\"index-banner\"]/div/div/div[2]/div/div/div/div[2]/form/div[1]/label")).click(); 
			driver.findElement(By.id("username")).sendKeys("admin");        //login page                       
			driver.findElement(By.id("password")).sendKeys("adminadmin");
			driver.findElement(By.xpath("//*[@id=\"login_btn\"]")).click();          //submit button to login
			
			Thread.sleep(2000);	
			String winHandleBefore11 = driver.getWindowHandle();
		    driver.findElement(By.xpath("//*[@id=\"main-console-container\"]/div/div[1]/div[2]/div/div[7]/div/div/a[5]")).click(); //open chat window
			Thread.sleep(2000);
	        for(String winHandle : driver.getWindowHandles())
	        {
	            driver.switchTo().window(winHandle);
	        }
	   	
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"allincall-popup\"]")).click(); //Click on bot
		
		Thread.sleep(2000);		
		JavascriptExecutor js=(JavascriptExecutor)driver;  
		js.executeScript("document.getElementById('allincall-chat-box').contentWindow.document.getElementById('user_input').focus()"); //Click on Ask something 
		Thread.sleep(2000); 
		js.executeScript("document.getElementById('allincall-chat-box').contentWindow.document.getElementById('user_input').value='Chat with an expert'");
		Thread.sleep(2000);
		js.executeScript("document.getElementById('allincall-chat-box').contentWindow.document.dispatchEvent(new KeyboardEvent('keyup', {'keyCode':13, 'which':13}));");
        
		Thread.sleep(2000);
		js.executeScript("document.getElementById('allincall-chat-box').contentWindow.document.getElementById('easychat-customer-name').focus()"); //Name
		Thread.sleep(2000);
		js.executeScript("document.getElementById('allincall-chat-box').contentWindow.document.getElementById('easychat-customer-name').value='rahul'");
		
		Thread.sleep(2000);
		js.executeScript("document.getElementById('allincall-chat-box').contentWindow.document.getElementById('easychat-customer-email').focus()"); //Email
		Thread.sleep(2000);
		js.executeScript("document.getElementById('allincall-chat-box').contentWindow.document.getElementById('easychat-customer-email').value='Kartik@gmail.com'");
		
		Thread.sleep(2000);
		js.executeScript("document.getElementById('allincall-chat-box').contentWindow.document.getElementById('easychat-customer-phone').focus()"); //Phone
		Thread.sleep(2000);
		js.executeScript("document.getElementById('allincall-chat-box').contentWindow.document.getElementById('easychat-customer-phone').value='9844567456'");
		
		Thread.sleep(2000);
		js.executeScript("document.getElementById('allincall-chat-box').contentWindow.document.getElementById(\"customer_info_form_div\").children[5].children[0].click()"); //Submit button
		Thread.sleep(2000);
		driver.switchTo().window(winHandleBefore11);	
		
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"home-button\"]")).click(); //Home button 
		driver.findElement(By.xpath("/html/body/div[2]/div[2]/div/div[3]/a/div/div[2]")).click(); //Click on live chat manager 
		
		Thread.sleep(5000);
		WebElement element52 = driver.findElement(By.xpath("//*[@id=\"buildchatbot-sidenav\"]/a")); // Click on chat 
		JavascriptExecutor jse52 = (JavascriptExecutor)driver;
		jse52.executeScript("arguments[0].click();", element52); 
		
		Thread.sleep(5000);
		js.executeScript("document.getElementsByTagName('iframe')[0].contentWindow.document.getElementById('query').value='how can I help you?'");
		Thread.sleep(2000);
		js.executeScript("document.getElementsByTagName('iframe')[0].contentWindow.document.getElementById('submit-response').click()");
		
		Thread.sleep(2000);
		for(String winHandle : driver.getWindowHandles())
        {
            driver.switchTo().window(winHandle);
        }
		
		Thread.sleep(2000);		
		JavascriptExecutor js7=(JavascriptExecutor)driver;  
		js.executeScript("document.getElementById('allincall-chat-box').contentWindow.document.getElementById('user_input').focus()"); //Click on Ask something 
		Thread.sleep(2000); 
		js.executeScript("document.getElementById('allincall-chat-box').contentWindow.document.getElementById('user_input').value='What is Fb?'");
		Thread.sleep(2000);
		js.executeScript("document.getElementById('allincall-chat-box').contentWindow.document.dispatchEvent(new KeyboardEvent('keyup', {'keyCode':13, 'which':13}));");
		
		Thread.sleep(2000);
		driver.switchTo().window(winHandleBefore11);	
		
		Thread.sleep(2000);
		js.executeScript("document.getElementsByTagName('iframe')[0].contentWindow.document.getElementsByTagName('a')[0].click()"); //End chat
		Thread.sleep(2000);
		js.executeScript("document.getElementsByTagName('iframe')[0].contentWindow.document.getElementsByTagName('a')[7].click()");
		
		Thread.sleep(2000);
		for(String winHandle : driver.getWindowHandles())
        {
            driver.switchTo().window(winHandle);
        }
		
		//AGENT side ---------------------------------------------------------------------------------------------

/*			
		driver.get("https://easychat-uat.allincall.in");
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"index-banner\"]/div/div/div[2]/div/div/div/div[2]/form/div[1]/label")).click(); 
		driver.findElement(By.id("username")).sendKeys("admin");        //login page                       
		driver.findElement(By.id("password")).sendKeys("adminadmin");
		driver.findElement(By.xpath("//*[@id=\"login_btn\"]")).click();          //submit button to login
		
		Thread.sleep(2000);
		driver.findElement(By.xpath("/html/body/div[1]/nav/div/div/div[1]/a[2]")).click(); //Click on home button 
		driver.findElement(By.xpath("/html/body/div[2]/div[2]/div/div[2]/a/div/div[1]/img")).click(); //Click on live chat manager
				
				driver.findElement(By.xpath("/html/body/div[2]/div[1]/div/div/a[2]")).click(); //Click on Archived chats button 
				Thread.sleep(2000);
				driver.findElement(By.xpath("//*[@id=\"buildchatbot-sidenav\"]/a[1]")).click(); //Click on first chat 
							
				Thread.sleep(2000);
				driver.findElement(By.xpath("/html/body/div[2]/div[1]/div/div/a[3]")).click(); //Click on Canned response button
				Thread.sleep(2000);
				driver.findElement(By.xpath("/html/body/div[2]/div[2]/div/div[2]/div[1]/a")).click(); //Click on new canned 
				Thread.sleep(2000);
				driver.findElement(By.xpath("//*[@id=\"canned-title\"]")).click(); // Click on title 
				driver.findElement(By.xpath("//*[@id=\"canned-title\"]")).sendKeys("Company"); 
				Thread.sleep(2000);
				driver.findElement(By.xpath("//*[@id=\"canned-keyword\"]")).click(); //Click on keyboard 
				driver.findElement(By.xpath("//*[@id=\"canned-keyword\"]")).sendKeys("sup");
				Thread.sleep(2000);
				driver.findElement(By.xpath("//*[@id=\"canned-response\"]")).click(); //Click on response 
				driver.findElement(By.xpath("//*[@id=\"canned-response\"]")).sendKeys("How can i help you?");
				Thread.sleep(2000);
				driver.findElement(By.xpath("//*[@id=\"canned-status\"]")).click(); //Status 
				Thread.sleep(2000);
				driver.findElement(By.xpath("//*[@id=\"modal-add-canned-response\"]/div[2]/a[2]")).click(); //Click on cancel button 
			//	driver.findElement(By.xpath("//*[@id=\"modal-add-canned-response\"]/div[2]/a[1]")).click(); //Click on create canned response 
						
*/									
		
		
//Manager side	------------------------------------------------------------------------------------------------------
		driver.get("https://easychat-uat.allincall.in/chat/bots/");
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"index-banner\"]/div/div/div[2]/div/div/div/div[2]/form/div[1]/label")).click(); 
		driver.findElement(By.id("username")).sendKeys("admin1");        //login page                       
		driver.findElement(By.id("password")).sendKeys("adminadmin");
		driver.findElement(By.xpath("//*[@id=\"login_btn\"]")).click();          //submit button to login
		
		Thread.sleep(2000);
		driver.findElement(By.xpath("/html/body/div[1]/nav/div/div/div[1]/a[2]")).click(); //Click on home button 
		driver.findElement(By.xpath("/html/body/div[2]/div[2]/div/div[2]/a/div/div[1]/img")).click(); //Click on live chat manager 
/*		
		
	//New button	
		Thread.sleep(2000);
		driver.findElement(By.xpath("/html/body/div[1]/nav/div/div/div[3]/div[3]/li/a")).click(); //New button 
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"new-agent-first-name\"]")).click(); //Click on First name 
		driver.findElement(By.xpath("//*[@id=\"new-agent-first-name\"]")).sendKeys("akshay");
		
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"new-agent-last-name\"]")).click(); //Click on last name 
		driver.findElement(By.xpath("//*[@id=\"new-agent-last-name\"]")).sendKeys("singh");
		
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"new-agent-phone\"]")).click(); //Click on phone number
		driver.findElement(By.xpath("//*[@id=\"new-agent-phone\"]")).sendKeys("9877665434");
		
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"new-agent-email\"]")).click(); //Click on email
		driver.findElement(By.xpath("//*[@id=\"new-agent-email\"]")).sendKeys("karan123@gmail.com");
		
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"new-agent-username\"]")).click(); //Click on Username 
		driver.findElement(By.xpath("//*[@id=\"new-agent-username\"]")).sendKeys("akshay");
		
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"livechat-password\"]")).click(); //Click on password 
		driver.findElement(By.xpath("//*[@id=\"livechat-password\"]")).sendKeys("123456");
		
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"modal-create-agent\"]/div[2]/a[1]")).click(); //Click on create new 
	//	driver.findElement(By.xpath("//*[@id=\"modal-create-agent\"]/div[2]/a[2]")).click(); //Click on cancel button
	 
	 
	
	//Customer list Tab
	
		Thread.sleep(2000);
		driver.findElement(By.xpath("/html/body/div[2]/div[1]/div/div/a[1]")).click(); //Click on customer list tab
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"table-agent-details_filter\"]/label/input")).click(); //Click on search
		driver.findElement(By.xpath("//*[@id=\"table-agent-details_filter\"]/label/input")).sendKeys("thor");
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"table-agent-details\"]/tbody/tr[1]/td[1]/a")).click(); //Click on one customer 
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"customer-details-102\"]/div/div/h4/center/a")).click(); //Click on close button 
	
*/		
    //Manage Agent Tab 
/*	
		Thread.sleep(2000);
		driver.findElement(By.xpath("/html/body/div[2]/div[1]/div/div/a[2]")).click(); //click on Manage Agent tab 
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"btn-delete-agent\"]")).click(); //Delete agent 
		Thread.sleep(2000);
		
		JavascriptExecutor js11=(JavascriptExecutor)driver; 
		js11.executeScript("document.getElementById('allincall-chat-box').contentWindow.document.getElementsByClassName('waves-effect waves-green btn red darken-3 white-text modal-close right')[2].click()");
		
		
//		WebElement element32 = driver.findElement(By.xpath("//*[@id=\"modal-delete-agent-21\"]/div[2]/a[2]")); //Cancel button
//		JavascriptExecutor jse32 = (JavascriptExecutor)driver;
//		jse32.executeScript("arguments[0].click();", element32);
		
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"table-agent-details_filter\"]/label/input")).click(); //Click on search 
		driver.findElement(By.xpath("//*[@id=\"table-agent-details_filter\"]/label/input")).sendKeys("raj");
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"table-agent-details\"]/tbody/tr/td[1]/a")).click(); //Click on one agent 
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"agent-details-22\"]/div/div/div[1]/h4/center/a")).click(); //Click on close button
		
		
		
	//Audit trail 
	
		Thread.sleep(2000);
		driver.findElement(By.xpath("/html/body/div[2]/div[1]/div/div/a[3]")).click(); //Click on audit trail 
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"select-agent-username\"]")).click(); //Click on search and select by agent username 
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"select-agent-username\"]/option[2]")).click(); //Select agent 
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"reportrange\"]")).click(); //Pick an interval 
		Thread.sleep(2000);
		driver.findElement(By.xpath("/html/body/div[4]/div[1]/ul/li[4]")).click(); //last 30 days 
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"submit-filter\"]")).click(); //Click on submit button
		
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"audit-trail-body\"]/tr[1]/td[1]/a")).click(); //Click on agent	
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"agent-details-143\"]/div/div/div[1]/h4/center/a")).click(); //Close agent details 
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"audit-trail-body\"]/tr[1]/td[2]/a")).click(); //Click on customer id 
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"customer-details-144\"]/div/div/h4/center/a")).click();  //Close Customer details
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"audit-trail-body\"]/tr[1]/td[3]/a")).click(); //Click on chat history
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"chat-details-144\"]/div/div/h4/center/a")).click(); //Close chat history
		
	
	//Settings
		
		//General settings
		
		Thread.sleep(2000);
		driver.findElement(By.xpath("/html/body/div[2]/div[1]/div/div/a[4]")).click(); //Click on settings 
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"customer-count-id\"]")).click(); //Click on enter the max number of customers
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"customer-count-id\"]")).clear();
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"customer-count-id\"]")).sendKeys("100");
		Thread.sleep(2000);
		WebElement element67 = driver.findElement(By.id("save-admin-settings")); //Click on save changes
		JavascriptExecutor jse67 = (JavascriptExecutor)driver;
		jse67.executeScript("arguments[0].click();", element67);  
		
		//Canned Response 
		
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"buildlivechat-sidenav\"]/a[2]")).click(); //Click on canned resposne button
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"main-manager-console-container\"]/div/div/div[2]/div[1]/a")).click(); //New button 
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"canned-title\"]")).click(); // Title 
		driver.findElement(By.xpath("//*[@id=\"canned-title\"]")).sendKeys("welcome");
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"canned-keyword\"]")).click(); //Keyword 
		driver.findElement(By.xpath("//*[@id=\"canned-keyword\"]")).sendKeys("Hi");
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"canned-response\"]")).click(); //Response 
		driver.findElement(By.xpath("//*[@id=\"canned-response\"]")).sendKeys("How Can I help you?");
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"modal-add-canned-response\"]/div[2]/a[1]")).click(); //Create canned resposne 
		
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"canned-response-table_filter\"]/label/input")).click(); //Search 
		driver.findElement(By.xpath("//*[@id=\"canned-response-table_filter\"]/label/input")).sendKeys("abc");
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"canned-response-body\"]/tr/td[6]/a[1]")).click(); //edit button
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"canned-keyword-10\"]")).clear(); //Keyword edit
		driver.findElement(By.xpath("//*[@id=\"canned-keyword-10\"]")).sendKeys("mouse");
		Thread.sleep(2000);
	//	driver.findElement(By.xpath("//*[@id=\"modal-edit-canned-response-10\"]/div[2]/a[1]")).click(); //Save changes 
		driver.findElement(By.xpath("//*[@id=\"modal-edit-canned-response-10\"]/div[2]/a[2]")).click(); //Cancel button
		
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"canned-response-body\"]/tr/td[6]/a[2]")).click(); //Delete button 
		Thread.sleep(2000);
		driver.findElement(By.xpath("//*[@id=\"modal-delete-canned-response-10\"]/div[2]/a[2]")).click(); //Cancel button pop up
	//	Thread.sleep(2000);
	//	driver.findElement(By.xpath("//*[@id=\"modal-delete-canned-response-10\"]/div[2]/a[1]")).click(); //delete button pop up
	
		
*/		
		
		
		
		
		
		
		
	}

}