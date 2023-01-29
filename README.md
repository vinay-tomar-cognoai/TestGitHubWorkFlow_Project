
# EasyChat
<blockquote>Full Stack Customer Relation Management Solution.</blockquote>

**`EasyChat Production`** | **`EasyChat Dev`** |
------------------- | ------------------- |
[console](https://app.getcogno.ai) | [console](https://easychat-dev.allincall.in) |

## Release Notes
- **v6.4.2**

- **Chatbot**
  - Features
	- Whatsapp Catalog feature
	- CSAT report in daily mailers
	- UX improvements in existing themes (Form widget & Additional improvements)
	- Revamp Edit Intent Page with Drag and Drop functionality (Bugs and improvements)
	- Do not translate keyword feature

  - Bugs Fixed
	- [Functionality issue] - [Daily mailer] - to be confirmed once mail received 
	- [Functionality issue] - [Bot page] - Getting an error 500 when opening any bot.
	- Search bar is hidden when searching intent in auto pop-up settings
	- UI Issue - Whatsapp channel buttons 
	- UI - The dropdown is opening above the select option
	- Horizontal Scroll bar appears unintuitively on the console
	- Equitas message history problem
	- In Arabic  'Powered by CognoAI' is not aligned properly
	- [Funcational issue]-[Suggest variation] - Too many toast messages come at once when clicking on suggest a variation.
	- [Functionality issue] - [ Combine analytics] - Message analytics or user analytics data of the last day is not coming in the graph when applying a filter for a web channel.
	- The down arrow on chatbot should adjust if no sticky buttons
	- [Functional Iusse] - [Cron Job issue] - The Cron job is not working it has to be triggered again and again.
	- Suggestions not working if Initiate conversation after welcome message is added
	- Video response error
	- Extra space after "Welcome to" on the landing page of the chatbot theme 3
	- Index page issues
	- User chat history UI issue
	- Build Bot crashing
	- [Ui Issue] - [Average session duration - analytics] - Timing is coming in second line.
	- Child intent name/ Recommendations - ui error
	- Initial question bug
	- [UI Issue] - [ Initial questions] - If intent names are big it's going outside the bot screen from right side.
	- Suggestions list not working when deployed on client websites
	- [UI issue]-[intent suggetion]- Ui issue is coming in suggetion because it's coming with horizontal scroll if intent name has without space.
	- Theme 4 > FAQ issue
	- The user language selected is Hindi after having LiveChat conversation, when the chat is disposed the language of the user changes to English again
	- [Functionality Issue] - [ Table response] - HTML tags are coming in the table when entering bold/italic/underline text.
	- [UI issue] - [Chat History] - Radio buttons are missing from the WhatsApp menu in the chat history.
	- Unanswered query affected by the campaign
	- CSAT Feedback form toggle is enable but haven't configure it. So, it is not getting submitted 
	- [Functionality issue] - [Bot share] - When sharing access to LiveChat and TMS by clicking on edit button in any user id.
	- Manu text is not changing in detected language.
	- [Functionality Issue] [When user change langugae and call the response widget, the Response widget appears in English under message history]
	- Remove the Viber Beta tag from CSAT filter.
	- [Functionality issue] When user change bot name from setting > Bot name and change langugae when using the bot , the bot name should get changed in particular language
	- Welcome Message Functionalities
	- Edit Intent page not loading - Giving 502 Error
	- Phonetic Typing / spell-checker issue
	- Webpage chat window errors
	- Auto detection issue
	- [Functionality issue] When user change language at time of CSAT response user get navigate to home page
	- When user click and hold mic button in android the blue frame appear on 'powered by'
	- [Functionality issue]- Not able to disable configure langauge settings toggle
	- Welcome banner name missing
	- [Functional issue]- Global filter Combined analytics
	- [Functionality issue] - [Export multilingual intent excel] - 500 error is coming when trying to export.
	- search issue while searching intents
	- [UI issue] - [ Form Widget]- The drop-down options are hiding behind the menu.
	- Message History Filter > Unanswered Query Filter Issue
	- [Functional issue] - [Edit intent page] - The page is getting unresponsive when opening any intent from manage intent.
	- Conversion analytics table data issue
	- [Functionality issue]- 500 error when opened multiple tabs
	- [Functionality issue] - [Dynamic form widget] - The options set for drop-down, checkbox and radio buttons from the front-end removes when integrate form API.
	- Font change not applying on theme 4
	- [Functioanality issue] - [ Data modal] - Data modal page is getting unresponsive and hangs when searching any long text in the search field.
	- [Error Handling] After user uploads any doc, contact or location on WhatsApp, proper error handling needs to be done
	- [Functionality issue] - [Menu icon] - The menu icon is not showing in the bot.
	- [UI issue] - [Data Model page] - Inside the search field get another box.
	- UI issue in console while adding initial questions
	- Bot accuracy count mismatches when calculated by formula and tallied with the value
	- [Functional issue] - [ Whatsapp channel language] - sometimes hindi language comes when any query.
	- CSS is defined in script tag
	- publish and update api documentation in console for latest version
	- Count of flows in Most frequent questions and Intent wise chart flow mismatches
	- Unable to save Tree
	- The input field UI distorts when LiveChat is connected(Mic, send, attachment) Theme-1
	- Suggestion List not working
	- Mic issue in safari and iOS device
	- Traffic sources optmisation
	- Autodetection for languages not working as expected
	- [Funcationality bug] - [Set time interval for Session Expiration] - Set time interval for Session Expiration is not working.
	- Minimise button not present in theme 3 when bot opened in mobile
	- File attachment error: After uploading the file unable to retrieve it from the POST Processor.
	- [Funcational issue] - [TMS flow in whatsApp]- User name is showing None when user send multiple images in attachment.
	- New URL Validator for JavaScript/Frontend
	- Google.com, www.google.com not being taken as valid URLs for card link
	- Dot extention file should be allowed across all products
	- Profile name is not valid bug not valid error message or valid correction
	- Channel feedback flow for chatbot is not working
	- [UI Issue] - [welcome banner] - The hand icon should not come when hovering over images.
	- [Functioanal issue] - [CSAT in WhatsApp language] -When after changing the language after talking in any one language, the CSAT is being triggered in the first language itself.
	- [Funcational issue] - [ CSAT ] - CSAT is still triggering when users start live chat after the conversation with bot and in message the bot name should show according to the bot name.
	- Spell check is not working when adding wrong words and train which don't have variations.
	- We are not able to crawl https://beta.sbimf.com/ in the Esearch functionality
	- Translation issues
	- [UI issue ] - [ welcome banner] - The welcome banner is overlapping with each other when loading first time in all the themes.
	- Conversion Percentage is more then 100%
	- [Functionality Issue]Timer not appear for resent code under forgat password ]
	- [Suggestions] Sticky Button 'Menu' option UI issue
	- [UX issue] - [ Bot manager console] - Bot manager console bots page should have text.
	- Bot Share > Show tag below the bot owner's username as "Bot Owner"
	- [SUGGESTION] -- Reducing width of chatbot box
	- Leveraging NLU at Node level rather than string match use-case
	- View welcome banner
	- Theme 4 Intent Icon Scroller
	- [Facebook] Quick recommendations should appear in card format.
	- Check all cronjobs where iterator could be used in EasyChatApp
	- Include WhatsApp Block Spam Analytics in Analytics External APIs
	- Console level optimizations
	- update oauthlib version to 3.2.1
	- [SUGGESTION] -- We should add tooltips everywhere we're using any word which might not be very intuitive to the end user
	- [SUGGESTION] -- Making language adding in chatbot more intuitive

  - Bugs Remaining
	- Speak out bot response library female voice issue in certain browser
	- Create Bot with Excel Page Bugs
	- [Functional issue]-[intent name multilingual]-  Some intents are not giving a response and always come in did you mean? suggestions.


- **Cobrowsing**
  - Features
    - Supervisor/Admin should be able to mark agents online/offline

  - Bugs Fixed
    - Sound notification not working on IOS devices
	- Through APIs user is able to put spaces in password and save
	- In calendar "Add Working Timing" modal incorrect error message when Days not select in dropdown
	- Admin console when user save blank "Number of times 'Connect with an agent' auto pop up after in-activity" column then error message come wrong
	- Admin console "No agent permit meeting toast" details not saved
	- In admin side mailer setting user is able to put special character in profile section
 	- Error message comes wrong when a user tries to save support document name by putting full stop
	- Sometimes unattended leads not export when set custom range
	- Admin side in Email setting user is able to set profile without selecting frequency of mail
	- Error messsage come wrong in agent end session modal
	- Error message come incorrect when user try to save empty maxmium leads count column
	- Error message come incorrect when user try to save empty "Auto assign timer (In secs)" count 
	- User is able to put "0" in "Auto end session timer (In mins) " model by copy-paste method
	- Error message come incorrect when user try to save empty "Number of times 'Connect with an agent' auto pop up after in-activity" count
	- Error message come incorrect when user try to save empty "Set in-activity time interval (In secs)" count
	- Error message comes incorrect when user try to save zero in "Greeting bubble auto pop up timer (In secs)" count 
	- User is able to save blank "Auto end session message" textbox
	- Toggle "Session Inactivity (In mins)" error toast message text comes incorrect
	- Invited agent session join chat bubble does not appear more than once
	- Agent connect message comes twice in case of session transfer
	- User is able to put special charachters in "Enable pre-defined remarks with buttons" text box
	- User is able to put zero or multiple numbers and save the "Reconnecting window timer (In mins)" timer box
	- Agent Connect Message doesn't get displayed on the agent's end in Inbound, GDL and Search Lead
	- Multiple toast message updates
	- Pre-defined remarks "Optional" toggle doesn't work
	- CSS Override when invoking CJS on https://www.paybima.com/health-insurance
	- Unattended lead count come wrong in mail
	- Agent console Microphone
	- Error message for From Date or To Date  missing is incorrect in all export modal present in admin, admin ally and supervisor console
	- Suggestion for error messages for all filter modal
	- Remove checkbox's from admin ally and supervisor's side
	- While exporting support history data in Custom Range, if no data is present we shouldn't allow downloading blank file
	- Admin side, in outbound anlytics "Service Request Analytics" data not loading
	- Support history session data for agents created via admin ally/supervisor is not available to admin
	- Fix : Session Started by parameter inside session details
	- Applying Inbound filter inside support history displays droplink sessions as well in addition to inbound sessions
	- Admin side, In calendar option edit model "cancel button" is not similar to other console mode
	- Admin side in outbound analytics button alignment is not correct
	- Most of the times in livechat of cobrowse user is not able to upload files
	- In generate drop link form blue color comes on text box
	- Admin side, calendar day color is not matches with theme color
	- Admin side in canned response section search logo is not correct align
	- UI issue in request in queue table
	- Supervisor and agent created through admin ally is not able to login
	- Move the wikipedia image used to check network speed to static.allincall.in
	- In "Active customer" section "No data available in table" text is not correctly align
	- Masking Fields sometimes doesn't work
	- Screen Capture is not masking the DIV ID's
	- When doing cobrowsing on LinkedIn login page, taking a screenshot doesn't render all parts of the page in the screenshot properly
	- Freeze Email ID field for users when trying to edit them 

  - Bugs Remaining
	- Unique Customers' wrong data log in mailer analytics and console analytics

- **Campaign**
  - Features
    - Need an additional parameter to map and filter in the Campaign Report API
	- Auto delete invalid numbers from the audience batch
	
  - Bugs Fixed
    - Need to set the user language for every session in the Campaign message
	- Functionality issue - document type template -  Untitled document name is coming on the end-user side.
	- Need to enable CSV file format for batch and template upload in Campaign
	- Incorrect calculation of success ratio on analytics
	- Changing multi-select to single dropdown for WhatsApp campaign report feature
	- The average % of successful campaign messages is not calculated correctly
	- Optimise the whatsapp campaign details page as it takes a lot of time to load with heavy data
	- Implementation of SQS in Campaign
	- Apply Cap limit on Bulk APIs
	- UI issue - When user Hover the cursor on overview page and  campaign reports page the button have flickering issues
	- Phone number audience number format validation which Excel sheets changes automatically
	- user should allow to add phone number without '+' sign before country code
	- When user open Campaign overview page leave for sometime, After revisiting If user opens any model user not able to click or move forward
	- Error in the report email for 0 or no data available
	- Functionality Issue - Incorrect result appear under Analytics
	- Cache the API key generated from whatsapp and use it instead of creating new key everytime
	- Creating a separate Service for updating the analytics for the Campaign in RBL
	- Future Date should be non selectable for custom filter under campaign overview page
	- UI issue - For campaigns which have single audience tooltip not appear properly for Recipient ID
	- Update the webhook for the new number for whatsapp campaign
	- For campaign that are in progress, the unauthorised page appears when clicked on scheduling calendar button

  - Bugs Remaining
	- When special characters are added in batch file name it does not download


- **LiveChat**
  - Features
    - Extension - Peak Hours Analytics - Updating to Bubble Chart
    - Same day console (NPS, etc) data download. More reports enabled through Kafka
    - CSAT score LiveChat export file: Common file for all information that includes CSAT Score

  - Bugs Fixed
    - [functional issue]-[active status of agent not reflected on admin console when agent logged in the first time.]
    - [Functional Issue]-[Email channel duration]-Email chat duration is incorrect
    - Updating password for Whatsapp Webhook
    - [Functional issue]-[Daily interaction data in the export report is not in correct format]
    - For past data of daily interaction reports need to be changed to the new format
    - Profile section not getting loaded first time
    - [Functional Issue]-Not able to save canned response after editing canned reponse.
    - [Functional issue]-[Reports]-[reports of last day exported as empty file.]
    - [Error Handling]-[Proper error text should be visible for selecting Bot]
    - [Functional Issue]-[Export]-When 2nd time a user clicks on the export button the date range "Today" is selected by default but the email id field is not visible
    - [Functional error]-[error messages should be separate for Description and Autoresponse in calendar]
    - [Functional Issue] - [Offline Chats event not triggered through channels apart from Web]
    - [functional issue]-[Whatsapp]-[Thumbnails of attachments not visible in chat history]
    - [Functional issue]-[Telegram]-[Thumbnails of attachment not visible in chat history]
    - [Functional issue]-[agent console]-[message with attachment still visible even agent cancel and reopen attachment modal]
    - [Functional issue]-[Android]-[Livechat session not ended even agent reports customer for blacklisted keyword]
    - [Functional issue]-[Telegram]-[If the agent copy-pastes a long paragraph and sends it to a customer then it is not received by the customer]
    - [Functional Issue]-[URL issues on Livechat Analytics page]
    - [Functional Issue]-Link sent by agent is recieved with <a> tag at bot end
    - [Functional Issue]-Link sent by agent is not clickable at bot side
    - [Functional Issue]-[multiline chat message ]- When agent enter multiline message in chat and refresh the page, then the multiline message showing <br> tag in that message.
    - [Functional issue]-[system message of warning visible on customer bot]
    - [Functional Issue] - [On End Chat Session, system message not sent to end customer]
    - [Functional issue]-[Cobrowsing session status visible ongoing in cobrowsing session history even session and chat is ended]
    - [Functional Issue]-[reply privately]- In chat history, if the admin or supervisor reply privately using special characters then special characters are not displayed properly
    - [Functional Issue]-In Arabic language error message for Invalid file is displayed in English
    - [Functional Issue]-[Reply privately]-When admin or supervisor send document having special characters in the filename then an error message is not displayed for filename having special characters
    - [Functional issue]-[Channels]-[Send Co-browsing request button should be disabled where Co-browsing is not supported]
    - [Functional Issue]-[System messages]- In chat history, system messages are displayed multiple times
    - [UI issue] - [ Chat bot history in livechat] - The same message is divided by a dollar but it's showing in livechat history with the dollar sign.
    - [Functional Issue]-In the Arabic language inactivity message is displayed in English
    - [Functional Issue]- Able to sent attachment more than 5 MB in size in whatsapp
    - [Functional Issue]-Customer send multiple attachments at a time but agent is receiving only one attachment
    - Code Refactoring for Mailer Analytics File Path
    - [Functional issue]-[Initial questions not coming after welcome message]
    - [Functional issue]-[Welcome message did not appear when chat ended due to inactivity.]
    - Agent console Microphone
    - [Functional Issue]-When a customer raises a request and refreshes the bot before getting connected to an agent then the agent connect timer gets hidden and the end chat button is visible on the bot even if the agent is not connected
    - [Functional Issue]-[Email channel duration]-Email chat duration is incorrect
    - [Functional Issue]-In the email conversation "Due to inactivity chat has ended" message is visible in chat thumbnail
    - [Functional Issue] - [Optimisation for Agent not ready report]
    - [Functional issue]-[Combined Analytics data loading issue]
    - Disabling Local DB in LiveChat

  - Bugs Remaining
    - [Functional Issue]-[Session Inactivity]- Many times session getting end to due inactivity, even when the Session inactivity toggle is turned off
    - X customer's chat reflected on y customer's console when connected with the same agent.
    - [Functional Issue]-Chat ended due to inactivity even when the auto chat disposal is disabled and even though the agent is able to send messages

- **v6.4.1**

- **ChatBot**
  - Features
    - Languages based analytics over mail
	- Spell Checker issue(addition/removal of wrong words)
	- Language Fine-tuning for WhatsApp Channel page
	- UX improvements in existing themes (Bot response & response widgets)
	- Bold/Italic/Links/Bullet points/Link issue in all channels
	- Revamp Edit Intent Page with Drag and Drop functionality

  - Bugs Fixed
    - [Functionality issue] - [ Facebook channel message count] - The intent response is counting as an Ananswerd query.
	- [Functionality issue] - [ Intent level feedback ] - intent level feedback coming for chat with an expert intent in WhatsApp.
	- [Functionality issue]-[Change language response and bot response]-[All channels]
	- [Functioanlity issue] - [Enable Input TextField	] - Input text filed is not coming for livechat.
	- [Functionality issue] Telegram - Welcome message not appearing
	- WhatsApp CSAT ping even when LiveChat is connected
	- [Functionality improvement]-[When user tries to select the same language again]-[Disclaimer modal]
	- [Error Handling] After user uploads any doc, contact or location on WhatsApp, proper error handling needs to be done
	- Incorrect loading of words from word dictionary
	- [Functionality issue]-[Welcome,Authentication,Failure message formatting issue]
	- 'Deploy Link' is saving even with invalid url and spaces
	- Even though email is not saved profile object is saved
	- [Functional issue] - [Speak out bot response] - When we separate a response from a dollar into several responses, the speaker speaks the dollar as a single response.
	- [UI issue] - [Message history] - The text overlapping with other text when send query Without space.

  - Bugs Remaining
	- [Emoji bot response issue]-[Emojis not present iin bot response in dfferent languages]
	- [Functionality issue]- [ Attachment widget] - UI issue coming when user clicks on the cross on uploading attachment.
	- [Funcational issue] - [TMS flow in whatsApp]- User name is showing None when user send multiple images in attachment.
	- [Funcationality bug] - [Set time interval for Session Expiration] - Set time interval for Session Expiration is not working
	- [Emoji bot response issue]-[Emojis not present iin bot response in dfferent languages]
	- Whatsapp bot response recommendations issue
	- [Funcational issue] - [ CSAT ] - CSAT is still triggering when users start live chat after the conversation with bot and in message the bot name should show according to the bot name.
	- [Functionality Issue] - [ Table response] - HTML tags are coming in the table when entering bold/italic/underline text.
	

- **Cobrowsing**
  - Features
    - Agent creation limitation from supervisor ends in Cobrowsing (default=2)
	- Redirection in outbound proxy cobrowsing (partially tested)
	- Support history and analytics in outbound proxy cobrowsing (yet to be tested)
	- Cross domain masking in outbound proxy cobrowsing (yet to be tested)
	- URLs on which lead should be converted in outbound proxy cobrowsing (yet to be tested)
	- Domain whitelisting in outbound proxy cobrowsing (yet to be tested)
	- URLs on which cobrowsing should be blocked in outbound proxy cobrowsing (yet to be tested)

  - Bugs Fixed
    - [Ui issue]-[Admin side, "Change logo" it should not be present in console setting ]
	- [Ui issue]-[Admin side, in go live date section calendar date selection issue]
	- [Ui issue]-[In "show floating button even after the lead is generated" button tool tip should contain "co-browsing" in sentence]
	- Document title is not correct
	- Support Agent left status not getting reflected in the Livechat window
	- [Functional issue]-[User is able to save blank "Auto end session message" textbox ]
	- [Functional issue]-[Admin console when user save blank "Number of times exit intent should pop up" column then error message come wrong]
	- Admin side deactivation issues when users are created by admin ally
	- Timer not working in real-time at the Agent Side
	- Change Lead status while closing session from Dashboard > Active customers
	- [Error handling issue]-[In cobrowse live chat If user tries to send a file to contain special characters from agent to customer or vice versa then error messages incorrect]
	- Generate drop link message going to SPAM
	- [Functional issue]-[In active customer section entries comes wrong in bottom]
	- Attachment Card UI Improvement
	- [Functional issue]-[User is able to put "0" in "Auto archive lead if agents are offline (In mins) " model by copy-paste method]

  - Bugs Remaining
	- [Functional issue]-[Supervisor created through API is not visibel to admin]
	- [Functional issue]-[Supervisor created through admin ally is not able to login]
	- [Functional issue]-[most of the times in livechat of cobrowse user is not able to upload files]
	- Masking Fields sometimes doesn't work
	- [Functional issue]-[Admin console "No agent permit meeting toast" details not saved]
	- Agent connect message comes twice in case of session transfer
	- Invited agent session join chat bubble does not appear more than once
	- Screen Capture is not masking the DIV ID's

- **Campaign**
  - Features
    - Campaign Analytics should get filter based on user numbers for WhatsApp Campaign
	
  - Bugs Fixed
    - UI issue - After hovering cursor to buttons in overview page delete button gets filicker
	- If table Meta data columns are not selected then also campaign gets scheduled.  Note: selecting meta data should be made mandatory
	- UI issue - After opening the dropdown for the metadata when all option are delete for column and user open the dropdown, dropdown not open properlly
	- When any invalid file for template is been attached valid reason should be displayed why the file is not been downloaded
	- Campaign Analytics Filter - Validation is required for the date filter
	- Functionality Issue - After error message appear when user not select the input value for date, when user select value error message not get closed
	- Functionality issue - After adding URL as a template name in some cases campaign runs but campaign name not appear on overview page
	- Google Sheet exported .xlsx files do not work on Campaign
	- Functionality issue - Some campaign are send successfully but In results it not reflcting anything also audience batch count for campaign is '0'
	- Applying a stable limit to audience batch sheet
	- Need to optimize the loading time for pagination on the Campaign overview page

  - Bugs Remaining
	- Functionality issue - Untitled document name is coming on the end-user side for document type template
	- UI issue - When user Hover the cursor on overview page and campaign reports page the button have flickering issues

- **LiveChat**
  - Features
	- Same day console (NPS, etc) data download
	- Added Peak Hours Analytics Daily and Average Hourly Interaction Graph
	- FTR to be added in analytics : FTR in the reports

  - Bugs Fixed
	- [UI Issue]-[Reports]- Some columns of Abandoned chats, Missed chats, Offline chats, Login-Logout time, and Agent not ready tables get hidden when the side menu is maximized
	- [UIUX]-[Livechat Customer]-[UI issue On customer side if customer upload attachment files.]
	- [Fuctional issue]-[In PIP mode voice call Mic icon position change by clicking on mic.]
	- [Functional Issue]-Supervisor not able to save "Maximum number of customers with whom an agent can chat at a time"
	- [Functioanlity issue] - [Enable Input TextField] - Input text filed is not coming for livechat.
	- Initial questions should get display incase when user click back button on livechat form
	- Welcome messages after system message
	- [Functional Issue]-When customer end the session "LiveChat session Ended." system message is not displayed directly welcome message is displayed.

  - Bugs Remaining
	- Customer name at agent side should be "None " as shown for email Id it should not show mobile number as customer name
	- Voice call status messages overlap while scrolling.
	- [UI Issue] - [Input field] - The UI of input field is not proper when input text field is disabled from settings and trigger livechat in theme
	- [Functional error]-[Livechat Customer]-[Multiple appearances of chat with an expert message on bot refresh]
	- Several others bugs, which are yet to be resolved.

- **v6.4**

- **ChatBot**
  - Features
    - Productizing Catalog Feature for WhatsApp- Phase 1
	- Catalog Feature for WhatsApp - Phase 2
	- DIY Product Phase 1
	- Do not translate keyword feature
	
  - Bugs Fixed
    - [UI issue] - Cards in message history getting overlapped
	- [Functionality Issue] - User not able to share Bot with the sandbox credentils ID's
	- [Functionality Issue] - [Language detection] - Calendar widgets/ Video recorder
	- [Functionality issue] - Message history page UI getting distorted when apply show enteries by 100.
	- Arabic message encoding issue while translating
	- [UI issue] - [ Tooltip of the bot buttons ] - The home button tooltip is not in right place.
	- [Functionality issue] - [Custom access to bot under bot manager also for easychat dev and sandbox credentions]
	- [Functional issue] - When we use $$$ separator in bot response, the speaker speaks the $$$ as a single response.
	- [UI Issue] - [Configure Language] - Not able to edit and select the 5th and last language chips.
	- WhatsApp CSAT ping even when LiveChat is connected
	- Functionality issue - Analytics Page > Combined Analytics Global Filter > Language filter Needs Improvement
	- Language dropdown UX issue on chatbot side

  - Bugs Remaining
	- [Functional issue] - [ Intent Flow abort in other languages] - When the user selecting the child's intent in other than english language flow termination confirmation is asking.
	- [Functionality issue] - [ Advance settings] - not able to open any options when clicking on the go button it's working.
	- [Functionality issue]- [ Attachment widget] - UI issue coming when user clicks on the cross on uploading attachment.
	- [Functionality issue] - [ Language translation] - Response is not translating after being separated by $$$.
	- 'Deploy Link' is saving even with invalid url and spaces
	- [Functionality issue]-[Welcome,Authentication,Failure message formatting issue]
	- [Functionality improvement]-[When user tries to select the same language again]-[Disclaimer modal]

- **Campaign**
  - Features
    - Customized report for WhatsApp campaigns
	- New API for event based trigger in campaign
	- Enable Dynamic URL CTA and Multi-Language templates for WhatsApp Campaign
	
  - Bugs Fixed
    - UI Issue - Select Variable Modal for Message body is broken in WhatsApp Campaign
	- The campaign fails when there is a variable in the Header message
	- UI Issue - When audience batch added which not have full data the map variables field have UI issue
	- API documentation should be available in the Campaign console - DIY Subtask
	- Functionality Issue - After clicking on download template under campaign user get navigate to home page

- **Cobrowsing**
  - Features
	- Cobrowsing on third party pages - Phase 1 Outbound
	- Toggle for Modified Inbound Approach in the frontend
	- Show request date time to agent

  - Bugs Fixed
	- Reverse cobrowsing livechat iframe not loading at first launch on agent side
	- Error message is incorrect when space is entered in name field of Add User modal
	- Error message come wrong In profile section name column
	- Without "field value" masking filed saved at admin side
	- Admin side in mailer setting checkbox color is not matching with console color
	- Admin console when user save blank "Number of times exit intent should pop up" column then error message come wrong
	- Remove button is present in profile picture modal even if there is no profile picture added
	- Issues in canned responses
	- In admin side when user put zero in "Set a maximum time duration for meetings (In mins)" then not able to do schedule meeting session and total system hang
	- Delete button color is different in advance setting
	- Admin console in sandbox credentials delete modal button color not matches with theme color
	- Sometimes admin to agent and online to offline toggle does not matches with theme color
	- Agent is able to access admin setting when user copy paste the URLs
	- JS has made the website Page scrollable

  - Bugs remaining
	- Sound notification not working on IOS devices
	- CSS Override when invoking CJS on https://www.paybima.com/health-insurance
	- Most of the times in livechat of cobrowse user is not able to upload files
	- In profile section of admin side user is able to put spaces in password and save
	- Sometimes not able to put other mail id in"Email address" filed
	- Error message for From Date or To Date  missing is incorrect in all export modal present in admin, admin ally and supervisor console
	- In calendar "Add Working Timing" modal incorrect error message when Days not select in dropdown
	- Admin console when user save blank "Number of times 'Connect with an agent' auto pop up after in-activity" column then error message come wrong
	- Admin console "No agent permit meeting toast" details not saved
	- In admin side mailer setting user is able to put special character in profile section
	- Error message comes wrong when a user tries to save support document name by putting full stop
	- Sometimes unattended leads not export when set custom range
	- Admin side in Email setting user is able to set profile without selecting frequency of mail
	- Agent details not come at customer side sometimes
	- Auto Transfer Logic Enhancement
	- Agent console Microphone
	- Masking Fields sometimes doesn't work
	- Timer not working in real-time at the Agent Side.

- **LiveChat**

  - Features

	- Chat transcript email to the customer: Email optionality at the end of a conversation
	- Toggle so that special character can be allowed in text and uploaded files
	- Agent creation limitation from supervisor ends - updated (Global limit for users under LiveChatAdmin, default = 100)

 - Bugs Fixed

	- [Functionality issue] - [ Dollar sign in welcome message] - A dollar sign is coming in a welcome message when the message is divided into a separate message.
	- Auto scrolling is not happening
	- [Functional issue]-[Customer is able to trigger livechat using sticky button even previous customers NPS form is pending.]
	- [UI-UX issue]-[Agent Console]-[the appearance of system message changes on agent console and same message repeated on refresh]
	- [Functional issue]-[Feedback form of Video call should visible in customer selected language]
	- [Functional issue]-[Multiple System message for video call ended on bot refresh ]
	- [Functional issue]-[messages sent with image attachment not visible in agents archive chat history]
	- [Functional issue]-[Chat dispose form]-[placeholder changes if special characters are used.]
	- [Functional issue]-[Customer bot]-[warning system message of the malicious file should be in customer selected language.]
	- [Functional issue]-[Admin]-[NPS feedback of customer not visible in admin chat history]
	- [Functional issue]-[Customer bot]-[warning message when invalid attachment is selected should visible in customer selected language]
	- [Error handling issue]-[Incorrect error message for select days for email chat auto disposal]
	- [Functional issue]-[Web Customer]-[warning Tooltip text for previous attachment not visible in the Hindi Language]
	- [UIUX issue]-[Agent console]-[Notification for Network issue not appear as expected]
	- [UI Issue]-[Followup leads]- In followup leads, Chat History text  is going outside the Chat History button
	- [Ui issue]-[Admin console]-[Ui of admin settings toggle changed on refresh]

 - Bugs Remaining

	- [Functional Issue]-[mutli lingual]-Message typed in English is not get translated in Hebrew and Azeri(Azerbaijani) languages
	- [Functional Issue]-[mutli lingual]-In the Hebrew language, "undefined" is written on the End Chat button
	- [Functional Issue]-[mutli lingual]- Azeri(Azerbaijani) language is RTL language  which is represented in LTR direction in bot
	- Several others bugs, which are yet to be resolved.

- **v6.3**
  
- **Cobrowsing**
  - Features
	- Canned responses in cobrowsing live chat
	- Customer side feedback and end session option for app cobrowsing
	- Email Sharing for Reverse Co-browsing
	- API Docs for Agent management

  - Bugs Fixed
	- Display default URL in GDL without tinyurl API call
	- After LiveChat session ends, broken image is visible on chatbot side
    - Functional Issue-Able to copy paste dash/minus sign in maximum lead input field
	- Functional Issue-In customer mode app cobrowsing the name field is accepting spaces
	- Functional issue- In remark model at agent side asterisk sign not come in inbound and outbound
	- Functional Issue-In Add User modal, choose supervisor text in dropdown is visible even if the supervisors are already selected
	- UI Issue-Inbound analytics, tooltip is incorrect on  NPS card
	- Customer side feedback and end session option for app cobrowsing
	- Category and language validation when adding and editing supervisors
	- Cleaning code-base and removing unnecessary file
	- Support History data fix for admin account
	- Agent Management changes for role conversion
	- Add upper cap to export in custom date range reports
	- UI and document source change for API Documents

  - Bugs remaining
	- Functional issue- most of the times in livechat of cobrowse user is not able to upload files
	- JS has made the website Page scrollable
	- Sound notification not working on IOS devices
	- Functional issue -Without "field value" masking filed saved at admin side
	- Error message is incorrect when space is entered in name field of Add User modal
	- Error message come wrong In profile section name column
	- In profile section of admin side user is able to put spaces in password and save
	- Sometimes not able to put other mail id in"Email address" filed
	- Error message for From Date or To Date  missing is incorrect in all export modal present in admin, admin ally and supervisor console
	- Timer not working in real-time at the Agent Side
	- Remove button is present in profile picture modal even if there is no profile picture added
	- CSS Override when invoking CJS on https://www.paybima.com/health-insurance
	- Masking Fields sometimes doesn't work
	- Agent console Microphone

- **ChatBot**
  - Features
	- Peak Hours ( Hour-wise Analytics )
	- Revamp ChatBot home page
	- Device bifurcation (desktop/mobile device)
	- Check and update all apis in  most of the internal api's django authentication is not thier so we need find them and 
	- Peak Hours ( Hour-wise Analytics )
	- Revamp ChatBot home page
	- Device bifurcation (desktop/mobile device)
	- Block spam users on WhatsApp
	- Removing Intuitive queries log from Unanswered queries 
	- Enabling feedback option only for the flows and can be disabled for the small talks
	- Whatsapp interactive menu format feature

  - Bugs Fixed
	- Forgot password infosec point
	- Download reports-Not receiving mails
    - Self-learning not working
	- when user add child intents and save without adding bot response intent get saved
	- Flow termination message error
	- Calender widget cancel issue
	- Mic functionality not working in android
	- Message History count and view
	- Tags saved as intent name - Error message
	- Cleaning code-base and removing unnecessary file
	- Check box and date widget issue in theme-4
	- TMS for android and IOS showing categories as button as well as dropdown both
	- User interection count is come according to the category of the intents.
	- Custom Share modal options issue

  - Bugs remaining
	- By clicking Next/Previous arrow blue screen appear's on images, cards, videos UI bug
	- Formatting issues after uploading faq's from excel
	- Suggestions related to Response Widget such as enabling/disabling of input text, tooltips etc
	- Set time interval for Session Expiration is not working.
	- Some intents are not giving a response and always come in did you mean suggestions.
	- Send button tooltip issue for android
	- New tag icon gets cut off from above while hovering
	- Timer does not appear for resend code under forget password
	- Same user query 2 different bot responses

- **Campaign**
  - Features
    - Capturing push messages in chat history and update the reports
	- Campaign namespace issue
	
  - Bugs Fixed
    - Text Issues on Campaign Analytics
	- Error handling for invalid time in the Campaign Dashboard
	- After uploading the template we always display the status as "Approved"
	- Display valid errors if the format is incorrect while uploading the batch file WhatsApp  Campaign

  - Bugs Remaining
	- UI Issue - Select Variable Modal for Message body is broken in WhatsApp Campaign

- **v6.2**
  
- **LiveChat**
  - Features
	- Agent side analytics and supervisor filter in reports
	- Mobile Number and Email Field validation in Customize End Chat Form
	- Improvements in Connect with an agent form
	- Show notification to agent when his/her internet is not working

  - Bugs Fixed
	- Agent did not receive notification when new customer joins chat
	- After LiveChat session ends, broken image is visible on chatbot side
    - LiveChat not working when third party cookies are blocked on bot side

- **Cobrowsing**
  - Features
    - Exit Intent And inactivity Pop up to be url based
    - Date of id creation/ deactivation/ activation in Agent Management
    - Common Dashboard for all agents where leads drop as unassigned (Requests in Queue)
    - Add Busy status in agent management
    - Downloading  Live Chat History from frontend 
    - Daily mailer option in Email settings
    - Dyte Integration Phase 1 in CognoMeet for only Scheduled meeting use case
    
  - Bugs Fixed
    - UI Issue in cobrowse session when agent request for edit access from a customer than that modal text are not 		left-aligned at customer side
    - Sandbox User shouldn't be able to create or edit sandbox users
    - Message popup not appearing on customer side when messages are sent through chat bubble from agent
    - In agent management available agent section status come online
    - Admin ally is able to create admin ally in itself by create user via excel
    - Supervisor created through admin ally is not visible to the admin
    - If category and language based assignment is on then if we click on greeting bubble the category selection modal is not get displayed
    - Automation could have 100% accuracy
    - Suggestions for Response widgets
    - UI issues in Active Customers Dashboard
    - Supervisor can transfer more leads to agents than its specified in maximum leads
    - Created agent/supervisor from admin ally not available in admin export
    - In mailer, text of Invalid Access is being shown in tables and graph
	- Changes in Agent Management
	- Incorrect "Lead-Type" for reverse and GDL session
	- Categores are not getting exported inside Support History
	- Agent remarks not register in declined leads of support history
	- Optimise the API which is getting called on the dashboard of Cobrowsing
	- Inbound Cobrowsing - Toggling not reflected at Agent Side
 
  - Bugs Remaining
    - Timer not working in real-time at the Agent Side
	- Masking Fields sometimes doesn't work
	- Most of the times in livechat of cobrowse user is not able to upload files
	- Sound notification not working on IOS devices
	- CSS Override when invoking CJS on https://www.paybima.com/health-insurance

- **ChatBot**
  - Features
    - GBM bugs and feature
    - Viber Integration Phase 2 Final
    - Unique session indication in bot window and message history - Phase 1
    - Redesign Chatbot analytics Page
    - Create Plugin for Ionic app 
    - Query Response time optimisations - Analysis
    - iOS Chatbot app development
    
  - Bugs Fixed
    - When user add file upload response widget it does not work
    - Checkbox for manage intent page not inline with other fields
    - Instagram sending failure message on unsending a previously sent message
    - Emoji Bot Response (bot responding "I'm not sure" message on sending emoji)
    - when user enable CSAT in quick bot creation all channel which have CSAT not get selected in setting
    - Calendar and Time picker issue
    - Tooltip placement (Tooltip placement for microphone in theme 2 modified)
    - Automation could have 100% accuracy
    - Suggestions for Response widgets
    - Intents appear in all channels even though the channel is deselected
    - Special characters in intent name results in special character in training questions which is not allowed
    - Bot messages are automatically getting scrolled when uploading any file
    - Quick bot creation app.getcogno Bugs
    - No call recording in user chat history
    - Clicking on back button for twitter channel bot give 'page not found' error
    - Wrong intent is selecting when select intent by click on enter in suggestion list
    - stop words - response issue (Bot giving suggestions on stop words)
    - Bot response formatting in Whatsapp
    - The object for first intent is not getting created in APIElapsedTimes
    - Spell checker Analysis and Optimisation
    - Time widget UI cutting when open in IOS (Mozilla firefox)
    - auto fix model comes the first time but doesn't work and second time model is not coming
	- Every message going under translation issue
	- CSAT words below emoji's for theme-4
	- Change language response and bot response
	- Configure email for whatsapp should appear in front of field
	- The response of intent enabling in initate after welcome converstion is that an internal issue is coming
	- Save web channel not working bug
	- Mic not getting disabled on clicking home button

  - Bugs Remaining
    - Same user query 2 different bot responses
	- Not getting bot response when calling intent manually and if bot have more than 3k intents
	- Bot loading Optimisation
	- Livechat UI issue
	- Suggestion List not working
	- Some intents are not giving a response and always come in did you mean suggestions
	- The fonts of urdu are different
	- Bot response after pressing home button
	- Check box and date widget issue in theme-4
	- 500 error when opened multiple tabs

- **Campaign**
 - Features
    - Add caller id and app id in Voice Campaign from frontend
    - Voice Bot disposition

 - Bugs Fixed
    - Template Variables for the whatsapp external campaign doesn't follow right naming conventions
	- WhatsApp Campaign Audience Upload is not accepting International Mobile Numbers
	- Issues in WhatsApp Campaign Schedule & Audience batch
	- An invalid template campaign is marked as Partially Completed if use an Invalid number

 - Bugs Remaining
	- Magic file extension checker returns .zip when batch uploaded from linux in CampaignApp


- **v6.1**
  
- **LiveChat**
  - Features
	- Exposable APIs for LiveChat Analytics
	- Calendar functionality Upgradation

  - Bugs Fixed
	- Automatic page refresh at admin side every few seconds
	- Not able to send or receive attachments in WhatsApp Channel
	- Agent able to access some admin-only pages.
	- Agent logged-in count is incorrect in analytics.
	- Customer able to communicate through voice call, video call or cobrowsing even after his/her chat is reported

- **Cobrowsing**
  - Features
	- Call transfer option during cobrowsing session(only works when Enable transfer toggle is onn)
	- Cobrowsing Request Start Time, Waiting Time and Summary has been added in MIS
	- Chat notifications on the browser
	- Session end url has been added in the report
  
  - Bugs Fixed
	- UI issues related to Dropdown arrow is fixed in advanced settings
	- Functional issue related to document icon in reverse cobrowsing is fixed
	- UI issues related to dropdown is fixed on Admin, Supervisor and Admin-Ally side
	- UI issues related to the filter button in follow up leads export is fixed
	- UI issues related to the column name colour in calendar is fixed
	- UI issue related to the file name colour in captured screenshot modal in support history is fixed
	- Functional issue related to top and bottom navbar position is fixed
	- Functional issue related to dragable in Product category is fixed
	- UI issue related to checkbox colour(matched to theme colour) is fixed in the document section
	- Functional issue in reverse cobrowsing when agent cancel the lead from their side before joining customer the 	lead does not come in unattended leads is fixed.
	- Functional issue related to Masked field warning showing even without an agent being connected is fixed.
	- UI issue in Analytics Meeting Initiated by customer (Floating button/ Icon) ,Meeting Initiated by customer (Greeting bubble) ,Meeting Initiated by customer(Inactivity Pop-up) cards text is going out of card is fixed
	- Functional issue related to Captured screenshot comes blank at agent side is fixed
	- Toast issue when agent ends the session from the console is fixed
	- Functional issue related to link is not clickable when agent send support document with link to customer is fixed
	- Functionality issue related to Chat bubble message stays at customer side after ending and restarting the session is fixed
	- Functional issue When navbar postion set right screen recording button not works properly is fixed
	- Text issue related to Audit Trail action name is fixed
	- Functional issue related to In Audit Trail export sheet is fixed
	- Functional issue when user minimise the browser agent side, agent automatically goes offline is fixed
	- Functional issue related to Broken Access control in file access management is fixed
	- Functional issue in invite agent option available in both cobrowsing and video call interface while doing Video calling while co-browsing is fixed

  - Bugs Remaining
	- Sometimes certain documents are not getting uploaded in livechat
	- Timer not working in real-time at the Agent Side
	- Incorrect Lead type in session details for reverse cobrowsing
	- Inbound Cobrowsing toggling not reflected at Agent Side
	- Masking Fields sometimes doesn't work
	- Location comes wrong in show agent detail modal on customer side
	- Sound notification not working on IOS devices

- **ChatBot**
  - Features
	- Quick Bot Creation Flow 
	- Viber integration
	- New Bot theme for FAQ bot
	- Intent Bubble Customization For custom Webpages
	- Chatbot Input field toggalable
	- Multi Factor Authentication
	- AMP iFrame Overlay Issue
	- All text and buttons to be aligned on the left side
	- Services Specified Chatbot on Mobile App
	- CSAT - Have words added below emojis

  - Bugs Fixed
	- CSAT Default Bot Response Order & Emoji Bot Response
	- Getting 404 page not found when click on Microsoft channel
	- Getting blank message image in bot when click on intent level feedback and without clicking on radio buttons send message
	- Ui getting distorted of manage intent page
	- Page getting hanged when clicking on the user-id link in message history of microsoft
	- Welcome banner - Dropdown issue
	- Language detection - Web and app.getcogno
	- deleted intents are still showing in suggestions
	- Build bot takes too long to load and no suggestions even after build bot
	- Bot logo overlapping with interface
	- Speak out bot response
	- Confirm Reset
	- For long text in table after calling table appered partially
	- Not getting First name and Last name when entered for login
	- Child intent/Confirm reset in another language issue
	- App.getcogno issues - Telegram channel
	- App.getcogno issues - Whatsapp channel - Ameyo
	- Web URL landing issue in other languages
	- Issues in GBM and RCS

  - Bugs Remaining
	- Attachemnt response widget - Flow abort - Bot messages are automatically getting scrolled when uploading any file
	- Emoji bot response
	- Speak out bot response


- **v5.9**
  
- **LiveChat**
  - Features
	- Ability to add multiple blacklisted keywords at once
	- Multiple agent select in filters in Performance report and Chat history section
	- Export user functionality in Manage Users

  - Bugs Fixed
	- Customer Source not visible during LiveChat in mobile view
	- Successfully raised ticket is not visible in Previously Raised Tickets section
	- Chat termination source is not visible in Chat History when chat is a transferred chat.
	- Voice Call status messages not reflected in console and chat history.
	- Updated npm packages to fix security issues
	- Added encryption of messages before transferring through websocket (VAPT fix)

- **Cobrowsing**
  - Features
	- For Admin ally/Supervisor added deactivate option in agent management
	- Document co-view in livechat has been made toggleable
	- Cobrowse settings page has been completely revamped
	- Unattended leads auto transfer count is now configurable
	- Assigning of unattended leads to agents under same supervisor has been added
	- Audit trail of the agents to whom an unattended lead is being transferred is now being maintained
	- Sound notification has been added for the greeting bubble and for all incoming livechat messages (works only when chat bubble functionality is enabled)
  
  - Bugs Fixed
	- UI issues related to theme colour have been fixed in "Agent Management"
	- Livechat window sizes fixed for reverse cobrowsing
	- Chat bubble icon upload issue fixed where if user uploads and icon, clicks on the reset button and then again tries to upload the same icon then it was not getting uploaded
	- In sandbox credentials, user was not able to select a date upto which he wants to extend the expiry of the credentials
	- In sandbox credentials, after clicking on the delete icon, save was coming. Now this issue has been fixed
	- UI issue fixed where theme colour was not reflecting for support document modal on agent side
	- Validation has been added for the "Deploy Link" field of the "Chrome Extension" setting
	- Chat window not working on agent side during a session
	- In Safari, Copy CJS and Copy Script buttons were not working
  
  - Bugs Remaining
	- When user reduces the window size, the Online toggle shifts to Offline
	- Sometimes certain documents are not getting uploaded in livechat

- **ChatBot**
  - Features
	- User ID wise data for intent-wise charflow 
	- Multiple agent select in filters in Performance report and Chat history section
	- Multilingual capability for all channels
	- Console Different Language Improvements - Phase 2
	- Handling Global Events: Silence detection, Repeat, Loop detection
	- Add other channels in Campaign API
	- Explosable APIs for ChatBot Analytics

  - Bugs Fixed
	- No Intent icon for Go back in other languages
	- Automated testing for default intents
	- Combine analytics- Form assist - Getting internal server error when clicking on the    download button of form assist
	- Fixed mailer Analytics average number of session session paramter bug
	- Moved EasyChat Analytics files to secured files for secure file management system (VAPT)
	- Getting Failure response in other than the English language in language detection and   read more/Read less.
	- RCS recommendation and choices Bug
	- Widget and ConfirmReset issue
	- Lead Generation automatically swiching to english if user change language
	- Dropped percentage for conversion analytics (Flow completion rate) giving negative value

  - Bugs Remaining
	- Web URL landing issue in other languages
	- Country code dropdown improvements
	- Not getting bot response when calling intent manually and if bot have more than 3k intents

- v2.2
  - Features
	- Automated Testing of Live Chat console
	- EasyChat APIs can be hit from certain server IPs only
	- Flow child buttons should be disabled when clicked but the normal intent buttons shouldn't be disabled when clicked
	- Edit and delete button in ticket categories (TMS)
	- Lead Generation module
	- Attachment upload should appear in the message history of users along with the link to the attachment
	- The FormAssist intent shouldn’t go through intent identification
	- Make the API integration functionality in EasyChat console userfriendly (make documentation)
	- Make the API integration functionality in EasyChat console to allow multiple programming languages - Java
	- "Add table" option in the EC console for bot response
	- Pagination where list of intents is shown
	- There should be a filter of FormAssist intents in Manage intents page
	- There should be a way to know whether FA and easysearch is enabled in a bot or not (an icon in the bot in manage bots page)
	- Bot suggestions should also be shown appropriately when a user writes abbreviations in the text box whose word mappers are already present in the bot 
	- Small talk added by default in bot
	- Encryption in the database level of entire platform (easychat, livechat etc)
	- Every API call should be logged with time stamp, request packet, response packet
	- formassist analytics
	- Make the API integration functionality in EasyChat console to allow multiple programming languages - Javascript
	- Make the API integration functionality in EasyChat console to allow multiple programming languages - PHP

  - Bugs Remaining
	- In create bot with excel, when the user choose type of excel file as  FAQs and upload excel of userflow, error has been shown. User should be navigated to bottom automatically when the error has been occured. - (Suggestion))
	- Same tag id should not be allowed in form assist
	- Validations in lead generation
	- Order of attachments in the message history is decremented
	- Form assist intents download button is not working in Usage analytics
	- Encoding error in message history while using export with dates (Excel) - easychat.allincall.in
	- Blank space is appearing in more info -> Easychat data collection   -easychat.allincall.in
	- Validations in lead generation - URL- easychat.allincall.in
	- Wrong chat history is showing in audit trail  - URL- easychat.allincall.in
	- In the chat room, chat with expert message is coming more than 2 times for agent when the customer connects again with the agent. - URL- easychat.allincall.in
	- Unable to edit the ticket in ticket categories
 
  - Bug Fixed
	- The bot should close with the same animation with which it is opening
	- Automation testing corrections and changes
	- Empty Add variation while creating intent
	- Automating testing - default bot should not be selected after completion of automation testing
	- Bot speak out response
	- Bot export-import bug : Order of children of an intent in an imported bot is reverse of the originally made bot which was exported
	- Bot export-import bug : While exporting a bot, multiple unwanted details are getting in the export json
	- When Automated testing is completed, the user doesn't get to know
	- In automated testing, user doesn't get to know which bot was tested
	- Apostrophe (') is appearing as unicode in message history (screenshot attached)
	- While adding a welcome banner, if you put a link without https (eg. bing.com), the link is not opening and an error page is opened
	- New intent which is created by the user should be saved at the top of the intent list.
	- When a user is neither a Livechat agent not manager, Livechat option shouldn't appear in his/her console
	- The "Kindly fill the following details" bot message bubble should not appear as shown in the screenshot attached
	- The "Kindly enter the ticket ID" bot message bubble should not appear as shown in the screenshot attached
	- When I'm on self learning and assessing the self learning data of a bot and then create a new intent from a user query directly from self learning section, wrong bot is being selected in create intent section
	- Agent is assumed to be online when he closes his browser directly without logging out
	- Extract FAQs file not opening properly in Ubuntu (working in Mac and Windows)
	- Data model reading issue
	- Logs don't come properly in Admin console - They sometimes come from top, sometimes from bottom, and may take lot of time to load
	- While saving the names of Processors, only unique names should be allowed to be saved
	- Edit (Save button) in ticket categories
	- Delete button in ticket categories
	- In form assist, bot is poping up when the user is stuck in a particular but intent response in the bot is not coming.  {Contains screenshot}
	- Extract Faqs as excel - 500 is showing when the user clicks on extract faqs as excel in export/import section.
	- On exporting the analytics dashboard, the exported PDF doesn't render properly
	- User should not be able to allow or type any message after the form has been provided to him/her in the chatbot. (Ask something field should be Disable)
	- The TMS admin is unable to edit the duration of an already existing ticket category
	- The error message appearing when an agent is not assigned to a ticket should be proper
	- When a long answer is given by bot, the scroll comes towards the end. It should scroll to the user's query with a "Read more" at the end of truncated bot reply
	- Deleted Intents are getting exported into Excel
	- Bugs in "Add table" option in the EC console for bot response
	- Word mappers
	- Validations in Supervisor
	- While creating an excel with bot when the intents are more than 200 and when the user  clicks on 2nd page default bot is coming
	- Deleted bots should not be seen in ticket categories for manager in TMS
	- Validations while creating new agent
